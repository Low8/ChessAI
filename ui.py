import pygame
import os
from board import Board
from controller import Controller

class Ui:
    def __init__(self, width = 800, height = 950):
        if not pygame.get_init():
            pygame.init()
        
        # Création de la fenêtre
        self.width = width
        self.height = height

        self.board_width = 750
        self.board_height = 750

        # Calcul des décalages pour centrer le plateau
        self.board_x_offset = (self.width - self.board_width) / 2
        self.board_y_offset = (self.height - self.board_height) / 2

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Jeu d'Échecs")
        
        # Calcul de la taille des cellules
        self.cell_width = self.board_width / 8
        self.cell_height = self.board_height / 8

        #taille des pieces capturées
        self.captured_cell_width = self.cell_width * 0.8
        self.captured_cell_height = self.cell_height * 0.8
        
        # Création du plateau (modèle)
        self.board = Board()
        self.controller = Controller(self.board)

        #création d'une 
        self.pieces_load = {}
        self.load_pieces()

        # button pour la promotion
        self.promotion_buttons = []

        # Pause boolean
        self.paused = False

    def load_pieces(self):
        path = os.path.join("assets", "other_pieces")

        pieces_type = ["b", "k", "n", "p", "q", "r"]
        pieces_color = ["w", "b"]

        for piece_type in pieces_type:
            for piece_color in pieces_color:
                piece_path = os.path.join(path, f"{piece_color}_{piece_type}.png")
                try:
                    img = pygame.image.load(piece_path)

                    img = pygame.transform.scale(img, (self.cell_width, self.cell_height))

                    self.pieces_load[f"{piece_color}_{piece_type}"] = img
                except:
                    print(f"Impossible de charger l'image: {piece_path}")


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    position = pygame.mouse.get_pos()

                    # Si ce n'est pas au tour de l'ia on gère les click utilisateurs
                    if not self.controller.current_player.is_ai:
                        if self.controller.promotion_available:
                            for button in self.promotion_buttons:
                                button_x, button_y, width, height, piece_type = button
                                if button_x <= position[0] <= button_x + width and button_y <= position[1] <= button_y + height:
                                    # L'utilisateur a sélectionné cette pièce pour la promotion
                                    self.controller.promote_pawn(piece_type)
                                    # Continuer le jeu après la promotion
                                    self.controller.next_turn()
                                    break
                        else:
                            # Ajustement de la position du clic pour prendre en compte le décalage
                            adjusted_position = (
                                position[0] - self.board_x_offset,
                                position[1] - self.board_y_offset
                            )
                            self.controller.handle_click(adjusted_position, self.cell_width, self.cell_height)
                            print(f"click {adjusted_position}")
                    # endif
                        

        return True
    
                

    def draw(self):
        self.screen.fill((50, 50, 50))  # Gris foncé pour mieux voir le plateau

        # Dessin des cellules
        for row in range(8):
            for column in range(8):
                cell = self.board.grid[row][column]

                # Calcul de la position avec décalage pour centrage
                x = column * self.cell_width + self.board_x_offset
                y = row * self.cell_height + self.board_y_offset

                # Dessin de la cellule
                pygame.draw.rect(
                    self.screen,
                    cell.color,
                    (x, y, self.cell_width, self.cell_height)
                )

                # Dessiner les indicateurs de mouvements légaux
                move_position = (row, column)
                if move_position in self.controller.legal_moves:
                    # Option 1: Cercle plein semi-transparent
                    indicator_surface = pygame.Surface((self.cell_width, self.cell_height), pygame.SRCALPHA)
                    pygame.draw.circle(
                        indicator_surface,
                        (180, 140, 255, 80),  # Vert semi-transparent
                        (self.cell_width // 2, self.cell_height // 2),
                        self.cell_width // 6
                    )
                    self.screen.blit(indicator_surface, (x, y))

                # Dessin de la pièce si présente
                if cell.piece:
                    piece_color = cell.piece.color
                    piece_type = cell.piece.type
                    image_name = f"{piece_color}_{piece_type}"

                    if image_name in self.pieces_load:
                        self.screen.blit(
                            self.pieces_load[image_name],
                            (x, y)
                        )

        # on affiche les bouton si il y a un cas possible détecté
        if not self.controller.current_player.is_ai:
            if self.controller.promotion_available:
                print("Tentative d'affichage des options de promotion")
                self.draw_promotion_options()


        if self.controller.game_over:
            # Créer un rectangle semi-transparent pour le fond du message
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Noir semi-transparent
            self.screen.blit(overlay, (0, 0))

            if self.controller.winner:
                font = pygame.font.SysFont("Arial", 48)
                text = font.render(f"Échec et mat! {self.controller.winner.name} gagne!", True, (255, 0, 0))
                text_rect = text.get_rect(center=(self.width//2, self.height//2))
                self.screen.blit(text, text_rect)
            else:
                font = pygame.font.SysFont("Arial", 48)
                text = font.render("Pat! Match nul.", True, (0, 0, 255))
                text_rect = text.get_rect(center=(self.width//2, self.height//2))
                self.screen.blit(text, text_rect)
                


        # gestion de la capture des piece
        if self.controller.white_player.captured_pieces:
            captured_pieces = self.controller.white_player.captured_pieces

            for i, captured_piece in enumerate(captured_pieces):
                if captured_piece:
                    piece_color = captured_piece.color
                    piece_type = captured_piece.type
                    image_name = f"{piece_color}_{piece_type}"

                    x = i * self.captured_cell_width * 0.5+ self.board_x_offset
                    y = self.board_y_offset + self.board_height

                    if image_name in self.pieces_load:
                        # Créer une version redimensionnée
                        small_image = pygame.transform.scale(self.pieces_load[image_name], (int(self.captured_cell_width), int(self.captured_cell_height)))
                        self.screen.blit(small_image, (x, y))
        
        if self.controller.black_player.captured_pieces:
            captured_pieces = self.controller.black_player.captured_pieces

            for i, captured_piece in enumerate(captured_pieces):
                if captured_piece:
                    piece_color = captured_piece.color
                    piece_type = captured_piece.type
                    image_name = f"{piece_color}_{piece_type}"

                    x = i * self.captured_cell_width * 0.5 + self.board_x_offset
                    y = self.board_y_offset - self.captured_cell_height

                    if image_name in self.pieces_load:
                        # Créer une version redimensionnée
                        small_image = pygame.transform.scale(self.pieces_load[image_name], (int(self.captured_cell_width), int(self.captured_cell_height)))
                        self.screen.blit(small_image, (x, y))


        
        pygame.display.flip()

    def draw_promotion_options(self):
        """Dessine les options de promotion si une promotion est en attente"""
        if not self.controller.promotion_available:
            return

        row, col = self.controller.promotion_position
        pawn_color = self.board.grid[row][col].piece.color

        # Créer un rectangle de fond pour les options
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Noir semi-transparent
        self.screen.blit(overlay, (0, 0))

        # Dessiner le texte de sélection
        font = pygame.font.SysFont("Arial", 32)
        text = font.render("Choisissez une pièce pour la promotion:", True, (255, 255, 255))
        self.screen.blit(text, (self.width // 2 - text.get_width() // 2, self.height // 2 - 100))

        # Dessiner les options (Dame, Tour, Fou, Cavalier)
        piece_types = ["q", "r", "b", "n"]
        piece_names = ["Dame", "Tour", "Fou", "Cavalier"]

        option_width = 120
        option_height = 120
        total_width = option_width * 4 + 30 * 3  # 4 options avec 3 espaces entre elles
        start_x = (self.width - total_width) // 2

        self.promotion_buttons = []

        for i, (piece_type, piece_name) in enumerate(zip(piece_types, piece_names)):
            button_x = start_x + i * (option_width + 30)
            button_y = self.height // 2

            # Dessiner le fond du bouton
            pygame.draw.rect(self.screen, (200, 200, 200), (button_x, button_y, option_width, option_height))

            # Dessiner le nom de la pièce
            name_text = font.render(piece_name, True, (0, 0, 0))
            self.screen.blit(name_text, (button_x + option_width // 2 - name_text.get_width() // 2, 
                                         button_y + option_height // 2 - name_text.get_height() // 2))

            # Stocker les informations du bouton pour la détection des clics
            self.promotion_buttons.append((button_x, button_y, option_width, option_height, piece_type))



    def handle_ai(self):
        if self.controller.current_player.is_ai and not self.paused and not self.controller.game_over:
            pygame.time.delay(200)
            self.controller.handle_ai()


    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running == True:
            clock.tick(30)
            
            self.handle_ai()
            running = self.handle_events()

            self.draw()
            if not self.controller.game_over:
                pass
        pygame.quit()