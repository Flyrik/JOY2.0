import re
from pathlib import Path
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class LocalTinyLlamaChat:
    """
    Local TinyLlama merged model wrapper (same behavior as your working test script),
    but with the correct path resolution when this file lives in: Source/Activities/llm_chat.py

    Model folder expected at:
      <PROJECT_ROOT>/Source/Models/tinyllama_empathetic_lora_v2_final_merged
    """

    def __init__(
        self,
        history_size: int = 4,
        max_input_tokens: int = 512,
        max_new_tokens: int = 80,
        temperature: float = 0.6,
        top_p: float = 0.9,
        repetition_penalty: float = 1.15,
        no_repeat_ngram_size: int = 3,
    ):
        # ✅ FIX: this file is in Source/Activities, so go up to project root:
        # .../Source/Activities/llm_chat.py -> parents[0]=Activities, [1]=Source, [2]=Project root
        project_root = Path(__file__).resolve().parents[2]

        self.model_dir = project_root / "Source" / "Models" / "tinyllama_empathetic_lora_v2_final_merged"
        if not self.model_dir.exists():
            raise FileNotFoundError(f"Model folder not found: {self.model_dir}")

        self.history_size = history_size
        self.max_input_tokens = max_input_tokens
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.repetition_penalty = repetition_penalty
        self.no_repeat_ngram_size = no_repeat_ngram_size

        self.history = []  # list of (role, text) where role in {"user","assistant"}

        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_dir), use_fast=True)
        self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            str(self.model_dir),
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto",
        )
        self.model.eval()

    def reset(self):
        self.history.clear()

    @staticmethod
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

    def build_prompt(self, user_msg: str) -> str:
        # Keep the same TinyLlama chat format
        prompt = (
            "<|system|>\n"
            "You are a kind and empathetic assistant.\n"
            "Rules: Reply in 1-3 short sentences. No HTML. No stories. Stay on the user's last message.\n"
        )

        for role, msg in self.history[-self.history_size:]:
            if role == "user":
                prompt += f"<|user|>\n{msg}\n"
            else:
                prompt += f"<|assistant|>\n{msg}\n"

        prompt += f"<|user|>\n{user_msg}\n<|assistant|>\n"
        return prompt

    def reply(self, user_msg: str) -> str:
        prompt = self.build_prompt(user_msg)

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_input_tokens,
        ).to(self.model.device)

        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=True,
                temperature=self.temperature,
                top_p=self.top_p,
                repetition_penalty=self.repetition_penalty,
                no_repeat_ngram_size=self.no_repeat_ngram_size,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        # Decode ONLY newly generated tokens
        prompt_len = inputs["input_ids"].shape[-1]
        new_tokens = out[0][prompt_len:]
        decoded = self.tokenizer.decode(new_tokens, skip_special_tokens=True)

        decoded = self.clean_and_cut(decoded)

        if not decoded:
            decoded = "Hi! How are you feeling today?"

        self.history.append(("user", user_msg))
        self.history.append(("assistant", decoded))
        return decoded
