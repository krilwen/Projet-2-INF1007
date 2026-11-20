# Nos décisions

Les validations A, B, C et D ont été faites.

| Choix | Options envisagées | Ce qu'on a retenu et pourquoi | Validation par la chargée |
| --- | --- | --- | --- |
| A - Domaine | Immobilier ou éducation | On a pris l'éducation. L'utilisateur pourra entrer les informations d'un élève et avoir une estimation de sa note finale. | Oui, 16 nov |
| B - Données | Boston House Prices ou Student Performance | On a pris Student Performance, avec student-por.csv. Ça correspond à notre sujet et il y a des notes à prédire, assez de lignes et les deux types de variables demandés. | Oui, 16 nov |
| C - Cible | Note finale ou réussite/échec | On prédit G3, la note finale sur 20. C'est donc une régression. | Oui, 17 nov |
| C - Entrées | Les colonnes du CSV | On utilise G1, G2, failures, studytime et schoolsup. Ça fait cinq entrées, dont une catégorielle. G1 et G2 doivent être connues, donc on prédit après la deuxième période. | Oui, 17 nov |
| C - Modèle | **Régression linéaire** ou arbre de régression | On part sur une régression linéaire. On veut tester si une formule qui additionne les contributions des cinq entrées permet d'estimer G3. | Oui, 17 nov |
| C - Mesure des erreurs | **RMSE** ou R² | On prend le RMSE pour mesurer les erreurs en points sur 20. Plus il est bas, mieux c'est. | Oui, 17 nov |
| C - Référence | Toujours prédire une même note | On utilise la moyenne des notes d'entraînement : 11,79/20. On regarde si la régression fait moins d'erreurs que de prédire cette note à chaque fois. | Oui, 17 nov |
| C - Séparation | Plusieurs répartitions possibles | On utilise 80 % des données pour entraîner et 20 % pour tester. random_state=42 garde les mêmes groupes à chaque exécution. | Oui, 17 nov |
| D - Interface et maquette | Interface locale | On a choisi Tkinter et présenté la maquette de la fenêtre principale. Tkinter permet d'afficher le formulaire, le graphique Matplotlib et l'historique dans l'application. | Oui, 18 nov |


## Vérifications pour B

| Critère | Vérification |
| --- | --- |
| CSV | Le fichier se lit avec pandas. Une ligne correspond à un élève. |
| 500 à 50 000 lignes | On a 649 lignes. |
| Au moins 5 entrées | Il y a 32 colonnes en dehors de G3 ; on en a choisi cinq. |
| Une cible claire | G3 est la note finale sur 20. |
| Une entrée numérique et une catégorielle | G1 et G2 sont numériques. schoolsup contient yes/no. |
| Source et licence | Le fichier vient de Kaggle. Ses valeurs sont identiques à celles d'UCI, qui indique CC BY 4.0. La source est citée dans le README. |
| Aucun identifiant personnel direct | Pas de nom, courriel ou adresse postale. address indique seulement urbain ou rural. |
| Jeux exclus | Ce n'est ni Iris, ni Titanic, ni MNIST. |

Sources : [Kaggle](https://www.kaggle.com/datasets/larsen0966/student-performance-data-set) et [UCI, avec la licence](https://archive.ics.uci.edu/dataset/320/student+performance).

## Résultat actuel

On a 519 élèves dans le groupe d'entraînement et 130 dans le groupe de test. Le RMSE est de 1,152 pour le modèle et de 3,173 pour la référence.

schoolsup est converti de yes/no en 1/0. studytime reste un code entier de 1 à 4, pas un nombre d'heures libre.
