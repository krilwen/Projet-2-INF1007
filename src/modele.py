"""Entrainement, predictions et sauvegarde de la regression lineaire."""

from functools import wraps
import json
import os
from time import perf_counter
from typing import Callable
from sklearn.metrics import r2_score
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression

from src.donnees import CIBLE, COLONNES_ENTREE, creer_variables, preparer_entrees
from src.exceptions import DonneeInvalideError


def calculer_rmse(reelles: object, predites: object) -> float:
    """Retourne le RMSE; exige deux listes de nombres de meme taille."""
    try:
        valeurs = np.asarray(reelles, dtype=float)
        estimations = np.asarray(predites, dtype=float)
    except (TypeError, ValueError) as erreur:
        raise DonneeInvalideError("Le RMSE exige des valeurs numeriques.") from erreur
    if valeurs.ndim != 1 or estimations.ndim != 1:
        raise DonneeInvalideError("Le RMSE attend des listes a une seule dimension.")
    if valeurs.size == 0 or valeurs.shape != estimations.shape:
        raise DonneeInvalideError("Le RMSE exige deux listes de meme taille, non vides.")
    if not np.isfinite(valeurs).all() or not np.isfinite(estimations).all():
        raise DonneeInvalideError("Le RMSE ne peut pas utiliser de valeurs manquantes ou infinies.")
    # On met les ecarts au carre avant de calculer leur moyenne.
    ecarts = valeurs - estimations
    moyenne_carres = np.mean(ecarts ** 2)
    return float(np.sqrt(moyenne_carres))


def chronometrer(fonction: Callable[..., None]) -> Callable[..., None]:
    """Ajoute une mesure du temps a la methode d'entrainement."""
    @wraps(fonction)
    def mesurer(
        self: "ModeleRegression", entrees: pd.DataFrame, cible: pd.Series,
    ) -> None:
        """Entraine et garde le temps ecoule si l'entrainement reussit."""
        debut = perf_counter()
        fonction(self, entrees, cible)
        self._duree_entrainement = perf_counter() - debut
    return mesurer


