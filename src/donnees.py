"""Exploration du CSV et preparation des cinq variables choisies."""

from abc import ABC, abstractmethod
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from src.exceptions import DonneeInvalideError


RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHEMIN_DONNEES = os.path.join(RACINE, "donnees", "student-por.csv")
COLONNES_ENTREE = ["G1", "G2", "failures", "studytime", "schoolsup"]
CIBLE = "G3"
GRAINE = 42
PART_TEST = 0.20


class Variable(ABC):
    """Classe de base pour les variables du formulaire."""

    def __init__(self, nom: str, libelle: str) -> None:
        """Recoit le nom de la colonne et le texte a afficher."""
        self._nom = nom
        self._libelle = libelle

    @property
    def nom(self) -> str:
        """Retourne le nom de la colonne."""
        return self._nom

    @abstractmethod
    def valider(self, valeur: object) -> float | str:
        """Retourne la valeur si elle est valide, sinon leve une erreur."""

    @abstractmethod
    def metadonnees(self) -> dict[str, object]:
        """Retourne les informations du champ pour le fichier JSON."""

    def __str__(self) -> str:
        """Retourne le nom et la description de la variable."""
        return f"{self._nom} : {self._libelle}"


class VariableNumerique(Variable):
    """Variable qui accepte un nombre dans un intervalle."""

    def __init__(
        self, nom: str, libelle: str, minimum: float,
        maximum: float, entier: bool = False,
    ) -> None:
        """Recoit les bornes et indique si le nombre doit etre entier."""
        super().__init__(nom, libelle)
        self._minimum = minimum
        self._maximum = maximum
        self._entier = entier

    def valider(self, valeur: object) -> float:
        """Retourne un nombre; leve une erreur si la saisie n'est pas valide."""
        if valeur is None or isinstance(valeur, (bool, np.bool_)):
            raise DonneeInvalideError(f"{self._libelle} : entrez un nombre.")
        if isinstance(valeur, str):
            valeur = valeur.strip().replace(",", ".")
        try:
            nombre = float(valeur)
        except (TypeError, ValueError, OverflowError) as erreur:
            raise DonneeInvalideError(f"{self._libelle} : entrez un nombre.") from erreur
        if not np.isfinite(nombre):
            raise DonneeInvalideError(f"{self._libelle} : nombre non valide.")
        if not self._minimum <= nombre <= self._maximum:
            raise DonneeInvalideError(
                f"{self._libelle} : valeur entre "
                f"{self._minimum:g} et {self._maximum:g} attendue."
            )
        if self._entier and not nombre.is_integer():
            raise DonneeInvalideError(f"{self._libelle} : entrez un entier.")
        return nombre

    def metadonnees(self) -> dict[str, object]:
        """Retourne les bornes et le type de nombre pour le JSON."""
        return {
            "nom": self._nom,
            "libelle": self._libelle,
            "type": "numerique",
            "minimum": self._minimum,
            "maximum": self._maximum,
            "entier": self._entier,
        }


class VariableCategorielle(Variable):
    """Variable qui accepte seulement les choix proposes."""

    def __init__(self, nom: str, libelle: str, categories: list[str]) -> None:
        """Recoit les choix possibles pour cette variable."""
        super().__init__(nom, libelle)
        self._categories = list(categories)

    def valider(self, valeur: object) -> str:
        """Retourne le choix en minuscules; leve une erreur s'il est inconnu."""
        if not isinstance(valeur, str):
            raise DonneeInvalideError(
                f"{self._libelle} : choisissez parmi {self._categories}."
            )
        categorie = valeur.strip().lower()
        if categorie not in self._categories:
            raise DonneeInvalideError(
                f"{self._libelle} : choisissez parmi {self._categories}."
            )
        return categorie

    def metadonnees(self) -> dict[str, object]:
        """Retourne la liste des choix pour le JSON."""
        return {
            "nom": self._nom,
            "libelle": self._libelle,
            "type": "categorielle",
            "categories": list(self._categories),
        }


def creer_variables() -> list[Variable]:
    """Retourne les cinq variables avec leurs valeurs acceptees."""
    return [
        VariableNumerique("G1", "Note de la premiere periode", 0, 20),
        VariableNumerique("G2", "Note de la deuxieme periode", 0, 20),
        VariableNumerique("failures", "Echecs scolaires anterieurs", 0, 3, True),
        VariableNumerique("studytime", "Tranche de temps d'etude (code)", 1, 4, True),
        VariableCategorielle("schoolsup", "Soutien scolaire supplementaire", ["no", "yes"]),
    ]


