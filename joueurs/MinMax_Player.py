import partie 
import numpy as np
import copy
from minmax import play_move, play_piece, MAX_DEPTH
import random
# On crée trois joueurs minmax : un spécialisé aussi bien dans le placement de pièces que dans le choix des pièces, un seulement dans le placement et un seulement dans le choix
# Voyons voir lequel est le meilleur

class MinMax(partie.Player):
    """MinMax agent"""

    def __init__(self, partie: partie.Quarto, joueur: int) -> None:
        super().__init__(partie)
        self.depth = MAX_DEPTH
        self.joueur = joueur


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

  
    def piece_available(self, piece) -> bool:
        # Iterate over the board and check if the given piece has already been played
        quarto = self.get_game()
        board = quarto.get_board_status()
        for row in board:
            for cell in row:
                if cell == piece:
                    return False
        return True