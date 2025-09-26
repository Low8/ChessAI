

class Piece:
    def __init__(self, color):
        self.color = color
        self.type = None
        self.first_move = True
    
    def get_possible_moves(self, start_position):
        """Retourne tous les mouvements théoriquement possibles selon les règles de la pièce"""
        pass

    def can_move_to(self, start_position, end_position, board):
        """Vérifie si cette pièce peut se déplacer selon ses règles, sans vérifier le chemin"""

        
        if board.would_move_cause_check(start_position, end_position, self.color):
            return False
        else:
            possible_moves = self.get_possible_moves(start_position)
            end_position_tuple = (end_position[0], end_position[1])
            return end_position_tuple in possible_moves
    


## PION
class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = 'p'

    def get_possible_moves(self, start_position):
        row, column = start_position
        possible_moves = []
        
        # Direction du mouvement: les pions blancs montent, les noirs descendent
        direction = -1 if self.color == "w" else 1
        
        # Mouvement simple vers l'avant
        new_row = row + direction
        if 0 <= new_row < 8:
            possible_moves.append((new_row, column))
            
            # Double mouvement pour le premier coup
            if self.first_move:
                new_row = row + 2 * direction
                if 0 <= new_row < 8:
                    possible_moves.append((new_row, column))

        

            # Captures en diagonale
            for col_offset in [-1, 1]:
                new_col = column + col_offset
                if 0 <= new_col < 8:
                    possible_moves.append((new_row, new_col))
        
        return possible_moves
        
    def can_move_to(self, start_position, end_position, board):
        """Surcharge pour gérer les règles spéciales du pion"""
        start_row, start_col = start_position
        end_row, end_col = end_position
        
        # Direction du mouvement
        direction = -1 if self.color == "w" else 1
        

        if board.would_move_cause_check(start_position, end_position, self.color):
            return False
        else:
            # Captures en diagonale (mouvement d'une case en diagonale)
            if abs(start_col - end_col) == 1 and (end_row - start_row) == direction:
                # Cas 1: Capture normale (il y a une pièce adverse sur la case cible)
                target_cell = board.grid[end_row][end_col]
                if target_cell.piece and target_cell.piece.color != self.color:
                    return True
                    
                # Cas 2: Prise en passant - vérification simplifiée
                if board.en_passant_target and (end_row, end_col) == board.en_passant_target:
                    print(f"Validating en passant at {end_row}, {end_col}")
                    return True
                    
                return False
            
            # Mouvement vertical (avancée)
            elif start_col == end_col:
                # Vérifier si la case d'arrivée est vide
                if board.grid[end_row][end_col].piece:
                    return False
                    
                # Mouvement simple (une case)
                if (end_row - start_row) == direction:
                    return True
                    
                # Double mouvement au premier coup
                if self.first_move and (end_row - start_row) == 2 * direction:
                    # Vérifier que la case intermédiaire est libre
                    intermediate_row = start_row + direction
                    if not board.grid[intermediate_row][start_col].piece:
                        return True
            
            return False
        
        


## CAVALIER
class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = 'n'

    def get_possible_moves(self, start_position):
        row, column = start_position
        moves = [
            (row+2, column+1), (row+2, column-1),
            (row-2, column+1), (row-2, column-1),
            (row+1, column+2), (row+1, column-2),
            (row-1, column+2), (row-1, column-2),
        ]
        
        # Filtrer les positions hors plateau
        return [(r, c) for r, c in moves if 0 <= r < 8 and 0 <= c < 8]


## BISHOP
class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = 'b'

    def get_possible_moves(self, start_position):
        row, column = start_position
        possible_moves = []

        directions = [(1,1), (1,-1), (-1,1), (-1,-1)]

        for x, y in directions:
            for distance in range(1, 8):
                new_x_pos = x * distance + row
                new_y_pos = y * distance + column
                if 0 <= new_x_pos < 8 and 0 <= new_y_pos < 8:
                    possible_moves.append((new_x_pos, new_y_pos))
        return possible_moves


## TOUR
class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = 'r'

    def get_possible_moves(self, start_position):
        row, column = start_position
        possible_moves = []

        # Horizontales: même ligne, colonnes différentes
        for c in range(8):
            if c != column:
                possible_moves.append((row, c))
                
        # Verticales: même colonne, lignes différentes
        for r in range(8):
            if r != row:
                possible_moves.append((r, column))
                
        return possible_moves


## QUEEN
class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = 'q'

    def get_possible_moves(self, start_position):
        # La reine combine les mouvements du fou et de la tour
        bishop = Bishop(self.color)
        rook = Rook(self.color)
        
        bishop_moves = bishop.get_possible_moves(start_position)
        rook_moves = rook.get_possible_moves(start_position)
        
        return bishop_moves + rook_moves


## ROI
class King(Piece):
    def __init__(self, color):
        super().__init__(color)
        self.type = 'k'

    def get_possible_moves(self, start_position):
        row, column = start_position
        possible_moves = []
        
        # Le roi peut se déplacer d'une case dans toutes les directions
        for r_offset in [-1, 0, 1]:
            for c_offset in [-1, 0, 1]:
                if r_offset == 0 and c_offset == 0:
                    continue  # Pas de mouvement sur place
                    
                new_x_pos = row + r_offset
                new_y_pos = column + c_offset
                
                if 0 <= new_x_pos < 8 and 0 <= new_y_pos < 8:
                    possible_moves.append((new_x_pos, new_y_pos))

        if self.first_move:
            possible_moves.append((row, column + 2))
            possible_moves.append((row, column - 2))
                    
        return possible_moves
    

    
    def can_move_to(self, start_position, end_position, board):
        start_row, start_column = start_position
        end_row, end_column = end_position

        if abs(end_row - start_row) <= 1 and abs(end_column - start_column) <= 1:
            return super().can_move_to(start_position, end_position, board)
        
        attacking_color = "b" if self.color == "w" else "w"
        if board.is_in_check(self.color):
            return False
        
        if self.first_move and start_row == end_row and abs(end_column - start_column) == 2:

            # Verification petit roque
            if (board.grid[end_row][6].piece == None and
                board.grid[end_row][5].piece == None):
                if (isinstance(board.grid[end_row][7].piece, (Rook)) and
                    board.grid[end_row][7].piece.first_move):
                    if (not board.is_cell_attacked((end_row, 6), attacking_color) and 
                        not board.is_cell_attacked((end_row, 5), attacking_color)):
                        return True
            
            # Vérification grand roque
            elif (board.grid[end_row][1].piece == None and 
                  board.grid[end_row][2].piece == None and 
                  board.grid[end_row][3].piece == None):
                if (isinstance(board.grid[end_row][0].piece, (Rook)) and
                    board.grid[end_row][0].piece.first_move):
                    if (not board.is_cell_attacked((end_row, 1), attacking_color) and 
                        not board.is_cell_attacked((end_row, 2), attacking_color) and
                        not board.is_cell_attacked((end_row, 3), attacking_color)):
                        return True
                
            else:
                return False