def preparer_entrees(
    table: pd.DataFrame, variables: list[Variable] | None = None,
) -> pd.DataFrame:
    """Retourne les entrees verifiees et encodees; refuse les valeurs invalides."""
    if table.empty:
        raise DonneeInvalideError("Les donnees d'entree sont vides.")
    if variables is None:
        variables = creer_variables()

    manquantes = []
    for variable in variables:
        if variable.nom not in table.columns:
            manquantes.append(variable.nom)
    if manquantes:
        raise DonneeInvalideError(f"Colonnes manquantes : {', '.join(manquantes)}.")
    resultat = pd.DataFrame(index=table.index)
    for variable in variables:
        resultat[variable.nom] = table[variable.nom].map(variable.valider)

    # Le modele utilise des nombres, donc on remplace no et yes par 0 et 1.
    resultat["schoolsup"] = resultat["schoolsup"].map({"no": 0, "yes": 1})
    return resultat


class JeuDeDonnees:
    """Garde les donnees chargees et les variables utilisees."""

    def __init__(self, chemin: str = CHEMIN_DONNEES) -> None:
        """Recoit le chemin du CSV sans le lire tout de suite."""
        self._chemin = chemin
        self._table: pd.DataFrame | None = None
        self._variables = creer_variables()

    def charger(self) -> pd.DataFrame:
        """Retourne le CSV charge; leve une erreur s'il manque ou est invalide."""
        if not os.path.isfile(self._chemin):
            raise DonneeInvalideError(f"CSV introuvable : {self._chemin}")
        try:
            with open(self._chemin, encoding="utf-8", newline="") as fichier:
                table = pd.read_csv(fichier)
        except (OSError, UnicodeError, pd.errors.ParserError, pd.errors.EmptyDataError) as erreur:
            raise DonneeInvalideError(f"Impossible de lire le CSV : {erreur}") from erreur
        if CIBLE not in table:
            raise DonneeInvalideError("La colonne cible G3 est absente.")
        preparer_entrees(table, self._variables)
        cible = VariableNumerique(CIBLE, "Note finale", 0, 20)
        table[CIBLE] = table[CIBLE].map(cible.valider)
        self._table = table
        return table.copy()

    @property
    def table(self) -> pd.DataFrame:
        """Retourne une copie des donnees; exige de les avoir chargees."""
        if self._table is None:
            raise DonneeInvalideError("Chargez le CSV avant de l'utiliser.")
        return self._table.copy()

    def preparer(self) -> tuple[pd.DataFrame, pd.Series]:
        """Retourne les cinq entrees et G3 a partir du CSV charge."""
        table = self.table
        entrees = preparer_entrees(table, self._variables)
        cible = table[CIBLE].copy()
        return entrees, cible

    def separer(
        self, part_test: float = PART_TEST, graine: int = GRAINE,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Retourne les deux groupes; refuse une part de test hors de 0 a 1."""
        if not 0 < part_test < 1:
            raise DonneeInvalideError("La part de test doit etre entre 0 et 1.")
        entrees, cible = self.preparer()
        if len(cible) < 2:
            raise DonneeInvalideError("Il faut au moins deux lignes pour separer les donnees.")
        return train_test_split(
            entrees, cible, test_size=part_test, random_state=graine,
        )

    def explorer(self, chemin_graphique: str) -> None:
        """Affiche le bilan et cree le graphique au chemin donne; exige un CSV charge."""
        df = self.table
        print("Dimensions (lignes, colonnes) :", df.shape)
        print(df.head())
        df.info()
        print(df.describe())
        print("Valeurs manquantes par colonne :")
        print(df.isna().sum())
        print("Doublons :", df.duplicated().sum())
        for colonne in df.select_dtypes(exclude="number").columns:
            print(f"\n{colonne} :")
            print(df[colonne].value_counts().head(10))
        self.graphique_exploration(chemin_graphique)
        print(f"\nGraphique enregistre : {chemin_graphique}")

    def graphique_exploration(self, chemin: str) -> None:
        """Enregistre l'histogramme au chemin donne; exige un CSV charge."""
        cible = self.table[CIBLE]
        os.makedirs(os.path.dirname(os.path.abspath(chemin)), exist_ok=True)
        figure, axe = plt.subplots(figsize=(8, 5))
        axe.hist(cible, bins=np.arange(-0.5, 21, 1), edgecolor="white")
        axe.set(
            title="Distribution des notes finales",
            xlabel="Note finale G3 (sur 20)", ylabel="Nombre d'eleves",
            xticks=range(0, 21, 2),
        )
        figure.tight_layout()
        figure.savefig(chemin, dpi=150)
        plt.close(figure)

    def __str__(self) -> str:
        """Retourne le nom du CSV et le nombre de lignes chargees."""
        lignes = 0
        if self._table is not None:
            lignes = len(self._table)
        return f"{os.path.basename(self._chemin)} : {lignes} lignes"
