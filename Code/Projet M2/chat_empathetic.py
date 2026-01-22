from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Chemin vers TON meilleur checkpoint (avec model.safetensors, config.json, etc.)
CHECKPOINT_DIR = "empathetic_model/checkpoint-625"

# 1) Charger le tokenizer du modèle de base
BASE_MODEL_NAME = "microsoft/DialoGPT-small"
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME)

# 2) Charger directement le modèle fine-tuné depuis le checkpoint
model = AutoModelForCausalLM.from_pretrained(CHECKPOINT_DIR)
 
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

def generate_reply(user_text: str, max_new_tokens: int = 80) -> str:
    # Format identique à l'entraînement : "User: ... \nBot:"
    formatted_input = f"User: {user_text}\nBot:"
    
    # On encode l'entrée de l'utilisateur avec un attention_mask explicite
    enc = tokenizer(
        formatted_input,
        return_tensors="pt"
    )
    input_ids = enc["input_ids"].to(device)
    attention_mask = enc["attention_mask"].to(device)

    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            min_new_tokens=10,              # forcer des réponses plus longues
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id,
            do_sample=True,
            top_p=0.95,                     # nucleus sampling plus large
            top_k=50,                       # limiter aux 50 meilleurs tokens
            temperature=0.7,                # température plus basse = plus cohérent
            repetition_penalty=1.2,         # pénalité répétition plus forte
            no_repeat_ngram_size=2          # éviter les répétitions de 2-grams
        )

    # Décoder la réponse complète
    full_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    
    # Extraire seulement la partie après "Bot:"
    if "Bot:" in full_text:
        reply = full_text.split("Bot:")[-1].strip()
    else:
        # Fallback : prendre seulement la partie générée
        generated_ids = output_ids[0, input_ids.shape[1]:]
        reply = tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
    
    # Nettoyage
    reply = reply.replace("_comma_", ",")
    reply = reply.replace("  ", " ")
    
    # Si réponse vide ou trop courte, réponse par défaut
    if len(reply) < 5:
        reply = "I'm here to listen. Can you tell me more about how you're feeling?"

    return reply

if __name__ == "__main__":
    print("Chat empathique (tape 'quit' pour sortir)")
    while True:
        user_text = input("Vous: ")
        if user_text.lower() in {"quit", "exit"}:
            break
        bot_reply = generate_reply(user_text)
        print("Bot:", bot_reply)