"""Enregistre et relit les prédictions de l'interface."""

import csv
from datetime import datetime
import os

from src.donnees import COLONNES_ENTREE
from src.exceptions import DonneeInvalideError


COLONNES_HISTORIQUE = ["date_heure", *COLONNES_ENTREE, "note_prevue"]


def enregistrer_prediction(chemin: str, valeurs: dict[str, float | str], note: float) -> None:
    """Ajoute les valeurs et la note au CSV. Une erreur d'écriture remonte à l'interface."""
    ligne = dict(valeurs)
    ligne["date_heure"] = datetime.now().isoformat(sep=" ", timespec="seconds")
    ligne["note_prevue"] = f"{note:.1f}"

    with open(chemin, "a", encoding="utf-8", newline="") as fichier:
        auteur = csv.DictWriter(fichier, fieldnames=COLONNES_HISTORIQUE)
        if fichier.tell() == 0:
            auteur.writeheader()
        auteur.writerow(ligne)


def lire_historique(chemin: str) -> list[dict[str, str]]:
    """Retourne les lignes du CSV, ou une liste vide avant la première prédiction."""
    if not os.path.isfile(chemin):
        return []

    with open(chemin, encoding="utf-8", newline="") as fichier:
        lecteur = csv.DictReader(fichier, strict=True)
        if lecteur.fieldnames is None:
            return []
        if lecteur.fieldnames != COLONNES_HISTORIQUE:
            raise DonneeInvalideError("Les colonnes du fichier d'historique sont incorrectes.")
        return list(lecteur)
