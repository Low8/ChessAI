from board import Board
from player import Player
from piece import (Piece, Pawn, Knight, Bishop, Rook, Queen, King)

class Controller:
    def __init__(self, board):
        ## Création du tableau
        self.board = board if board else Board()

        ## Création des deux joueur
        self.white_player = Player("w", "joueur blanc", True, "minmax")
        self.black_player = Player("b", "joueur noir", True, "random")
        self.winner = None

        self.game_over = False

        self.current_player = self.white_player
        self.current_piece = None

        # position actuel et derniere position
        self.current_position = [0, 0]
        self.last_position = [-1, -1]

        # stockage des moves légaux pour les afficher ensuite
        self.legal_moves = []

        # Pour la promotion des pion
        self.promotion_available = False
        self.promotion_position = None

    def get_legal_moves(self, position):
        """
        Délègue au plateau la recherche des mouvements légaux
        """
        return self.board.get_legal_moves(position)

    def is_valid_move(self, start_position, end_position):
        """
        Délègue au plateau la vérification de la validité du mouvement
        """
        print(f"Checking move from {start_position} to {end_position}")
        return self.board.is_move_valid(start_position, end_position)

    def is_path_clear(self, start_position, end_position):
        """
        Délègue au plateau la vérification du chemin
        """
        return self.board.is_path_clear(start_position, end_position)

    def execute_move(self, start_position, end_position):
        """
        Méthode unifiée pour exécuter un mouvement après validation.
        Gère les mouvements spéciaux (roque, prise en passant) et réguliers.
        
        Retourne True si le mouvement a été exécuté avec succès, False sinon.
        """
        # Vérifier si le mouvement est valide
        if not self.is_valid_move(start_position, end_position):
            print(f"Mouvement invalide de {start_position} à {end_position}")
            return False
            
        # Récupérer la pièce à déplacer
        piece = self.board.grid[start_position[0]][start_position[1]].piece
        if not piece:
            print(f"Aucune pièce à la position {start_position}")
            return False
            
        # Gérer le roque
        if isinstance(piece, King) and abs(start_position[1] - end_position[1]) == 2:
            castling_success = self.board.execute_castling(start_position, end_position)
            return castling_success
            
        # Gérer la prise en passant
        if isinstance(piece, Pawn) and tuple(end_position) == self.board.en_passant_target:
            captured_piece = self.board.execute_en_passant(start_position, end_position)
            if captured_piece:
                self.current_player.add_captured_piece(captured_piece)
                return True
            return False
            
        # Mouvement standard
        captured_piece = self.board.change_piece(
            end_position[0], end_position[1],
            piece,
            start_position
        )
        
        # Mettre à jour l'état de la pièce et du plateau
        self.board.grid[start_position[0]][start_position[1]].piece = None
        if hasattr(piece, 'first_move'):
            piece.first_move = False
            
        # Gérer la capture
        if captured_piece:
            self.current_player.add_captured_piece(captured_piece)
            
        return True

    def handle_click(self, position, cell_width, cell_height):
        ## determination du numéro de ligne ligne et de colonne du click
        self.current_position[0] = int(position[1] // cell_width)
        self.current_position[1] = int(position[0] // cell_height)

        # Vérification des limites du plateau
        if not (0 <= self.current_position[0] < 8 and 0 <= self.current_position[1] < 8):
            return False
        
        cell = self.board.grid[self.current_position[0]][self.current_position[1]]

        # selection dune piece de notre couleur
        if self.last_position[0] != -1 and self.last_position[1] != -1:
            if cell.piece and cell.piece.color == self.current_player.color:
                # Mise à jour de la sélection
                self.last_position[0] = self.current_position[0]
                self.last_position[1] = self.current_position[1]
                self.legal_moves = self.get_legal_moves(self.last_position)

            # si on ne click pas sur une piece de notre couleur alors on tente un deplacement
            else:
                # Exécuter le mouvement via la méthode unifiée
                if self.execute_move(self.last_position, self.current_position):
                    # Vérifier la promotion des pions après un mouvement réussi
                    piece = self.board.grid[self.current_position[0]][self.current_position[1]].piece
                    if isinstance(piece, Pawn):
                        end_row = self.current_position[0]
                        if (piece.color == "w" and end_row == 0) or (piece.color == "b" and end_row == 7):
                            self.promotion_position = (end_row, self.current_position[1])
                            self.promotion_available = True
                            return  # Attendre la sélection de promotion
                    
                    # Réinitialiser et passer au tour suivant
                    self.last_position = [-1, -1]
                    self.next_turn()
        
        # Première sélection
        else:
            # Vérifier qu'on sélectionne bien une pièce de sa couleur
            if cell.piece and cell.piece.color == self.current_player.color:
                self.last_position[0] = self.current_position[0]
                self.last_position[1] = self.current_position[1]

                # Calculer et stocker les mouvements légaux
                self.legal_moves = self.get_legal_moves(self.last_position)

    def next_turn(self):
        if self.check_for_pawn_promotion():
            return

        self.current_player = self.black_player if self.current_player == self.white_player else self.white_player
        self.legal_moves = []

        # self.board.debug_dame_en_danger()

        # Déléguer au modèle la vérification de l'état du jeu
        game_status = self.board.check_game_status(self.current_player.color)
        
        if game_status == "checkmate":
            self.handle_checkmate()
        elif game_status == "stalemate":
            self.handle_stalemate()

    def check_for_pawn_promotion(self):
        # on mets à jour les attribut de promotion si il y a un cas de promotion
        promotion_position = self.board.pawn_in_last_row(self.current_player.color)
        print("checking pawn promotion")

        if promotion_position:
            self.promotion_position = promotion_position
            self.promotion_available = True
            return True
        
        self.promotion_position = None
        return False
    
    def promote_pawn(self, new_piece_type):
        """Coordonne la promotion d'un pion en déléguant au modèle"""
        if not self.promotion_position:
            print("Pas de position de promotion définie")
            return False
        
        # Déléguer au modèle la promotion effective
        old_piece = self.board.promote_pawn(self.promotion_position, new_piece_type)
        
        if old_piece:
            # Gestion de l'état du contrôleur
            self.promotion_available = False
            self.promotion_position = None
            print("Promotion réussie")
            return True
        else:
            print("Échec de la promotion")
            return False

    def handle_checkmate(self):
        self.winner = self.white_player if self.current_player.color == "b" else self.black_player
    
        # Afficher un message ou déclencher un événement de fin de partie
        print(f"Échec et mat ! Le {self.winner.name} gagne la partie !")
        self.game_over = True

    def handle_stalemate(self):
        print("Pat ! La partie se termine par un match nul.")
        self.game_over = True

    def handle_ai(self):
        correct_move = False

        # Obtenir le mouvement choisi par l'IA
        start_position, end_position = self.current_player.ai_agent.choose_move(self.current_player.color, self.board)
        # Vérifier si un mouvement valide a été trouvé
        if start_position is None or end_position is None:
            print("L'IA n'a pas pu trouver de mouvement valide")
            self.next_turn()  # Passer le tour
            return
        
        print(f"IA joue: {start_position} -> {end_position}")

        # Exécuter le mouvement en utilisant la méthode unifiée
        if self.execute_move(start_position, end_position):
            # Vérifier la promotion des pions après un mouvement réussi
            piece = self.board.grid[end_position[0]][end_position[1]].piece
            if isinstance(piece, Pawn):
                end_row = end_position[0]
                if (piece.color == "w" and end_row == 0) or (piece.color == "b" and end_row == 7):
                    # Pour l'IA, choisir automatiquement la dame comme promotion
                    self.promotion_position = (end_row, end_position[1])
                    self.promote_pawn("q")
            # Passer au tour suivant
            self.next_turn()
        else:
            print("Mouvement invalide choisi par l'IA")
            self.next_turn()