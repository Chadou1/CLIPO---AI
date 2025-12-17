import os
import random
import re
import time
import gc
import logging
from typing import Optional, Tuple
import librosa
import numpy as np
from moviepy.editor import (
    VideoFileClip, concatenate_videoclips, AudioFileClip, TextClip,
    CompositeVideoClip, vfx, ImageClip
)
from scipy.signal import find_peaks
from PIL import Image, ImageDraw, ImageFont
import psutil
from yt_dlp import YoutubeDL

# Configure logging
logger = logging.getLogger(__name__)

# Environment configuration for performance
os.environ["OMP_NUM_THREADS"] = str(os.cpu_count())
os.environ["OPENBLAS_NUM_THREADS"] = str(os.cpu_count())
os.environ["MKL_NUM_THREADS"] = str(os.cpu_count())

# Patch PIL for older MoviePy versions if needed
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

class LibraryVideoGenerator:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.max_cpu_percent = 100
        self.max_ram_bytes = 8 * 1024**3  # 16 GB

    def check_resource_limits(self):
        """Monitor system resources and throttle if necessary"""
        cpu = psutil.cpu_percent(interval=0.1)
        mem = self.process.memory_info().rss
        if cpu > self.max_cpu_percent:
            time.sleep(0.1 + (cpu - self.max_cpu_percent) / 100)
        if mem > self.max_ram_bytes:
            logger.warning(f"High memory usage: {mem / 1024**3:.2f} GB")
            # We don't raise error to avoid crashing, just warn
            gc.collect()

    def download_youtube_audio(self, url: str, output_dir: str) -> str:
        """Download audio from YouTube URL"""
        os.makedirs(output_dir, exist_ok=True)

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(output_dir, "%(id)s.%(ext)s"),
            "quiet": True,
            "noplaylist": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = info.get("duration", 0)
            if duration > 10 * 60: # Limit to 10 mins
                raise ValueError("YouTube video is too long (max 10 mins).")
            
            info = ydl.extract_info(url, download=True)
            extension = info['ext']
            raw_path = os.path.join(output_dir, f"{info['id']}.{extension}")

            safe_title = re.sub(r'[\\/*?:"<>|]', "", info['title'])
            # Use a unique name to avoid conflicts
            safe_filename = f"{safe_title}_{int(time.time())}"
            downloaded_path = os.path.join(output_dir, f"{safe_filename}.{extension}")
            
            # Rename if needed, or just use raw path if rename fails
            try:
                os.rename(raw_path, downloaded_path)
            except OSError:
                downloaded_path = raw_path

        audio_path = os.path.join(output_dir, f"{safe_filename}.mp3")
        
        # Convert to MP3 using MoviePy to ensure compatibility
        try:
            audio_clip = AudioFileClip(downloaded_path)
            audio_clip.write_audiofile(audio_path, logger=None)
            audio_clip.close()
            os.remove(downloaded_path)
        except Exception as e:
            if os.path.exists(downloaded_path):
                os.remove(downloaded_path)
            raise e

        return audio_path

    def get_valid_music_file(self, music_dir: str) -> str:
        """Get a random valid music file from directory"""
        if not os.path.exists(music_dir):
            raise FileNotFoundError(f"Music directory not found: {music_dir}")
            
        files = [f for f in os.listdir(music_dir) if f.lower().endswith(('.mp3', '.wav'))]
        if not files:
            raise FileNotFoundError(f"No music files found in {music_dir}")

        for _ in range(10):
            candidate = random.choice(files)
            path = os.path.join(music_dir, candidate)
            try:
                # Test load
                librosa.load(path, sr=22050, duration=1)
                return path
            except Exception:
                continue
        raise RuntimeError("No valid music file found after 10 attempts.")

    def find_best_bass_section(self, y, sr, duration):
        """Find the section with the most bass energy"""
        self.check_resource_limits()
        hop_length = sr // 2
        samples = int(duration * sr)
        max_energy = 0
        best_start = 0
        
        # Ensure we don't go out of bounds
        if len(y) <= samples:
            return 0
            
        for i in range(0, len(y) - samples, hop_length):
            segment = y[i:i+samples]
            S = np.abs(librosa.stft(segment))
            bass_energy = S[0:20, :].mean()
            if bass_energy > max_energy:
                max_energy = bass_energy
                best_start = i / sr
            self.check_resource_limits()
        return best_start

    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        lines = []
        for paragraph in text.splitlines():
            if paragraph.strip() == "":
                lines.append("")
                continue

            words = paragraph.split()
            line = ""
            for word in words:
                test_line = f"{line} {word}".strip()
                if font.getbbox(test_line)[2] <= max_width:
                    line = test_line
                else:
                    lines.append(line)
                    line = word
            if line:
                lines.append(line)
        return "\n".join(lines)

    def create_text_clip(self, text, size, duration, font_path, font_size=48, margin=75):
        """Create a transparent image clip with text"""
        self.check_resource_limits()
        W, H = size
        
        try:
            font = ImageFont.truetype(font_path, font_size)
        except OSError:
            # Fallback to default if font fails
            logger.warning(f"Could not load font {font_path}, using default")
            font = ImageFont.load_default()

        text = text.replace(":ligne", "\n")

        wrapped_text = self.wrap_text(text, font, W - 2 * margin)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, spacing=6)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (W - text_width) // 2
        y = H // 2 + 100 # Offset from center

        # Shadow
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                draw.multiline_text((x + dx, y + dy), wrapped_text, font=font, fill="black", align="center", spacing=6)
        
        # Main text
        draw.multiline_text((x, y), wrapped_text, font=font, fill="white", align="center", spacing=6)

        np_img = np.array(img)
        clip = ImageClip(np_img).set_duration(duration)
        return clip

    def resize_and_crop_to_vertical(self, clip, target_resolution):
        """Resize and crop video to vertical aspect ratio"""
        self.check_resource_limits()
        clip = clip.resize(height=target_resolution[1])
        clip = clip.crop(x_center=clip.w / 2, width=target_resolution[0], height=target_resolution[1])
        return clip

    def apply_bw_intensity(self, clip, intensity):
        """Apply black and white filter with intensity"""
        self.check_resource_limits()
        if intensity <= 0:
            return clip
        if intensity >= 100:
            return clip.fx(vfx.blackwhite)
        
        # Intensity is 0-100, convert to 0-1
        alpha = intensity / 100.0
        bw_clip = clip.fx(vfx.blackwhite)
        
        # Composite original and BW
        return CompositeVideoClip([
            clip.set_opacity(1 - alpha),
            bw_clip.set_opacity(alpha)
        ]).set_duration(clip.duration)

    def generate_video(self, 
                      text: str, 
                      video_dir: str, 
                      music_dir: str, 
                      font_dir: str, 
                      output_dir: str,
                      fps: int = 30,
                      font_filename: str = "FUTRFW.TTF",
                      bw_intensity: int = 0,
                      speed: int = 4,
                      font_size: int = 48,
                      resolution: str = "720p") -> str:
        """
        Main generation function
        """
        
        # Determine resolution dimensions
        if resolution == "1080p":
            target_res = (1080, 1920)
        else:
            target_res = (720, 1280)
            
        font_path = os.path.join(font_dir, font_filename)
        clip_segments = []
        music = None
        final = None
        text_clip = None
        final_clip = None

        try:
            # 1. Music Selection
            # If music_dir contains a specific file (e.g. from YouTube download), use it
            # Otherwise pick random
            if os.path.isfile(music_dir): 
                music_path = music_dir
            else:
                music_path = self.get_valid_music_file(music_dir)
            
            logger.info(f"Using music: {music_path}")

            # 2. Analyze Audio
            y, sr = librosa.load(music_path, sr=22050)
            S = np.abs(librosa.stft(y))
            bass = S[0:20, :].mean(axis=0)

            base_threshold = np.mean(bass) * 1.2
            peaks, _ = find_peaks(bass, height=base_threshold, distance=sr * 0.1 // 512)
            all_beat_times = librosa.frames_to_time(peaks, sr=sr)

            # 3. Determine Duration and Section
            video_duration_range = (8, 12)
            duration = random.randint(*video_duration_range)
            
            # Ensure duration doesn't exceed audio length
            audio_duration = librosa.get_duration(y=y, sr=sr)
            if duration > audio_duration:
                duration = audio_duration - 1
                
            start_time = self.find_best_bass_section(y, sr, duration)
            
            # Load music clip
            music = AudioFileClip(music_path).subclip(start_time, start_time + duration)

            # 4. Beat Matching
            beat_times = [t for t in all_beat_times if start_time <= t <= start_time + duration]
            
            interval_min = 1.0 / speed
            filtered_beats = []
            last_beat = -10

            for t in beat_times:
                if t - last_beat >= interval_min:
                    filtered_beats.append(t)
                    last_beat = t

            # Fill in missing beats if necessary
            expected_nb_beats = int(duration * speed)
            if len(filtered_beats) < expected_nb_beats:
                missing = expected_nb_beats - len(filtered_beats)
                extra_beats = np.linspace(start_time, start_time + duration, missing + 2)[1:-1]
                combined = sorted(set(filtered_beats + list(extra_beats)))
                filtered_beats = []
                last_beat = -10
                for t in combined:
                    if t - last_beat >= interval_min:
                        filtered_beats.append(t)
                        last_beat = t

            if not filtered_beats or filtered_beats[-1] < start_time + duration:
                filtered_beats.append(start_time + duration)

            # 5. Video Assembly
            video_files = [
                f for f in os.listdir(video_dir)
                if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))
            ]
            
            if not video_files:
                raise FileNotFoundError(f"No video files found in {video_dir}")

            for i in range(len(filtered_beats) - 1):
                self.check_resource_limits()
                interval = filtered_beats[i+1] - filtered_beats[i]
                
                # Skip extremely short clips
                if interval < 0.1:
                    continue

                video_file = random.choice(video_files)
                video_path = os.path.join(video_dir, video_file)
                
                # Load clip
                clip = VideoFileClip(video_path)
                
                # Ensure clip is long enough
                if clip.duration < interval:
                    # Loop if too short
                    clip = clip.loop(duration=interval)
                else:
                    # Random start
                    max_start = clip.duration - interval
                    start = random.uniform(0, max_start)
                    clip = clip.subclip(start, start + interval)

                clip = self.resize_and_crop_to_vertical(clip, target_res)
                clip = self.apply_bw_intensity(clip, bw_intensity)
                clip = clip.set_duration(interval).set_fps(fps)
                clip_segments.append(clip)

            final_clip = concatenate_videoclips(clip_segments, method="compose")
            final_clip = final_clip.set_audio(music)
            
            # 6. Text Overlay
            text_clip = self.create_text_clip(text, target_res, final_clip.duration, font_path, font_size)
            final = CompositeVideoClip([final_clip, text_clip], size=target_res)
            final = final.set_fps(fps)
            
            # 7. Export
            output_filename = f"lib_video_{int(time.time())}_{random.randint(1000,9999)}.mp4"
            output_path = os.path.join(output_dir, output_filename)
            
            final.write_videofile(
                output_path, 
                fps=fps, 
                codec="libx264", 
                audio_codec="aac",
                threads=4,
                preset="medium" # Balance speed/quality
            )

            return output_path

        except Exception as e:
            logger.error(f"Error generating video: {e}")
            raise e
            
        finally:
            # Cleanup
            try:
                if clip_segments:
                    for clip in clip_segments:
                        clip.close()
                if final_clip:
                    final_clip.close()
                if text_clip:
                    text_clip.close()
                if final:
                    final.close()
                if music:
                    music.close()
                
                gc.collect()
            except Exception as cleanup_error:
                logger.warning(f"Cleanup error: {cleanup_error}")
