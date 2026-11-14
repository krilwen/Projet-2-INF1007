import os
import pandas as pd
import matplotlib.pyplot as plt

CHEMIN = os.path.join("donnees", "student-por.csv")
CIBLE = "G3"

df = pd.read_csv(CHEMIN)

print("Dimensions (lignes, colonnes) :", df.shape)
print(df.head())

df.info()                      # types et valeurs non nulles
print(df.describe())           # min, max, moyenne des colonnes numériques
print(df.isna().sum())         # valeurs manquantes par colonne
print("Doublons :", df.duplicated().sum())

# Valeurs fréquentes pour chaque colonnes
for colonne in df.select_dtypes(include="object").columns:
    print(f"\n{colonne} :")
    print(df[colonne].value_counts().head(10))


# GRAPHIQUE :

plt.figure(figsize=(8, 5))
df[CIBLE].hist(bins=30)          
plt.title("Distribution de la variable cible")
plt.xlabel(CIBLE)
plt.ylabel("Nombre d'observations")
plt.savefig("exploration_cible.png")
plt.show()