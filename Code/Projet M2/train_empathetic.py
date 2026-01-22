from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling
import pandas as pd
import torch

# --- Charger le CSV préparé complet ---
df = pd.read_csv("empatheticdialogues_train_prepared.csv")

# --- NETTOYER les artefacts du CSV (_comma_ → ,) ---
def clean_text(text):
    """Remplace les artefacts par des caractères normaux"""
    if pd.isna(text):
        return ""
    text = str(text)
    text = text.replace("_comma_", ",")
    text = text.replace("  ", " ")  # espaces doubles
    return text.strip()

df["utterance"] = df["utterance"].apply(clean_text)
df["response"] = df["response"].apply(clean_text)

# --- FILTRER les données pour garder seulement les bonnes réponses ---
# Filtrer les réponses trop courtes
df = df[df["response"].str.len() >= 15].reset_index(drop=True)

# Filtrer les réponses qui commencent par "Yes" ou "No" seuls (souvent hors contexte)
df = df[~df["response"].str.match(r'^(Yes|No)[,\s]', case=False, na=False)].reset_index(drop=True)

print(f"Après filtrage : {len(df)} exemples")

# --- Tokenizer (charger AVANT de créer le format) ---
BASE_MODEL_NAME = "microsoft/DialoGPT-small"
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token  # nécessaire pour padding

# --- Format pour modèle causal : séquence complète "User: X Bot: Y" ---
# DialoGPT est un modèle causal, il apprend à prédire le token suivant
# On lui donne la séquence complète et il apprend à continuer après "Bot:"
df["text"] = "User: " + df["utterance"] + "\nBot: " + df["response"] + tokenizer.eos_token

df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle global

# --- Créer Dataset HF et split train / validation ---
dataset = Dataset.from_pandas(df[["text"]])
dataset = dataset.train_test_split(test_size=0.05, seed=42)
train_dataset = dataset["train"]
eval_dataset = dataset["test"]

def tokenize(examples):
    # Tokeniser la séquence complète
    return tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=128,
    )

train_dataset = train_dataset.map(tokenize, batched=True, remove_columns=["text"])
eval_dataset = eval_dataset.map(tokenize, batched=True, remove_columns=["text"])

# Pour un modèle causal, les labels = input_ids (on apprend à prédire le token suivant)
train_dataset = train_dataset.map(lambda x: {"labels": x["input_ids"]})
eval_dataset = eval_dataset.map(lambda x: {"labels": x["input_ids"]})

train_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])
eval_dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "labels"])

# Data collator pour le language modeling
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,  # Pas de masked LM, c'est un modèle causal
)

# --- Modèle ---
model = AutoModelForCausalLM.from_pretrained(BASE_MODEL_NAME)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# --- Arguments d'entraînement optimisés ---
training_args = TrainingArguments(
    output_dir="./empathetic_model",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,          # 3 époques pour bien apprendre
    learning_rate=1e-5,          # LR encore plus bas pour stabilité
    warmup_steps=500,
    weight_decay=0.01,
    save_steps=1000,
    eval_strategy="steps",
    eval_steps=1000,
    logging_steps=100,
    save_total_limit=3,           # Garder plus de checkpoints
    fp16=torch.cuda.is_available(),
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,
    report_to=None,
    prediction_loss_only=True,   # Pour le language modeling
)

# --- Trainer ---
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    data_collator=data_collator,
)

print("GPU dispo :", torch.cuda.is_available())
# --- Lancer l'entraînement ---
trainer.train()
