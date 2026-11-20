# Projet 2 – INF1007

Notre application estime la note finale d’un élève sur 20 après les deux premières périodes. On entre les deux notes, les échecs précédents, la tranche de temps d’étude et le soutien scolaire. La fenêtre affiche la note estimée sur un graphique et garde les prédictions dans un historique.

On utilise les 649 lignes de [student-por.csv](donnees/student-por.csv), un fichier du jeu *Student Performance* de Paulo Cortez (2008), sous licence CC BY 4.0. [Source UCI](https://doi.org/10.24432/C5TG7T) · [Copie Kaggle](https://www.kaggle.com/datasets/larsen0966/student-performance-data-set)

## Installer et lancer

Avec Python 3.12, ouvre PowerShell à la racine du projet et exécute ces commandes.

~~~powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.main
~~~

La dernière commande ouvre la fenêtre Tkinter avec le modèle sauvegardé. Ajoute `--entrainer` à cette commande pour entraîner le modèle à nouveau.

## Résultats

Sur les 130 élèves du groupe de test, la régression a un **RMSE de 1,152** et un **R² de 0,864**. La référence, qui prédit toujours la moyenne des notes d’entraînement (11,79/20), donne un RMSE de **3,173**. [Graphique d’évaluation](modeles/evaluation_modele.png)

## Code et tests

- `donnees/` contient le CSV et `modeles/` le modèle sauvegardé et ses métadonnées.
- Dans `src/`, `main.py` lance le programme. `donnees.py` prépare les entrées et `modele.py` fait les prédictions. `interface.py` affiche la fenêtre et `historique.py` gère les prédictions enregistrées.
- `tests/` contient les tests de la logique du projet.

Pour le chapitre 7, le décorateur `chronometrer` mesure le temps d’entraînement du modèle.

**39 tests passent**, avec **61 % de couverture** sur `src`. [GitHub Actions](https://github.com/krilwen/Projet-2-INF1007/actions/workflows/tests.yml) lance les tests à chaque push ou pull request. Pour mesurer la couverture chez toi, lance ces commandes.

~~~powershell
.\.venv\Scripts\python.exe -m coverage run --source=src -m pytest
.\.venv\Scripts\python.exe -m coverage report
~~~

Documentation consultée · [pandas](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html) · [scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html) · [Tkinter](https://docs.python.org/fr/3/library/tkinter.html)
