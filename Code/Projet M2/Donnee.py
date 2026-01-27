import pandas as pd

RAW_PATH = "empatheticdialogues/train.csv"
OUT_PATH = "empatheticdialogues_train_prepared.csv"

df = pd.read_csv(RAW_PATH, engine="python", on_bad_lines="skip")
df = df.sort_values(["conv_id", "utterance_idx"]).reset_index(drop=True)

pairs = []

for conv_id, g in df.groupby("conv_id"):
    g = g.sort_values("utterance_idx").reset_index(drop=True)

    for i in range(len(g) - 1):
        u = str(g.loc[i, "utterance"]).strip()
        r = str(g.loc[i + 1, "utterance"]).strip()

        if u and r:
            pairs.append((u, r))

prepared = pd.DataFrame(pairs, columns=["utterance", "response"])
prepared.to_csv(OUT_PATH, index=False)

print("✅ Prepared file saved:", OUT_PATH)
print("✅ Nb pairs:", len(prepared))

prepared.head()