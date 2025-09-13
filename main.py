# main.py
import time
import os
import json
import logging
import argparse
from joueurs import MinMax_Player
import partie
import multiprocessing as mp
from joueurs.RandomPlayer import RandomPlayer
from joueurs.HumanPlayer import HumanPlayer
from joueurs.MinMax_Player import MinMax
from tqdm import tqdm
from quarto_gui import QuartoGUI

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
    tour= game.check_tour()
    return winner, tour, time_taken


def run_multiple_games(n_games, player1_cls, player1_args, player2_cls, player2_args, n_jobs=mp.cpu_count()):
    """Exécute n_games en parallèle avec multiprocessing."""
    tasks = [(player1_cls, player1_args, player2_cls, player2_args)] * n_games

    with mp.Pool(processes=n_jobs) as pool:
        results = list(
            tqdm(
                pool.imap_unordered(run_matchup, tasks),
                total=n_games
            )
        )

    wr = sum(1 for r, _, _ in results if r == 1)
    dr = sum(1 for r, _, _ in results if r == -1)
    tours_moyen = sum(t for _,t,_ in results)/len(results)
    time_taken = sum(t for _,_,t in results)/len(results)
    return wr, dr, tours_moyen, time_taken


def main():
    n_games = 4
    resultats_path = "resultats.json"
    if os.path.exists(resultats_path):
        with open(resultats_path, "r") as f:
            resultats= json.load(f)
    else:
        resultats = {}
    
    wr, dr, tours_moyens, mean_time_taken = run_multiple_games(n_games, RandomPlayer, (), RandomPlayer, ())
    resultats.setdefault("Random vs Random", {})
    resultats["Random vs Random"]["wins"]= wr
    resultats["Random vs Random"]["draws"] = dr
    resultats["Random vs Random"]["tours_moyens"]= tours_moyens
    resultats["Random vs Random"]["temps moyen pris en secondes"]= mean_time_taken

    with open(resultats_path, "w") as f:
        json.dump(resultats,f,ensure_ascii=False, indent=2)
    # Random vs MinMax(3)
    print("Lancement de la partie de Random vs negamax_selection_specialized")
    wr, dr, tours_moyens, mean_time_taken = run_multiple_games(n_games, RandomPlayer, (), MinMax, (1,))
    print(f"Random vs negamax_selection_specialized ({n_games} games): wins: {wr}, draws: {dr}")
    resultats.setdefault("Random vs negamax_selection_specialized", {})
    resultats["Random vs negamax_selection_specialized"]["wins"]= wr
    resultats["Random vs negamax_selection_specialized"]["draws"] = dr
    resultats["Random vs negamax_selection_specialized"]["tours_moyens"]= tours_moyens
    resultats["Random vs negamax_selection_specialized"]["temps moyen pris en secondes"]= mean_time_taken
    with open(resultats_path, "w") as f:
        json.dump(resultats,f,ensure_ascii=False, indent=2)
    
    # MinMax(1) vs MinMax(2)
    print("Lancement de la partie de negamax_complete vs negamax_placement_specialized")
    wr, dr, tours_moyens, mean_time_taken = run_multiple_games(n_games, MinMax, (1,), MinMax, (2,))
    print(f"negamax_complete vs negamax_placement_specialized ({n_games} games): wins: {wr}, draws: {dr}")
    resultats.setdefault("negamax_complete vs negamax_placement_specialized", {})
    resultats["negamax_complete vs negamax_placement_specialized"]["wins"]= wr
    resultats["negamax_complete vs negamax_placement_specialized"]["draws"] = dr
    resultats["negamax_complete vs negamax_placement_specialized"]["tours_moyens"]= tours_moyens
    resultats["negamax_complete vs negamax_placement_specialized"]["temps moyen pris en secondes"]= mean_time_taken
    with open(resultats_path, "w") as f:
        json.dump(resultats,f,ensure_ascii=False, indent=2)

    # MinMax(2) vs MinMax(3)
    print("Lancement de la partie de negamax_complete vs negamax_placement_specialized")
    wr, dr, tours_moyens, mean_time_taken = run_multiple_games(n_games, MinMax, (2,), MinMax, (3,))
    print(f"negamax_placement_specialized vs negamax_selection_specialized ({n_games} games): wins: {wr}, draws: {dr}")
    resultats.setdefault("negamax_placement_specialized vs negamax_selection_specialized", {})
    resultats["negamax_placement_specialized vs negamax_selection_specialized"]["wins"]= wr
    resultats["negamax_placement_specialized vs negamax_selection_specialized"]["draws"] = dr
    resultats["negamax_placement_specialized vs negamax_selection_specialized"]["tours_moyens"]= tours_moyens
    resultats["negamax_placement_specialized vs negamax_selection_specialized"]["temps moyen pris en secondes"]= mean_time_taken
    with open(resultats_path, "w") as f:
        json.dump(resultats,f,ensure_ascii=False, indent=2)


def main_gui():
    """Mode graphique : une seule partie affichée en temps réel"""
    game = partie.Quarto()
    game.set_players((RandomPlayer(game), RandomPlayer(game)))
    gui = QuartoGUI(game, image_folder="images_pieces")
    
    # Ajouter l'observateur de l'interface graphique au jeu
    game.add_observer(gui.on_update)

    # Lancer la partie dans un thread pour ne pas bloquer Tkinter
    game.run()

    gui.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=2, help='increase log verbosity')
    parser.add_argument('-d',
                        '--debug',
                        action='store_const',
                        dest='verbose',
                        const=2,
                        help='log debug messages (same as -vv)')
    parser.add_argument("--gui", action="store_true", help="Run the graphical interface")


    args = parser.parse_args()

    if args.verbose == 0:
        logging.getLogger().setLevel(level=logging.WARNING)
    elif args.verbose == 1:
        logging.getLogger().setLevel(level=logging.INFO)
    elif args.verbose == 2:
        logging.getLogger().setLevel(level=logging.DEBUG)
    if args.gui:
        main_gui()
    else:
        main()
    

## NOUVELLE ETAPE : run_cli et run_gui à rendre disponible, une fois cela réalisé : tout est bon !!