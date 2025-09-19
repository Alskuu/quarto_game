from copy import deepcopy
import math

INF = float('inf')
WIN = 10000  # score terminal >> somme des scores des heuristiques. Le signe sera appliqué par negamax.

# récupère la liste de tous les coups possibles
def get_all_possible_moves(game):
    list = []
    board = game.get_board_status()
    for i in range(4):
        for j in range(4):
            if board[i][j] == -1:
                list.append((j, i))
    return list

def get_available_pieces(game):
    used = {int(v) for v in game.get_board_status().ravel().tolist() if v != -1}
    return [p for p in range(16) if p not in used]

# Lignes: 4 lignes + 4 colonnes + 2 diagonales = 10
LINES = []
# Ajouter les lignes horizontales
for y in range(4):
    LINES.append([(x, y) for x in range(4)])
# Ajouter les colonnes verticales  
for x in range(4):
    LINES.append([(x, y) for y in range(4)])
# Ajouter les diagonales
LINES.append([(i, i) for i in range(4)])  # Diagonale principale
LINES.append([(i, 3 - i) for i in range(4)])  # Diagonale secondaire

def line_values(game, line):
    """Renvoie les indices de pièces présents sur une ligne donnée [(x,y)...]."""
    b = game.get_board_status()
    return [int(b[y, x]) for (x, y) in line]

def is_quarto_line(vals):
    """
    Vérifie si une ligne est gagnante :
    - aucune case vide
    - au moins un attribut (bit parmi 4) est commun à toutes les pièces de la ligne.
    """
    if any(v == -1 for v in vals): 
        return False
    for k in range(4):
        b0 = (vals[0] >> k) & 1
        if all(((v >> k) & 1) == b0 for v in vals):
            return True
    return False

def line_alive(vals):
    """
    Vérifie si une ligne est encore "vivante" :
    c’est-à-dire si les pièces déjà posées partagent au moins un attribut en commun,
    ce qui laisse une possibilité future de victoire sur cette ligne.
    """
    filled = [v for v in vals if v != -1]
    if len(filled) <= 1: 
        return True
    for k in range(4):
        b0 = (filled[0] >> k) & 1
        if all(((v >> k) & 1) == b0 for v in filled):
            return True
    return False

def line_best_coherence(vals):
    """
    Donne le nombre maximum de pièces déjà alignées avec un attribut commun (0..3).
    Ex : si 3 pièces partagent une caractéristique, retourne 3.
    """
    filled = [v for v in vals if v != -1]
    if not filled: 
        return 0
    best = 0
    for k in range(4):
        b0 = (filled[0] >> k) & 1
        if all(((v >> k) & 1) == b0 for v in filled):
            best = max(best, len(filled))
    return best  # 0..3 (4 serait déjà gagné)


# ---------------------------------
# Magnitudes positives côté PLACEMENT
# ---------------------------------
def immediate_wins_with_piece_mag(game, piece):
    """Nombre de placements (x,y) qui gagnent immédiatement avec 'piece' (>=0)."""
    count = 0
    for (x, y) in get_all_possible_moves(game):
        g = deepcopy(game)
        g.select(piece)
        g.place(x, y)
        if g.check_winner() != -1:
            count += 1
    return count  # 0..(cases vides)

def mobility_mag(game):
    """Nombre de cases jouables (>=0)."""
    return len(get_all_possible_moves(game))

def immediate_blocks_possible_mag(game, piece):
    """
    Nombre de placements qui permettent de bloquer une menace immédiate de l’adversaire :
    c.-à-d. réduire le nombre de lignes "prêtes à gagner" de l’adversaire.
    """
    before_t1 = 0
    for line in LINES:
        vals = line_values(game, line)
        if line_alive(vals) and line_best_coherence(vals) == 3 and vals.count(-1) == 1:
            before_t1 += 1
    if before_t1 == 0:
        return 0
    blocks = 0
    for (x, y) in get_all_possible_moves(game):
        g = deepcopy(game)
        g.select(piece)
        g.place(x, y)
        after_t1 = 0
        for line in LINES:
            vals = line_values(g, line)
            if line_alive(vals) and line_best_coherence(vals) == 3 and vals.count(-1) == 1:
                after_t1 += 1
        if after_t1 < before_t1:
            blocks += 1
    return blocks

# --------------------------------
# Magnitudes positives côté SELECTION
# --------------------------------
def toxicity_of_piece(game, piece):
    """
    Toxicité brute d'une pièce = nombre de coups adverses gagnants immédiats
    si on lui donne cette pièce.
    """
    return immediate_wins_with_piece_mag(game, piece)

def selection_magnitudes(game):
    """
    Heuristique pour la phase de sélection (donner une pièce à l’adversaire) :
      - safe_max = nb de coups "sûrs" max (cases - toxicité max)
      - safe_avg = nb de coups "sûrs" moyens (cases - toxicité moyenne)
      - H_div    = diversité (entropie des attributs restants des pièces disponibles)
    Toutes les valeurs sont positives et favorables.
    """
    avail = get_available_pieces(game)
    empties = len(get_all_possible_moves(game))
    if not avail:
        return 0, 0.0, 0.0

    tox_list = [toxicity_of_piece(game, p) for p in avail]
    tox_max = max(tox_list)
    tox_avg = sum(tox_list) / len(tox_list)

    safe_max = max(0, empties - tox_max)
    safe_avg = max(0.0, empties - tox_avg)

    # diversité via entropie des bits
    H = 0.0
    for k in range(4):
        # La ligne suivante permet de vérifier si il y a un 1 à la position k dans la décomposition binaire de notre pièce
        ones = sum(((p >> k) & 1) for p in avail)
        zeros = len(avail) - ones
        for n in (zeros, ones):
            if n > 0:
                p = n / len(avail)
                H -= p * math.log2(p)
    return tox_max, tox_avg, H


# Évaluation ABSOLUE (toujours ≥ 0)
W_IW, W_MOB, W_BLK = 80, 1, 50
W_TOX_MAX, W_TOX_AVG, W_DIV = 70, 15, 3

def state_eval_abs(game, phase, piece_to_place, depth):
    """
    Fonction d’évaluation ABSOLUE pour Negamax :
    - Retourne toujours un score positif (magnitude).
    - Negamax applique ensuite le signe selon le joueur courant.
    
    Règles :
      - Si victoire détectée → WIN + depth (plus tôt = plus grand).
      - Si partie finie (nulle) → 0.
      - Sinon → somme pondérée de plusieurs critères :
        * Phase placement : victoires immédiates, forks, cohérence, mobilité, blocages.
        * Phase sélection : sécurité (faible toxicité) + diversité des pièces.
    """
    g = deepcopy(game)
    if g.check_winner() != -1:
        return WIN + depth
    if g.check_finished():
        return 0

    score = 0.0

    if phase == "placement":
        if piece_to_place is None:
            return 0.0
        iw  = immediate_wins_with_piece_mag(g, piece_to_place)
        mob = mobility_mag(g)
        blk = immediate_blocks_possible_mag(g, piece_to_place)

        score += (W_IW * iw
                  + W_MOB * mob
                  + W_BLK * blk)

    elif phase == "selection":
        tox_max, tox_avg, Hdiv = selection_magnitudes(g)
        score += (W_TOX_MAX * tox_max
                  + W_TOX_AVG * tox_avg
                  + W_DIV * Hdiv)

    return max(0.0, float(score))
