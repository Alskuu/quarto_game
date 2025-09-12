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

def verifier_victoire(grille:list[list[Any]]) -> bool:
    lignes = grille
    colonnes = list(zip(*grille)) # Magnifique ligne
    diagonales = [[grille[i][i] for i in range(4)], [grille[i][3 - i] for i in range(4)]]

    for groupe in lignes + colonnes + diagonales:
        if any(p is None for p in groupe):
            continue
        for attr in ['hauteur', 'couleur', 'forme', 'plein']:
            valeurs = [getattr(p, attr) for p in groupe]
            # getattr(x, 'y') is equivalent to x.y
            if all(v == valeurs[0] for v in valeurs):
                return True
    return False

