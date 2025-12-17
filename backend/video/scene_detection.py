from scenedetect import detect, ContentDetector, AdaptiveDetector
from typing import List, Tuple

def detect_scenes(video_path: str, threshold: float = 27.0) -> List[Tuple[float, float]]:
    """Detect scene changes in video"""
    scene_list = detect(video_path, ContentDetector(threshold=threshold))
    
    scenes = []
    for scene in scene_list:
        start_time = scene[0].get_seconds()
        end_time = scene[1].get_seconds()
        scenes.append((start_time, end_time))
    
    return scenes

def detect_silence_breaks(audio_amplitude: List[float], threshold: float = 0.01) -> List[int]:
    """Detect silence breaks for natural clip boundaries"""
    silence_indices = []
    
    for i, amplitude in enumerate(audio_amplitude):
        if amplitude < threshold:
            silence_indices.append(i)
    
    return silence_indices
