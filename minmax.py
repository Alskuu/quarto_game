from copy import deepcopy
import random
import itertools
import numpy

EVAL_TIE = 0  # cette valeur pour les matchs nuls a seulement un intérêt en fin de jeu, où l'heuristique n'importera plus
EVAL_WIN = 10000 # Grand score qui doit être largement supérieur à la somme des heuristiques.
MAX_DEPTH = 4
INF = float('inf')

# Les lignes suivantes sont inspirées du pseudo-code du alphabeta pruning sur le wikipedia d'alpha-beta pruning
def minmax1(game, depth, maximizingPlayer, phase, alpha=-INF, beta=INF):
    # phase = "placement" ou "selection"
    
    if depth == 0 or game.check_winner() != -1:
        return state_eval(game, depth, maximizingPlayer)
    
    if phase == "placement":
        # On doit placer la pièce donnée
        moves = get_all_possible_moves(game)
        if maximizingPlayer:
            best = -INF
            for move in moves:
                g = deepcopy(game) # C'est crucial ici : permet de ne pas modifier l'état véritable du jeu
                g.place(move[0], move[1])
                # après un placement, on passe à la phase "selection"
                val = minmax1(g, depth-1, maximizingPlayer, "selection")
                best = max(best, val)
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
            return best
        else:
            best = INF
            for move in moves:
                g = deepcopy(game)
                g.place(move[0], move[1])
                val = minmax1(g, depth-1, maximizingPlayer, "selection")
                best = min(best, val)
                beta = min(beta, best)
                if beta <= alpha:
                    break
            return best
    
    elif phase == "selection":
        # Ici, le joueur choisit une pièce pour l’autre
        available_pieces = list(set(range(16)) - set(game._board.ravel()))
        if maximizingPlayer:
            best = -INF
            for piece in available_pieces:
                g = deepcopy(game)
                g.select(piece)
                # On prend la contraposée de maximizingPlayer car on change de joueur après la sélection
                val = minmax1(g, depth-1, not maximizingPlayer, "placement")
                best = max(best, val)
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
            return best
        else:
            best = INF
            for piece in available_pieces:
                g = deepcopy(game)
                g.select(piece)
                val = minmax1(g, depth-1, not maximizingPlayer, "placement")
                best = min(best, val)
                beta = min(beta, best)
                if beta <= alpha:
                    break
            return best
        
def eval_for_current_player(game, depth, phase):
    """
    Cette fonction doit renvoyer un score positif si la position est bonne
    pour LE JOUEUR QUI DOIT JOUER dans 'game' (point de vue courant).
    """
    piece_to_place = game.get_selected_piece() if phase == "placement" else None
    # state_eval_abs doit renvoyer une magnitude >=0 ; le signe est géré par negamax.
    return state_eval_abs(game, depth, True)


def negamax_complete(game, depth, phase, alpha=-INF, beta=INF):
    # Arrêt (terminal ou horizon)
    if depth == 0 or game.check_winner() != -1 or game.check_finished():
        return eval_for_current_player(game, depth, phase)

    best = -INF

    if phase == "placement":
        # On place la pièce déjà sélectionnée
        moves = get_all_possible_moves(game)  # liste de (x, y)
        for (x, y) in moves:
            g = deepcopy(game)
            g.place(x, y)
            # après un placement on passe à la phase "selection"
            val = negamax_complete(g, depth-1, "selection", beta, alpha)
            if val > best:
                best = val
            if best > alpha:
                alpha = best
            if alpha >= beta:
                break  # élagage α–β
        return best

    elif phase == "selection":
        # Ici, le joueur choisit une pièce pour l’autre
        available_pieces = list(set(range(16)) - set(game._board.ravel()))
        for piece in available_pieces:
            g = deepcopy(game)
            g.select(piece)
            # Après la sélection, on change de joueur, et donc on veut minimiser le score du joueur adverse
            # après la sélection on passe à la phase "placement"
            val = -negamax_complete(g, depth-1, "placement", -beta, -alpha)
            if val > best:
                best = val
            if best > alpha:
                alpha = best
            if alpha >= beta:
                break
        return best
