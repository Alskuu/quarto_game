import json
import matplotlib.pyplot as plt
import os

def tracer_camembert(json_path, dossier_sortie="resultats_graphes"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # On ne garde que les clés principales (pas les "meta")
    for match, infos in data.items():
        if "(meta)" in match:
            continue

        joueur1, joueur2 = match.split(" vs ")
        games = infos["games"]
        victoires_j2 = infos["wins"]
        nuls = infos["draws"]
        defaites_j2 = games - victoires_j2 - nuls

        # Préparer les données
        labels = [f"Victoires {joueur2}", f"Victoires {joueur1}", "Nuls"]
        sizes = [victoires_j2, defaites_j2, nuls]
        colors = ["blue", "red", "green"]

        # Tracer le camembert
        plt.figure(figsize=(6, 6))
        def make_autopct(values):
            def my_autopct(pct):
                total = sum(values)
                val = int(round(pct * total / 100.0))
                return f"{pct:.1f}% ({val})"
            return my_autopct

        plt.pie(sizes, labels=labels, colors=colors,
                autopct=make_autopct(sizes), startangle=90,
                wedgeprops={'edgecolor': 'black'})
        plt.title(f"Résultats : {joueur1} vs {joueur2}\n(Nb parties : {games})")

        # Sauvegarder
        os.makedirs(dossier_sortie, exist_ok=True)
        fichier_sortie = os.path.join(dossier_sortie, f"{joueur1}_vs_{joueur2}.png")
        plt.savefig(fichier_sortie, dpi=300)
        plt.close()

        print(f"Graphique sauvegardé dans {fichier_sortie}")


tracer_camembert("resultats.json")
