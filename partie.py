import numpy as np
from abc import ABC, abstractmethod
import copy
from model import generer_pieces, Piece

class Player(ABC):
    def __init__(self, quarto) -> None:
        self.__quarto = quarto

    @abstractmethod
    def choose_piece(self) -> int:
        pass

    @abstractmethod
    def place_piece(self) -> tuple[int, int]:
        pass

    def get_game(self):
        return self.__quarto


class Quarto(object):

    MAX_PLAYERS = 2
    BOARD_SIDE = 4

    def __init__(self) -> None:
        self.__players = ()
        self.reset()
        self.__observers = []  # liste des callbacks, utiles pour le giu
        self.current_tour = 1
        

    def add_observer(self, callback):
        """Ajoute une fonction de rappel qui sera appelée sur chaque mise à jour."""
        self.__observers.append(callback)

    def notify(self, event_type: str, data: dict = None):
        """Notifie tous les observateurs avec un événement."""
        for cb in self.__observers:
            cb(event_type, data or {})
    
    def __deepcopy__(self, memo):
            """Copie profonde sans les observateurs"""
            new_game = Quarto()
            new_game._board = copy.deepcopy(self._board, memo)
            new_game.__binary_board = copy.deepcopy(self.__binary_board, memo)
            new_game.__pieces = copy.deepcopy(self.__pieces, memo)
            new_game._current_player = self._current_player
            new_game.__selected_piece_index = self.__selected_piece_index
            new_game.__players = self.__players
            # Ne pas copier les observateurs (les objets tkinter ne sont pas copiables)
            new_game.__observers = []
            return new_game

        # Une deepcopy est une copie indépendante, récursive et complète de notre objet
        # On renvoie une deepcopy pour protéger l’état interne du jeu.
        # Ainsi, même si le joueur modifie l’objet retourné, cela n’affectera pas
        # les vraies pièces utilisées dans la partie.

    def reset(self):
        self._board = np.ones(
            shape=(self.BOARD_SIDE, self.BOARD_SIDE), dtype=int) * -1
        self.__binary_board = np.full(
            shape=(self.BOARD_SIDE, self.BOARD_SIDE, 4), fill_value=np.nan)
        self.__pieces = generer_pieces()
        self._current_player = 0
        self.__selected_piece_index = -1

    def set_players(self, players: tuple[Player, Player]) -> None:
        self.__players = players

    def get_current_player(self) -> int:
        '''
        Gets the current player
        '''
        return self._current_player

    def select(self, pieceIndex: int) -> bool:
        '''
        select a piece. Returns True on success
        '''
        if pieceIndex not in self._board:
            self.__selected_piece_index = pieceIndex
            self.notify("select", {"player": self._current_player, "piece": pieceIndex})
            return True
        return False

    def place(self, x: int, y: int) -> bool:
        '''
        Place piece in coordinates (x, y). Returns true on success
        '''
        if self.__placeable(x, y):
            self._board[y, x] = self.__selected_piece_index
            self.__binary_board[y,
                                x][:] = self.__pieces[self.__selected_piece_index].binary
            self.notify("place", {"player": self._current_player, "x": x, "y": y, "piece": self.__selected_piece_index})
            return True
        return False

    def __placeable(self, x: int, y: int) -> bool:
        return not (y < 0 or x < 0 or x > 3 or y > 3 or self._board[y, x] >= 0)

    def get_board_status(self) -> np.ndarray:
        '''
        Get the current board status (pieces are represented by index)
        '''
        return copy.deepcopy(self._board)

    def get_selected_piece(self) -> int:
        '''
        Get index of selected piece
        '''
        return copy.deepcopy(self.__selected_piece_index)

    def check_tour(self):
        return self.current_tour
        

    def __check_horizontal(self) -> int:
        hsum = np.sum(self.__binary_board, axis=1)

        if self.BOARD_SIDE in hsum or 0 in hsum:
            return self._current_player
        else:
            return -1

    def __check_vertical(self):
        vsum = np.sum(self.__binary_board, axis=0)

        if self.BOARD_SIDE in vsum or 0 in vsum:
            return self._current_player
        else:
            return -1

    def __check_diagonal(self):
        dsum1 = np.trace(self.__binary_board, axis1=0, axis2=1)
        dsum2 = np.trace(np.fliplr(self.__binary_board), axis1=0, axis2=1)

        if self.BOARD_SIDE in dsum1 or self.BOARD_SIDE in dsum2 or 0 in dsum1 or 0 in dsum2:
            return self._current_player
        else:
            return -1

    def check_winner(self) -> int:
        '''
        Check who is the winner
        '''
        l = [self.__check_horizontal(), self.__check_vertical(),
             self.__check_diagonal()]

        for elem in l:
            if elem >= 0:
                return elem
        return -1

    def check_finished(self) -> bool:
        '''
        Check who is the loser
        '''
        for row in self._board:
            for elem in row:
                if elem == -1:
                    return False
        return True
    
    def run(self) -> int:
        '''
        Run the game (with output for every move)
        '''
        winner = -1
        while winner < 0 and not self.check_finished():
            piece_ok = False
            while not piece_ok: # Utile pour le RandomPlayer par exemple qui ne prend pas en compte les pièces disponibles ou non 
                piece_ok = self.select(
                    self.__players[self._current_player].choose_piece())
            piece_ok = False
            self._current_player = (
                self._current_player + 1) % self.MAX_PLAYERS
            print(f'Joueur actuel: {self._current_player}')
            self.notify("next_player", {"player": self._current_player, "piece": self.__selected_piece_index})
            while not piece_ok:
                x, y = self.__players[self._current_player].place_piece()
                piece_ok = self.place(x, y)
                print("Nous avons terminé le tour numéro : ", self.current_tour)
            self.current_tour += 1
            winner = self.check_winner()
        #self.print()
        self.notify("end", {"winner": winner})
        print(winner)
        return winner

