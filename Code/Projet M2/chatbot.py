import re
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# --- KEEP THIS PATH EXACTLY ---
PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_DIR = PROJECT_ROOT / "Source" / "Models" / "tinyllama_empathetic_lora_v2_final_merged"

print("[INFO] MODEL_DIR:", MODEL_DIR)
if not MODEL_DIR.exists():
    raise FileNotFoundError(f"Model folder not found: {MODEL_DIR}")

tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR), use_fast=True)
tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    str(MODEL_DIR),
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",
)
model.eval()

history = []

def clean_and_cut(text: str) -> str:
    # Cut if it starts leaking role tokens or weird artifacts
    cut_markers = ["<|user|>", "<|assistant|>", "<|system|>", "<!--"]
    for m in cut_markers:
        idx = text.find(m)
        if idx != -1:
            text = text[:idx]

    # Remove any leftover broken tag fragments
    text = re.sub(r"<\|\|.*?\|\|>", " ", text)
    text = re.sub(r"<\|\|.*?>", " ", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text

def build_prompt(user_msg: str) -> str:
    # Keep the same TinyLlama chat format
    prompt = (
        "<|system|>\n"
        "You are a kind and empathetic assistant.\n"
        "Rules: Reply in 1-3 short sentences. No HTML. No stories. Stay on the user's last message.\n"
    )

    for role, msg in history[-4:]:
        if role == "user":
            prompt += f"<|user|>\n{msg}\n"
        else:
            prompt += f"<|assistant|>\n{msg}\n"

    prompt += f"<|user|>\n{user_msg}\n<|assistant|>\n"
    return prompt

def bot_reply(user_text: str) -> str:
    prompt = build_prompt(user_text)

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(model.device)

    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=80,
            do_sample=True,
            temperature=0.6,     # slightly lower = less random nonsense
            top_p=0.9,
            repetition_penalty=1.15,
            no_repeat_ngram_size=3,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode ONLY newly generated tokens
    prompt_len = inputs["input_ids"].shape[-1]
    new_tokens = out[0][prompt_len:]
    decoded = tokenizer.decode(new_tokens, skip_special_tokens=True)

    decoded = clean_and_cut(decoded)

    if not decoded:
        decoded = "Hi! How are you feeling today?"

    history.append(("user", user_text))
    history.append(("assistant", decoded))
    return decoded


print("\n--- TinyLlama empathic chat (merged) (type 'quit' to stop, '/reset' to clear memory) ---")
while True:
    msg = input("YOU: ").strip()
    if msg.lower() in ["quit", "exit"]:
        print("BOT: Bye!")
        break
    if msg == "/reset":
        history.clear()
        print("BOT: Memory cleared.")
        continue
    if not msg:
        continue
    print("BOT:", bot_reply(msg))