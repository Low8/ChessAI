import random
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

        # Fonction permettant d'évaluer le tableau en fonction d'une couleur
        # On ajoute les points de la piece si elle est de la couleur voulu sinon on les soustrer

        points = {
            "p" : 1,
            "n" : 3,
            "b" : 3,
            "r" : 5,
            "q" : 9,
            "k" : 100
        }

        score = 0

        for x in range(8):
            for y in range(8):
                piece = board.grid[x][y].piece
                if piece:
                    value = points.get(piece.type, 0)
                    if piece.color == color:
                        score += value
                    else:
                        score -= value

        return score
    
    def choose_move(self, color, board):

        all_playable_pieces = [
            (x, y)
            for x in range(8)
            for y in range(8)
            if board.grid[x][y].piece
            and board.grid[x][y].piece.color == color
            and board.get_legal_moves([x, y])
        ]

        best_move = None
        current_best_score = -float('inf')

        for x, y in all_playable_pieces:
            piece = board.grid[x][y].piece
            if piece:
                legal_moves = board.get_legal_moves([x, y])
                if legal_moves:
                    for a, b in legal_moves:
                        captured_piece = board.change_piece(a, b, piece, (x, y))
                        
                        score = self.evaluate(color, board)

                        board.undo_move((x, y), (a, b), captured_piece)

                        if score > current_best_score:
                            current_best_score = score
                            best_move = [[x, y, a, b]]
                        elif score == current_best_score:
                            best_move.append([x, y, a, b])
                            
        
        if best_move:
            random_best_move = random.choice(best_move)

            start_position = (random_best_move[0], random_best_move[1])
            end_position = (random_best_move[2], random_best_move[3])

            return start_position, end_position


        if not best_move:
            random_ai = Random_ai()
            return random_ai.choose_move(color, board)

        start_position = (best_move[0], best_move[1])
        end_position = (best_move[2], best_move[3])

        return start_position, end_position