class ModeleRegression:
    """Garde la regression, la moyenne de reference et les resultats."""

    def __init__(self) -> None:
        """Prepare le modele vide et les cinq variables."""
        self._regression: LinearRegression | None = None
        self._variables = creer_variables()
        self._moyenne_reference: float | None = None
        self._resultats: dict[str, float] = {}
        self._duree_entrainement = 0.0
        self._nombre_entrainement = 0
        self._nombre_test = 0

    @property
    def moyenne_reference(self) -> float:
        """Retourne la moyenne de reference; exige un modele entraine."""
        if self._moyenne_reference is None:
            raise DonneeInvalideError("Le modele n'est pas encore entraine.")
        return self._moyenne_reference
        
    @property
    def rmse(self) -> float:
        """Retourne le RMSE du modele sur le groupe de test."""
        if "rmse_modele" not in self._resultats:
            raise DonneeInvalideError("Le RMSE du modele n'est pas disponible.")
        return self._resultats["rmse_modele"]

    @chronometrer
    def entrainer(self, entrees: pd.DataFrame, cible: pd.Series) -> None:
        """Entraine avec les entrees encodees; refuse les notes invalides."""
        if entrees.empty or len(entrees) != len(cible):
            raise DonneeInvalideError("Les entrees et les notes doivent avoir la meme taille, non nulle.")
        notes = np.asarray(cible, dtype=float)
        if notes.ndim != 1 or not np.isfinite(notes).all():
            raise DonneeInvalideError("Les notes d'entrainement ne sont pas valides.")
        regression = LinearRegression()
        regression.fit(entrees[COLONNES_ENTREE], notes)
        self._regression = regression
        self._moyenne_reference = float(np.mean(notes))
        self._nombre_entrainement = len(notes)
        self._nombre_test = 0
        self._resultats = {}

    def predire(self, entrees: pd.DataFrame) -> np.ndarray:
        """Retourne les notes predites; exige des entrees et un modele pret."""
        if self._regression is None:
            raise DonneeInvalideError("Entrainez ou chargez le modele avant de predire.")
        if entrees.empty:
            raise DonneeInvalideError("Aucune entree a predire.")
        return self._regression.predict(entrees[COLONNES_ENTREE])

    def predire_un(self, saisies: dict[str, object]) -> float:
        """Retourne la note d'un eleve; refuse les saisies invalides."""
        entrees = preparer_entrees(pd.DataFrame([saisies]), self._variables)
        return float(self.predire(entrees)[0])

    def evaluer(self, entrees_test: pd.DataFrame, cible_test: pd.Series) -> dict[str, float]:
        """Retourne les RMSE du modele et de la reference sur les memes eleves."""
        predictions = self.predire(entrees_test)
        reference = np.full(len(predictions), self.moyenne_reference)
        self._resultats = {
            "rmse_modele": calculer_rmse(cible_test, predictions),
            "r2_modele": r2_score(cible_test, predictions),
            "rmse_reference": calculer_rmse(cible_test, reference),
        }
        self._nombre_test = len(predictions)
        return dict(self._resultats)

    def sauvegarder(self, dossier: str, separation: dict[str, object] | None = None) -> None:
        """Enregistre les deux fichiers; exige d'avoir entraine et evalue."""
        if self._regression is None or not self._resultats:
            raise DonneeInvalideError("Entrainez et evaluez le modele avant de le sauvegarder.")
        os.makedirs(dossier, exist_ok=True)
        if separation is None:
            separation = {}

        metadonnees = {
            "modele": "LinearRegression",
            "cible": CIBLE,
            "colonnes": COLONNES_ENTREE,
            "variables": [variable.metadonnees() for variable in self._variables],
            "encodage": {"schoolsup": {"no": 0, "yes": 1}},
            "studytime": {
                "1": "Moins de 2 h par semaine",
                "2": "De 2 a 5 h par semaine",
                "3": "De 5 a 10 h par semaine",
                "4": "Plus de 10 h par semaine",
            },
            "moyenne_reference": self.moyenne_reference,
            "resultats": dict(self._resultats),
            "nombre_entrainement": self._nombre_entrainement,
            "nombre_test": self._nombre_test,
            "separation": dict(separation),
            "duree_entrainement_secondes": self._duree_entrainement,
            "versions": {
                "scikit_learn": sklearn.__version__,
                "numpy": np.__version__, "pandas": pd.__version__,
            },
        }
        chemin_modele = os.path.join(dossier, "regression_lineaire.joblib")
        chemin_json = os.path.join(dossier, "metadonnees.json")
        with open(chemin_modele, "wb") as fichier:
            joblib.dump(self._regression, fichier)
        with open(chemin_json, "w", encoding="utf-8") as fichier:
            json.dump(metadonnees, fichier, ensure_ascii=False, indent=2, allow_nan=False)
            fichier.write("\n")

    @classmethod
    def charger(cls, dossier: str) -> "ModeleRegression":
        """Retourne le modele sauvegarde; leve une erreur si un fichier manque."""
        chemin_modele = os.path.join(dossier, "regression_lineaire.joblib")
        chemin_json = os.path.join(dossier, "metadonnees.json")
        for chemin in (chemin_modele, chemin_json):
            if not os.path.isfile(chemin):
                raise DonneeInvalideError(f"Fichier du modele introuvable : {chemin}")
        with open(chemin_json, encoding="utf-8") as fichier:
            metadonnees = json.load(fichier)
        if metadonnees.get("colonnes") != COLONNES_ENTREE:
            raise DonneeInvalideError("Les colonnes du modele ne correspondent pas au projet.")
        with open(chemin_modele, "rb") as fichier:
            regression = joblib.load(fichier)
        if not isinstance(regression, LinearRegression):
            raise DonneeInvalideError("Le fichier ne contient pas une regression lineaire.")
        modele = cls()
        modele._regression = regression
        modele._moyenne_reference = float(metadonnees["moyenne_reference"])
        modele._resultats = dict(metadonnees["resultats"])
        modele._nombre_entrainement = int(metadonnees["nombre_entrainement"])
        modele._nombre_test = int(metadonnees["nombre_test"])
        modele._duree_entrainement = float(metadonnees["duree_entrainement_secondes"])
        return modele


def graphique_evaluation(reelles: pd.Series, predites: np.ndarray, chemin: str) -> None:
    """Enregistre le graphique; refuse des listes de notes incompatibles."""
    calculer_rmse(reelles, predites)
    os.makedirs(os.path.dirname(os.path.abspath(chemin)), exist_ok=True)
    figure, axe = plt.subplots(figsize=(7, 6))
    axe.scatter(reelles, predites, alpha=0.6, label="Eleves du groupe de test")
    axe.plot([0, 20], [0, 20], "--", color="black", label="Prediction exacte")
    axe.set(
        title="Notes predites et notes reelles",
        xlabel="Note reelle G3 (sur 20)", ylabel="Note predite (sur 20)",
    )
    axe.legend()
    figure.tight_layout()
    figure.savefig(chemin, dpi=150)
    plt.close(figure)
