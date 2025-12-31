import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import joblib

# --- Charger les données ---
train = pd.read_csv(
    "C:\\Users\\flori\\Desktop\\JOY2.0\\Code\\Projet M2\\empatheticdialogues\\train.csv",
    engine='python',
    on_bad_lines='skip'
)
valid = pd.read_csv(
    "C:\\Users\\flori\\Desktop\\JOY2.0\\Code\\Projet M2\\empatheticdialogues\\valid.csv",
    engine='python',
    on_bad_lines='skip'
)
test = pd.read_csv(
    "C:\\Users\\flori\\Desktop\\JOY2.0\\Code\\Projet M2\\empatheticdialogues\\test.csv",
    engine='python',
    on_bad_lines='skip'
)

X_train, y_train = train['utterance'], train['selfeval']
X_valid, y_valid = valid['utterance'], valid['selfeval']
X_test,  y_test  = test['utterance'], test['selfeval']

# --- Nettoyer les labels (extraire le score final) ---
# --- Nettoyer les labels (extraire le score final) ---
y_train_clean = y_train.str.extract(r'(\d)$')[0]  # peut contenir NaN
y_valid_clean = y_valid.str.extract(r'(\d)$')[0]
y_test_clean  = y_test.str.extract(r'(\d)$')[0]

# Supprimer les lignes où on n'a pas de chiffre
train = train[y_train_clean.notna()]
valid = valid[y_valid_clean.notna()]
test  = test[y_test_clean.notna()]

# Recalculer X et y après filtrage
X_train, y_train_clean = train['utterance'], y_train_clean[y_train_clean.notna()].astype(int)
X_valid, y_valid_clean = valid['utterance'], y_valid_clean[y_valid_clean.notna()].astype(int)
X_test,  y_test_clean  = test['utterance'],  y_test_clean[y_test_clean.notna()].astype(int)

print("Distribution des labels après nettoyage :")
print(y_train_clean.value_counts())

# --- TF-IDF Vectorization ---
vectorizer = TfidfVectorizer(max_features=5000)
X_train_vec = vectorizer.fit_transform(X_train)
X_valid_vec = vectorizer.transform(X_valid)
X_test_vec  = vectorizer.transform(X_test)

# --- Entraîner le modèle ---
model = LogisticRegression(max_iter=1000, class_weight='balanced')
model.fit(X_train_vec, y_train_clean)

# --- Évaluer sur validation ---
y_valid_pred = model.predict(X_valid_vec)
print("=== Validation ===")
print(classification_report(y_valid_clean, y_valid_pred))

# --- Évaluer sur test ---
y_test_pred = model.predict(X_test_vec)
print("=== Test ===")
print(classification_report(y_test_clean, y_test_pred))

# --- Sauvegarder le modèle et le vectorizer ---
#joblib.dump(model, "trained_model.pkl")
#joblib.dump(vectorizer, "vectorizer.pkl")
#print("Modèle et vectorizer sauvegardés !")
