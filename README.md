# Projet-2-INF1007

https://www.kaggle.com/datasets/arunjathari/bostonhousepricedata
on prend lui :

https://www.kaggle.com/datasets/larsen0966/student-performance-data-set

1. Explorer et nettoyer :
Les données ont été chargées avec pandas : 649 élèves, 33 colonnes (16 numériques, 17 catégorielles). Nous avons vérifié les types, les valeurs manquantes, les doublons et les valeurs aberrantes. Voici ce que nous avons trouvée : aucune valeur manquante, aucun doublon, et toutes les valeurs sont dans des intervalles plausibles (âge de 15 à 22 ans, notes de 0 à 19). Aucune correction n’a donc été nécessaire.

L’histogramme de la note finale G3 (exploration_cible.png) montre une distribution en cloche centrée vers 11-12, un pic à 10 (la note de passage) et un petit groupe d’une quinzaine d’élèves à 0, probablement des élèves qui n’ont pas passé l’examen final. Nous avons décidé de les garder, car ils représentent des échecs réels et que l’application doit pouvoir détecter les élèves à risque. Les retirer ferait paraître les échecs moins nombreux et pourrait fausser la prédiction.

2. Définir le problème :
Notre variable cible est “G3” qui est la note final des élèves dans nos données. C’est un problème de type de régression car notre donnée cible est un nombre (x/20). Notre métrique d’évaluation est le RMSE (racine de l’erreur quadratique moyenne), qui exprime l’erreur moyenne de nos prédictions en points sur 20. Nous la comparons à une référence simple : prédire toujours la moyenne des notes d’entraînement. Nous complétons avec le pourcentage de décisions réussite/échec correctes, en appliquant la note de passage au Portugal (10/20, soit 50 %) aux notes prédites. Nous justifions ce choix car le but de notre application est de prédire la réussite d’un élève, c’est-à-dire de savoir s’il obtiendra une note G3 supérieure ou égale à 10 : le RMSE mesure la qualité de la note prédite, et le seuil de 10 la transforme en décision.

