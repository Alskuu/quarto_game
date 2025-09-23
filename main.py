# main.py
import time
import os
import json
import argparse
import math
import multiprocessing as mp
from tqdm import tqdm

import partie
from joueurs.RandomPlayer import RandomPlayer
from joueurs.HumanPlayer import HumanPlayer
from joueurs.MinMax_Player import MinMax
from quarto_gui import QuartoGUI

BATCH_SIZE = 16
RESULTS_PATH = "resultats.json"
RESULTS_CI_PATH = "resultats_cibisss_prof_3.json"

# Création de fonctions permettant d'arrêter les parties lorsque nous avons une bonne confiance dans nos résultats
def z_from_conf(level: float) -> float:
    """Renvoie la valeur z, c'est-à-dire les quantiles de la loi normale standard N(0,1) 
    pour un niveau de confiance (0.90, 0.95, 0.99).
    """
    table = {0.90: 1.6448536269514722, 0.95: 1.959963984540054, 0.99: 2.5758293035489004}
    return table.get(level, table[0.95])

def wilson_half_width(successes: int, trials: int, z: float) -> float:
    """Demi-largeur de l'IC de Wilson pour une proportion (succès/trials)."""
    if trials <= 0:
        return float('inf')
    p_hat = successes / trials
    z2 = z * z
    denom = 1 + z2 / trials
    # center = (p_hat + z2/(2*trials)) / denom  # utile si tu veux le centre
    margin = (z * math.sqrt((p_hat * (1 - p_hat) + z2 / (4 * trials)) / trials)) / denom
    return margin

def estimate_ci(wins: int, draws: int, games: int, conf_level: float, exclude_draws: bool):
    """Calcule p̂ et demi-largeur (Wilson) selon l'option d’exclusion des nulles.
    ci signifie confidence interval"""
    z = z_from_conf(conf_level)
    if exclude_draws:
        decisives = games - draws
        p_hat = (wins / decisives) if decisives > 0 else float('nan')
        half = wilson_half_width(wins, decisives, z)
        denom_used = decisives
    else:
        p_hat = wins / games if games > 0 else float('nan')
        half = wilson_half_width(wins, games, z)
        denom_used = games
    return p_hat, half, denom_used

