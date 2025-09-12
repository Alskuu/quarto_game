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

        self.canvas = tk.Canvas(
            self.root,
            width=self.game.BOARD_SIDE * self.cell_size,
            height=self.game.BOARD_SIDE * self.cell_size,
            bg="white"
        )
        self.canvas.pack()

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

    def draw_grid(self):
        """Dessine la grille vide"""
        for i in range(self.game.BOARD_SIDE):
            for j in range(self.game.BOARD_SIDE):
                x0 = j * self.cell_size
                y0 = i * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="black", width=2)

    def update_board(self):
        """Met à jour le plateau avec les pièces posées"""
        board = self.game.get_board_status()
        self.canvas.delete("piece")  # On enlève les pièces avant de redessiner
        for i in range(self.game.BOARD_SIDE):
            for j in range(self.game.BOARD_SIDE):
                piece_index = board[i, j]
                if piece_index >= 0:  # une pièce est posée
                    x = j * self.cell_size + self.cell_size // 2
                    y = i * self.cell_size + self.cell_size // 2
                    if piece_index in self.piece_images:
                        self.canvas.create_image(x, y, image=self.piece_images[piece_index], tags="piece")

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