from ai import Ai, Random_ai, MinMax_ai

class Player:
    def __init__(self, color, name = "player", is_ai = False, ai_agent = None):
        self.name = name
        self.color = color
        self.captured_pieces = []
        self.in_check = False
        self.is_ai = is_ai
        if self.is_ai and ai_agent:
            agents = {
                "random": Random_ai,
                "minmax": MinMax_ai
            }
            self.ai_agent = agents.get(ai_agent)()
        
        # Définir l'ordre des pièces (de la moins à la plus importante)
        self.piece_order = {
            'p': 1,  # Pion
            'n': 2,  # Cavalier
            'b': 3,  # Fou
            'r': 4,  # Tour
            'q': 5,  # Dame
            'k': 6   # Roi
        }

    def add_captured_piece(self, piece):
        """
        Ajoute une pièce capturée et trie la liste selon un ordre personnalisé
        """
        if piece and hasattr(piece, 'type'):
            self.captured_pieces.append(piece)
            # Trier selon l'ordre défini dans self.piece_order
            # Si le type n'est pas dans le dictionnaire, lui donner une valeur élevée (99)
            self.captured_pieces.sort(key=lambda p: self.piece_order.get(p.type, 99))