'''
def minmax2(game, depth, maximizingPlayer,phase, alpha:float=-INF, beta:float=INF):
    if depth == 0 or game.check_winner() != -1:
        return state_eval(game, depth, maximizingPlayer)
    
    # On doit placer la pièce donnée
    moves = get_all_possible_moves(game)
    if phase == "placement":
        if maximizingPlayer:
            best = -INF
            for move in moves:
                g = deepcopy(game) # C'est crucial ici : permet de ne pas modifier l'état véritable du jeu
                g.place(move[0], move[1])
                # après un placement, on passe à la phase "selection" de la pièce
                val = minmax2(g, depth-1, "selection", maximizingPlayer)
                best = max(best, val)
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
            return best
        else:
            best = INF
            for move in moves:
                g = deepcopy(game)
                g.place(move[0], move[1])
                val = minmax2(g, depth-1, "selection", maximizingPlayer)
                best = min(best, val)
                beta = min(beta, best)
                if beta <= alpha:
                    break
            return best
    elif phase == "selection":
        if maximizingPlayer:
            best = -INF
            available_pieces = list(set(range(16)) - set(game._board.ravel()))
            g = deepcopy(game)
            piece_ok = False
            while not piece_ok:
                piece = random.randint(0,16)
                if piece in available_pieces:
                    piece_ok = True
            g.select(piece)
            val = minmax2(g, depth-1, "placement", not maximizingPlayer)
            best = max(best, val)
            return best
        else:
            best = INF
            available_pieces = list(set(range(16)) - set(game._board.ravel()))
            g = deepcopy(game)
            piece_ok = False
            while not piece_ok:
                piece = random.randint(0,16)
                if piece in available_pieces:
                    piece_ok = True
            g.select(piece)
            val = minmax2(g, depth-1, "placement", not maximizingPlayer)
            best = min(best, val)
            return best
'''

def negamax_placement_specialized(game, depth, phase, alpha=-INF, beta=INF):
    """Négamax avec α–β, spécialisé sur la phase 'placement'.
       Phase 'selection' = un seul tirage aléatoire d'une pièce disponible.
    """
    # Terminal / horizon
    if depth == 0 or game.check_winner() != -1 or game.check_finished():
        return eval_for_current_player(game, depth, phase)


    if phase == "placement":
        best = -INF
        # On doit placer la pièce déjà sélectionnée
        moves = get_all_possible_moves(game)  # iterable de (x, y)

        for (x, y) in moves:
            g = deepcopy(game)
            g.place(x, y)
            # après un placement on passe à la phase "selection"
            val = negamax_placement_specialized(g, depth-1, "selection", beta, alpha)
            if val > best:
                best = val
            if best > alpha:
                alpha = best
            if alpha >= beta:
                break  # élagage alpha-beta
        return best

    elif phase == "selection":
        # Choix aléatoire d'une seule pièce 
        available_pieces = list(set(range(16)) - set(game._board.ravel()))

        piece = random.choice(available_pieces)
        g = deepcopy(game)
        g.select(piece)
        g._current_player = (g.get_current_player() + 1) % game.MAX_PLAYERS
        return -negamax_placement_specialized(g, depth-1, "placement", -beta, -alpha)

def negamax_selection_specialized(game, depth, phase, alpha=-INF, beta=INF):
    if depth == 0 or game.check_winner() != -1 or game.check_finished():
        return eval_for_current_player(game, depth, phase)

    if phase == "selection":
        best = -INF
        available_pieces = list(set(range(16)) - set(game._board.ravel()))
        for piece in available_pieces:
            g = deepcopy(game)
            g.select(piece)
            val = -negamax_selection_specialized(g, depth-1, "placement", -beta, -alpha)
            if val > best:
                best = val
            if best > alpha:
                alpha = best
            if alpha >= beta:
                break
        return best
    
    elif phase == "placement":
        best = -INF
        moves = get_all_possible_moves(game)
        choice = random.choice(moves)
        g = deepcopy(game)
        g.place(choice[0], choice[1])
        return negamax_selection_specialized(g, depth-1, "selection", beta, alpha)



