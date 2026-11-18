# Projet 2 - INF1007

On veut prédire G3, la note finale d'un élève sur 20. On utilise une régression linéaire avec les notes des deux premières périodes et trois autres informations. Pour l'instant, ça fonctionne en ligne de commande. L'interface reste à faire.

## Données

On a pris [Student Performance sur Kaggle](https://www.kaggle.com/datasets/larsen0966/student-performance-data-set). On utilise le fichier donnees/student-por.csv : 649 lignes et 33 colonnes.

On n'a trouvé aucune valeur manquante ni aucun doublon. On garde les 15 notes G3 à zéro, car on n'a pas établi que ce sont des erreurs.

Le fichier contient les mêmes valeurs que l'[original d'UCI](https://archive.ics.uci.edu/dataset/320/student+performance), sous licence CC BY 4.0.
Source originale : Cortez, P. (2008). *Student Performance*. UCI Machine Learning Repository. https://doi.org/10.24432/C5TG7T.

## Variables choisies

| Entrée | Ce qu'elle représente | Valeurs |
| --- | --- | --- |
| G1 | Note de la première période | 0 à 20 |
| G2 | Note de la deuxième période | 0 à 20 |
| failures | Échecs scolaires antérieurs | Entier de 0 à 3 dans ce CSV |
| studytime | Temps d'étude par semaine, par tranche | Code de 1 à 4 |
| schoolsup | Soutien scolaire supplémentaire | yes ou no, converti en 1 ou 0 |

Pour studytime, les codes sont : 1 = moins de 2 h, 2 = 2 à 5 h, 3 = 5 à 10 h et 4 = plus de 10 h. On utilise ces codes comme des nombres dans le modèle.

On prédit après la deuxième période, puisque G1 et G2 doivent déjà être connues.

## Pour lancer le projet

Depuis la racine du projet, avec Python 3.12 :

~~~powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
~~~

Pour explorer le CSV et créer [le graphique des notes](exploration_cible.png) :

~~~powershell
.\.venv\Scripts\python.exe main.py --explorer
~~~

Pour entraîner et sauvegarder le modèle :

~~~powershell
.\.venv\Scripts\python.exe main.py
~~~

Pour prédire une note avec la sauvegarde :

~~~powershell
.\.venv\Scripts\python.exe main.py --predire 12 13 0 2 yes
~~~

Les cinq valeurs sont dans l'ordre du tableau. Cet exemple donne environ 13,24/20. Le modèle est rechargé sans refaire l'entraînement.

Sans argument, main.py lance l'entraînement. Le bouton Run sur src/main.py fonctionne aussi, même si le terminal est ouvert dans le dossier parent.

## Résultats

On a séparé les données en deux groupes : 519 élèves pour entraîner le modèle et 130 pour le tester. On utilise random_state=42 pour retrouver les mêmes groupes à chaque exécution.

La moyenne des notes du groupe d'entraînement est de 11,79/20. La référence prédit cette note pour tous les élèves du groupe de test.

| Méthode | RMSE sur les 130 élèves de test |
| --- | --- |
| Toujours prédire 11,79/20 | 3,173 |
| Utiliser la régression | 1,152 |

Plus le RMSE est bas, plus les prédictions sont proches des vraies notes. Sur ce groupe de test, le modèle fait mieux que la référence.

Le [graphique du test](modeles/evaluation_modele.png) montre aussi des erreurs : une note réelle de zéro est prédite autour de 9. Le modèle peut donc se tromper de plusieurs points. Le score vient d'une seule séparation des données, et la formule ne garantit pas une note entre 0 et 20.

## Organisation du code

- donnees.py : lecture et exploration du CSV, graphique des notes, vérification des valeurs, conversion de schoolsup et séparation des données.
- modele.py : entraînement, prédiction, calcul du RMSE et sauvegarde.
- exceptions.py : notre erreur personnalisée.
- main.py : les commandes pour lancer le tout.

Ces quatre fichiers sont dans src. Le main.py à la racine appelle src/main.py. Les classes VariableNumerique et VariableCategorielle héritent de Variable et vérifient les saisies chacune à leur façon. JeuDeDonnees et ModeleRegression contiennent une liste de ces variables.

Le modèle est dans modeles/regression_lineaire.joblib. Le fichier modeles/metadonnees.json contient les colonnes, les valeurs acceptées, les scores et les versions utilisées. Les versions des bibliothèques sont fixées dans requirements.txt.

Pour le chapitre 7, on utilise un décorateur nommé chronometrer. Il mesure le temps d'entraînement et le garde dans le JSON.

## Tests

~~~powershell
.\.venv\Scripts\python.exe -m coverage run --source=src -m pytest -v
.\.venv\Scripts\python.exe -m coverage report -m
~~~

Dernier résultat local : 40 cas de test réussis, avec 94 % de couverture sur src.

On teste les saisies, la séparation des groupes, le calcul du RMSE, la moyenne de référence et la sauvegarde. Le RMSE est vérifié avec un calcul connu et avec scikit-learn. GitHub Actions lance aussi pytest à chaque push et pull request.

## Documentation utilisée

- [pandas : lire un CSV](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
- [scikit-learn : LinearRegression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html)
- [scikit-learn : train_test_split](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html)
- [scikit-learn : sauvegarder un modèle](https://scikit-learn.org/stable/model_persistence.html)
- [Matplotlib : graphique de points](https://matplotlib.org/stable/api/_as_gen/matplotlib.axes.Axes.scatter.html)
- [coverage : mesurer la couverture](https://coverage.readthedocs.io/en/latest/commands/cmd_run.html)

Il reste à choisir la technologie et la maquette pour D, puis à faire l'interface, son graphique et l'historique des prédictions. On ajoutera la documentation de l'interface quand elle sera choisie.
