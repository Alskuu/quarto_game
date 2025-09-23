import tkinter as tk
from PIL import Image, ImageTk
import os
import time

class QuartoGUI:
    def __init__(self, game, image_folder="images_pieces"):
        """
        Interface graphique pour Quarto.
        - game : instance de Quarto
        - image_folder : dossier contenant les images des pièces
        """
        self.game = game
        self.image_folder = image_folder

        self.root = tk.Tk()
        self.root.title("Quarto - Partie en cours")

        # Zone en haut : joueur courant + pièce à placer
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10)

        self.player_label = tk.Label(self.top_frame, text="Joueur ?", font=("Arial", 16, "bold"))
        self.player_label.pack(side="left", padx=20)

        # Configuration du canvas
        self.cell_size = 100

        self.piece_canvas = tk.Canvas(self.top_frame, width=self.cell_size, height=self.cell_size, bg="lightgray")
        self.piece_canvas.pack(side="left", padx=20)

        # Canvas principal du plateau (avec espace pour les coordonnées)
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack()
        
        # Zone pour le plateau et ses coordonnées
        self.board_container = tk.Frame(self.board_frame)
        self.board_container.pack()
        
        # Frame pour les coordonnées Y (ordonnées) à gauche
        self.y_labels_frame = tk.Frame(self.board_container)
        self.y_labels_frame.pack(side="left")
        
        # Labels pour les coordonnées Y (ordonnées)
        for i in range(self.game.BOARD_SIDE):
            label = tk.Label(self.y_labels_frame, text=str(i), font=("Arial", 10, "bold"), height=1)
            label.pack()

        # Frame pour le plateau et les coordonnées X
        self.board_x_frame = tk.Frame(self.board_container)
        self.board_x_frame.pack(side="left")
        
        # Labels pour les coordonnées X (abscisses) au-dessus du plateau
        self.x_labels_frame = tk.Frame(self.board_x_frame)
        self.x_labels_frame.pack()
        
        # Frame pour les numéros des colonnes
        self.column_labels_frame = tk.Frame(self.x_labels_frame)
        self.column_labels_frame.pack()
        
        for j in range(self.game.BOARD_SIDE):
            label = tk.Label(self.column_labels_frame, text=str(j), font=("Arial", 10, "bold"), width=2)
            label.pack(side="left")

        self.canvas = tk.Canvas(
            self.board_x_frame,
            width=self.game.BOARD_SIDE * self.cell_size,
            height=self.game.BOARD_SIDE * self.cell_size,
            bg="white"
        )
        self.canvas.pack()

        # Zone pour les pièces non utilisées (en dessous du plateau)
        self.available_pieces_frame = tk.Frame(self.root)
        self.available_pieces_frame.pack(pady=10)
        
        self.available_pieces_label = tk.Label(self.available_pieces_frame, text="Pièces disponibles :", font=("Arial", 12, "bold"))
        self.available_pieces_label.pack()
        
        # Canvas pour afficher les pièces disponibles (4x4)
        self.available_canvas = tk.Canvas(
            self.available_pieces_frame,
            width=4 * (self.cell_size // 2),
            height=4 * (self.cell_size // 2),
            bg="lightblue"
        )
        self.available_canvas.pack(pady=5)

        ## Charger toutes les images des pièces (indexées de 0 à 15)
        self.piece_images = {}

        for i in range(16):
            img_path = os.path.join(self.image_folder, f"{i}.png")
            
            # Ouvrir l'image, la redimensionner et la convertir pour Tkinter
            img = Image.open(img_path).resize((self.cell_size - 10, self.cell_size - 10))
            tk_img = ImageTk.PhotoImage(img)

            # Ajouter à la liste
            self.piece_images[i]=tk_img

        # Dessiner la grille initiale
        self.draw_grid()
        # Dessiner les pièces disponibles initiales
        self.draw_available_pieces()

    def draw_grid(self):
        """Dessine la grille vide avec des axes gradués"""
        # Dessiner la grille
        for i in range(self.game.BOARD_SIDE):
            for j in range(self.game.BOARD_SIDE):
                x0 = j * self.cell_size
                y0 = i * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="black", width=2)
        
        # Dessiner les axes gradués avec des flèches
        # Axe X (horizontal) - gradué
        self.canvas.create_line(0, 0, self.game.BOARD_SIDE * self.cell_size, 0, fill="red", width=2)
        # Graduations sur l'axe X
        for j in range(self.game.BOARD_SIDE + 1):
            x = j * self.cell_size
            self.canvas.create_line(x, 0, x, 8, fill="red", width=2)
        # Numéros de graduation au-dessus avec label X
        for j in range(self.game.BOARD_SIDE):
            x = j * self.cell_size + self.cell_size // 2
            self.canvas.create_text(x, 20, text=f"X={j}", font=("Arial", 12, "bold"), fill="black")
        # Flèche de l'axe X
        arrow_size = 15
        self.canvas.create_polygon(
            self.game.BOARD_SIDE * self.cell_size - arrow_size, 0,
            self.game.BOARD_SIDE * self.cell_size, arrow_size,
            self.game.BOARD_SIDE * self.cell_size, -arrow_size,
            fill="red", outline="red"
        )
        
        # Axe Y (vertical) - gradué
        self.canvas.create_line(0, 0, 0, self.game.BOARD_SIDE * self.cell_size, fill="blue", width=2)
        # Graduations sur l'axe Y
        for i in range(self.game.BOARD_SIDE + 1):
            y = i * self.cell_size
            self.canvas.create_line(0, y, 8, y, fill="blue", width=2)
        # Numéros de graduation à gauche avec label Y
        for i in range(self.game.BOARD_SIDE):
            y = i * self.cell_size + self.cell_size // 2
            self.canvas.create_text(20, y, text=f"Y={i}", font=("Arial", 12, "bold"), fill="black")
        # Flèche de l'axe Y
        self.canvas.create_polygon(
            0, self.game.BOARD_SIDE * self.cell_size - arrow_size,
            arrow_size, self.game.BOARD_SIDE * self.cell_size,
            -arrow_size, self.game.BOARD_SIDE * self.cell_size,
            fill="blue", outline="blue"
        )

    def draw_available_pieces(self):
        """Dessine les pièces disponibles sans numéros"""
        self.available_canvas.delete("all")
        
        # Taille des pièces dans la zone disponible (plus petites)
        small_cell_size = self.cell_size // 2
        
        # Obtenir le statut du plateau pour savoir quelles pièces sont utilisées
        board = self.game.get_board_status()
        used_pieces = set()
        for i in range(self.game.BOARD_SIDE):
            for j in range(self.game.BOARD_SIDE):
                if board[i, j] >= 0:
                    used_pieces.add(board[i, j])
        
        # Dessiner les pièces non utilisées dans une grille 4x4
        piece_count = 0
        for i in range(16):
            if i not in used_pieces:
                row = piece_count // 4
                col = piece_count % 4
                
                x = col * small_cell_size + small_cell_size // 2
                y = row * small_cell_size + small_cell_size // 2
                
                # Dessiner l'image de la pièce
                if i in self.piece_images:
                    # Créer une version plus petite de l'image
                    small_img = Image.open(os.path.join(self.image_folder, f"{i}.png")).resize((small_cell_size - 5, small_cell_size - 5))
                    small_tk_img = ImageTk.PhotoImage(small_img)
                    
                    # Stocker la référence pour éviter la suppression par le garbage collector
                    if not hasattr(self, 'small_piece_images'):
                        self.small_piece_images = {}
                    self.small_piece_images[i] = small_tk_img
                    
                    self.available_canvas.create_image(x, y, image=small_tk_img)
                
                piece_count += 1

    def update_board(self):
        """Met à jour le plateau avec les pièces posées"""
        board = self.game.get_board_status()
        self.canvas.delete("piece")  # On enlève seulement les pièces, pas les axes et coordonnées
        for i in range(self.game.BOARD_SIDE):
            for j in range(self.game.BOARD_SIDE):
                piece_index = board[i, j]
                if piece_index >= 0:  # une pièce est posée
                    x = j * self.cell_size + self.cell_size // 2
                    y = i * self.cell_size + self.cell_size // 2
                    if piece_index in self.piece_images:
                        self.canvas.create_image(x, y, image=self.piece_images[piece_index], tags="piece")
        
        # Mettre à jour aussi les pièces disponibles
        self.draw_available_pieces()

        self.root.update_idletasks()
        self.root.update()

    def on_update(self, event_type, data):
        """Réagit aux notifications de Quarto"""
        if event_type == "select":
            # Un joueur a choisi une pièce pour l'autre
            player = (data["player"] + 1)%2
            piece = data["piece"]
            self.player_label.config(text=f"Joueur {player} doit placer :")
            self.piece_canvas.delete("all")
            self.piece_canvas.create_image(
                self.cell_size//2, self.cell_size//2,
                image=self.piece_images[int(piece)]
            )
        elif event_type == "next_player":
            player = data["player"]
            piece = data["piece"]
            self.player_label.config(text=f"Joueur {player} a placé :")
            self.piece_canvas.delete("all")
            self.piece_canvas.create_image(
                self.cell_size//2, self.cell_size//2,
                image=self.piece_images[int(piece)]
            )
        elif event_type == "place":
            self.update_board()
        elif event_type == "end":
            winner = data["winner"]
            if winner >= 0:
                self.player_label.config(text=f" Joueur {winner} a gagné ! ")
            else:
                self.player_label.config(text="Match nul !")
        self.root.update_idletasks()
        self.root.update()

    def start(self):
        """Boucle principale Tkinter"""
        self.root.mainloop()