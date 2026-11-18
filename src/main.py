"""Point de depart pour explorer les donnees, entrainer ou predire."""

import argparse
import os
import sys

# Permet aussi de lancer ce fichier directement avec le bouton Run de VS Code.
if __package__ is None or __package__ == "":
    dossier_projet = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, dossier_projet)

from src.donnees import CHEMIN_DONNEES, COLONNES_ENTREE, GRAINE, PART_TEST, RACINE, JeuDeDonnees
from src.exceptions import DonneeInvalideError
from src.modele import ModeleRegression, graphique_evaluation


def entrainer_projet(chemin_csv: str, dossier_sortie: str) -> dict[str, float]:
    """Retourne les scores et sauvegarde le modele; signale les erreurs de donnees."""
    jeu = JeuDeDonnees(chemin_csv)
    jeu.charger()
    x_train, x_test, y_train, y_test = jeu.separer()
    modele = ModeleRegression()
    modele.entrainer(x_train, y_train)
    resultats = modele.evaluer(x_test, y_test)
    modele.sauvegarder(
        dossier_sortie, {"part_test": PART_TEST, "graine": GRAINE},
    )
    graphique_evaluation(
        y_test, modele.predire(x_test),
        os.path.join(dossier_sortie, "evaluation_modele.png"),
    )
    resultats["moyenne_reference"] = modele.moyenne_reference
    resultats["nombre_entrainement"] = len(y_train)
    resultats["nombre_test"] = len(y_test)
    return resultats


def main(arguments: list[str] | None = None) -> int:
    """Lance la commande; retourne 0 si tout fonctionne, sinon 1."""
    analyseur = argparse.ArgumentParser(description="Prediction de la note finale G3.")
    actions = analyseur.add_mutually_exclusive_group()
    actions.add_argument("--explorer", action="store_true", help="Afficher le bilan du CSV et creer son graphique.")
    actions.add_argument("--entrainer", action="store_true", help="Entrainer, evaluer et sauvegarder.")
    actions.add_argument(
        "--predire", nargs=5, metavar=("G1", "G2", "FAILURES", "STUDYTIME", "SCHOOLSUP"),
        help="Predire avec la sauvegarde; schoolsup vaut yes ou no.",
    )
    analyseur.add_argument("--donnees", default=CHEMIN_DONNEES, help="Chemin du CSV.")
    analyseur.add_argument(
        "--sortie", default=os.path.join(RACINE, "modeles"), help="Dossier du modele sauvegarde.",
    )
    options = analyseur.parse_args(arguments)
    try:
        if options.explorer:
            jeu = JeuDeDonnees(options.donnees)
            jeu.charger()
            jeu.explorer(os.path.join(RACINE, "exploration_cible.png"))
        # Sans option, on lance l'entrainement.
        elif options.predire is None:
            resultats = entrainer_projet(options.donnees, options.sortie)
            print(
                f"Entrainement : {resultats['nombre_entrainement']} eleves ; "
                f"test : {resultats['nombre_test']} eleves."
            )
            print(f"Note de reference : {resultats['moyenne_reference']:.2f}/20")
            print(f"RMSE de reference : {resultats['rmse_reference']:.3f}")
            print(f"RMSE du modele : {resultats['rmse_modele']:.3f}")
            print(f"Fichiers enregistres dans : {os.path.abspath(options.sortie)}")
        else:
            modele = ModeleRegression.charger(options.sortie)
            saisies = dict(zip(COLONNES_ENTREE, options.predire))
            note = modele.predire_un(saisies)
            print(f"Note finale estimee : {note:.2f}/20")
    except (DonneeInvalideError, OSError, ValueError) as erreur:
        print(f"Erreur : {erreur}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
