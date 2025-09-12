# main.py

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
    winner = game.run()
    tour= game.check_tour()
    return winner, tour


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

    wr = sum(1 for r, _ in results if r == 1)
    dr = sum(1 for r, _ in results if r == -1)
    tours_moyen = sum(t for _,t in results)/len(results)
    return wr, dr, tours_moyen


def main():
    n_games = 4
    resultats_path = "resultats.json"
    if os.path.exists(resultats_path):
        with open(resultats_path, "r") as f:
            resultats= json.load(f)
    else:
        resultats = {}
    
    wr, dr, tours_moyens = run_multiple_games(n_games, RandomPlayer, (), RandomPlayer, ())
        
    # Random vs MinMax(3)
    print("Lancement de la partie de Random vs MinMax3")
    wr, dr, tours_moyens = run_multiple_games(n_games, RandomPlayer, (), MinMax, (1,))
    print(f"Random vs MinMax3 ({n_games} games): wins: {wr}, draws: {dr}")
    resultats.setdefault("Random vs MinMax3", {})
    resultats["Random vs MinMax3"]["wins"]= wr
    resultats["Random vs MinMax3"]["draws"] = dr
    resultats["Random vs MinMax3"]["tours_moyens"]= tours_moyens
    with open(resultats_path, "w") as f:
        json.dump(resultats,f,ensure_ascii=False, indent=2)
    
    # MinMax(1) vs MinMax(2)
    print("Lancement de la partie de MinMax1 vs MinMax2")
    wr, dr, tours_moyens = run_multiple_games(n_games, MinMax, (1,), MinMax, (2,))
    print(f"MinMax1 vs MinMax2 ({n_games} games): wins: {wr}, draws: {dr}")
    resultats.setdefault("MinMax1 vs MinMax2", {})
    resultats["MinMax1 vs MinMax2"]["wins"]= wr
    resultats["MinMax1 vs MinMax2"]["draws"] = dr
    resultats["MinMax1 vs MinMax2"]["tours_moyens"]= tours_moyens
    with open(resultats_path, "w") as f:
        json.dump(resultats,f,ensure_ascii=False, indent=2)

    # MinMax(2) vs MinMax(3)
    print("Lancement de la partie de MinMax1 vs MinMax2")
    wr, dr, tours_moyens = run_multiple_games(n_games, MinMax, (2,), MinMax, (3,))
    print(f"MinMax2 vs MinMax3 ({n_games} games): wins: {wr}, draws: {dr}")
    resultats.setdefault("MinMax2 vs MinMax3", {})
    resultats["MinMax2 vs MinMax3"]["wins"]= wr
    resultats["MinMax2 vs MinMax3"]["draws"] = dr
    resultats["MinMax2 vs MinMax3"]["tours_moyens"]= tours_moyens
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