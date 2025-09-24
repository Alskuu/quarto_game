Hello everyone and welcome to the Quarto game !

Pour lancer le jeu qui s'enregistre sur un json automatiquement écrire dans le terminal ceci :  
"python main.py--ci" ("poetry run python main.py --ci" avec poetry)
Modifier la partie "if args.ci:" de la fonction main() dans main.py pour modifier les joueurs 

Pour jouer au jeu avec une interface graphique, modifier main_gui pour modifier les joueurs et exécuter dans le terminal : 
python main.py --gui

Les pièces sont définies en binaire(-1) (False = 0 et True = 1) :
(False, False, False, False ) # 0
(False, False, False, True)  # 1
(False, False, True, False)  # 2
(False, False, True, True)  # 3
(False, True, False, False)  # 4
(False, True, False, True)  # 5
(False, True, True, False)  # 6
(False, True, True, True)  # 7
(True, False, False, False)  # 8
(True, False, False, True)  # 9
(True, False, True, False)  # 10
(True, False, True, True)  # 11
(True, True, False, False)  # 12
(True, True, False, True)  # 13
(True, True, True, False)  # 14
(True, True, True, True)  # 15

Les joueurs sont les suivants :

    - HumanPlayer : joueur humain, pouvant jouer en écrivant poetry run python main.py --gui sur le terminal 
    - RandomPlayer : joueur qui prend toutes ses décision aléatoirement 
    - MinMax1 : negamax$_$complete il utilise l'algorithme Negamax (variante de MiniMax ainsi que la fonction d'évaluation composée de toutes nos heuristiques). 
    - MinMax2 : negamax$_$placement$_$specialized : pareil que MinMax1 mais l'applique que lors de la phase de placement 
    - MinMax3 : negamax$_$selection$_$specialized : de même mais que sur la phase de sélection 
    - MinMax4 : (minmax1 dans mon code car c'est le premier joueur que j'avais créé) algorithme classique MiniMax avec une fonction d'évaluation qui ne détecte que les fins de partie et identifie si c'est une victoire, une défaite ou un match nul. 
    - MinMax5 : (minmax2 dans mon code) de même que MinMax4 mais applique l'algorithme que lors de la phase de placement

Pour l'implémentation des algorithmes minimax et le alpha beta pruning :
Voici les sources qui m'ont été utiles :
https://papers-100-lines.medium.com/the-minimax-algorithm-and-alpha-beta-pruning-tutorial-in-30-lines-of-python-code-e4a3d97fa144
https://en.wikipedia.org/wiki/Minimax#:~:text=A%20minimax%20algorithm%20is%20a,or%20state%20of%20the%20game.
https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning

Pour MiniMax nous nous sommes aussi inspiré d'un github auquel nous avons apporté pleins de modifications poru faire en sorte que :
- le placement de la pièce choisie par l'adversaire soit aussi un choix stratégique (et pas seulement le choix de la pièce)
- Je garde quand même la même profondeur d'arbre car sinon cela prendrait trop de temps

Pour négamax, voici comment nous avons pu l'utiliser pour simplifier le calcul des heuristiques etdiviser par deux la place prise par le code. 
Tout cela grâce à la propriété de jeu à somme nulle : https://en.wikipedia.org/wiki/Negamax

Concernant le choix des heuristiques je me suis fortement inspiré du site suivant pour pouvoir trouver les différentes idées de fonctions nécessaires (contrôle des lignes/menaces) : https://cdn.aaai.org/AAAI/2007/AAAI07-180.pdf

Si vous êtes intéressés pour avoir les résultats de tous les matchs pour s'éviter les plusieurs heures nécessaires pour faire fonctionner le programme.
Contactez moi via mon mail a.riahii@outlook.fr
