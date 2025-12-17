import ffmpeg
import os
from typing import Optional

def extract_audio(video_path: str, output_path: Optional[str] = None) -> str:
    """Extract audio from video file"""
    if output_path is None:
        output_path = video_path.rsplit('.', 1)[0] + '.wav'
    
    try:
        (
            ffmpeg
            .input(video_path)
            .output(output_path, ac=1, ar='16000', format='wav')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return output_path
    except ffmpeg.Error as e:
        raise Exception(f"Failed to extract audio: {e.stderr.decode()}")

def get_video_info(video_path: str) -> dict:
    """Get video metadata"""
    try:
        probe = ffmpeg.probe(video_path)
        video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        
        return {
            'duration': float(probe['format']['duration']),
            'width': int(video_info['width']),
            'height': int(video_info['height']),
            'fps': eval(video_info['r_frame_rate']),
            'codec': video_info['codec_name']
        }
    except Exception as e:
        raise Exception(f"Failed to get video info: {str(e)}")

def cut_video_segment(
    input_path: str,
    output_path: str,
    start_time: float,
    end_time: float
) -> str:
    """Cut a segment from video"""
    try:
        duration = end_time - start_time
        (
            ffmpeg
            .input(input_path, ss=start_time, t=duration)
            .output(output_path, codec='copy')
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return output_path
    except ffmpeg.Error as e:
        raise Exception(f"Failed to cut video: {e.stderr.decode()}")

def resize_to_vertical(
    input_path: str,
    output_path: str,
    width: int = 1080,
    height: int = 1920
) -> str:
    """Resize video to vertical 9:16 format"""
    try:
        (
            ffmpeg
            .input(input_path)
            .filter('scale', width, height, force_original_aspect_ratio='decrease')
            .filter('pad', width, height, '(ow-iw)/2', '(oh-ih)/2')
            .output(output_path, vcodec='libx264', crf=23)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return output_path
    except ffmpeg.Error as e:
        raise Exception(f"Failed to resize video: {e.stderr.decode()}")

def add_watermark(
    input_path: str,
    output_path: str,
    watermark_text: str = "ClipGenius AI"
) -> str:
    """Add watermark to video"""
    try:
        (
            ffmpeg
            .input(input_path)
            .drawtext(
                text=watermark_text,
                fontsize=30,
                fontcolor='white@0.5',
                x='(w-text_w)/2',
                y='h-th-20'
            )
            .output(output_path, vcodec='libx264', crf=23)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        return output_path
    except ffmpeg.Error as e:
        raise Exception(f"Failed to add watermark: {e.stderr.decode()}")
