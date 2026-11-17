# Projet 2 - INF1007

On veut estimer la note finale d'un élève à partir des informations du jeu de données Student Performance. Le modèle et l'interface restent à faire.

## Données

On a choisi [Student Performance sur Kaggle](https://www.kaggle.com/datasets/larsen0966/student-performance-data-set).
Le fichier utilisé est `donnees/student-por.csv`. Ses valeurs et ses colonnes sont identiques à celles du fichier original publié par [UCI sous licence CC BY 4.0](https://archive.ics.uci.edu/dataset/320/student+performance).

Source originale : Cortez, P. (2008). *Student Performance*. UCI Machine Learning Repository. https://doi.org/10.24432/C5TG7T.

Le CSV contient 649 lignes et 33 colonnes. On n'a trouvé aucune valeur manquante ni aucun doublon. La colonne `G3` contient 15 notes égales à zéro. On les garde pour l'instant : on n'a pas établi que ce sont des erreurs.

## Ce qu'on veut prédire

La cible est `G3`, la note finale sur 20. On part sur une régression, puisqu'on veut prédire une note.

On prévoit d'utiliser le RMSE pour mesurer l'erreur en points sur 20. On comparera le modèle à une prédiction simple : donner à chaque élève la moyenne des notes de l'ensemble d'entraînement. Cette comparaison n'a pas encore été faite.

## Installation et tests

Depuis la racine du projet, avec Python 3.12 :

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -v
```

Pour le moment, on a un test qui vérifie le CSV : sa présence, le nombre de lignes et de colonnes d'entrée, la cible et les types de variables. GitHub Actions lance les tests à chaque push et pull request.

## Exploration

```powershell
.\.venv\Scripts\python.exe EXPLORATION.py
```

Le script affiche les informations du CSV et un histogramme de `G3`. Il enregistre aussi le graphique dans `exploration_cible.png`.

## Où on en est

- `EXPLORATION.py` : exploration des données.
- `tests/test_donnees.py` : premier test pour la CI.
- `src/` : fichiers prévus pour le code, encore vides.
- `modeles/` : aucun modèle sauvegardé pour le moment.

Il reste à choisir les variables d'entrée et le modèle, faire l'entraînement et l'évaluation, puis créer l'interface. Il faudra aussi compléter les tests, mesurer la couverture et ajouter les références de documentation consultées.
