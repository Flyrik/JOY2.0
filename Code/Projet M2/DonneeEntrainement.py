import re
import torch
import pandas as pd
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model

# =========================
# PATHS
# =========================
PREPARED_PATH = "empatheticdialogues_train_prepared.csv"
OUT_DIR = "/content/tinyllama_empathetic_lora_v2"

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(PREPARED_PATH, engine="python", on_bad_lines="skip")

def clean(text):
    text = str(text)
    text = text.replace("_comma_", ",")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

df["utterance"] = df["utterance"].apply(clean)
df["response"] = df["response"].apply(clean)

# =========================
# FILTER BAD RESPONSES
# =========================
df = df[df["utterance"].str.len() >= 2]
df = df[df["response"].str.len() >= 8]

# ❌ remove short question-only answers
df = df[~(
    df["response"].str.contains(r"\?$") &
    (df["response"].str.len() < 40)
)]

df = df[~df["response"].str.lower().str.startswith(
    ("why ", "what ", "how ")
)]

df = df.reset_index(drop=True)

print("✅ Pairs after filtering:", len(df))

# =========================
# ADD MANUAL COMMON CASES
# =========================
extras = [
    ("hello", "Hello 🙂 How can I help you today?"),
    ("hi", "Hi there. I'm here if you want to talk."),
    ("hey", "Hey 🙂 I'm listening."),
    ("thanks", "You're welcome. Take care 🙂"),
    ("thank you", "You're welcome. I wish you the best."),
    ("goodbye", "Goodbye. Take care of yourself."),
    ("bye", "Bye. I hope things get better for you."),
]

extra_df = pd.DataFrame(extras, columns=["utterance", "response"])
df = pd.concat([df, extra_df], ignore_index=True)

print("✅ Added common phrases")

# =========================
# MODEL
# =========================
BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=True)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="auto"
)

# =========================
# LoRA
# =========================
lora = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    task_type="CAUSAL_LM",
    bias="none",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
)

model = get_peft_model(model, lora)
model.print_trainable_parameters()

# =========================
# FORMAT CHAT
# =========================
SYSTEM_PROMPT = (
    "You are an empathetic assistant.\n"
    "Rules:\n"
    "- Do NOT ask questions unless explicitly asked.\n"
    "- Keep responses short (1 or 2 sentences).\n"
    "- Be calm, supportive, and polite.\n"
)

def format_chat(u, r):
    return (
        "<|system|>\n" + SYSTEM_PROMPT +
        "<|user|>\n" + u + "\n"
        "<|assistant|>\n" + r + tokenizer.eos_token
    )

df["text"] = df.apply(lambda x: format_chat(x["utterance"], x["response"]), axis=1)

# =========================
# DATASET
# =========================
dataset = Dataset.from_pandas(df[["text"]])
dataset = dataset.train_test_split(test_size=0.05, seed=42)

# =========================
# TOKENIZE + MASK
# =========================
def tokenize_and_mask(batch):
    enc = tokenizer(batch["text"], padding="max_length", truncation=True, max_length=256)
    labels = []
    marker = "<|assistant|>\n"

    for text, ids in zip(batch["text"], enc["input_ids"]):
        lab = ids.copy()
        idx = text.find(marker)
        prefix_ids = tokenizer(text[:idx+len(marker)], add_special_tokens=False)["input_ids"]
        for i in range(len(prefix_ids)):
            lab[i] = -100
        labels.append(lab)

    enc["labels"] = labels
    return enc

train_ds = dataset["train"].map(tokenize_and_mask, batched=True, remove_columns=["text"])
eval_ds  = dataset["test"].map(tokenize_and_mask, batched=True, remove_columns=["text"])

train_ds.set_format(type="torch")
eval_ds.set_format(type="torch")

# =========================
# TRAIN
# =========================
args = TrainingArguments(
    output_dir=OUT_DIR,
    per_device_train_batch_size=1,  # CPU = batch petit
    gradient_accumulation_steps=8,  # compense le batch
    num_train_epochs=3,
    learning_rate=1e-4,
    warmup_ratio=0.05,
    logging_steps=50,
    save_steps=500,
    fp16=False,          # CPU ne supporte pas fp16
    report_to="none",
)


trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_ds,
    eval_dataset=eval_ds,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

trainer.train()

trainer.model.save_pretrained(f"{OUT_DIR}/final_adapter")
tokenizer.save_pretrained(f"{OUT_DIR}/final_adapter")

print("✅ Training v2 finished")