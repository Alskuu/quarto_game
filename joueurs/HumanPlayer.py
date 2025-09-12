import partie 
import numpy as np 

class HumanPlayer(partie.Player):
    """Human player via console input"""

    def __init__(self, partie: partie.Quarto) -> None:
        super().__init__(partie)

    def choose_piece(self) -> int:
        # On propose de choisir une pièce libre
        board = self.get_game().get_board_status()
        all_pieces = set(range(16))
        used_pieces = set(board.flatten()) - {-1} #Fait de la matrice avec toutes une liste 1D
        available = sorted(list(all_pieces - used_pieces))

        print(f"Available pieces: {available}")
        piece = -1
        while piece not in available:
            try:
                piece = int(input("Choose a piece (0–15): "))
            except ValueError:
                pass
        return piece

    def place_piece(self) -> tuple[int, int]:
        # On propose une case libre
        board = self.get_game().get_board_status()
        empty = [(x, y) for y in range(4) for x in range(4) if board[y, x] == -1]
        print(f"Cellules vides : {empty}")
        pos = (-1, -1)
        print("La case (0,0) commence dans le coin en haut à a gauche")
        while pos not in empty:
            try:
                x = int(input("Choisis x (0–3): "))
                y = int(input("Choosis y (0–3): "))
                pos = (x, y)
            except ValueError:
                pass
        return pos