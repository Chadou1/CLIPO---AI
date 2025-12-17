from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
from typing import List, Dict
import os

def create_subtitle_clip(text: str, duration: float, size: tuple = (1080, 1920)) -> TextClip:
    """Create a styled subtitle clip TikTok-style"""
    
    return TextClip(
        text,
        fontsize=60,
        color='white',
        font='Arial-Bold',
        stroke_color='black',
        stroke_width=3,
        method='caption',
        size=(size[0] - 100, None),
        align='center'
    ).set_duration(duration)

def add_subtitles_to_video(
    video_path: str,
    output_path: str,
    subtitles: List[Dict],
    style: str = "simple"
) -> str:
    """Add animated subtitles to video"""
    
    video = VideoFileClip(video_path)
    subtitle_clips = []
    
    for subtitle in subtitles:
        start_time = subtitle['start']
        duration = subtitle['end'] - subtitle['start']
        text = subtitle['text']
        
        # Create subtitle clip
        txt_clip = create_subtitle_clip(text, duration, video.size)
        
        # Position at bottom center
        txt_clip = txt_clip.set_position(('center', video.size[1] - 300))
        txt_clip = txt_clip.set_start(start_time)
        
        subtitle_clips.append(txt_clip)
    
    # Composite video with subtitles
    final_video = CompositeVideoClip([video] + subtitle_clips)
    
    final_video.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        fps=video.fps,
        preset='medium'
    )
    
    video.close()
    final_video.close()
    
    return output_path

def apply_zoom_effect(video_path: str, output_path: str) -> str:
    """Apply zoom in/out effect"""
    
    video = VideoFileClip(video_path)
    
    # Simple zoom in effect
    zoomed = video.resize(lambda t: 1 + 0.1 * (t / video.duration))
    
    zoomed.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac',
        fps=video.fps
    )
    
    video.close()
    zoomed.close()
    
    return output_path

def crop_to_face(video_path: str, output_path: str, bbox: tuple = None) -> str:
    """Crop video to focus on face (9:16 auto-reframe)"""
    
    video = VideoFileClip(video_path)
    
    # If no bbox provided, use center crop
    if bbox is None:
        w, h = video.size
        target_w, target_h = 1080, 1920
        
        # Calculate center crop
        x1 = (w - target_w) // 2
        y1 = (h - target_h) // 2
        
        cropped = video.crop(x1=x1, y1=y1, width=target_w, height=target_h)
    else:
        x, y, w, h = bbox
        cropped = video.crop(x1=x, y1=y, width=w, height=h)
    
    cropped.write_videofile(
        output_path,
        codec='libx264',
        audio_codec='aac'
    )
    
    video.close()
    cropped.close()
    
    return output_path
