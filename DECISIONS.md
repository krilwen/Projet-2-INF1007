# Nos choix

## Validation A - Domaine

| Choix | Options envisagées | Choix retenu et justification | Validé par chargé|
| --- | --- | --- | --- |
| Domaine | Immobilier ou éducation | On a choisi l'éducation. La question est simple : estimer la note finale d'un élève à partir de ses informations. Dans l'application, l'utilisateur pourra remplir les champs et obtenir une estimation sur 20. | Oui |

## Validation B - Jeu de données

| Choix | Options envisagées | Choix retenu et justification | Validé par chargé |
| --- | --- | --- | --- |
| Jeu de données | Boston House Prices ou Student Performance | On a pris Student Performance, avec le fichier student-por.csv. Il correspond au domaine choisi, contient assez de lignes et propose des variables numériques et catégorielles pour l'interface. |   Oui |

On a vérifié les critères suivants :

| Critère de l'énoncé | Ce qu'on a vérifié |
| --- | --- |
| Format CSV | Le fichier se charge avec pandas. Une ligne correspond à un élève. |
| Entre 500 et 50 000 lignes | Le fichier contient 649 lignes. |
| Au moins 5 colonnes d'entrée | Il y a 32 colonnes possibles si on retire G3. On choisira celles à utiliser pour le modèle. |
| Une cible claire | G3 est la note finale sur 20. |
| Variables numériques et catégorielles | Parmi les 32 colonnes possibles, pandas charge 15 colonnes numériques et 17 catégorielles. Par exemple : age est numérique et school est catégorielle. |
| Source et licence | Le fichier vient de Kaggle. Ses valeurs et ses colonnes sont identiques au fichier original d'UCI, publié sous licence CC BY 4.0. On doit citer la source. |
| Aucune information permettant d'identifier directement une personne | Les colonnes ne contiennent ni nom, ni courriel, ni adresse postale. La colonne address indique seulement un milieu urbain ou rural. |
| Jeux exclus | Ce n'est ni Iris, ni Titanic, ni MNIST. |

Sources : [version Kaggle](https://www.kaggle.com/datasets/larsen0966/student-performance-data-set) et [source originale UCI, avec la licence](https://archive.ics.uci.edu/dataset/320/student+performance).

Référence : Cortez, P. (2008). *Student Performance*. UCI Machine Learning Repository. https://doi.org/10.24432/C5TG7T.

## Validation C - Cible, métrique et modèle

Voici les choix qu'on propose pour C. Ils restent à présenter à l'auxiliaire avant l'entraînement.

| Choix | Options envisagées | Choix retenu et justification | Validé par l'auxiliaire (date) |
| --- | --- | --- | --- |
| Cible et type de problème | Prédire la note G3 ou une catégorie réussite/échec | On part sur G3 et une régression. On veut donner une estimation de la note sur 20. | À valider |
| Métrique | RMSE ou R² | On retient le RMSE, car il exprime l'erreur en points sur 20. Plus il est bas, plus les prédictions sont proches des notes réelles. | À valider |
| Référence de comparaison | Toujours prédire une même note | On utilisera la moyenne des notes de l'ensemble d'entraînement. On comparera son RMSE à celui du modèle sur le même ensemble de test. | À valider |
| Modèle proposé | Régression linéaire ou arbre de régression | On propose une régression linéaire avec scikit-learn. C'est un modèle simple pour commencer et expliquer comment les entrées contribuent à la note estimée. On évaluera ses limites sur les données de test. | À valider |

Documentation du modèle proposé : [LinearRegression - scikit-learn](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html).

On n'a pas encore entraîné de modèle ni calculé de score. Le choix des variables d'entrée et la technologie d'interface restent à préciser.
