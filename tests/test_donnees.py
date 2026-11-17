"""Premier test de verification du jeu de donnees, execute aussi dans la CI."""

import os

import pandas as pd
from pandas.api.types import is_numeric_dtype


def test_csv_respecte_les_criteres_du_projet() -> None:
    """Sans argument, verifie le CSV; echoue si absent ou non conforme."""
    racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    chemin = os.path.join(racine, "donnees", "student-por.csv")

    assert os.path.isfile(chemin), "Le CSV doit etre present dans donnees/."
    with open(chemin, encoding="utf-8", newline="") as fichier:
        donnees = pd.read_csv(fichier)

    assert 500 <= len(donnees) <= 50_000
    assert "G3" in donnees.columns, "La cible G3 doit etre presente."
    assert is_numeric_dtype(donnees["G3"]), "La cible doit etre numerique."
    assert donnees["G3"].notna().all(), "Chaque ligne doit avoir une cible."

    caracteristiques = donnees.drop(columns="G3")
    assert caracteristiques.shape[1] >= 5
    assert not caracteristiques.select_dtypes(include="number").empty
    assert not caracteristiques.select_dtypes(exclude="number").empty
