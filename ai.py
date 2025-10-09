import random
import copy
import time
from board import Board
from multiprocessing import Pool, cpu_count

class Ai:
    def choose_move(self, color, board):
        pass



class Random_ai:
    def choose_move(self, color, board):

        # Ici on test juste une case de départ et une case d'arriver aléatoirment jusquà trouver:
        # - Pour le départ une piece de la couleur du joueur
        # - Pour l'arriver une case qui se trouve dans les légal move de cette piece

        is_good_color = False
        is_valid_move = False

        while not is_good_color:
            start_rand_x = random.randint(0, 7)
            start_rand_y = random.randint(0, 7)

            piece = board.grid[start_rand_x][start_rand_y].piece
            moves = board.get_legal_moves([start_rand_x, start_rand_y])

            if piece:
                if moves:
                    if piece.color == color:
                        is_good_color = True
        
        while not is_valid_move:
            end_rand_x = random.randint(0, 7)
            end_rand_y = random.randint(0, 7)

            if (end_rand_x, end_rand_y) in moves:
                is_valid_move = True


        start_position = (start_rand_x, start_rand_y)
        end_position = (end_rand_x, end_rand_y)
        return start_position, end_position


# Fonction helper pour multiprocessing (DOIT être au niveau du module)
def _evaluate_move_parallel(args):
    """Fonction helper pour évaluer un coup en parallèle"""
    move_data, board, color, depth = args
    x, y, a, b = move_data
    
    # Recréer le board

    
    piece = board.grid[x][y].piece
    captured_piece = board.change_piece(a, b, piece, (x, y))
    
    ai = MinMax_ai()
    score = ai.minMax(color, board, depth - 1, -float('inf'), float('inf'), False)
    
    board.undo_move((x, y), (a, b), captured_piece)
    
    return (score, x, y, a, b)


