Hello everyone and welcome to the Quarto game !

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