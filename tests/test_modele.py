"""Tests du calcul des erreurs, de la regression et de sa sauvegarde."""

import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import root_mean_squared_error
from sklearn.linear_model import LinearRegression

from src.donnees import COLONNES_ENTREE
from src.exceptions import DonneeInvalideError
from src.main import main
from src.modele import ModeleRegression, calculer_rmse


def test_rmse_connu_et_identique_a_sklearn() -> None:
    """Verifie notre RMSE avec un calcul simple et avec scikit-learn."""
    reelles = [0, 0]
    predites = [3, 4]
    resultat = calculer_rmse(reelles, predites)
    # (3 au carre + 4 au carre) / 2 = 12.5, puis on prend la racine.
    assert resultat == pytest.approx(np.sqrt(12.5))
    assert resultat == pytest.approx(root_mean_squared_error(reelles, predites))


@pytest.mark.parametrize(
    "reelles,predites",
    [([], []), ([1], [1, 2]), ([float("nan")], [1]),
     ([1], [float("inf")]), ([[1]], [[1]]), (["abc"], [1])],
)
def test_rmse_refuse_les_donnees_invalides(reelles: object, predites: object) -> None:
    """Verifie qu'on refuse des listes vides ou des notes incorrectes."""
    with pytest.raises(DonneeInvalideError):
        calculer_rmse(reelles, predites)


def test_modele_retrouve_une_relation_connue(modele_simple: ModeleRegression) -> None:
    """Verifie que le modele retrouve 13 quand G1 vaut 6 dans notre exemple."""
    note = modele_simple.predire_un({
        "G1": 6, "G2": 0, "failures": 0, "studytime": 1, "schoolsup": "no",
    })
    assert note == pytest.approx(13.0)


def test_reference_uniquement_calculee_sur_entrainement(
    modele_simple: ModeleRegression, entrees_simples: pd.DataFrame,
) -> None:
    """Verifie que les notes du test ne changent pas la moyenne d'entrainement."""
    assert modele_simple.moyenne_reference == pytest.approx(6.0)
    test = entrees_simples.iloc[:2].copy()
    test["G1"] = [8, 9]
    notes_test = pd.Series([17.0, 19.0])
    resultats = modele_simple.evaluer(test, notes_test)
    assert resultats["rmse_modele"] == pytest.approx(0, abs=1e-10)
    assert resultats["rmse_reference"] == pytest.approx(np.sqrt((11**2 + 13**2) / 2))
    assert modele_simple.moyenne_reference == pytest.approx(6.0)


def test_prediction_avant_entrainement(entrees_simples: pd.DataFrame) -> None:
    """Verifie l'erreur si on veut predire avant l'entrainement."""
    with pytest.raises(DonneeInvalideError, match="Entrainez"):
        ModeleRegression().predire(entrees_simples)


def test_sauvegarde_exige_une_evaluation(
    modele_simple: ModeleRegression, tmp_path: Path,
) -> None:
    """Verifie qu'il faut calculer les scores avant de sauvegarder."""
    with pytest.raises(DonneeInvalideError, match="evaluez"):
        modele_simple.sauvegarder(str(tmp_path))


def test_sauvegarde_recharge_modele_et_metadonnees(
    modele_simple: ModeleRegression, entrees_simples: pd.DataFrame, tmp_path: Path,
) -> None:
    """Verifie les predictions et les informations apres rechargement."""
    modele_simple.evaluer(entrees_simples, 2 * entrees_simples["G1"] + 1)
    modele_simple.sauvegarder(str(tmp_path), {"part_test": 0.2, "graine": 42})
    recharge = ModeleRegression.charger(str(tmp_path))
    assert recharge.predire(entrees_simples) == pytest.approx(
        modele_simple.predire(entrees_simples)
    )
    with open(tmp_path / "metadonnees.json", encoding="utf-8") as fichier:
        informations = json.load(fichier)
    assert informations["colonnes"] == COLONNES_ENTREE
    assert informations["moyenne_reference"] == pytest.approx(6.0)
    assert informations["variables"][0]["maximum"] == 20
    assert informations["variables"][-1]["categories"] == ["no", "yes"]
    assert informations["encodage"]["schoolsup"] == {"no": 0, "yes": 1}
    assert informations["duree_entrainement_secondes"] >= 0


def test_rechargement_fichier_absent(tmp_path: Path) -> None:
    """Verifie l'erreur quand la sauvegarde n'existe pas."""
    with pytest.raises(DonneeInvalideError, match="introuvable"):
        ModeleRegression.charger(str(tmp_path))


def test_commande_csv_absent_sans_traceback(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    """Verifie que la commande affiche un message si le CSV manque."""
    code = main(["--entrainer", "--donnees", str(tmp_path / "absent.csv")])
    sortie = capsys.readouterr()
    assert code == 1
    assert "introuvable" in sortie.err
    assert "Traceback" not in sortie.err


def test_commandes_entrainer_puis_predire_sans_reentrainer(
    petit_csv: Path, tmp_path: Path, capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Entraine, sauvegarde, puis verifie une prediction sans reentrainer."""
    dossier = tmp_path / "sortie"
    code = main([
        "--entrainer", "--donnees", str(petit_csv), "--sortie", str(dossier),
    ])
    assert code == 0
    assert "RMSE du modele" in capsys.readouterr().out
    assert (dossier / "regression_lineaire.joblib").is_file()
    assert (dossier / "metadonnees.json").is_file()
    assert (dossier / "evaluation_modele.png").stat().st_size > 0

    def interdire_entrainement(*arguments: object, **options: object) -> None:
        """Fait echouer le test si on appelle fit pendant la prediction."""
        raise AssertionError("La prediction ne doit pas reentrainer le modele.")

    monkeypatch.setattr(LinearRegression, "fit", interdire_entrainement)
    code = main([
        "--predire", "12", "13", "0", "2", "yes", "--sortie", str(dossier),
    ])
    assert code == 0
    assert "Note finale estimee" in capsys.readouterr().out


def test_lancement_direct_depuis_un_autre_dossier(
    petit_csv: Path, tmp_path: Path,
) -> None:
    """Verifie l'entrainement depuis un autre dossier."""
    projet = Path(__file__).resolve().parent.parent
    sortie = tmp_path / "modele"
    resultat = subprocess.run(
        [
            sys.executable, str(projet / "src" / "main.py"),
            "--entrainer", "--donnees", str(petit_csv), "--sortie", str(sortie),
        ],
        cwd=tmp_path, capture_output=True, text=True, timeout=60,
    )
    assert resultat.returncode == 0, resultat.stderr
    assert "RMSE du modele" in resultat.stdout
    assert (sortie / "regression_lineaire.joblib").is_file()


def test_commande_explorer_sans_entrainer(
    petit_csv: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
) -> None:
    """Verifie le bilan et le graphique sans creer un modele."""
    monkeypatch.setattr("src.main.RACINE", str(tmp_path))
    code = main(["--explorer", "--donnees", str(petit_csv)])
    sortie = capsys.readouterr()
    assert code == 0
    assert "Dimensions (lignes, colonnes) : (8, 6)" in sortie.out
    assert "Doublons : 0" in sortie.out
    assert (tmp_path / "exploration_cible.png").stat().st_size > 0
    assert not (tmp_path / "modeles" / "regression_lineaire.joblib").exists()
