import random
import copy
from board import Board

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

class MinMax_ai:
    def evaluate(self, color, board):
        """
        Évalue la position du plateau pour une couleur donnée
        Score positif = bon pour 'color', Score négatif = mauvais pour 'color'
        """

        opponent_color = "b" if color == "w" else "w"

        # Avant tout un echec renvoie imédiatement le pire score possbile ou le meilleur en cas de victoire

        if board.check_game_status(color) == 'checkmate':
            return -1000000
        elif board.check_game_status(color) == 'stalemate':
            return 0
        
        if board.check_game_status(opponent_color) == 'checkmate':
            return 1000000
        


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
        my_pieces = board.get_all_playable_pieces(color)
        my_moves = 0
        for x, y in my_pieces:
            moves = board.get_legal_moves((x, y))
            for move in moves:
                my_moves += 1

        opponent_pieces = board.get_all_playable_pieces(opponent_color)
        opponent_moves = 0
        for x, y in opponent_pieces:
            moves = board.get_legal_moves((x, y))
            for move in moves:
                opponent_moves += 1

        score += (my_moves - opponent_moves) * 2
        
        return score
    
    def minMax(self, color, board, deep, IS_MAX = True):

        if deep == 0 or board.check_game_status(color) != 'ongoing':
            return self.evaluate(color, board)
        
        if IS_MAX:
            current_color = color
            best_score = -float('inf')
        else:
            current_color = 'b' if color == 'w' else 'w'
            best_score = float('inf')

        all_playable_pieces = board.get_all_playable_pieces(current_color)

        if IS_MAX:
            for x, y in all_playable_pieces:
                piece = board.grid[x][y].piece
                moves = board.get_legal_moves((x, y))
                for a, b in moves:
                    new_board = copy.deepcopy(board)
                    new_piece = new_board.grid[x][y].piece
                    new_board.change_piece(a, b, new_piece, (x, y))
                    score = self.minMax(color, new_board, deep - 1, not IS_MAX)
                    best_score = max(best_score, score)
        else:
            for x, y in all_playable_pieces:
                piece = board.grid[x][y].piece
                moves = board.get_legal_moves((x, y))
                for a, b in moves:
                    new_board = copy.deepcopy(board)
                    new_piece = new_board.grid[x][y].piece
                    new_board.change_piece(a, b, new_piece, (x, y))
                    score = self.minMax(color, new_board, deep - 1, not IS_MAX)
                    best_score = min(best_score, score)
        
        return best_score
        


    def choose_move(self, color, board, deep = 2):
        all_playable_pieces = board.get_all_playable_pieces(color)
        best_score = -float('inf')

        for x, y in all_playable_pieces:
            piece = board.grid[x][y].piece
            moves = board.get_legal_moves((x, y))
            for a, b in moves:
                new_board = copy.deepcopy(board)
                new_piece = new_board.grid[x][y].piece
                new_board.change_piece(a, b, new_piece, (x, y))
                current_score = self.minMax(color, new_board, deep - 1, False)
                if current_score > best_score:
                    best_score = current_score
                    start_best_move_position = (x, y)
                    end_best_move_position = (a, b)

        return start_best_move_position, end_best_move_position
        





        # all_playable_pieces = [
        #     (x, y)
        #     for x in range(8)
        #     for y in range(8)
        #     if board.grid[x][y].piece
        #     and board.grid[x][y].piece.color == color
        #     and board.get_legal_moves([x, y])
        # ]

        # best_move = None
        # current_best_score = -float('inf')

        # for x, y in all_playable_pieces:
        #     piece = board.grid[x][y].piece
        #     if piece:
        #         legal_moves = board.get_legal_moves([x, y])
        #         if legal_moves:
        #             for a, b in legal_moves:
        #                 captured_piece = board.change_piece(a, b, piece, (x, y))
                        
        #                 score = self.evaluate(color, board)

        #                 board.undo_move((x, y), (a, b), captured_piece)

        #                 if score > current_best_score:
        #                     current_best_score = score
        #                     best_move = [[x, y, a, b]]
        #                 elif score == current_best_score:
        #                     best_move.append([x, y, a, b])
                            
        
        # if best_move:
        #     random_best_move = random.choice(best_move)

        #     start_position = (random_best_move[0], random_best_move[1])
        #     end_position = (random_best_move[2], random_best_move[3])

        #     return start_position, end_position


        # if not best_move:
        #     random_ai = Random_ai()
        #     return random_ai.choose_move(color, board)

        # start_position = (best_move[0], best_move[1])
        # end_position = (best_move[2], best_move[3])

        # return start_position, end_position