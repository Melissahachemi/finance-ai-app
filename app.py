import pandas as pd

# 1. On charge le fichier CSV "sale" dans Python
df = pd.read_csv("depenses.csv")

# 2. On demande à Python de nous l'afficher dans le terminal
print("--- VOICI NOTRE FICHIER DE BASE ---")
print(df)