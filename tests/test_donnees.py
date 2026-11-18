"""Tests du CSV et des valeurs qu'on accepte dans les champs."""

import os
from pathlib import Path

import pandas as pd
import pytest
from pandas.api.types import is_numeric_dtype

from src.donnees import (
    COLONNES_ENTREE, JeuDeDonnees, VariableCategorielle, VariableNumerique,
    preparer_entrees,
)
from src.exceptions import DonneeInvalideError


def test_csv_respecte_les_criteres_du_projet() -> None:
    """Verifie que le CSV respecte les criteres de base du projet."""
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


def test_preparation_selectionne_et_encode_sans_modifier_le_csv(petit_csv: Path) -> None:
    """Verifie les cinq colonnes et la conversion yes/no sans changer le CSV."""
    jeu = JeuDeDonnees(str(petit_csv))
    originale = jeu.charger()
    entrees, cible = jeu.preparer()
    assert list(entrees.columns) == COLONNES_ENTREE
    assert entrees["schoolsup"].tolist()[:2] == [1, 0]
    assert originale["schoolsup"].tolist()[:2] == ["yes", "no"]
    assert cible.iloc[0] == pytest.approx(9.0)
    originale.loc[0, "G3"] = 20
    assert jeu.table.loc[0, "G3"] == pytest.approx(9.0)


def test_separation_reproductible_et_sans_chevauchement(petit_csv: Path) -> None:
    """Verifie qu'on retrouve les memes groupes et qu'ils ne se melangent pas."""
    jeu = JeuDeDonnees(str(petit_csv))
    jeu.charger()
    premiere = jeu.separer()
    seconde = jeu.separer()
    for gauche, droite in zip(premiere, seconde):
        assert gauche.equals(droite)
    x_train, x_test, y_train, y_test = premiere
    assert set(x_train.index).isdisjoint(x_test.index)
    assert set(x_train.index) | set(x_test.index) == set(range(8))
    assert len(x_train) == 6 and len(x_test) == 2
    assert x_train.index.equals(y_train.index)
    assert x_test.index.equals(y_test.index)


def test_csv_manquant(tmp_path: Path) -> None:
    """Verifie l'erreur quand le CSV n'existe pas."""
    with pytest.raises(DonneeInvalideError, match="introuvable"):
        JeuDeDonnees(str(tmp_path / "absent.csv")).charger()


def test_csv_sans_cible(petit_csv: Path) -> None:
    """Verifie qu'on refuse un CSV sans G3."""
    with open(petit_csv, encoding="utf-8") as fichier:
        table = pd.read_csv(fichier).drop(columns="G3")
    with open(petit_csv, "w", encoding="utf-8", newline="") as fichier:
        table.to_csv(fichier, index=False)
    with pytest.raises(DonneeInvalideError, match="G3"):
        JeuDeDonnees(str(petit_csv)).charger()


def test_entrees_sans_colonne_requise() -> None:
    """Verifie qu'on refuse une ligne ou il manque des entrees."""
    with pytest.raises(DonneeInvalideError, match="Colonnes manquantes"):
        preparer_entrees(pd.DataFrame([{"G1": 12}]))


@pytest.mark.parametrize("valeur", ["", "abc", None, float("nan"), float("inf"), -1, 21, True])
def test_note_invalide(valeur: object) -> None:
    """Verifie qu'une note vide ou incorrecte est refusee."""
    with pytest.raises(DonneeInvalideError):
        VariableNumerique("G1", "Note", 0, 20).valider(valeur)


@pytest.mark.parametrize("valeur", [0, 20, "12,5"])
def test_note_valide_et_bornes(valeur: object) -> None:
    """Verifie les notes 0 et 20, et une note ecrite avec une virgule."""
    resultat = VariableNumerique("G1", "Note", 0, 20).valider(valeur)
    if valeur == "12,5":
        attendu = 12.5
    else:
        attendu = float(valeur)
    assert resultat == pytest.approx(attendu)


@pytest.mark.parametrize("valeur", [0, 5, 2.5])
def test_studytime_exige_un_code_entier(valeur: object) -> None:
    """Verifie que studytime accepte seulement les codes entiers de 1 a 4."""
    with pytest.raises(DonneeInvalideError):
        VariableNumerique("studytime", "Temps d'etude", 1, 4, True).valider(valeur)


def test_validation_categorielle() -> None:
    """Accepte YES avec des espaces, mais refuse un choix inconnu."""
    variable = VariableCategorielle("schoolsup", "Soutien", ["no", "yes"])
    assert variable.valider(" YES ") == "yes"
    with pytest.raises(DonneeInvalideError):
        variable.valider("peut-etre")


def test_acces_avant_chargement() -> None:
    """Verifie qu'on ne peut pas preparer les donnees avant de les charger."""
    with pytest.raises(DonneeInvalideError, match="Chargez"):
        JeuDeDonnees().preparer()
