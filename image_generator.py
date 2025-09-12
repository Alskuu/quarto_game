from PIL import Image, ImageDraw
import os

""" Penser dans un deuxième temps à décrire si c'est des couleurs, hauteurs... (ce que c'est réellement finalement)"""
def dessiner_piece(h:int, c:int, f:int, p:int, taille:int=60) -> Image: 
    couleur_fond = (200, 200, 200)
    couleur_piece = (0, 0, 0) if c == 1 else (255, 255, 255) 
    # Si c vaut 1, c'est une pièce blanche et si c vaut 0 c'est une pièce noire 

    if h == 0:
        taille_forme = taille // 2
    else:
        taille_forme = int(taille * 0.8)

    img = Image.new("RGBA", (taille, taille), couleur_fond)
    draw = ImageDraw.Draw(img)

    x0 = (taille - taille_forme) // 2
    y0 = (taille - taille_forme) // 2
    x1 = x0 + taille_forme
    y1 = y0 + taille_forme

    if f == 0:
        if p == 1:
            draw.rectangle([x0, y0, x1, y1], fill=couleur_piece)
        else:
            draw.rectangle([x0, y0, x1, y1], outline=couleur_piece, width=3)
    else:
        if p == 1:
            draw.ellipse([x0, y0, x1, y1], fill=couleur_piece)
        else:
            draw.ellipse([x0, y0, x1, y1], outline=couleur_piece, width=3)

    return img

def generer_et_sauvegarder_images(dossier: str="images"):
    if not os.path.exists(dossier):
        os.makedirs(dossier)

    for h in [0, 1]:
        for c in [0, 1]:
            for f in [0, 1]:
                for p in [0, 1]:
                    img = dessiner_piece(h, c, f, p)
                    nom_fichier = f"{dossier}/piece_{h}{c}{f}{p}.png"
                    img.save(nom_fichier)
                    print(f"Sauvegardé : {nom_fichier}")
