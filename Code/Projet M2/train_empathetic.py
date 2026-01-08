from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
import pandas as pd

# --- Charger le CSV préparé ---
df = pd.read_csv("empatheticdialogues_train_prepared.csv")

# --- Pour test rapide : réduire le dataset à 5000 exemples ---
df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle
dataset = Dataset.from_pandas(df[:5000])  # seulement 5000 exemples pour tester

# --- Tokenizer ---
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
tokenizer.pad_token = tokenizer.eos_token  # nécessaire pour padding

def tokenize(batch):
    return tokenizer(
        batch['utterance'],
        text_target=batch['response'],
        truncation=True,
        padding='max_length',
        max_length=64  # réduire la longueur max pour accélérer
    )

dataset = dataset.map(tokenize, batched=True)
dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])

# --- Modèle ---
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")

# --- Arguments d'entraînement ---
training_args = TrainingArguments(
    output_dir="./empathetic_model",
    per_device_train_batch_size=4,  # augmenter si tu as plus de RAM
    num_train_epochs=1,  # 1 epoch pour tester rapidement
    save_steps=500,
    save_total_limit=2,
    logging_steps=100,
    fp16=False,  # CPU → pas utile
    report_to=None  # désactive wandb/tensorboard pour gagner du temps
)

# --- Trainer ---
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset
)

# --- Lancer l'entraînement ---
trainer.train()
