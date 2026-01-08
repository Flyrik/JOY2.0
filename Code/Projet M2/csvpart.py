import pandas as pd

# Charger le CSV original
df = pd.read_csv(
    "C:/Users/flori/Desktop/JOY2.0/Code/Projet M2/empatheticdialogues/train.csv",
    engine="python",
    on_bad_lines="skip",
    sep=','
)

# Trier par conversation et par ordre d'utterance
df = df.sort_values(by=['conv_id', 'utterance_idx'])

# Créer la colonne response comme l'utterance suivante dans la même conversation
df['response'] = df.groupby('conv_id')['utterance'].shift(-1)

# Supprimer les lignes qui n'ont pas de réponse
df = df.dropna(subset=['response'])

# Garder seulement ce qui est nécessaire
df = df[['utterance', 'response']]

# Sauvegarder un CSV prêt pour l'entraînement
df.to_csv("empatheticdialogues_train_prepared.csv", index=False)
print(df.head())
