import whisper
from faster_whisper import WhisperModel
import os
from typing import List, Dict

USE_FASTER_WHISPER = True
USE_GPU = os.getenv("USE_GPU", "true").lower() == "true"

def transcribe_audio(audio_path: str) -> List[Dict]:
    """Transcribe audio using Whisper or Faster-Whisper"""
    
    if USE_FASTER_WHISPER:
        return transcribe_with_faster_whisper(audio_path)
    else:
        return transcribe_with_whisper(audio_path)

def transcribe_with_faster_whisper(audio_path: str) -> List[Dict]:
    """Transcribe using Faster-Whisper (optimized)"""
    device = "cuda" if USE_GPU else "cpu"
    compute_type = "float16" if USE_GPU else "int8"
    
    model = WhisperModel("large-v3", device=device, compute_type=compute_type)
    
    segments, info = model.transcribe(
        audio_path,
        beam_size=5,
        word_timestamps=True,
        vad_filter=True
    )
    
    transcription = []
    for segment in segments:
        transcription.append({
            'start': segment.start,
            'end': segment.end,
            'text': segment.text.strip(),
            'words': [
                {
                    'word': word.word,
                    'start': word.start,
                    'end': word.end,
                    'probability': word.probability
                }
                for word in segment.words
            ] if segment.words else []
        })
    
    return transcription

def transcribe_with_whisper(audio_path: str) -> List[Dict]:
    """Transcribe using OpenAI Whisper"""
    device = "cuda" if USE_GPU else "cpu"
    model = whisper.load_model("large-v3", device=device)
    
    result = model.transcribe(audio_path, word_timestamps=True)
    
    transcription = []
    for segment in result['segments']:
        transcription.append({
            'start': segment['start'],
            'end': segment['end'],
            'text': segment['text'].strip(),
            'words': [
                {
                    'word': word['word'],
                    'start': word['start'],
                    'end': word['end'],
                    'probability': word.get('probability', 0.0)
                }
                for word in segment.get('words', [])
            ]
        })
    
    return transcription
