import tkinter as tk
from tkinter import ttk

from src.donnees import charger_variables, valider_saisies
from src.donnees import VariableCategorielle
from src.exceptions import DonneeInvalideError

CHEMIN_JSON = "modeles/metadonnees.json"


class Application:
    """Fenêtre principale : champs de saisie et validation."""

    def __init__(self, fenetre, variables):
        """Reçoit la fenêtre Tkinter et la liste des variables."""
        self._fenetre = fenetre
        self._variables = variables
        self._champs = {}
        fenetre.title("Prédiction de la note finale (G3)")
        self._construire_champs()
        self._construire_zone_resultat()

    def _construire_champs(self):
        """Crée un champ par variable, selon son type."""
        ligne = 0
        for variable in self._variables:
            etiquette = tk.Label(self._fenetre, text=variable.libelle)
            etiquette.grid(row=ligne, column=0, padx=10, pady=5, sticky="w")
            if isinstance(variable, VariableCategorielle):
                choix = variable.metadonnees()["categories"]
                champ = ttk.Combobox(self._fenetre, values=choix, state="readonly")
                champ.set(choix[0])
            else:
                champ = tk.Entry(self._fenetre)
            champ.grid(row=ligne, column=1, padx=10, pady=5)
            self._champs[variable.nom] = champ
            ligne = ligne + 1

    def _construire_zone_resultat(self):
        """Crée le bouton, la zone d'erreur et la zone de résultat."""
        ligne = len(self._variables)
        bouton = tk.Button(self._fenetre, text="Prédire", command=self._predire)
        bouton.grid(row=ligne, column=0, columnspan=2, pady=10)
        self._erreur = tk.Label(self._fenetre, text="", fg="red")
        self._erreur.grid(row=ligne + 1, column=0, columnspan=2)
        self._resultat = tk.Label(self._fenetre, text="")
        self._resultat.grid(row=ligne + 2, column=0, columnspan=2, pady=5)

    def _predire(self):
        """Valide les saisies; affiche l'erreur ou les valeurs acceptées."""
        saisies = {}
        for nom in self._champs:
            saisies[nom] = self._champs[nom].get()
        try:
            valeurs = valider_saisies(self._variables, saisies)
        except DonneeInvalideError as erreur:
            self._resultat.config(text="")
            self._erreur.config(text=str(erreur))
            return
        self._erreur.config(text="")
        self._resultat.config(text="Saisies valides : " + str(valeurs))


def lancer():
    """Charge les variables et ouvre la fenêtre."""
    try:
        variables = charger_variables(CHEMIN_JSON)
    except DonneeInvalideError as erreur:
        print("Erreur :", erreur)
        return
    fenetre = tk.Tk()
    Application(fenetre, variables)
    fenetre.mainloop()
