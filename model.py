from typing import Any, List 

class Piece:
    def __init__(self, h:bool, c:bool, f:bool, p:bool):
        self.hauteur = h
        self.couleur = c
        self.forme = f
        self.plein = p

    def __repr__(self) -> str:
        return f"{self.hauteur}{self.couleur}{self.forme}{self.plein}"

    def to_str(self):
        return f"{self.hauteur}{self.couleur}{self.forme}{self.plein}"

    @property
    def binary(self):
        # Return 4-bit representation expected by the engine (0/1)
        return [int(self.hauteur), int(self.couleur), int(self.forme), int(self.plein)]

def generer_pieces() -> List[Piece]:
    return [
        Piece(h, c, f, p)
        for h in [True, False]
        for c in [True, False]
        for f in [True, False]
        for p in [True, False]
    ]

