# Utilisation de l'IA


(log crée par codex  )

On a utilisé l'IA pour nous aider sur les points ci-dessous. Les vérifications sont indiquées pour chaque demande.

| Outil | Ce qu'on a demandé | Réponse reçue | Vérification faite | Décision |
| --- | --- | --- | --- | --- |
| IA (outil non précisé dans notre première note) | Aider à créer la structure du projet. | Une organisation avec src, tests, donnees et modeles. | Les dossiers sont présents et correspondent à la structure suggérée dans l'énoncé. | Gardé. |
| ChatGPT / Codex | Comparer notre projet à l'énoncé pour voir ce qu'il reste à faire. | L'exploration est commencée, mais le modèle, l'interface et les tests restent à développer. | Lecture de l'énoncé et des fichiers. À ce moment-là, les fichiers de src et les tests étaient vides. | Gardé comme liste de travail. |
| ChatGPT / Codex | Ajouter un premier test pour la CI. | Un test qui charge le CSV et vérifie les critères de base du jeu de données. | Exécution avec pytest : 1 test réussi en local. La capture GitHub après le push montre aussi une exécution réussie. | Gardé. |
| ChatGPT / Codex | Expliquer pourquoi la CI échouait avant. | pytest ne trouvait aucun test dans les fichiers vides. | Vérification de la dernière exécution en échec sur GitHub : l'étape des tests avait terminé avec le code 5. | Gardé. | 
| ChatGPT / Codex | Réécrire la structure du README, les décisions et ce journal plus simplement(faire des tableau pour lecture plus facile). | Des textes qui distinguent ce qui est fait de ce qui reste à faire. | Comparaison avec les fichiers présents et les échanges de cette conversation. | Gardé comme version de travail. |