class MinMax_ai:
    def __init__(self):
        self.transposition_table = {}

    def hash_board(self, board):

        """
        Crée une clé unique pour représenter l'état du plateau
        de la forme couleurpiece typedepiece
        """
        board_string = ""
        for x in range(8):
            for y in range(8):
                piece = board.grid[x][y].piece
                if piece:
                    board_string += f"{piece.color}{piece.type}"
                else:
                    board_string += "."
        return board_string

    def pawns_structure(self, board, position):
        '''
        Méthode permettant de mettre un bonus ou malus en fonction de la structure de pion
        C'est à dire des pions bien en diagonale qui se défendent entre eux
        '''

        x, y = position
        color = board.grid[x][y].piece.color

        score = 0

        if color == 'w':
            # Vérifier pion allié en diagonale gauche
            if x - 1 >= 0 and y - 1 >= 0:
                if board.grid[x - 1][y - 1].piece:
                    if board.grid[x - 1][y - 1].piece.type == 'p' and board.grid[x - 1][y - 1].piece.color == color:
                        score += 50

            # Vérifier pion allié en diagonale droite
            if x - 1 >= 0 and y + 1 < 8:
                if board.grid[x - 1][y + 1].piece:
                    if board.grid[x - 1][y + 1].piece.type == 'p' and board.grid[x - 1][y + 1].piece.color == color:
                        score += 50

            # Vérifier pion doublé (même colonne devant)
            if x - 1 >= 0:
                if board.grid[x - 1][y].piece:
                    if board.grid[x - 1][y].piece.type == 'p' and board.grid[x - 1][y].piece.color == color:
                        score -= 50

        else:  # color == 'b'
            # Vérifier pion allié en diagonale gauche
            if x + 1 < 8 and y - 1 >= 0:
                if board.grid[x + 1][y - 1].piece:
                    if board.grid[x + 1][y - 1].piece.type == 'p' and board.grid[x + 1][y - 1].piece.color == color:
                        score += 50

            # Vérifier pion allié en diagonale droite
            if x + 1 < 8 and y + 1 < 8:
                if board.grid[x + 1][y + 1].piece:
                    if board.grid[x + 1][y + 1].piece.type == 'p' and board.grid[x + 1][y + 1].piece.color == color:
                        score += 50

            # Vérifier pion doublé (même colonne devant)
            if x + 1 < 8:
                if board.grid[x + 1][y].piece:
                    if board.grid[x + 1][y].piece.type == 'p' and board.grid[x + 1][y].piece.color == color:
                        score -= 50

        return score

    def oppening_evaluate(self, color, board):
        points = {
            "p": 1000,
            "n": 3200,
            "b": 3300,
            "r": 5000,
            "q": 9000,
        }

        # Pions en ouverture
        pawn_position_bonus = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [60, 60, 80, 150, 150, 80, 60, 60],
            [20, 40, 80, 130, 130, 80, 40, 20],
            [10, 30, 70, 120, 120, 70, 30, 10],
            [5, 20, 60, 100, 100, 60, 20, 5],
            [0, 10, 30, 60, 60, 30, 10, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]

        knight_position_bonus = [
            [0, 10, 20, 30, 30, 20, 10, 0],
            [10, 30, 40, 60, 60, 40, 30, 10],
            [20, 40, 70, 90, 90, 70, 40, 20],
            [30, 60, 90, 110, 110, 90, 60, 30],
            [30, 60, 90, 110, 110, 90, 60, 30],
            [20, 40, 70, 90, 90, 70, 40, 20],
            [10, 30, 40, 60, 60, 40, 30, 10],
            [0, 10, 20, 30, 30, 20, 10, 0],
        ]

        bishop_position_bonus = [
            [0, 10, 20, 20, 20, 20, 10, 0],
            [10, 30, 40, 50, 50, 40, 30, 10],
            [20, 40, 70, 90, 90, 70, 40, 20],
            [20, 50, 90, 110, 110, 90, 50, 20],
            [20, 50, 90, 110, 110, 90, 50, 20],
            [20, 40, 70, 90, 90, 70, 40, 20],
            [10, 30, 40, 50, 50, 40, 30, 10],
            [0, 10, 20, 20, 20, 20, 10, 0],
        ]

        # Tours en ouverture
        rook_position_bonus = [
            [0,  0,  0,  0,  0,  0,  0,  0],   # Ligne 8
            [10, 15, 15, 15, 15, 15, 15, 10],  # Ligne 7 (7ème rangée = excellent)
            [0,  5,  5,  5,  5,  5,  5,  0],   # Ligne 6
            [0,  0,  0,  0,  0,  0,  0,  0],   # Ligne 5
            [0,  0,  0,  0,  0,  0,  0,  0],   # Ligne 4
            [0,  0,  0,  0,  0,  0,  0,  0],   # Ligne 3
            [0,  0,  0,  0,  0,  0,  0,  0],   # Ligne 2
            [0,  0,  0,  5,  5,  0,  0,  0]    # Ligne 1 (colonnes centrales = petit bonus)
        ]

        # Dame en ouverture (NE PAS sortir tôt)
        queen_position_bonus = [
            [0,  0,  0,  0,  0,  0,  0,  0],   # Ligne 8
            [0,  5,  5,  5,  5,  5,  5,  0],   # Ligne 7
            [0,  5, 10, 10, 10, 10,  5,  0],   # Ligne 6
            [0,  5, 10, 10, 10, 10,  5,  0],   # Ligne 5
            [0,  5, 10, 10, 10, 10,  5,  0],   # Ligne 4
            [0,  5, 10, 10, 10, 10,  5,  0],   # Ligne 3
            [0,  5, 10,  5,  5, 10,  5,  0],   # Ligne 2
            [0,  0,  0,  0,  0,  0,  0,  0]    # Ligne 1 (position initiale = neutre)
        ]

        # Roi en ouverture (rester en sécurité, roqué)
        king_position_bonus = [
            [0,  0,  0,  0,  0,  0,  0,  0],   # Ligne 8
            [0,  0,  0,  0,  0,  0,  0,  0],   # Ligne 7
            [0,  0,  0,  0,  0,  0,  0,  0],   # Ligne 6
            [0,  0,  0,  0,  0,  0,  0,  0],   # Ligne 5
            [0,  0,  0,  0,  0,  0,  0,  0],   # Ligne 4
            [0,  0,  0,  0,  0,  0,  0,  0],   # Ligne 3
            [5,  5,  0,  0,  0,  0,  5,  5],   # Ligne 2 (près du roque)
            [75, 70,  5,  0,  0,  5, 70,  75]    # Ligne 1 (roqué = bon)
        ]

        score = 0

        for x in range(8):
            for y in range(8):
                piece = board.grid[x][y].piece
                if piece:
                    value = points.get(piece.type, 0)

                    if piece.type == "p":
                        if piece.color == "w":
                            value += pawn_position_bonus[x][y]
                        else:
                            value += pawn_position_bonus[7-x][y]

                    elif piece.type == "n":
                        if piece.color == "w":
                            value += knight_position_bonus[x][y]
                        else:
                            value += knight_position_bonus[7-x][y]

                    elif piece.type == "b":
                        if piece.color == "w":
                            value += bishop_position_bonus[x][y]
                        else:
                            value += bishop_position_bonus[7-x][y]

                    elif piece.type == "r":
                        if piece.color == "w":
                            value += rook_position_bonus[x][y]
                        else:
                            value += rook_position_bonus[7-x][y]

                    elif piece.type == "q":
                        if piece.color == "w":
                            value += queen_position_bonus[x][y]
                        else:
                            value += queen_position_bonus[7-x][y]

                    elif piece.type == "k":
                        if piece.color == "w":
                            value += king_position_bonus[x][y]
                        else:
                            value += king_position_bonus[7-x][y]

                    if piece.color == color:
                        score += value
                    else:
                        score -= value

        return score

    def middle_evaluate(self, color, board):
        points = {
            "p": 1000,
            "n": 3200,
            "b": 3300,
            "r": 5000,
            "q": 9000,
        }

        # Pions en milieu de partie
        pawn_position_bonus = [
            [0,  0,  0,  0,  0,  0,  0,  0],   # Ligne 0
            [90, 90, 90, 90, 90, 90, 90, 90],  # Ligne 1
            [25, 25, 35, 50, 50, 35, 25, 25],  # Ligne 2
            [15, 15, 20, 45, 45, 20, 15, 15],  # Ligne 3
            [10, 10, 15, 40, 40, 15, 10, 10],  # Ligne 4
            [5,  5,  10, 20, 20, 10,  5,  5],  # Ligne 5
            [0,  0,   0,  0,  0,  0,  0,  0],  # Ligne 6
            [0,  0,   0,  0,  0,  0,  0,  0]   # Ligne 7
        ]

        # Cavaliers en milieu de partie
        knight_position_bonus = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [0,  5,  5,  5,  5,  5,  5,  0],
            [0,  5, 15, 20, 20, 15,  5,  0],
            [0, 10, 20, 25, 25, 20, 10,  0],
            [0,  5, 20, 25, 25, 20,  5,  0],
            [0,  5, 15, 20, 20, 15,  5,  0],
            [0,  0,  5, 10, 10,  5,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ]

        # Fous en milieu de partie
        bishop_position_bonus = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [0,  5,  5,  5,  5,  5,  5,  0],
            [0,  5, 15, 20, 20, 15,  5,  0],
            [0, 10, 15, 20, 20, 15, 10,  0],
            [0,  5, 20, 20, 20, 20,  5,  0],
            [0, 15, 20, 20, 20, 20, 15,  0],
            [0, 10,  5,  5,  5,  5, 10,  0],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ]

        # Tours en milieu de partie
        rook_position_bonus = [
            [5,  5,  5,  5,  5,  5,  5,  5],
            [15, 20, 20, 20, 20, 20, 20, 15],  # 7ème rangée = très bon
            [5, 10, 10, 10, 10, 10, 10,  5],
            [0,  5,  5,  5,  5,  5,  5,  0],
            [0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  5,  5,  0,  0,  0]
        ]

        # Dame en milieu de partie
        queen_position_bonus = [
            [0,  5,  5,  5,  5,  5,  5,  0],
            [0,  5, 10, 10, 10, 10,  5,  0],
            [0,  5, 15, 15, 15, 15,  5,  0],
            [0, 10, 15, 20, 20, 15, 10,  0],
            [0, 10, 15, 20, 20, 15, 10,  0],
            [0,  5, 15, 15, 15, 15,  5,  0],
            [0,  5, 10, 10, 10, 10,  5,  0],
            [0,  0,  5,  5,  5,  5,  0,  0]
        ]

        # Roi en milieu de partie (rester en sécurité)
        king_position_bonus = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0],
            [10, 10,  5,  0,  0,  5, 10, 10],
            [15, 20, 10,  0,  0, 10, 20, 15]
        ]

        score = 0

        for x in range(8):
            for y in range(8):
                piece = board.grid[x][y].piece
                if piece:
                    value = points.get(piece.type, 0)

                    if piece.type == "p":
                        if piece.color == "w":
                            value += pawn_position_bonus[x][y]
                        else:
                            value += pawn_position_bonus[7-x][y]

                    elif piece.type == "n":
                        if piece.color == "w":
                            value += knight_position_bonus[x][y]
                        else:
                            value += knight_position_bonus[7-x][y]

                    elif piece.type == "b":
                        if piece.color == "w":
                            value += bishop_position_bonus[x][y]
                        else:
                            value += bishop_position_bonus[7-x][y]

                    elif piece.type == "r":
                        if piece.color == "w":
                            value += rook_position_bonus[x][y]
                        else:
                            value += rook_position_bonus[7-x][y]

                    elif piece.type == "q":
                        if piece.color == "w":
                            value += queen_position_bonus[x][y]
                        else:
                            value += queen_position_bonus[7-x][y]

                    elif piece.type == "k":
                        if piece.color == "w":
                            value += king_position_bonus[x][y]
                        else:
                            value += king_position_bonus[7-x][y]

                    if piece.color == color:
                        score += value
                    else:
                        score -= value

        return score

    def end_evaluate(self, color, board):
        points = {
            "p": 1000,
            "n": 3200,
            "b": 3300,
            "r": 5000,
            "q": 9000,
        }

        # Pions en fin de partie (promotion prioritaire)
        pawn_position_bonus = [
            [0,   0,   0,   0,   0,   0,   0,   0],
            [100, 100, 100, 100, 100, 100, 100, 100],
            [60,  60,  70,  80,  80,  70,  60,  60],
            [40,  40,  50,  60,  60,  50,  40,  40],
            [20,  20,  30,  40,  40,  30,  20,  20],
            [10,  10,  15,  20,  20,  15,  10,  10],
            [0,   0,   0,   0,   0,   0,   0,   0],
            [0,   0,   0,   0,   0,   0,   0,   0]
        ]

        # Cavaliers en fin de partie
        knight_position_bonus = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [0,  5,  5,  5,  5,  5,  5,  0],
            [0,  5, 15, 20, 20, 15,  5,  0],
            [0, 10, 20, 25, 25, 20, 10,  0],
            [0,  5, 20, 25, 25, 20,  5,  0],
            [0,  5, 15, 20, 20, 15,  5,  0],
            [0,  0,  5, 10, 10,  5,  0,  0],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ]

        # Fous en fin de partie
        bishop_position_bonus = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [0, 10,  5,  5,  5,  5, 10,  0],
            [0, 10, 15, 20, 20, 15, 10,  0],
            [0,  5, 20, 20, 20, 20,  5,  0],
            [0, 10, 15, 20, 20, 15, 10,  0],
            [0,  5, 10, 15, 15, 10,  5,  0],
            [0,  5,  5,  5,  5,  5,  5,  0],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ]

        # Tours en fin de partie
        rook_position_bonus = [
            [10, 10, 10, 10, 10, 10, 10, 10],
            [20, 25, 25, 25, 25, 25, 25, 20],  # 7ème rangée = excellent
            [10, 15, 15, 15, 15, 15, 15, 10],
            [5,  10, 10, 10, 10, 10, 10,  5],
            [0,   5,  5,  5,  5,  5,  5,  0],
            [0,   0,  0,  0,  0,  0,  0,  0],
            [0,   0,  0,  0,  0,  0,  0,  0],
            [0,   0,  0,  5,  5,  0,  0,  0]
        ]

        # Dame en fin de partie
        queen_position_bonus = [
            [0,  5,  5,  5,  5,  5,  5,  0],
            [0, 10, 10, 10, 10, 10, 10,  0],
            [0, 10, 15, 20, 20, 15, 10,  0],
            [0, 15, 20, 25, 25, 20, 15,  0],
            [0, 10, 20, 25, 25, 20, 10,  0],
            [0, 10, 15, 20, 20, 15, 10,  0],
            [0,  5, 10, 10, 10, 10,  5,  0],
            [0,  0,  5,  5,  5,  5,  0,  0]
        ]

        # Roi en fin de partie (aller au centre !)
        king_position_bonus = [
            [0,  5, 10, 15, 15, 10,  5,  0],
            [5, 10, 15, 20, 20, 15, 10,  5],
            [10, 15, 20, 25, 25, 20, 15, 10],
            [15, 20, 25, 30, 30, 25, 20, 15],
            [15, 20, 25, 30, 30, 25, 20, 15],
            [10, 15, 20, 25, 25, 20, 15, 10],
            [5, 10, 15, 20, 20, 15, 10,  5],
            [0,  5, 10, 15, 15, 10,  5,  0]
        ]

        score = 0

        for x in range(8):
            for y in range(8):
                piece = board.grid[x][y].piece
                if piece:
                    value = points.get(piece.type, 0)

                    if piece.type == "p":
                        if piece.color == "w":
                            value += pawn_position_bonus[x][y]
                        else:
                            value += pawn_position_bonus[7-x][y]

                    elif piece.type == "n":
                        if piece.color == "w":
                            value += knight_position_bonus[x][y]
                        else:
                            value += knight_position_bonus[7-x][y]

                    elif piece.type == "b":
                        if piece.color == "w":
                            value += bishop_position_bonus[x][y]
                        else:
                            value += bishop_position_bonus[7-x][y]

                    elif piece.type == "r":
                        if piece.color == "w":
                            value += rook_position_bonus[x][y]
                        else:
                            value += rook_position_bonus[7-x][y]

                    elif piece.type == "q":
                        if piece.color == "w":
                            value += queen_position_bonus[x][y]
                        else:
                            value += queen_position_bonus[7-x][y]

                    elif piece.type == "k":
                        if piece.color == "w":
                            value += king_position_bonus[x][y]
                        else:
                            value += king_position_bonus[7-x][y]

                    if piece.color == color:
                        score += value
                    else:
                        score -= value

        return score
    
    def evaluate(self, color, board):
        """
        Évalue la position du plateau pour une couleur donnée
        Score positif = bon pour 'color', Score négatif = mauvais pour 'color'
        """

        opponent_color = "b" if color == "w" else "w"

        N1, N2 = 15, 40

        score = 0

        if board.nb_moves <= N1:
            score += self.oppening_evaluate(color, board)
        elif board.nb_moves > N1 and board.nb_moves <= N2:
            score += self.middle_evaluate(color, board)
        else:
            score += self.end_evaluate(color, board)


        my_mobility = self._calculate_pseudo_legal_moves(board, color)
        opponent_mobility = self._calculate_pseudo_legal_moves(board, opponent_color)

        score += (my_mobility - opponent_mobility) * 0
        
        return score


        '''
        opponent_color = "b" if color == "w" else "w"
        

        # Different tableau selon la valeur et la position des pieces

        points = {
            "p": 100,
            "n": 320,
            "b": 330,
            "r": 500,
            "q": 900,
        }
        
        # Bonus de position pour les pions (encourage l'avancement)
        pawn_position_bonus = [
            [0,  0,  0,  0,  0,  0,  0,  0],  # Ligne 0 (promotion)
            [50, 50, 50, 50, 50, 50, 50, 50],  # Ligne 1
            [10, 10, 20, 30, 30, 20, 10, 10],  # Ligne 2
            [5,  5, 10, 25, 25, 10,  5,  5],   # Ligne 3
            [0,  0,  0, 20, 20,  0,  0,  0],   # Ligne 4
            [5, -5,-10,  0,  0,-10, -5,  5],   # Ligne 5
            [5, 10, 10,-20,-20, 10, 10,  5],   # Ligne 6
            [0,  0,  0,  0,  0,  0,  0,  0]    # Ligne 7
        ]
        
        # Bonus de position pour les cavaliers (encourage le centre)
        knight_position_bonus = [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 15, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ]
        
        score = 0

        # Ajout des bonus de placement des pieces selon les tableau ci-dessus
        for x in range(8):
            for y in range(8):
                piece = board.grid[x][y].piece
                if piece:
                    value = points.get(piece.type, 0)
                    
                    if piece.type == "p":
                        if piece.color == "w":
                            value += pawn_position_bonus[x][y]
                        else:
                            value += pawn_position_bonus[7-x][y]
                    
                    elif piece.type == "n":
                        if piece.color == "w":
                            value += knight_position_bonus[x][y]
                        else:
                            value += knight_position_bonus[7-x][y]
                    
                    # Ajouter ou soustraire selon la couleur
                    if piece.color == color:
                        score += value
                    else:
                        score -= value
        
        # Bonus pour la mobilité (nombre de coups légaux) Une piece avec beaucoup 
        # de posibilité de déplacement sera plus forte qu'une avec moins
        my_mobility = self._calculate_pseudo_legal_moves(board, color)
        opponent_mobility = self._calculate_pseudo_legal_moves(board, opponent_color)

        score += (my_mobility - opponent_mobility) * 2
        
        return score
        '''
    
    def _calculate_pseudo_legal_moves(self, board, color):
        """
        Calcule RAPIDEMENT le nombre de coups pseudo-légaux (sans vérifier les échecs)
        Version OPTIMISÉE avec gestion spéciale par type de pièce
        """
        move_count = 0
    
        for x in range(8):
            for y in range(8):
                piece = board.grid[x][y].piece
                if piece and piece.color == color:
                    possible_moves = piece.get_possible_moves((x, y))
    
                    for move in possible_moves:
                        move_x, move_y = move
                        
                        # ✅ Vérifier que le coup est dans le plateau
                        if not (0 <= move_x < 8 and 0 <= move_y < 8):
                            continue
                        
                        target_piece = board.grid[move_x][move_y].piece
                        
                        # Ne pas capturer ses propres pièces
                        if target_piece and target_piece.color == color:
                            continue
                        
                        # ✅ OPTIMISATION : Cavaliers et Roi n'ont pas besoin de is_path_clear
                        if piece.type in ['n', 'k']:
                            move_count += 1
                        # ✅ Pions : vérification simple
                        elif piece.type == 'p':
                            # Mouvement en avant : case vide
                            if move_y == y and not target_piece:
                                move_count += 1
                            # Capture diagonale : pièce ennemie présente
                            elif move_y != y and target_piece:
                                move_count += 1
                        # Pour les autres pièces (tour, fou, dame) : vérifier le chemin
                        else:
                            if board.is_path_clear((x, y), move):
                                move_count += 1
    
        return move_count
    
    def _order_moves(self, board, moves_list):
        """
        Trie une liste de coups pour améliorer l'élagage alpha-bêta
        
        Args:
            board: Le plateau actuel
            moves_list: Liste de tuples (x, y, a, b) où:
                - (x, y) = position de départ
                - (a, b) = position d'arrivée
        
        Returns:
            Liste triée des mêmes coups, meilleurs en premier
        """
        piece_values = {
            "p": 1,
            "n": 3,
            "b": 3,
            "r": 5,
            "q": 9,
        }
        
        scored_moves = []
        
        for x, y, a, b in moves_list:
            score = 0
            
            piece = board.grid[x][y].piece
            target = board.grid[a][b].piece
            
            # Piece
            if target:

                victim_value = piece_values.get(target.type, 0)
                attacker_value = piece_values.get(piece.type, 0)
                score += 1000 + (10 * victim_value - attacker_value)
            
            # Centre
            center_distance = abs(a - 3.5) + abs(b - 3.5)
            score -= center_distance
            
            # Promotion d'un pion
            if piece.type == "p":
                if (piece.color == "w" and a == 0) or (piece.color == "b" and a == 7):
                    score += 500
            
            scored_moves.append((score, x, y, a, b))
        

        scored_moves.sort(reverse=True, key=lambda move: move[0])
        
        # Retourner seulement les coups (sans les scores)
        return [(x, y, a, b) for score, x, y, a, b in scored_moves]
    
    def minMax(self, color, board, depth, alpha, beta, IS_MAX = True):
        '''

        '''
        board_key = self.hash_board(board)

        if board_key in self.transposition_table:
            stored_depth, stored_score = self.transposition_table[board_key]
            if stored_depth >= depth:
                return stored_score

        if IS_MAX:
            current_color = color
            best_score = -float('inf')
        else:
            current_color = 'b' if color == 'w' else 'w'
            best_score = float('inf')

        if depth == 0:
            score = self.evaluate(color, board)
            self.transposition_table[board_key] = (depth, score)

            return score
        
        

        all_playable_pieces = board.get_all_playable_pieces(current_color)


        # On récupère la liste de coup pour les classé dans l'ordre des meilleurs aux pire pour ensuite faire
        # les faire en premier et que l'élagage alpha beta soit plus performant

        all_moves = []
        for x, y in all_playable_pieces:
            moves = board.get_legal_moves((x, y))
            for a, b in moves:
                all_moves.append((x, y, a, b))


        if not all_moves:
            # Vérifier si c'est mat ou pat
            if board.is_in_check(current_color):
                # Échec et mat
                score = -1000000 if IS_MAX else 1000000
            else:
                # Pat (match nul)
                score = 0
            self.transposition_table[board_key] = (depth, score)
            return score

        all_moves = self._order_moves(board, all_moves)


        if IS_MAX:
            for x, y, a, b in all_moves:
                piece = board.grid[x][y].piece
                captured_piece = board.change_piece(a, b, piece, (x, y))
                score = self.minMax(color, board, depth - 1, alpha, beta, not IS_MAX)
                board.undo_move((x, y), (a, b), captured_piece)

                best_score = max(best_score, score)
                alpha = max(best_score, alpha)

                if beta <= alpha:
                    break
        else:
            for x, y, a, b in all_moves:
                piece = board.grid[x][y].piece
                captured_piece = board.change_piece(a, b, piece, (x, y))
                score = self.minMax(color, board, depth - 1, alpha, beta, not IS_MAX)
                board.undo_move((x, y), (a, b), captured_piece)

                best_score = min(best_score, score)
                beta = min(best_score, beta)

                if beta <= alpha:
                    break

        self.transposition_table[board_key] = (depth, best_score)

        return best_score
        


    def choose_move(self, color, board, depth=3, use_parallel=True):
        all_playable_pieces = board.get_all_playable_pieces(color)
        
        # AJOUTÉ: Si use_parallel est True, utiliser multiprocessing
        # On test en parrallele sur le nombre de processeur de la machine tous les premier coup
        # pas l'algo minMax pour ne pas le perturbé
        # On commence donc par colecter tous les premier coup possible on en créer une liste
        # puis on en créer une liste que l'on passe à la fonction _evaluate_move_parallel dans 
        # une boucle qui execute la liste une par une sur tous les processeur à la fois

        start_time = time.time()

        if use_parallel:
            all_moves = []
            for x, y in all_playable_pieces:
                piece = board.grid[x][y].piece
                moves = board.get_legal_moves((x, y))
                for a, b in moves:
                    all_moves.append((x, y, a, b))
            
            if not all_moves:
                return None, None
            
            args_list = [(move, board, color, depth) for move in all_moves]
            
            with Pool(processes=cpu_count()) as pool:
                results = pool.map(_evaluate_move_parallel, args_list)

            best_result = max(results, key=lambda x: x[0])
            score, x, y, a, b = best_result
            
            print(time.time() - start_time)

            return (x, y), (a, b)
        
        # Code original si use_parallel=False
        else:
            best_score = -float('inf')

            for x, y in all_playable_pieces:
                piece = board.grid[x][y].piece
                moves = board.get_legal_moves((x, y))
                for a, b in moves:
                    captured_piece = board.change_piece(a, b, piece, (x, y))
                    current_score = self.minMax(color, board, depth - 1, -float('inf'), float('inf'), False)
                    board.undo_move((x, y), (a, b), captured_piece)

                    if current_score > best_score:
                        best_score = current_score
                        start_best_move_position = (x, y)
                        end_best_move_position = (a, b)
            
            print(f"Temps mis pour le coup : {time.time() - start_time}")
            
            return start_best_move_position, end_best_move_position