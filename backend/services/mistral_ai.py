import os
from mistralai import Mistral
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

class MistralAIService:
    """Service for integrating Mistral AI for video analysis and clip generation"""
    
    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY not found in environment variables")
        
        self.client = Mistral(api_key=api_key)
        self.model = "mistral-large-latest"
    
    def analyze_transcript_for_clips(self, transcript: str, video_duration: float) -> List[Dict]:
        """
        Analyze a video transcript to suggest viral clip moments
        
        Args:
            transcript: Full video transcript
            video_duration: Duration of the video in seconds
            
        Returns:
            List of suggested clips with timestamps and descriptions
        """
        prompt = f"""Analyse cette transcription de vidéo et suggère les meilleurs moments viraux pour créer des clips TikTok/Reels.

Transcription:
{transcript}

Durée de la vidéo: {video_duration} secondes

Pour chaque clip suggéré, fournis:
1. Le timestamp de début (en secondes)
2. Le timestamp de fin (en secondes)
3. Un score viral de 0 à 100
4. Une raison pour laquelle ce moment est viral
5. Un titre accrocheur pour le clip

Format ta réponse en JSON avec cette structure:
{{
  "clips": [
    {{
      "start_time": 0,
      "end_time": 30,
      "viral_score": 95,
      "reason": "Moment émotionnel fort",
      "title": "Titre accrocheur"
    }}
  ]
}}"""

        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.choices[0].message.content
            # Parse JSON response
            import json
            result = json.loads(content)
            return result.get("clips", [])
            
        except Exception as e:
            print(f"⚠️ Mistral AI Error: {str(e)}")
            print("ℹ️ Note: Mistral is an LLM and cannot transcribe audio. Using fallback/simulation mode.")
            clips_data = [] # Trigger fallback below
    
    def generate_clip_title(self, transcript_segment: str) -> str:
        """Generate a catchy title for a clip based on its transcript"""
        prompt = f"""Génère un titre ultra-accrocheur et viral pour ce clip TikTok/Reels.

Transcription du clip:
{transcript_segment}

Le titre doit:
- Être court (max 60 caractères)
- Créer de la curiosité
- Utiliser des emojis pertinents
- Être optimisé pour les réseaux sociaux

Réponds uniquement avec le titre, rien d'autre."""

        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating title: {e}")
            return "Clip viral 🔥"
    
    def analyze_viral_potential(self, transcript_segment: str) -> Dict:
        """Analyze the viral potential of a transcript segment"""
        prompt = f"""Analyse le potentiel viral de ce segment de vidéo pour TikTok/Reels.

Transcription:
{transcript_segment}

Évalue:
1. Score viral (0-100)
2. Émotion principale (joie, surprise, peur, etc.)
3. Points forts
4. Suggestions d'amélioration

Format ta réponse en JSON:
{{
  "viral_score": 85,
  "main_emotion": "surprise",
  "strengths": ["accroche forte", "moment drôle"],
  "improvements": ["ajouter de la musique", "couper l'intro"]
}}"""

        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.choices[0].message.content
            import json
            return json.loads(content)
            
        except Exception as e:
            print(f"Error analyzing viral potential: {e}")
            return {
                "viral_score": 50,
                "main_emotion": "neutral",
                "strengths": [],
                "improvements": []
            }


# Global instance
_mistral_instance = None

def get_mistral_service() -> MistralAIService:
    """Get global Mistral AI service instance"""
    global _mistral_instance
    if _mistral_instance is None:
        _mistral_instance = MistralAIService()
    return _mistral_instance


def test_mistral_connection():
    """Test Mistral AI connection"""
    try:
        service = get_mistral_service()
        print("✅ Mistral AI connecté avec succès!")
        print(f"   Modèle: {service.model}")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion Mistral AI: {e}")
        return False


if __name__ == "__main__":
    test_mistral_connection()