def play_move(game, depth, joueur):
    scored_moves = []

    tour = game.check_tour()
    if tour == 1:
        scored_moves.append(((0,0),10))
    
    else:
        if joueur==1:
            for move in get_all_possible_moves(game):
                game_t = deepcopy(game)
                game_t.place(move[0], move[1])
                scored_moves.append((move, negamax_complete(game_t, depth, True,"placement"))) ## Selon moi c'est nécessairement True ici, dans le sens où c'est le move qu'on veut pour nous faire gagner !!
            scored_moves.sort(key=lambda x: x[1], reverse=True) # On trie dans l'ordre décroissant des scores

        elif joueur==2:
            for move in get_all_possible_moves(game):
                game_t = deepcopy(game)
                game_t.place(move[0], move[1])
                scored_moves.append((move,negamax_placement_specialized(game_t, depth, True)))
            scored_moves.sort(key=lambda x: x[1], reverse=True) # On trie dans l'ordre décroissant des scores


        else:
            for move in get_all_possible_moves(game):
                game_t = deepcopy(game)
                game_t.place(move[0], move[1])
                scored_moves.append((move,negamax_selection_specialized(game_t, depth, True)))
            scored_moves.sort(key=lambda x: x[1], reverse=True) # On trie dans l'ordre décroissant des scores


    return scored_moves[0][0] if scored_moves[0][1] != float('-inf') or  scored_moves[0][1] != -1 else None 

def play_piece(game,depth, joueur):
    scored_pieces = []

    tour = game.check_tour()
    if tour == 1:
        scored_pieces.append((0, 10))
    
    else:
        if joueur==1:
            for piece in list(set(range(16)) - set(game._board.ravel())):
                game_t = deepcopy(game)
                game_t.select(piece)
                scored_pieces.append((piece,negamax_complete(game_t, depth, False, "selection")))
            scored_pieces.sort(key=lambda x: x[1], reverse=True)
        
        elif joueur==2:
            for piece in list(set(range(16)) - set(game._board.ravel())):
                game_t = deepcopy(game)
                game_t.select(piece)
                scored_pieces.append((piece,negamax_placement_specialized(game_t, depth, False)))
            scored_pieces.sort(key=lambda x: x[1], reverse=True)
        
        else:
            for piece in list(set(range(16)) - set(game._board.ravel())):
                game_t = deepcopy(game)
                game_t.place(piece)
                scored_pieces.append((piece,negamax_selection_specialized(game_t, depth, True)))
            scored_pieces.sort(key=lambda x: x[1], reverse=True)


    return scored_pieces[0][0] if scored_pieces[0][1] != float('-inf') or  scored_pieces[0][1] != -1 else None 

# récupère la liste de tous les coups possibles
def get_all_possible_moves(game):
    list = []
    board = game.get_board_status()
    for i in range(4):
        for j in range(4):
            if board[i][j] == -1:
                list.append((j, i))
    return list

def state_eval(game_state, depth, joueur):
    '''
    Computes the evaluation of the state of the game
    '''
    if joueur ==1:
        max_depth = 4
    else:
        max_depth = 8
    if game_state.check_winner() != -1:
        return -EVAL_WIN + depth if not is_maximizing else EVAL_WIN - (max_depth - depth) 
        # Lorsque le joueur adverse a joué juste avant nous avons is_maximizing = True et donc ici cela signifie que le minmaxplayer concerné a perdu
        # et dans l'autre cas cela vaut un certain score selon le tour (depth) auquel on gagne
    elif game_state.check_finished():
        return 0
    else:
        return -1