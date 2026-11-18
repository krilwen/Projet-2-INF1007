# Journal IA

On a utilisé l'IA pour des explications, de la rédaction et du code. (L'IA a été utilisé pour faire se tableau et les tableau dans README.md et DECISIONS.md)

| Outil | Demande | Réponse reçue | Vérification | Décision |
| --- | --- | --- | --- | --- |
|ChatGPT | Aider à créer la structure du projet. | Une structure avec src, tests, donnees et modeles. | Les dossiers sont présents et correspondent à l'exemple de l'énoncé. | Gardé. |
| ChatGPT / Codex | Regarder l'énoncé et dire ce qu'il reste à faire. | Une liste des parties manquantes. | Lecture de l'énoncé et des fichiers. À ce moment-là, les fichiers de src étaient vides. | Gardé comme liste de travail. |
| ChatGPT / Codex | Faire fonctionner le premier test CI et expliquer l'échec. | Un test du CSV. L'échec venait du fait que les fichiers de tests étaient vides. | Test réussi en local, puis CI verte sur GitHub après le push.| Gardé. |
| ChatGPT / Codex | Corriger la partie données et régression avec nos cinq entrées. | Du code corrigé et amélioré pour les parties : charger, vérifier, entraîner, prédire et sauvegarder. | Entraînement local sur 519 élèves, test sur 130. RMSE de 1,152. Une prédiction fonctionne aussi après rechargement. | Gardé comme base à relire et à comprendre. |
| ChatGPT / Codex | Expliquer et calculer la référence. | Prédire la moyenne des notes d'entraînement. | Le JSON donne 11,79/20. Un test vérifie que les notes de test ne changent pas cette moyenne. | Corrigé dans la fiche : la référence vient du groupe d'entraînement, pas du CSV complet, dont la moyenne était de 11,91/20. |
| ChatGPT / Codex | Écrire les tests du modèle et des données. | Des tests sur les saisies, les calculs et les sauvegardes. | 37 cas réussis. Le RMSE est comparé à un calcul connu et à scikit-learn. Un autre test vérifie une formule dont on connaît le résultat. | Gardé. |
| ChatGPT / Codex | Corriger le lancement avec main.py et le bouton Run de VS Code. | Un main.py à la racine et une correction des imports pour le lancement direct de src/main.py. Sans argument, on entraîne le modèle. | Les deux fichiers sont testés depuis un autre dossier. Le lancement depuis le dossier parent fonctionne : 39 cas réussis au total. | Gardé. |
