"""Donnees inventees pour tester le code sans utiliser le vrai CSV."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.donnees import COLONNES_ENTREE
from src.modele import ModeleRegression


@pytest.fixture
def petit_csv(tmp_path: Path) -> Path:
    """Cree un CSV temporaire de huit eleves et retourne son chemin."""
    table = pd.DataFrame({
        "G1": [8, 9, 10, 11, 12, 13, 14, 15],
        "G2": [9, 10, 10, 12, 11, 14, 13, 16],
        "failures": [1, 0, 0, 1, 0, 0, 0, 0],
        "studytime": [1, 2, 3, 2, 4, 3, 2, 1],
        "schoolsup": ["yes", "no", "yes", "no", "no", "yes", "no", "no"],
        "G3": [9, 10, 11, 12, 12, 14, 14, 16],
    })
    chemin = tmp_path / "eleves.csv"
    with open(chemin, "w", encoding="utf-8", newline="") as fichier:
        table.to_csv(fichier, index=False)
    return chemin


@pytest.fixture
def entrees_simples() -> pd.DataFrame:
    """Retourne six lignes ou seule la note G1 change."""
    return pd.DataFrame({
        "G1": np.arange(6, dtype=float), "G2": np.zeros(6),
        "failures": np.zeros(6), "studytime": np.ones(6),
        "schoolsup": np.zeros(6),
    }, columns=COLONNES_ENTREE)


@pytest.fixture
def modele_simple(entrees_simples: pd.DataFrame) -> ModeleRegression:
    """Retourne un modele entraine avec la formule G3 = 2 * G1 + 1."""
    modele = ModeleRegression()
    modele.entrainer(entrees_simples, 2 * entrees_simples["G1"] + 1)
    return modele
