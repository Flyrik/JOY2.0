import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Charger les données
data = pd.read_csv(
    "C:\\Users\\flori\\Desktop\\JOY2.0\\Code\\Projet M2\\empatheticdialogues\\train.csv",
    engine="python",
    on_bad_lines="skip"
)

# Trier par dialogue et tour
data = data.sort_values(["conv_id", "utterance_idx"])

pairs = []

for i in range(len(data) - 1):
    row = data.iloc[i]
    next_row = data.iloc[i + 1]

    # utilisateur → listener
    if row["speaker_idx"] == 0 and next_row["speaker_idx"] == 1:
        pairs.append({
            "input": row["utterance"],
            "response": next_row["utterance"]
        })

pairs_df = pd.DataFrame(pairs)
print(pairs_df.head())
