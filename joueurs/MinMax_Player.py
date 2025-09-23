import partie 
import numpy as np
import copy
from minmax import play_move, play_piece
import random
# On crée trois joueurs minmax : un spécialisé aussi bien dans le placement de pièces que dans le choix des pièces, un seulement dans le placement et un seulement dans le choix
# Voyons voir lequel est le meilleur

class MinMax(partie.Player):
    """MinMax agent"""

    def __init__(self, partie: partie.Quarto, joueur: int) -> None:
        super().__init__(partie)
        self.joueur = joueur
        self.depth = self.get_depth()

    
    def get_depth(self):
        if self.joueur==1:
            return 3
        elif self.joueur==2:
            return 4
        else:
            return 4
# En effet, comme les deux autres joueurs ne calculent que le placement ou la sélection 
# et donc à l'autre phase, le programme tourne plus rapidement bien que l'on perde un de profondeur. 

    def place_piece(self) -> tuple[int, int]:
        '''place_piece en utilisant minmax'''
        game = self.get_game()
        move = play_move(game, self.depth, self.joueur)
        print("Voici ce qui pose problème : ", move)
        if move != None:
            print("La pièce a été positionné à la position :", move)
            return move
        else:
            move_ok = False
            while not move_ok:
                x = random.randint(0,3)
                y = random.randint(0,3)
                move_ok = (game._board[y, x] >= 0)
            move =(x,y)
            print("La pièce a été positionné à la position : ", move)
            return move

    
    def choose_piece(self):
        game = self.get_game()
        piece = play_piece(game, self.depth, self.joueur)
        if piece != None:
            print("La pièce choisie est la numéro : ", piece)
            return piece
        else:
            piece = random.randint(0,15)
            piece_ok = game.select(piece)
            while not piece_ok:
                piece = random.randint(0,15)
                piece_ok = game.select(piece)
                print("La pièce choisie est la numéro : ", piece)
            return piece