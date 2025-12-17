import os
import json
import random
import re
from moviepy.editor import VideoFileClip
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================
VIDEO_FILE = "video_keo.mp4"
AUDIO_FILE = "audio.mp3"
API_KEY = os.getenv("GROQ_API_KEY")

NUM_CLIPS = 6
MIN_CLIP_DURATION = 15
MAX_CLIP_DURATION = 80
MAX_RETRY_ATTEMPTS = 2  # Nombre de relances maximum

if not (2 <= NUM_CLIPS <= 10):
    raise ValueError("NUM_CLIPS doit être entre 2 et 10")

print("""
==============================
   SCRIPT DECOUPE TIKTOK IA   
==============================
""")

# ============================================================
# UTILITAIRE : EXTRAIRE JSON
# ============================================================
def extract_json(text):
    """Tente d'extraire un JSON valide dans la réponse LLM."""
    # Bloc ```json ... ```
    match = re.search(r"```json(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Bloc ``` ... ``` (sans spécifier json)
    match = re.search(r"```(.*?)```", text, re.DOTALL)
    if match:
        content = match.group(1).strip()
        # Enlever le mot "json" s'il est au début
        if content.startswith("json"):
            content = content[4:].strip()
        return content

    # JSON brut (tableau)
    match = re.search(r"(\[\s*\{.*?\}\s*\])", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Essayer de parser directement si ça commence par [
    text_stripped = text.strip()
    if text_stripped.startswith("[") and text_stripped.endswith("]"):
        return text_stripped

    raise ValueError("Aucun JSON valide trouvé dans la réponse IA.")


# ============================================================
# FONCTION PRINCIPALE (AVEC RELANCE)
# ============================================================
def process_video_clips(attempt_number=1):
    """Traite la vidéo et retourne le nombre de clips générés."""
    
    print(f"\n{'='*50}")
    print(f"   TENTATIVE {attempt_number}/{MAX_RETRY_ATTEMPTS + 1}")
    print(f"{'='*50}\n")
    
    # ============================================================
    # 1️⃣ EXTRACTION AUDIO
    # ============================================================
    print("[1/4] Extraction de l'audio...")

    video = VideoFileClip(VIDEO_FILE)
    video.audio.write_audiofile(AUDIO_FILE)

    print("Audio exporté ✔️")
    print("\n--- INFO VIDEO ---")
    print(f"Durée : {video.duration:.2f} sec")
    print(f"Résolution : {video.w}x{video.h}\n")


    # ============================================================
    # 2️⃣ TRANSCRIPTION AVEC WHISPER (GROQ)
    # ============================================================
    print("[2/4] Transcription de l'audio...")

    client = Groq(api_key=API_KEY)

    with open(AUDIO_FILE, "rb") as f:
        transcription = client.audio.transcriptions.create(
            file=("audio.mp3", f.read()),
            model="whisper-large-v3",
            temperature=0,
            response_format="verbose_json"
        )

    segments = transcription.segments
    full_text = transcription.text

    print(f"\n{len(segments)} segments trouvés ✔️")
    print(full_text[:300] + "...\n")

    # Créer un JSON avec timestamps pour l'IA
    segments_with_time = []
    for seg in segments:
        segments_with_time.append({
            "start": seg["start"],
            "end": seg["end"],
            "text": seg["text"]
        })


    # ============================================================
    # 3️⃣ ANALYSE IA DES PASSAGES VIRAL
    # ============================================================
    print("[3/4] Analyse IA des passages viraux...")

    # Créer une version formatée de la transcription avec timestamps
    formatted_transcript = ""
    for i, seg in enumerate(segments_with_time):
        formatted_transcript += f"[{seg['start']:.2f}s → {seg['end']:.2f}s] {seg['text']}\n"

    prompt = f"""
You are an elite TikTok virality expert. From the transcript below, extract EXACTLY {NUM_CLIPS} clips that are ALL viral, emotionally powerful, controversial, or socially impactful. At least one clip MUST be longer than 60 seconds.

TRANSCRIPTION WITH TIMESTAMPS:
{formatted_transcript}

RULES — ZERO EXCEPTIONS:
1) Duration: ALL clips MUST be {MIN_CLIP_DURATION}-{MAX_CLIP_DURATION}s. At least one >60s. No approximation or fake timestamps.
2) Structure: Start/end on full sentences, no mid-sentence cuts, coherent text.
3) Timestamps: Only exact transcript timestamps. No inventions, no rounding.
4) No Overlap: Clips MUST be chronological and never share the same seconds.
5) Diversity: Each clip MUST cover a COMPLETELY DIFFERENT topic. No repeated themes.
6) Virality: Prioritize shocking, controversial, emotional, thought-provoking, or debate-triggering moments. Assign viral_score 0–100.
7) Hook: Each clip MUST contain a strong hook (surprising idea, emotional punch, controversial statement).
8) Output: STRICT JSON ONLY: [{{"start_time":..., "end_time":..., "text":"...", "viral_score":..., "topic":"unique", "reason":"why viral"}}]. No comments, no markdown, EXACTLY {NUM_CLIPS} valid clips.

If ANY clip violates ANY rule, regenerate internally until ALL {NUM_CLIPS} clips are valid.
"""

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=1,
        max_completion_tokens=30000
    )

    response_text = completion.choices[0].message.content

    print("\n--- RETOUR IA (RAW) ---")
    print(response_text[:500] + "...\n")

    try:
        clean_json = extract_json(response_text)
        print("--- JSON EXTRAIT ---")
        print(clean_json[:300] + "...\n")
        viral_passages = json.loads(clean_json)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON : {e}")
        print("Contenu problématique :")
        print(clean_json[:500])
        raise
    except ValueError as e:
        print(f"❌ {e}")
        print("Réponse complète de l'IA :")
        print(response_text)
        raise

    # Validation et tri des passages
    valid_passages = []
    for passage in viral_passages:
        start = passage.get("start_time")
        end = passage.get("end_time")
        
        if start is None or end is None:
            print(f"⚠️ Passage ignoré : timestamps manquants")
            continue
        
        duration = end - start
        
        if duration < MIN_CLIP_DURATION:
            print(f"⚠️ Passage ignoré : trop court ({duration:.1f}s)")
            continue
        
        if duration > MAX_CLIP_DURATION:
            print(f"⚠️ Passage ignoré : trop long ({duration:.1f}s)")
            continue
        
        valid_passages.append(passage)

    # Trier par score de viralité décroissant
    valid_passages.sort(key=lambda x: x.get("viral_score", 0), reverse=True)

    # Garder seulement NUM_CLIPS passages
    viral_passages = valid_passages[:NUM_CLIPS]

    print(f"Analyse IA terminée ✔️ ({len(viral_passages)} clips valides)\n")


    # ============================================================
    # 4️⃣ DÉCOUPE FINALE AVEC TIMESTAMPS DIRECTS
    # ============================================================

    print("[4/4] Découpe finale TikTok...\n")

    clips_generated = 0

    for i, passage in enumerate(viral_passages):
        start_time = passage["start_time"]
        end_time = passage["end_time"]
        text = passage["text"]
        score = passage.get("viral_score", 0)
        reason = passage.get("reason", "N/A")
        
        duration = end_time - start_time

        print(f"\n--- Clip {i+1}/{len(viral_passages)} ---")
        print(f"Texte : {text[:100]}...")
        print(f"Start = {start_time:.2f}s | End = {end_time:.2f}s | Durée = {duration:.2f}s")
        print(f"Viralité = {score}/100 | Raison : {reason}")

        # Vérifier que les timestamps sont dans la durée de la vidéo
        if start_time < 0 or end_time > video.duration:
            print(f"⚠️ Timestamps hors limites → ignoré.")
            continue

        if duration < MIN_CLIP_DURATION or duration > MAX_CLIP_DURATION:
            print(f"⚠️ Clip hors durée ({duration:.2f}s) → ignoré.")
            continue

        clip = video.subclip(start_time, end_time)

        # Format TikTok 720x1280
        clip = clip.resize(height=1280)
        clip = clip.crop(
            width=720,
            height=1280,
            x_center=clip.w / 2,
            y_center=clip.h / 2
        )

        output_file = f"clip_tiktok_{i+1}_score{score}.mp4"
        print(f"Export en cours → {output_file}")

        clip.write_videofile(
            output_file,
            fps=30,
            codec="libx264",
            audio_codec="aac"
        )
        
        clips_generated += 1

    # Fermer la vidéo
    video.close()
    
    return clips_generated


# ============================================================
# BOUCLE DE RELANCE SI MOINS DE 3 CLIPS
# ============================================================
try:
    attempt = 1
    clips_count = 0
    
    while attempt <= MAX_RETRY_ATTEMPTS + 1:
        clips_count = process_video_clips(attempt)
        
        print(f"\n{'='*50}")
        print(f"   RÉSULTAT : {clips_count} clips générés")
        print(f"{'='*50}\n")
        
        if clips_count >= 3:
            print("✅ Objectif atteint : au moins 3 clips générés !")
            break
        else:
            if attempt < MAX_RETRY_ATTEMPTS + 1:
                print(f"⚠️ Seulement {clips_count} clip(s) généré(s).")
                print(f"🔄 Relance automatique (tentative {attempt + 1}/{MAX_RETRY_ATTEMPTS + 1})...\n")
                attempt += 1
            else:
                print(f"❌ Échec : seulement {clips_count} clip(s) après {MAX_RETRY_ATTEMPTS + 1} tentatives.")
                break

    print("\n====================================")
    print(f"  ✅ Processus terminé : {clips_count} clips TikTok générés !")
    print("====================================")

finally:
    # Suppression du fichier audio
    if os.path.exists(AUDIO_FILE):
        try:
            os.remove(AUDIO_FILE)
            print(f"\n🗑️ Fichier audio '{AUDIO_FILE}' supprimé avec succès.")
        except Exception as e:
            print(f"\n⚠️ Impossible de supprimer '{AUDIO_FILE}' : {e}")
    else:
        print(f"\n⚠️ Fichier audio '{AUDIO_FILE}' introuvable (déjà supprimé ou jamais créé).")