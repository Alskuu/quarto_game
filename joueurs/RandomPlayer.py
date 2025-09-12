import partie
import random


class RandomPlayer(partie.Player):
    """Random player"""

    def __init__(self, partie: partie.Quarto) -> None:
        super().__init__(partie)

    def choose_piece(self) -> int:
        piece_choisie = random.randint(0, 15)
        print("La pièce choisie est la pièce numéro : ", piece_choisie)
        return piece_choisie

    def place_piece(self) -> tuple[int, int]:
        position = (random.randint(0, 3), random.randint(0, 3))
        print("La position choisie est la suivante : ", position)
        return position