from typing import List, Dict, Tuple
import os
from .transcription import transcribe_audio
from .scene_detection import detect_scenes
from .ai_analysis import calculate_viral_score_heuristic, detect_hooks, suggest_emojis, shorten_subtitle
from .face_detection import detect_faces_in_video, analyze_emotions, get_optimal_crop_box
from .ffmpeg_utils import extract_audio, get_video_info, cut_video_segment, resize_to_vertical, add_watermark
from .video_effects import add_subtitles_to_video, crop_to_face

class VideoProcessor:
    def __init__(self, video_path: str, temp_dir: str = "./storage/temp"):
        self.video_path = video_path
        self.temp_dir = temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        
        self.video_info = None
        self.audio_path = None
        self.transcript = None
        self.scenes = None
        self.faces = None
        self.clips = []
    
    def process(self) -> List[Dict]:
        """Full video processing pipeline - 100% FREE"""
        
        # Step 1: Get video info
        print("Getting video info...")
        self.video_info = get_video_info(self.video_path)
        
        # Step 2: Extract audio
        print("Extracting audio...")
        self.audio_path = extract_audio(
            self.video_path,
            os.path.join(self.temp_dir, "audio.wav")
        )
        
        # Step 3: Transcribe
        print("Transcribing audio...")
        self.transcript = transcribe_audio(self.audio_path)
        
        # Step 4: Detect scenes
        print("Detecting scenes...")
        self.scenes = detect_scenes(self.video_path)
        
        # Step 5: Detect faces (optional, can be slow)
        print("Detecting faces...")
        try:
            self.faces = detect_faces_in_video(self.video_path)
        except Exception as e:
            print(f"Face detection skipped: {e}")
            self.faces = []
        
        # Step 6: Identify viral moments using FREE heuristic analysis
        print("Identifying viral moments (FREE analysis)...")
        self.clips = self.identify_viral_clips()
        
        return self.clips
    
    def identify_viral_clips(self, min_duration: float = 15, max_duration: float = 60) -> List[Dict]:
        """Identify potential viral clips from transcript using FREE heuristic analysis"""
        
        clips = []
        
        # Detect hooks first using pattern matching
        hooks = detect_hooks(self.transcript)
        
        # Create clips around hooks
        for hook in hooks:
            segment_idx = hook['segment_index']
            
            # Extend clip duration
            start_idx = max(0, segment_idx - 1)
            end_idx = min(len(self.transcript) - 1, segment_idx + 3)
            
            start_time = self.transcript[start_idx]['start']
            end_time = self.transcript[end_idx]['end']
            duration = end_time - start_time
            
            # Ensure duration constraints
            if duration < min_duration:
                end_time = min(start_time + max_duration, self.video_info['duration'])
            elif duration > max_duration:
                end_time = start_time + max_duration
            
            # Get transcript segment
            transcript_text = ' '.join([
                seg['text'] for seg in self.transcript[start_idx:end_idx+1]
            ])
            
            # Calculate viral score using FREE heuristic analysis
            viral_score = calculate_viral_score_heuristic(transcript_text)
            
            clips.append({
                'start_time': start_time,
                'end_time': end_time,
                'duration': end_time - start_time,
                'transcript': transcript_text,
                'viral_score': viral_score,
                'hook_type': hook['type']
            })
        
        # Sort by viral score
        clips.sort(key=lambda x: x['viral_score'], reverse=True)
        
        # Return top clips
        return clips[:10]
    
    def generate_clip(
        self,
        clip_data: Dict,
        output_path: str,
        style: str = "simple",
        add_watermark_flag: bool = False
    ) -> str:
        """Generate final clip with effects"""
        
        temp_clip = os.path.join(self.temp_dir, f"temp_clip_{os.path.basename(output_path)}")
        temp_resized = os.path.join(self.temp_dir, f"temp_resized_{os.path.basename(output_path)}")
        temp_subtitled = os.path.join(self.temp_dir, f"temp_subtitled_{os.path.basename(output_path)}")
        
        # Step 1: Cut segment
        print(f"Cutting clip from {clip_data['start_time']} to {clip_data['end_time']}...")
        cut_video_segment(
            self.video_path,
            temp_clip,
            clip_data['start_time'],
            clip_data['end_time']
        )
        
        # Step 2: Auto-reframe to 9:16
        print("Reframing to 9:16...")
        if self.faces:
            # Face-tracking crop
            crop_box = get_optimal_crop_box(self.faces, (self.video_info['width'], self.video_info['height']))
            crop_to_face(temp_clip, temp_resized, crop_box)
        else:
            # Simple resize
            resize_to_vertical(temp_clip, temp_resized)
        
        # Step 3: Prepare subtitles
        print("Adding subtitles...")
        subtitles = self.prepare_subtitles(clip_data)
        
        # Step 4: Add subtitles
        add_subtitles_to_video(temp_resized, temp_subtitled, subtitles, style)
        
        # Step 5: Add watermark if needed
        if add_watermark_flag:
            print("Adding watermark...")
            add_watermark(temp_subtitled, output_path)
        else:
            os.rename(temp_subtitled, output_path)
        
        # Cleanup temp files
        for temp_file in [temp_clip, temp_resized, temp_subtitled]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        return output_path
    
    def prepare_subtitles(self, clip_data: Dict) -> List[Dict]:
        """Prepare subtitles for clip using FREE emoji suggestion"""
        
        start_time = clip_data['start_time']
        end_time = clip_data['end_time']
        
        # Filter transcript segments within clip timeframe
        clip_segments = [
            seg for seg in self.transcript
            if seg['start'] >= start_time and seg['end'] <= end_time
        ]
        
        # Adjust timestamps to clip start
        subtitles = []
        for seg in clip_segments:
            text = shorten_subtitle(seg['text'])
            emojis = suggest_emojis(text)  # FREE emoji suggestion
            
            if emojis:
                text = f"{text} {' '.join(emojis)}"
            
            subtitles.append({
                'start': seg['start'] - start_time,
                'end': seg['end'] - start_time,
                'text': text
            })
        
        return subtitles