# Etape de la gestion des JSONs
def load_results(path: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # fichier corrompu -> on repart sur du propre
            return {}
    return {}

def accumulate(results: dict, key: str, add_games: int, add_wins: int, add_draws: int,
               add_tours_total: float, add_time_total_sec: float) -> dict:
    """Cumule des totaux pour un matchup donné."""
    bucket = results.setdefault(key, {
        "games": 0,
        "wins": 0,
        "draws": 0,
        "tours_total": 0.0,
        "total_time_sec": 0.0
    })
    bucket["games"] += add_games
    bucket["wins"] += add_wins
    bucket["draws"] += add_draws
    bucket["tours_total"] += add_tours_total/add_games
    bucket["total_time_sec"] += add_time_total_sec
    return results

# Passage aux matchs

def run_matchup(args):
    """Exécute une partie et retourne le résultat."""
    player1_cls, player1_args, player2_cls, player2_args = args
    game = partie.Quarto()
    game.set_players(
        (player1_cls(game, *player1_args), player2_cls(game, *player2_args))
    )
    time_start = time.time()
    winner = game.run()
    time_end = time.time()
    time_taken = time_end - time_start
    tour = game.check_tour() # On a fait une erreur ici, le run devrait renvoyer le numéro du dernier tour si on veut avoir le numéro, je me suis rendu compte de l'erreur en rédigeant le rapport final après avoir fait tourné pendant plusieurs heures les parties, donc je ne me relancerai pas là-dedans.
    return winner, tour, time_taken

def run_multiple_games(n_games, player1_cls, player1_args, player2_cls, player2_args, n_jobs=mp.cpu_count()):
    """Exécute n_games en parallèle avec multiprocessing, retourne des TOTAUX (pas des moyennes)."""
    tasks = [(player1_cls, player1_args, player2_cls, player2_args)] * n_games
    with mp.Pool(processes=n_jobs) as pool:
        results = list(
            tqdm(pool.imap_unordered(run_matchup, tasks), total=n_games)
        )

    wins = sum(1 for r, _, _ in results if r == 1)
    draws = sum(1 for r, _, _ in results if r == -1)
    tours_total = sum(t for _, t, _ in results)
    time_total = sum(t for _, _, t in results)
    return wins, draws, tours_total, time_total

# Checkpoint toutes les 100 parties pour garder des informations si l'ordinateur s'éteint ainsi que pour suivre les résultats des parties en direct

def play_series_with_checkpoints(series_name: str, n_games: int,
                                 player1_cls, player1_args,
                                 player2_cls, player2_args,
                                 batch_size: int = BATCH_SIZE):
    """Joue n_games en batchs, met à jour le JSON à chaque batch (cumul)."""
    remaining = n_games
    while remaining > 0:
        cur = min(batch_size, remaining)
        wr, dr, tours_total, time_total = run_multiple_games(
            cur, player1_cls, player1_args, player2_cls, player2_args
        )

        # Charger, cumuler, écrire immédiatement (checkpoint)
        results = load_results(RESULTS_PATH)
        results = accumulate(results, series_name, cur, wr, dr, tours_total, time_total)
        with open(RESULTS_PATH, "w") as f:
            json.dump(results,f, indent=4)

        # Affichage d’un petit récap en direct
        print(f"[{series_name}] Batch fini : +{cur} games, +{wr} wins, +{dr} draws")

        remaining -= cur

# Variante avec des intervalles de confiance :
def play_until_ci_with_checkpoints(series_name: str,
                                   target_halfwidth: float,
                                   conf_level: float,
                                   player1_cls, player1_args,
                                   player2_cls, player2_args,
                                   batch_size: int = BATCH_SIZE,
                                   exclude_draws: bool = False,
                                   max_games: int = 200000):
    """
    Joue par batchs et s'arrête quand la demi-largeur de l'IC de Wilson
    sur p(P1 gagne) <= target_halfwidth au niveau conf_level.
    - exclude_draws=False : p = P(victoire) sur toutes les parties (les nulles comptent comme 'non-gagnées').
    - exclude_draws=True  : p = P(victoire | partie décisive), nulles exclues du dénominateur.
    Checkpoint JSON après chaque batch (accumulation des totaux).
    """
    total_games_before = 0
    # Charger l'état existant si on relance (reprise sur accident/arrêt)
    results = load_results(RESULTS_PATH)
    if series_name in results:
        b = results[series_name]
        total_games_before = int(b.get("games", 0))
        print(f"[{series_name}] Reprise : déjà {total_games_before} parties cumulées.")

    while True:
        results = load_results(RESULTS_CI_PATH)
        bucket = results.get(series_name, {"games": 0, "wins": 0, "draws": 0, "tours_total": 0.0, "time_total_sec": 0.0})
        games_so_far = int(bucket["games"])
        wins_so_far = int(bucket["wins"])
        draws_so_far = int(bucket["draws"])

        if games_so_far >= max_games:
            print(f"[{series_name}] Arrêt (max_games atteint : {max_games}).")
            break

        cur = min(batch_size, max_games - games_so_far)
        wr, dr, tours_total, time_total = run_multiple_games(cur, player1_cls, player1_args, player2_cls, player2_args)

        # Checkpoint (cumuler et écrire)
        results = accumulate(results, series_name, cur, wr, dr, tours_total, time_total)
        # On calcule l'IC sur le bucket à jour avant d’écrire la méta
        b = results[series_name]
        p_hat, half, denom_used = estimate_ci(
            wins=int(b["wins"]),
            draws=int(b["draws"]),
            games=int(b["games"]),
            conf_level=conf_level,
            exclude_draws=exclude_draws
        )

        # On ajoute une section 'meta' pour visualiser l’état de l’IC
        results[series_name + " (meta)"] = {
            "confidence_level": conf_level,
            "target_halfwidth": target_halfwidth,
            "exclude_draws": exclude_draws,
            "p_win_estimate": p_hat,
            "halfwidth": half,
            "denominator_used": denom_used,
            "games_total": int(b["games"]),
            "wins_total": int(b["wins"]),
            "draws_total": int(b["draws"]),
            "losses_total": int(b["games"] - b["wins"] - b["draws"]),
            "tours_moyens": (b["tours_total"] / b["games"]) if b["games"] else 0.0,
            "temps_moyen_sec": (b["total_time_sec"] / b["games"]) if b["games"] else 0.0
        }

        print(f"[{series_name}] Batch +{cur} => games={b['games']}, wins={b['wins']}, draws={b['draws']}, "
              f"p̂={'{:.4f}'.format(p_hat) if isinstance(p_hat, float) else p_hat} ± {half:.4f} (niveau {int(conf_level*100)}%, denom={denom_used})")

        with open(RESULTS_CI_PATH, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        # Critère d'arrêt
        if denom_used > 0 and half <= target_halfwidth:
            print(f"[{series_name}] Critère atteint : demi-largeur {half:.4f} ≤ {target_halfwidth:.4f}.")
            break

# main et GUI
 
def main():
    if args.ci:
        # --- MODE ARRÊT ADAPTATIF ---
        # Série 1 : Random vs MinMax(1)
        '''
        series_1 = "negamax_placement_specialized vs negamax_complete"
        print(f"Lancement (CI) : {series_1}")
        play_until_ci_with_checkpoints(series_1, args.ci_halfwidth, args.ci_level,
                                       MinMax, (2,), MinMax, (1,),
                                       batch_size=BATCH_SIZE,
                                       exclude_draws=args.exclude_draws,
                                       max_games=args.max_games)
        
        series_2 = "negamax_placement_specialized vs minmax2"
        print(f"Lancement (CI) : {series_2}")
        play_until_ci_with_checkpoints(series_2, args.ci_halfwidth, args.ci_level,
                                       MinMax, (2,), MinMax, (5,),
                                       batch_size=BATCH_SIZE,
                                       exclude_draws=args.exclude_draws,
                                       max_games=args.max_games)

        # Série 3 : MinMax(1) vs MinMax(3)
        series_3 = "minmax2 vs negamax_placement_complete"
        print(f"Lancement (CI) : {series_3}")
        play_until_ci_with_checkpoints(series_3, args.ci_halfwidth, args.ci_level,
                                       MinMax, (5,), MinMax, (2,),
                                       batch_size=BATCH_SIZE,
                                       exclude_draws=args.exclude_draws,
                                       max_games=args.max_games)'''

         # Série 5 : MinMax(3) vs MinMax(3)
        series_4= "minmax1 vs negamax_placement_specialized"
        print(f"Lancement (CI) : {series_4}")
        play_until_ci_with_checkpoints(series_4, args.ci_halfwidth, args.ci_level,
                                       MinMax, (4,), MinMax, (2,),
                                       batch_size=BATCH_SIZE,
                                       exclude_draws=args.exclude_draws,
                                       max_games=args.max_games)
        series_4a="negamax_placement_specialized vs minmax1"
        print("Lancement (CI) ",series_4a )
        play_until_ci_with_checkpoints(series_4a, args.ci_halfwidth, args.ci_level,
                                       MinMax, (2,), MinMax, (4,),
                                       batch_size=BATCH_SIZE,
                                       exclude_draws=args.exclude_draws,
                                       max_games=args.max_games)
        
        # Série 5 : MinMax(3) vs MinMax(3)
        series_5= "minmax1 vs negamax_complete"
        print(f"Lancement (CI) : {series_5}")
        play_until_ci_with_checkpoints(series_5, args.ci_halfwidth, args.ci_level,
                                       MinMax, (4,), MinMax, (1,),
                                       batch_size=BATCH_SIZE,
                                       exclude_draws=args.exclude_draws,
                                       max_games=args.max_games)
        series_5a="negamax_complete vs minmax1"
        print(f"Lancement (CI) : {series_5a}")
        play_until_ci_with_checkpoints(series_5a, args.ci_halfwidth, args.ci_level,
                                       MinMax, (1,), MinMax, (4,),
                                       batch_size=BATCH_SIZE,
                                       exclude_draws=args.exclude_draws,
                                       max_games=args.max_games)
        
    else:
        # Mode 
        n_games = 1000  # total (sera joué en batchs BATCH_SIZE)
        # Série 1
        series_1 = "Random vs negamax_selection_specialized"
        print(f"Lancement de la série : {series_1}")
        play_series_with_checkpoints(series_1, n_games, MinMax, (1,), MinMax, (3,))
        # Série 2
        series_2 = "negamax_complete vs negamax_placement_specialized"
        print(f"Lancement de la série : {series_2}")
        play_series_with_checkpoints(series_2, n_games, MinMax, (1,), MinMax, (2,))
        # Série 3
        series_3 = "negamax_placement_specialized vs negamax_selection_specialized"
        print(f"Lancement de la série : {series_3}")
        play_series_with_checkpoints(series_3, n_games, MinMax, (2,), MinMax, (3,))


def main_gui():
    """Mode graphique : une seule partie affichée en temps réel"""
    game = partie.Quarto()
    game.set_players((RandomPlayer(game), RandomPlayer(game)))
    gui = QuartoGUI(game, image_folder="images_pieces")
    game.add_observer(gui.on_update)
    game.run()
    gui.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ci", action="store_true",
                    help="Mode arrêt adaptatif : s'arrête quand l'IC (Wilson) atteint la demi-largeur cible.")
    parser.add_argument("--ci-level", type=float, default=0.95,
                        help="Niveau de confiance (ex: 0.95).")
    parser.add_argument("--ci-halfwidth", type=float, default=0.08,
                        help="Demi-largeur cible (ex: 0.08 pour ±8%).")
    parser.add_argument("--exclude-draws", action="store_true",
                        help="Estimer p = P(win | décisif) en excluant les nulles du dénominateur.")
    parser.add_argument("--max-games", type=int, default=1200,
                        help="Garde-fou : nombre maximum de parties.")
    parser.add_argument("--gui", action="store_true", help="Run the graphical interface")
    args = parser.parse_args()

    if args.gui:
        main_gui()
    else:
        main()
