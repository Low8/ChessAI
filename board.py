from cell import Cell
from piece import Rook, Knight, Bishop, Queen, King, Pawn

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.generate_board()
        self.en_passant_target = None  # Position où la prise en passant est possible

    def generate_board(self):
        for x in range(8):
            for y in range(8):
                if (x + y) % 2 == 0:
                    color = (255, 255, 255)  # Blanc
                else:
                    color = (150, 111, 84)  # Gris foncé
                    
                self.grid[x][y] = Cell(color)
        self.ini_pieces_position()

    def ini_pieces_position(self):
        # Code existant sans modification
        self.grid[0][0].piece = Rook("b")
        self.grid[0][1].piece = Knight("b")
        self.grid[0][2].piece = Bishop("b")
        self.grid[0][3].piece = Queen("b")
        self.grid[0][4].piece = King("b")
        self.grid[0][5].piece = Bishop("b")
        self.grid[0][6].piece = Knight("b")
        self.grid[0][7].piece = Rook("b")
        self.grid[1][0].piece = Pawn("b")
        self.grid[1][1].piece = Pawn("b")
        self.grid[1][2].piece = Pawn("b")
        self.grid[1][3].piece = Pawn("b")
        self.grid[1][4].piece = Pawn("b")
        self.grid[1][5].piece = Pawn("b")
        self.grid[1][6].piece = Pawn("b")
        self.grid[1][7].piece = Pawn("b")
        
        self.grid[7][0].piece = Rook("w")
        self.grid[7][1].piece = Knight("w")
        self.grid[7][2].piece = Bishop("w")
        self.grid[7][3].piece = Queen("w")
        self.grid[7][4].piece = King("w")
        self.grid[7][5].piece = Bishop("w")
        self.grid[7][6].piece = Knight("w")
        self.grid[7][7].piece = Rook("w")
        self.grid[6][0].piece = Pawn("w")
        self.grid[6][1].piece = Pawn("w")
        self.grid[6][2].piece = Pawn("w")
        self.grid[6][3].piece = Pawn("w")
        self.grid[6][4].piece = Pawn("w")
        self.grid[6][5].piece = Pawn("w")
        self.grid[6][6].piece = Pawn("w")
        self.grid[6][7].piece = Pawn("w")

    def change_piece(self, x, y, piece, start_position=None):
        """Change une pièce à la position donnée et retourne l'ancienne pièce"""
        if not (0 <= x < 8 and 0 <= y < 8):
            return None
        
        old_piece = self.grid[x][y].piece
        self.grid[x][y].piece = piece
        
        # Si c'est un pion qui se déplace de 2 cases, définir la cible de prise en passant
        if piece and start_position and isinstance(piece, Pawn):
            start_row, start_col = start_position
            if abs(start_row - x) == 2:  # Mouvement de 2 cases

                # On met la cible sur la première case et non la deuxième

                en_passant_row = (start_row + x) // 2
                self.en_passant_target = (en_passant_row, y)
                print(f"En passant target set to: {self.en_passant_target}")
            else:
                self.en_passant_target = None
        else:
            self.en_passant_target = None
            
        return old_piece

    def undo_move(self, start_pos, end_pos, captured_piece):
        """
        Annule un coup :
        - Replace la pièce à sa position initiale
        - Remet la pièce capturée (s'il y en avait une)
        - Réinitialise la cible en_passant
        """
        start_x, start_y = start_pos
        end_x, end_y = end_pos
    
        # Déplace la pièce de end vers start
        moved_piece = self.grid[end_x][end_y].piece
        self.change_piece(start_x, start_y, moved_piece)
    
        # Replace la pièce capturée à end (ou None si pas de capture)
        self.change_piece(end_x, end_y, captured_piece)
    
        # Réinitialise la cible de prise en passant
        self.en_passant_target = None
    
    def is_cell_attacked(self, position, attacking_color):
        # attacking color = color que l'on veut attaquer
        row, column = position

        # on parcour tout le tableau on regarde si il y a une piece de la meme couleur 
        # que la couleur que l'on veut attaquer. 
        # Puis on regarde si la piece peux atteindre avec un moove possible la position.
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c].piece
                if piece and piece.color == attacking_color:
                    # Pour un pion
                    if isinstance(piece, Pawn):
                        direction = -1 if piece.color == "w" else 1
                        if r + direction == row and (c + 1 == column or c - 1 == column):
                            return True
                    # Pour les autres pièces
                    elif self._can_piece_attack_without_check_verification(piece, (r, c), position):
                        return True
        return False
    
    def _can_piece_attack_without_check_verification(self, piece, start_position, end_position):
        """
        Vérifie si une pièce peut attaquer une position, sans vérifier l'échec
        Cette méthode est utilisée par is_cell_attacked pour éviter la récursion infinie
        """
        # Pour les pions, traitement spécial des diagonales d'attaque
        if isinstance(piece, Pawn):
            start_row, start_col = start_position
            end_row, end_col = end_position
            direction = -1 if piece.color == "w" else 1
            return (end_row - start_row) == direction and abs(end_col - start_col) == 1

        # Pour le roi, uniquement les mouvements d'une case
        if isinstance(piece, King):
            start_row, start_col = start_position
            end_row, end_col = end_position
            return abs(end_row - start_row) <= 1 and abs(end_col - start_col) <= 1

        # Pour les autres pièces, vérifier les mouvements possibles sans récursion
        possible_moves = piece.get_possible_moves(start_position)
        if end_position in possible_moves:
            # Pour les pièces qui ne peuvent pas sauter, vérifier si le chemin est dégagé
            if isinstance(piece, (Rook, Bishop, Queen)):
                return self.is_path_clear(start_position, end_position)
            return True

        return False

    def is_in_check(self, king_color):
        # On commence par chercher le roi
        # puis on vérifie si le roi est sur une case qui se fait attaquer
        king_position = None

        king_position = None
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c].piece
                if isinstance(piece, King) and piece.color == king_color:
                    king_position = (r, c)
                    break
            if king_position:
                break

        if not king_position:
            return False
        
        attacking_color = "b" if king_color == "w" else "w"
        return self.is_cell_attacked(king_position, attacking_color)
    
    def would_move_cause_check(self, start_postion, end_position, king_color):
        # dans cette méthode on simule le mouvement de la piece on vérifie si ce mouvement met
        # en echec le roi de notre couleur puis restaure le mouvement

        start_row, start_column = start_postion
        end_row, end_column = end_position

        moving_piece = self.grid[start_row][start_column].piece
        captured_piece = self.grid[end_row][end_column].piece

        self.grid[start_row][start_column].piece = None
        self.grid[end_row][end_column].piece = moving_piece

        is_in_check =  self.is_in_check(king_color)

        self.grid[start_row][start_column].piece = moving_piece
        self.grid[end_row][end_column].piece = captured_piece

        return is_in_check
    
    def is_checkmate(self, king_color):
        # On regarde si le roi est en echec
        # puis on cherche si une piece à au moins un coup valide
        # si aucune piece n'en a alors on retourne vrai
        if not self.is_in_check(king_color):
            return False
        
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c].piece
                if piece and king_color == piece.color:
                    legals_move = self.get_legal_moves((r, c))
                    if legals_move != []:
                        return False
        return True
    
    def is_stalemate(self, king_color):
        # On cherche si une piece à au moins un coup valide
        # si aucune piece n'en a alors on retourne vrai
        # on ne regarde pas si le roi est en echec à la base
        
        for r in range(8):
            for c in range(8):
                piece = self.grid[r][c].piece
                if piece and king_color == piece.color:
                    legals_move = self.get_legal_moves((r, c))
                    if legals_move != []:
                        return False
        return True
    
    def pawn_in_last_row(self, color):
        row = 0 if color == "w" else 7

        for c in range(8):
            piece = self.grid[row][c].piece
            if piece and isinstance(piece, Pawn) and piece.color == color:
                return (row, c)
        return None
    
        
    def is_path_clear(self, start_position, end_position):
        """Vérifie si le chemin entre deux positions est libre"""
        start_row, start_column = start_position
        end_row, end_column = end_position

        x_direction = 0 if start_row == end_row else (1 if start_row < end_row else -1)
        y_direction = 0 if start_column == end_column else (1 if start_column < end_column else -1)

        current_row, current_column = start_row + x_direction, start_column + y_direction
        while (current_row, current_column) != (end_row, end_column):
            if self.grid[current_row][current_column].piece:
                return False  # Chemin bloqué
            current_row += x_direction
            current_column += y_direction
        
        return True
        
    def is_move_valid(self, start_position, end_position):
        """Vérifie si un mouvement est valide selon les règles d'échecs"""
        # Vérifier les limites du plateau
        if not (0 <= start_position[0] < 8 and 0 <= start_position[1] < 8 and 
                0 <= end_position[0] < 8 and 0 <= end_position[1] < 8):
            return False
        
        start_row, start_column = start_position
        end_row, end_column = end_position
        
        # Récupérer la pièce à déplacer
        piece = self.grid[start_row][start_column].piece
        if not piece:
            return False
        
        # Récupérer la pièce à la position d'arrivée
        target_cell = self.grid[end_row][end_column]

        # Vérifier qu'on ne capture pas une pièce de sa propre couleur
        if target_cell.piece and target_cell.piece.color == piece.color:
            return False
            
        # Vérifier si le mouvement est valide pour cette pièce
        if not piece.can_move_to(start_position, end_position, self):
            return False
            
        # Pour les pièces qui ne peuvent pas sauter, vérifier si le chemin est dégagé
        if isinstance(piece, (Rook, Bishop, Queen)):
            if not self.is_path_clear(start_position, end_position):
                return False
                
        
                
        return True
        
    def get_legal_moves(self, position):
        """Retourne tous les mouvements légaux pour une pièce à une position donnée"""
        row, column = position
        piece = self.grid[row][column].piece
        
        if not piece:
            return []
            
        # Récupérer tous les mouvements théoriques
        possible_moves = piece.get_possible_moves(position)
        legal_moves = []
        
        # Filtrer pour ne garder que les mouvements légaux
        for move in possible_moves:
            if self.is_move_valid(position, move):
                legal_moves.append(move)
                
        return legal_moves

    def promote_pawn(self, position, new_piece_type):
        """Promotion d'un pion en une autre pièce"""
        row, col = position
        pawn = self.grid[row][col].piece
        
        if not pawn or not isinstance(pawn, Pawn):
            return None
        
        # Création de la nouvelle pièce
        new_piece = None
        if new_piece_type == "q":
            new_piece = Queen(pawn.color)
        elif new_piece_type == "b":
            new_piece = Bishop(pawn.color)
        elif new_piece_type == "n":
            new_piece = Knight(pawn.color)
        elif new_piece_type == "r":
            new_piece = Rook(pawn.color)
            
        # Remplacement du pion
        if new_piece:
            old_piece = self.grid[row][col].piece
            self.grid[row][col].piece = new_piece
            return old_piece
        
        return None

    def execute_castling(self, king_position, target_position):
        """Exécute le mouvement de roque"""
        king_row, king_col = king_position
        target_row, target_col = target_position
        
        # Déterminer la position de la tour
        is_kingside = target_col > king_col
        rook_old_col = 7 if is_kingside else 0
        rook_new_col = 5 if is_kingside else 3
        
        # Récupérer les pièces
        king = self.grid[king_row][king_col].piece
        rook = self.grid[king_row][rook_old_col].piece
        
        if not king or not rook:
            return False
        
        # Déplacer les pièces
        self.grid[king_row][target_col].piece = king
        self.grid[king_row][king_col].piece = None
        self.grid[king_row][rook_new_col].piece = rook
        self.grid[king_row][rook_old_col].piece = None
        
        # Mettre à jour l'état des pièces
        king.first_move = False
        rook.first_move = False
        
        return True

    def execute_en_passant(self, pawn_position, target_position):
        """Exécute une prise en passant"""
        pawn_row, pawn_col = pawn_position
        target_row, target_col = target_position
        
        # Récupérer le pion qui capture
        pawn = self.grid[pawn_row][pawn_col].piece
        
        if not pawn or not isinstance(pawn, Pawn):
            return None
        
        # La position du pion capturé est sur la même ligne que le pion qui capture
        # et sur la même colonne que la cible
        capture_row = pawn_row
        capture_col = target_col
        
        # Récupérer le pion capturé
        captured_pawn = self.grid[capture_row][capture_col].piece
        
        # Exécuter le mouvement
        self.grid[target_row][target_col].piece = pawn
        self.grid[pawn_row][pawn_col].piece = None
        self.grid[capture_row][capture_col].piece = None
        
        return captured_pawn

    def check_game_status(self, color):
        """Vérifie l'état du jeu pour un joueur donné"""
        if self.is_checkmate(color):
            return "checkmate"
        elif self.is_stalemate(color):
            return "stalemate"
        else:
            return "ongoing"

    