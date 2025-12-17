from deepface import DeepFace
import cv2
import numpy as np
from typing import List, Dict, Tuple

def detect_faces_in_video(video_path: str, sample_rate: int = 30) -> List[Dict]:
    """Detect faces in video frames"""
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    faces_data = []
    frame_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Sample frames
        if frame_count % sample_rate == 0:
            try:
                # Detect faces
                faces = DeepFace.extract_faces(
                    img_path=frame,
                    detector_backend='opencv',
                    enforce_detection=False
                )
                
                timestamp = frame_count / fps
                
                for face in faces:
                    face_region = face['facial_area']
                    faces_data.append({
                        'timestamp': timestamp,
                        'bbox': (face_region['x'], face_region['y'], 
                                face_region['w'], face_region['h']),
                        'confidence': face.get('confidence', 0)
                    })
            except Exception as e:
                print(f"Error detecting face at frame {frame_count}: {str(e)}")
        
        frame_count += 1
    
    cap.release()
    return faces_data

def analyze_emotions(video_path: str, timestamps: List[float]) -> List[Dict]:
    """Analyze emotions at specific timestamps"""
    
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    emotions_data = []
    
    for timestamp in timestamps:
        frame_number = int(timestamp * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        ret, frame = cap.read()
        if not ret:
            continue
        
        try:
            # Analyze emotion
            result = DeepFace.analyze(
                img_path=frame,
                actions=['emotion'],
                enforce_detection=False,
                detector_backend='opencv'
            )
            
            if result:
                emotions_data.append({
                    'timestamp': timestamp,
                    'emotions': result[0]['emotion'],
                    'dominant_emotion': result[0]['dominant_emotion']
                })
        except Exception as e:
            print(f"Error analyzing emotion at {timestamp}s: {str(e)}")
    
    cap.release()
    return emotions_data

def get_optimal_crop_box(faces_data: List[Dict], video_size: Tuple[int, int]) -> Tuple[int, int, int, int]:
    """Calculate optimal crop box for face tracking"""
    
    if not faces_data:
        # Default center crop
        w, h = video_size
        target_w, target_h = 1080, 1920
        x = (w - target_w) // 2
        y = (h - target_h) // 2
        return (x, y, target_w, target_h)
    
    # Calculate average face position
    avg_x = np.mean([f['bbox'][0] for f in faces_data])
    avg_y = np.mean([f['bbox'][1] for f in faces_data])
    avg_w = np.mean([f['bbox'][2] for f in faces_data])
    avg_h = np.mean([f['bbox'][3] for f in faces_data])
    
    # Calculate crop box centered on face
    target_w, target_h = 1080, 1920
    
    center_x = avg_x + avg_w / 2
    center_y = avg_y + avg_h / 2
    
    crop_x = max(0, int(center_x - target_w / 2))
    crop_y = max(0, int(center_y - target_h / 2))
    
    # Ensure crop box is within video bounds
    video_w, video_h = video_size
    if crop_x + target_w > video_w:
        crop_x = video_w - target_w
    if crop_y + target_h > video_h:
        crop_y = video_h - target_h
    
    return (crop_x, crop_y, target_w, target_h)
