import csv
import os
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from src.donnees import RACINE, JeuDeDonnees, VariableCategorielle
from src.donnees import charger_variables, valider_saisies
from src.exceptions import DonneeInvalideError
from src.historique import COLONNES_HISTORIQUE, enregistrer_prediction, lire_historique
from src.modele import ModeleRegression

DOSSIER_MODELE = os.path.join(RACINE, "modeles")
CHEMIN_JSON = os.path.join(DOSSIER_MODELE, "metadonnees.json")
CHEMIN_HISTORIQUE = os.path.join(RACINE, "historique.csv")
SEUIL_REUSSITE = 10


class Application:
    """Fenêtre principale avec les saisies, la prédiction et l'historique."""

    def __init__(self, fenetre, variables, modele, notes):
        """Reçoit la fenêtre, les variables, le modèle et les notes G3."""
        self._fenetre = fenetre
        self._variables = variables
        self._modele = modele
        self._notes = notes
        self._champs = {}
        fenetre.title("Prédiction de la note finale (G3)")
        self._construire_champs()
        self._construire_zone_resultat()
        self._construire_graphique()

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

    def _construire_zone_resultat(self) -> None:
        """Ajoute les boutons, le résultat"""
        ligne = len(self._variables)
        bouton = tk.Button(self._fenetre, text="Prédire", command=self._predire)
        bouton.grid(row=ligne, column=0, pady=10)
        bouton_historique = tk.Button(
            self._fenetre, text="Voir l'historique", command=self._afficher_historique,
        )
        bouton_historique.grid(row=ligne, column=1, pady=10)
        self._erreur = tk.Label(self._fenetre, text="", fg="red")
        self._erreur.grid(row=ligne + 1, column=0, columnspan=2)
        self._resultat = tk.Label(self._fenetre, text="")
        self._resultat.grid(row=ligne + 2, column=0, columnspan=2, pady=5)
        
      

    def _afficher_historique(self) -> None:
        """Ouvre les prédictions sauvegardées et affiche un message si la lecture échoue."""
        fenetre = tk.Toplevel(self._fenetre)
        fenetre.title("Historique des prédictions")
        fenetre.transient(self._fenetre)

        try:
            predictions = lire_historique(CHEMIN_HISTORIQUE)
        except (DonneeInvalideError, OSError, UnicodeError, csv.Error) as erreur:
            tk.Label(fenetre, text=f"Impossible de lire l'historique. {erreur}").pack(padx=15, pady=15)
            return

        if not predictions:
            tk.Label(fenetre, text="Aucune prédiction enregistrée.").pack(padx=15, pady=15)
            return

        tableau = ttk.Treeview(fenetre, columns=COLONNES_HISTORIQUE, show="headings")
        titres = ["Date et heure", "G1", "G2", "Échecs", "Étude (code)", "Soutien", "Note / 20"]
        for colonne, titre in zip(COLONNES_HISTORIQUE, titres):
            tableau.heading(colonne, text=titre)
            tableau.column(colonne, width=150 if colonne == "date_heure" else 85, anchor="center")

        for prediction in reversed(predictions):
            valeurs = [prediction[colonne] for colonne in COLONNES_HISTORIQUE]
            tableau.insert("", "end", values=valeurs)

        barre = ttk.Scrollbar(fenetre, orient="vertical", command=tableau.yview)
        tableau.configure(yscrollcommand=barre.set)
        barre.pack(side="right", fill="y")
        tableau.pack(side="left", fill="both", expand=True)

    def _construire_graphique(self):
        """Crée la zone Matplotlib et dessine le graphique de départ."""
        ligne = len(self._variables) + 4
        self._figure = Figure(figsize=(5, 3))
        self._axe = self._figure.add_subplot(111)
        self._canvas = FigureCanvasTkAgg(self._figure, master=self._fenetre)
        self._canvas.get_tk_widget().grid(row=ligne, column=0, columnspan=2)
        self._dessiner_graphique(None)

    def _dessiner_graphique(self, note):
        """Dessine les notes des élèves, le seuil de 10 et la note prévue."""
        self._axe.clear()
        self._axe.hist(
            self._notes, bins=list(range(0, 22)),
            color="lightgray", edgecolor="white", label="Notes finales (élèves)",
        )
        self._axe.axvline(
            SEUIL_REUSSITE, color="red", linestyle="--", label="Seuil de réussite (10)",
        )
        if note is not None:
            self._axe.axvline(
                note, color="blue", label="Note prévue : " + f"{note:.1f}",
            )
        self._axe.set_title("Note prévue parmi les notes finales")
        self._axe.set_xlabel("Note finale G3 (sur 20)")
        self._axe.set_ylabel("Nombre d'élèves")
        self._axe.legend()
        self._canvas.draw()

    def _predire(self) -> None:
        """Prédit et enregistre la note si les cinq saisies sont valides."""
        saisies = {}
        for nom in self._champs:
            saisies[nom] = self._champs[nom].get()
        try:
            valeurs = valider_saisies(self._variables, saisies)
            note = self._modele.predire_un(saisies)
            rmse = self._modele.rmse
        except (DonneeInvalideError, ValueError) as erreur:
            self._resultat.config(text="")
            self._erreur.config(text=str(erreur))
            return
        # Une régression linéaire peut sortir de 0 à 20 : on ramène la note dans l'intervalle.
        note = max(0, min(20, float(note)))
        if note >= SEUIL_REUSSITE:
            verdict = "réussite probable"
        else:
            verdict = "échec probable"
        self._erreur.config(text="")
        self._resultat.config(
            text=f"Note prévue : {note:.1f} / 20 → {verdict}\n"
                 f"Erreur sur le groupe de test (RMSE) : {rmse:.3f} point(s)"
        )
        self._dessiner_graphique(note)
        try:
            enregistrer_prediction(CHEMIN_HISTORIQUE, valeurs, note)
        except (OSError, csv.Error) as erreur:
            self._erreur.config(text=f"Prédiction non enregistrée. {erreur}")


def lancer():
    """Charge les variables, le modèle et les notes, puis ouvre la fenêtre."""
    try:
        variables = charger_variables(CHEMIN_JSON)
        modele = ModeleRegression.charger(DOSSIER_MODELE)
        notes = JeuDeDonnees().charger()["G3"]
    except (DonneeInvalideError, OSError, ValueError) as erreur:
        print("Erreur :", erreur)
        return
    fenetre = tk.Tk()
    Application(fenetre, variables, modele, notes)
    fenetre.mainloop()
