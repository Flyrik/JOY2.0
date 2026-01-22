"""
Solution simple avec embeddings sémantiques
Trouve la meilleure réponse empathique dans ton dataset
AMÉLIORÉ : Gère le contexte de conversation
"""
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class EmpatheticChatbot:
    def __init__(self, csv_path="empatheticdialogues_train_prepared.csv"):
        print("Chargement du modèle...")
        # Modèle léger pour embeddings sémantiques
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("Chargement des données...")
        df = pd.read_csv(csv_path)
        
        # Nettoyer les artefacts
        def clean_text(text):
            if pd.isna(text):
                return ""
            return str(text).replace("_comma_", ",").strip()
        
        df["utterance"] = df["utterance"].apply(clean_text)
        df["response"] = df["response"].apply(clean_text)
        
        # Filtrer les réponses trop courtes et améliorer la qualité
        df = df[df["response"].str.len() >= 15].reset_index(drop=True)
        
        # Filtrer les réponses qui commencent par "Yes" ou "No" seuls (souvent hors contexte)
        df = df[~df["response"].str.match(r'^(Yes|No)[,\s]', case=False, na=False)].reset_index(drop=True)
        
        self.data = df
        print(f"Chargement de {len(df)} exemples...")
        
        # Encoder toutes les utterances une seule fois
        print("Encodage des données (cela peut prendre 1-2 minutes)...")
        self.utterance_embeddings = self.encoder.encode(
            df["utterance"].tolist(),
            show_progress_bar=True,
            batch_size=32
        )
        
        # Encoder aussi les réponses pour meilleure recherche
        self.response_embeddings = self.encoder.encode(
            df["response"].tolist(),
            show_progress_bar=True,
            batch_size=32
        )
        
        # Historique de conversation
        self.conversation_history = []
        
        print("✅ Prêt !\n")
    
    def reply(self, user_input: str) -> str:
        """Trouve la réponse la plus empathique en tenant compte du contexte"""
        # Ajouter à l'historique
        self.conversation_history.append(user_input)
        # Garder seulement les 3 derniers messages
        if len(self.conversation_history) > 3:
            self.conversation_history = self.conversation_history[-3:]
        
        # Créer un contexte combiné (les 2-3 derniers messages)
        context = " ".join(self.conversation_history[-2:]) if len(self.conversation_history) > 1 else user_input
        
        # Encoder le contexte complet
        context_embedding = self.encoder.encode([context])
        
        # Calculer les similarités avec les utterances
        similarities = cosine_similarity(context_embedding, self.utterance_embeddings)[0]
        
        # Prendre les top 5 candidats au lieu de juste le meilleur
        top_k = 5
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Filtrer les réponses qui ne font pas sens avec le contexte
        best_response = None
        best_score = 0
        
        for idx in top_indices:
            response = self.data.iloc[idx]["response"]
            similarity = similarities[idx]
            
            # Vérifier que la réponse ne contredit pas directement l'utilisateur
            # (évite "Yes" quand l'utilisateur dit "No")
            if self._is_response_appropriate(user_input, response):
                # Score combiné : similarité utterance + similarité réponse
                response_embedding = self.response_embeddings[idx:idx+1]
                response_similarity = cosine_similarity(context_embedding, response_embedding)[0][0]
                combined_score = similarity * 0.7 + response_similarity * 0.3
                
                if combined_score > best_score:
                    best_score = combined_score
                    best_response = response
        
        # Si on n'a rien trouvé de bon, prendre le meilleur quand même
        if best_response is None:
            best_idx = top_indices[0]
            best_response = self.data.iloc[best_idx]["response"]
            best_score = similarities[best_idx]
        
        # Si la similarité est trop faible, réponse par défaut empathique
        if best_score < 0.3:
            default_responses = [
                "I'm here to listen. Can you tell me more about how you're feeling?",
                "That sounds difficult. I'm here to support you.",
                "Thank you for sharing that with me. How can I help?",
                "I understand this is hard. What would make you feel better?"
            ]
            import random
            return random.choice(default_responses)
        
        return best_response
    
    def _is_response_appropriate(self, user_input: str, response: str) -> bool:
        """Vérifie si la réponse est appropriée au contexte"""
        user_lower = user_input.lower()
        response_lower = response.lower()
        
        # Évite les contradictions directes
        if "no" in user_lower and response_lower.startswith("yes"):
            return False
        if "yes" in user_lower and "no" in response_lower[:10]:
            return False
        
        # Évite les réponses qui répètent exactement ce que l'utilisateur vient de dire
        if len(user_lower) > 10 and user_lower[:20] in response_lower:
            return False
        
        return True
    
    def reset_conversation(self):
        """Réinitialise l'historique de conversation"""
        self.conversation_history = []


# Test
if __name__ == "__main__":
    chatbot = EmpatheticChatbot()
    
    print("="*50)
    print("Chat empathique - Tape 'quit' pour sortir, 'reset' pour réinitialiser")
    print("="*50 + "\n")
    
    while True:
        user_text = input("Vous: ")
        if user_text.lower() in {"quit", "exit"}:
            break
        if user_text.lower() == "reset":
            chatbot.reset_conversation()
            print("Conversation réinitialisée.\n")
            continue
        
        response = chatbot.reply(user_text)
        print(f"Bot: {response}\n")
