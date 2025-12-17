import os
import json
import time
import re
import yt_dlp
import shutil
from pytubefix import YouTube
from pytubefix.cli import on_progress
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import cycle
from groq import Groq
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
from utils.file_storage import get_storage
from models.schemas import VideoStatus

from PIL import Image

# Monkey patch MoviePy resize function if PIL.Image.ANTIALIAS is missing
if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

# Configuration
# Configuration
# GROQ_API_KEY will be managed dynamically
DEFAULT_GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# API Key Rotation Logic
API_KEYS = []
API_KEY_ITERATOR = None

def load_api_keys():
    """Load API keys from environment variables"""
    global API_KEYS, API_KEY_ITERATOR
    
    loaded_keys = []
    
    # 1. Main key
    if DEFAULT_GROQ_API_KEY:
        loaded_keys.append(DEFAULT_GROQ_API_KEY)
        
    # 2. Backup keys (GROQ_API_KEY_2, _3, etc.)
    for key, value in os.environ.items():
        if key.startswith("GROQ_API_KEY_") and value:
            loaded_keys.append(value)
            
    if not loaded_keys:
        print("⚠️ No GROQ_API_KEY found in environment variables.")
        # Fallback to prevent crash, though it will likely fail later
        loaded_keys = ["missing_key"]
        
    print(f"🔑 Loaded {len(loaded_keys)} API keys from environment.")
    API_KEYS = loaded_keys
    API_KEY_ITERATOR = cycle(API_KEYS)

def get_next_api_key():
    """Get next API key from rotation"""
    global API_KEY_ITERATOR
    if API_KEY_ITERATOR is None:
        load_api_keys()
    
    key = next(API_KEY_ITERATOR)
    # Mask key for logging
    masked = key[:4] + "..." + key[-4:] if len(key) > 8 else "..."
    # print(f"🔑 Using Groq API Key: {masked}") 
    return key
MIN_CLIP_DURATION = 10  # Accept shorter clips to find more
MAX_CLIP_DURATION = 80
MAX_RETRY_ATTEMPTS = 5

def download_youtube_video(url, output_path):
    """Download YouTube video using a comprehensive 'Kitchen Sink' strategy"""
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"📥 Downloading from YouTube: {url}")
    print(f"📁 Output path: {output_path}")

    # --- PHASE 1: cookies.txt (The Nuclear Option) ---
    # If the user has provided a cookies.txt file, use it. This is the most reliable method.
    cookies_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cookies.txt")
    if os.path.exists(cookies_file):
        print(f"🍪 [Phase 1] Found cookies.txt! Using it with yt-dlp...")
        from yt_dlp import YoutubeDL
        try:
            opts = {
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
                "outtmpl": output_path,
                "quiet": False,
                "no_warnings": False,
                "cookiefile": cookies_file,
                # User-agent spoofing
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                if _handle_downloaded_file(file_path, output_path):
                    final_path = file_path if os.path.exists(file_path) else output_path
                    print(f"🎉 Download successful (cookies.txt)! Returning: {final_path}")
                    return final_path
        except Exception as e:
            print(f"⚠️ [Phase 1] cookies.txt failed: {str(e)[:100]}")

    # --- PHASE 2: Pytubefix (No Auth) ---
    # Try different clients to bypass bot detection without login
    
    # Helper to process the YouTube object
    def process_yt_object(yt_obj):
        print(f"✅ Video Title: {yt_obj.title}")
        # Get highest resolution progressive stream (usually 720p)
        stream = yt_obj.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if not stream:
            print("⚠️ No progressive stream found, trying adaptive...")
            stream = yt_obj.streams.filter(file_extension='mp4').order_by('resolution').desc().first()
        if not stream:
            raise Exception("No suitable stream found")
        print(f"⬇️ Downloading stream: {stream.resolution} ({stream.filesize / (1024*1024):.2f} MB)")
        out_file = stream.download(output_path=os.path.dirname(output_path))
        if os.path.exists(out_file):
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(out_file, output_path)
            print(f"🎉 Download successful! Returning: {output_path}")
            return output_path
        return None

    pytubefix_clients = ['ANDROID', 'IOS', 'TV', 'WEB', 'MWEB', 'TV_EMBED']
    for client in pytubefix_clients:
        print(f"🤖 [Phase 2] Trying Pytubefix Client: {client}...")
        try:
            yt = YouTube(url, client=client)
            result = process_yt_object(yt)
            if result: return result
        except Exception as e:
            print(f"⚠️ [Phase 2] Client {client} failed: {str(e)[:100]}")

    # --- PHASE 3: yt-dlp (Browser Cookies) ---
    # Try borrowing cookies from installed browsers
    print("🍪 [Phase 3] Switching to yt-dlp with browser cookies...")
    from yt_dlp import YoutubeDL

    browsers = ['chrome', 'edge', 'firefox']
    base_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": output_path,
        "quiet": False,
        "no_warnings": False,
        "nopart": False,
    }

    for browser in browsers:
        print(f"🍪 [Phase 3] Trying cookies from: {browser}...")
        try:
            opts = base_opts.copy()
            opts["cookiesfrombrowser"] = (browser,)
            
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
                
                if _handle_downloaded_file(file_path, output_path):
                    final_path = file_path if os.path.exists(file_path) else output_path
                    print(f"🎉 Download successful! Returning: {final_path}")
                    return final_path
        except Exception as e:
            print(f"⚠️ [Phase 3] Browser {browser} failed: {str(e)[:100]}")

    # --- PHASE 4: yt-dlp OAuth (Interactive) ---
    # This is the new standard fallback for when automated methods fail
    print("🔐 [Phase 4] Trying yt-dlp with OAuth2...")
    try:
        opts = base_opts.copy()
        opts["username"] = "oauth2"  # Triggers OAuth flow
        opts["password"] = ""        # Not needed for OAuth
        
        with YoutubeDL(opts) as ydl:
            print("ℹ️  Please check console for Google/YouTube login code if prompted.")
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            if _handle_downloaded_file(file_path, output_path):
                final_path = file_path if os.path.exists(file_path) else output_path
                print(f"🎉 Download successful (OAuth)! Returning: {final_path}")
                return final_path
    except Exception as e:
        print(f"❌ [Phase 4] yt-dlp OAuth failed: {str(e)[:100]}")

    # --- PHASE 5: Last Resort (Pytubefix OAuth) ---
    print("🔐 [Phase 5] All automated methods failed. Trying Pytubefix OAuth...")
    try:
        print("ℹ️ If prompted, please check the console for a Google/YouTube login code.")
        yt = YouTube(url, 'WEB', use_oauth=True, allow_oauth_cache=True)
        result = process_yt_object(yt)
        if result: return result
    except Exception as e:
        print(f"❌ [Phase 5] Pytubefix OAuth strategy failed: {e}")

    return None


def _handle_downloaded_file(file_path, output_path):
    """Helper to handle .part files and verify download success"""
    print(f"🔍 [DEBUG] Checking file_path: {file_path}")
    print(f"🔍 [DEBUG] Output_path: {output_path}")
    print(f"🔍 [DEBUG] File exists? {os.path.exists(file_path)}")
    
    # If the file doesn't exist, check for .part file (Windows lock issue)
    if not os.path.exists(file_path):
        part_file = file_path + ".part"
        if os.path.exists(part_file):
            print(f"⚠️ Fichier .part détecté, tentative de renommage manuel...")
            # Wait a bit for file handles to release
            time.sleep(2)
            try:
                # Try to rename manually
                shutil.move(part_file, file_path)
                print(f"✅ Renommage manuel réussi: {part_file} → {file_path}")
            except Exception as rename_error:
                print(f"❌ Impossible de renommer (fichier verrouillé): {rename_error}")
                # Wait longer and retry
                time.sleep(5)
                try:
                    shutil.move(part_file, file_path)
                    print(f"✅ Renommage réussi après attente: {file_path}")
                except Exception as final_error:
                    print(f"⚠️ Utilisation du fichier .part directement")
                    # Use .part file directly if rename still fails
                    file_path = part_file
    
    if os.path.exists(file_path):
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"✅ Téléchargement OK → {file_path} ({file_size_mb:.2f} MB)")
        return True
    else:
        print(f"❌ Fichier introuvable après téléchargement: {file_path}")
        # List files in directory to debug
        dir_path = os.path.dirname(file_path)
        if os.path.exists(dir_path):
            print(f"📂 [DEBUG] Files in directory {dir_path}:")
            for f in os.listdir(dir_path):
                print(f"   - {f}")
        return False

def extract_json(text):
    """Extract valid JSON from LLM response with robust error handling."""
    # Try to extract from code blocks first
    match = re.search(r"```json(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    match = re.search(r"```(.*?)```", text, re.DOTALL)
    if match:
        content = match.group(1).strip()
        if content.startswith("json"):
            content = content[4:].strip()
        return content

    # Try to find JSON array pattern
    match = re.search(r"(\[\s*\{.*?\}\s*\])", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    # Check if text is already JSON-like
    text_stripped = text.strip()
    if text_stripped.startswith("["):
        # Handle potentially truncated JSON
        if not text_stripped.endswith("]"):
            # Try to find the last complete object
            last_complete = text_stripped.rfind("}")
            if last_complete != -1:
                # Close the array properly
                text_stripped = text_stripped[:last_complete + 1] + "]"
        return text_stripped

    raise ValueError("No valid JSON found in AI response.")


### max retries == nombre de fois qu'il ra envoyer une requête à l'IA
def process_video_groq(video_id: int, video_path: str, output_folder: str, quality_settings: dict = None, clip_count: int = 16, max_retries: int = 5, plan: str = "free"):
    """
    Process video using Groq (Whisper + LLM) and MoviePy.
    Note: output_folder should be the clips directory, not uploads.
    """
    print(f"\n{'='*60}")
    print(f"🎬 Starting Groq processing for video {video_id}")
    print(f"   Requested clips: {clip_count}")
    print(f"   Quality: {quality_settings.get('resolution', '720p')} @ {quality_settings.get('fps', 30)}fps")
    print(f"{'='*60}\n")
    
    storage = get_storage()
    storage.update_video_status(video_id, VideoStatus.PROCESSING.value)

    if not quality_settings:
        quality_settings = {"resolution": "720p", "fps": 30}

    # Ensure output folder (clips directory) exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Use temp folder for audio
    temp_folder = os.path.join(os.path.dirname(output_folder), "temp")
    os.makedirs(temp_folder, exist_ok=True)
    audio_file = os.path.join(temp_folder, f"audio_{video_id}.mp3")
    
    # Validate clip count
    if not (3 <= clip_count <= 24):  # Allow up to 24 clips max
        print(f"⚠️ Invalid clip_count {clip_count}, using default 12")
        clip_count = 16
    
    video = None
    try:
        # 1. Extract Audio
        print("[1/4] Extracting audio (compressed)...")
        video = VideoFileClip(video_path)
        # Compress audio to 24k mono to avoid 25MB limit and speed up extraction
        video.audio.write_audiofile(audio_file, bitrate="24k", ffmpeg_params=["-ac", "1"], logger=None)
        
        file_size_mb = os.path.getsize(audio_file) / (1024 * 1024)
        print(f"✅ Audio extracted: {file_size_mb:.2f} MB - Video duration: {video.duration:.2f}s")
        
        storage.update_video(video_id, {"duration": video.duration})

        # 2. Transcription with Whisper (Groq)
        print("[2/4] Transcribing audio with Whisper...")
        
        # Get a rotated API key for this video processing session
        current_api_key = get_next_api_key()
        client = Groq(api_key=current_api_key)
        
        with open(audio_file, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=("audio.mp3", f.read()),
                model="whisper-large-v3",
                temperature=0,
                response_format="verbose_json"
            )
            
        segments = transcription.segments
        print(f"✅ Transcription complete - {len(segments)} segments found")
        
        # Format for AI
        segments_with_time = []
        formatted_transcript = ""
        for seg in segments:
            segments_with_time.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"]
            })
            formatted_transcript += f"[{seg['start']:.2f}s → {seg['end']:.2f}s] {seg['text']}\n"

        # 3. AI Analysis with segment-based processing
        print(f"[3/4] Analyzing viral passages (requesting {clip_count} clips)...")
        
        # Split transcript into segments if too long
        SEGMENT_SIZE = 30000  # Increased for better coverage of long videos
        transcript_segments = []
        
        if len(formatted_transcript) > SEGMENT_SIZE:
            print(f"📊 Transcript is {len(formatted_transcript)} chars, splitting into segments of {SEGMENT_SIZE} chars...")
            
            # Split by segment size
            for i in range(0, len(formatted_transcript), SEGMENT_SIZE):
                segment = formatted_transcript[i:i + SEGMENT_SIZE]
                transcript_segments.append(segment)
            
            print(f"✂️ Created {len(transcript_segments)} segments to process")
        else:
            # Single segment if transcript is short enough
            transcript_segments.append(formatted_transcript)
        
        # Accumulate all clips from all segments
        all_accumulated_clips = []
        
        # Process each segment
        for segment_idx, transcript_segment in enumerate(transcript_segments):
            print(f"\n{'='*60}")
            print(f"📝 Processing segment {segment_idx + 1}/{len(transcript_segments)}")
            print(f"{'='*60}")
            
            # Each segment gets 3 attempts for faster processing
            segment_attempts = 3
            
            for attempt in range(segment_attempts):
                if attempt > 0:
                    print(f"\n🔄 Segment {segment_idx + 1} - Retry {attempt}/{segment_attempts - 1}")
                
                # Calculate how many clips to request for this segment
                # Request MORE clips per segment to maximize discovery  
                clips_per_segment = max(30, clip_count // len(transcript_segments))  # Increased from 20 to 30

                
                prompt = f"""
You are an elite TikTok virality expert. From the transcript below, extract UP TO {clips_per_segment} clips that are viral, emotionally powerful, controversial, or socially impactful.

TRANSCRIPTION WITH TIMESTAMPS:

2) **Structure**: Start/end on full sentences, no mid-sentence cuts, coherent text
3) **Timestamps**: Use ONLY exact timestamps from the transcript above. No inventions, no rounding.
4) **No Overlap**: Clips MUST be chronological and never share the same seconds.
5) **Diversity**: Each clip MUST cover a COMPLETELY DIFFERENT topic. No repeated themes.
6) **Virality**: Prioritize shocking, controversial, emotional, thought-provoking moments. Assign viral_score 0–100.
7) **Hook**: Each clip MUST contain a strong hook (surprising idea, emotional punch, controversial statement).
8) **Output Format**: STRICT JSON ONLY - Array of objects with: start_time, end_time, text, viral_score, topic, reason
   - No markdown, no code blocks, no comments - JUST the JSON array
   - Each "reason" field must be a COMPLETE sentence explaining why this clip is viral-worthy

EXAMPLE OUTPUT FORMAT:
[
  {{"start_time": 120.5, "end_time": 145.2, "text": "Full transcript excerpt here", "viral_score": 85, "topic": "Topic Name", "reason": "Complete explanation of why this is viral-worthy."}},
  {{"start_time": 200.0, "end_time": 230.5, "text": "Another excerpt", "viral_score": 78, "topic": "Different Topic", "reason": "Another complete explanation."}}
]

Extract {clips_per_segment} high-quality viral clips. Every clip MUST be {MIN_CLIP_DURATION}-{MAX_CLIP_DURATION} seconds.
"""

                try:
                    # Rotate to next API key for each attempt to avoid rate limits
                    current_api_key = get_next_api_key()
                    client = Groq(api_key=current_api_key)
                    
                    # Use stable model with large context
                    completion = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct", 
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,  # Slightly lower for more consistency
                        max_completion_tokens=8192  # Max allowed by Groq for this model
                    )
                    
                    response_text = completion.choices[0].message.content
                    
                except Exception as api_error:
                    error_msg = str(api_error)
                    print(f"⚠️ Groq API Error (Segment {segment_idx + 1}, Attempt {attempt + 1}): {error_msg[:200]}")
                    
                    # If rate limit, try next key immediately
                    if "rate_limit" in error_msg.lower() or "429" in error_msg:
                        print("🔄 Rate limit hit, rotating to next API key...")
                        time.sleep(1)  # Brief pause
                    else:
                        time.sleep(3)  # Longer wait for other errors
                    continue
                
                try:
                    clean_json = extract_json(response_text)
                    
                    # Debug: Log the response if parsing fails later
                    try:
                        viral_passages = json.loads(clean_json)
                    except json.JSONDecodeError as json_err:
                        print(f"⚠️ JSON Parse Error: {json_err}")
                        print(f"🔍 Raw AI response (first 500 chars): {response_text[:500]}")
                        print(f"🔍 Extracted JSON (first 500 chars): {clean_json[:500]}")
                        
                        # Try multiple repair strategies
                        viral_passages = None
                        
                        # Strategy 1: Remove trailing commas
                        try:
                            clean_json_fixed = clean_json.replace(",]", "]").replace(",}", "}")
                            viral_passages = json.loads(clean_json_fixed)
                            print("✅ JSON fixed by removing trailing commas")
                        except:
                            pass
                        
                        # Strategy 2: Fix unclosed strings and objects
                        if viral_passages is None:
                            try:
                                # Find last complete object
                                last_brace = clean_json.rfind("}")
                                if last_brace != -1:
                                    # Try closing the array after last complete object
                                    clean_json_fixed = clean_json[:last_brace + 1]
                                    if not clean_json_fixed.strip().endswith("]"):
                                        clean_json_fixed += "]"
                                    # Remove trailing commas again
                                    clean_json_fixed = clean_json_fixed.replace(",]", "]").replace(",}", "}")
                                    viral_passages = json.loads(clean_json_fixed)
                                    print("✅ JSON repaired by closing incomplete structure")
                            except:
                                pass
                        
                        # Strategy 3: Try to extract individual valid objects
                        if viral_passages is None:
                            try:
                                # Find all complete objects
                                objects = re.findall(r'\{[^{}]*"start_time"[^{}]*"end_time"[^{}]*\}', clean_json)
                                if objects:
                                    viral_passages = []
                                    for obj_str in objects:
                                        try:
                                            obj = json.loads(obj_str)
                                            viral_passages.append(obj)
                                        except:
                                            continue
                                    if viral_passages:
                                        print(f"✅ Extracted {len(viral_passages)} objects individually")
                            except:
                                pass
                        
                        if viral_passages is None:
                            print("❌ Could not parse JSON even after all repair attempts, skipping this response")
                            continue
                    
                    # Validate passages
                    valid_passages = []
                    invalid_reasons = {"no_timestamps": 0, "invalid_duration": 0, "other": 0}
                    
                    for passage in viral_passages:
                        start = passage.get("start_time")
                        end = passage.get("end_time")
                        if start is None or end is None:
                            invalid_reasons["no_timestamps"] += 1
                            continue
                        
                        try:
                            start = float(start)
                            end = float(end)
                        except (ValueError, TypeError):
                            invalid_reasons["other"] += 1
                            continue
                        
                        duration = end - start
                        
                        # --- SMART CLIP EXPANSION ---
                        # If clip is too short (e.g. 5-10s), try to expand it to MIN_CLIP_DURATION
                        if 5 <= duration < MIN_CLIP_DURATION:
                            needed = MIN_CLIP_DURATION - duration
                            # Expand equally on both sides if possible
                            expand_start = needed / 2
                            expand_end = needed / 2
                            
                            # Check bounds (assuming we don't have exact video duration here easily, 
                            # but start can't be < 0. We'll be conservative)
                            new_start = max(0, start - expand_start)
                            new_end = end + expand_end
                            
                            print(f"🔧 Expanding short clip ({duration:.1f}s) to {new_end - new_start:.1f}s")
                            start = new_start
                            end = new_end
                            duration = end - start

                        if duration < MIN_CLIP_DURATION or duration > MAX_CLIP_DURATION:
                            invalid_reasons["invalid_duration"] += 1
                            continue
                        
                        passage["start_time"] = start
                        passage["end_time"] = end
                        valid_passages.append(passage)
                    
                    # Log validation stats
                    total_returned = len(viral_passages)
                    if total_returned > 0:
                        print(f"📊 AI returned {total_returned} clips, {len(valid_passages)} passed validation")
                        if len(valid_passages) < total_returned:
                            print(f"   ❌ Rejected: {invalid_reasons['no_timestamps']} no timestamps, "
                                  f"{invalid_reasons['invalid_duration']} bad duration ({MIN_CLIP_DURATION}-{MAX_CLIP_DURATION}s), "
                                  f"{invalid_reasons['other']} other")
                    else:
                        print(f"⚠️ AI returned 0 clips in JSON array")
                    
                    print(f"✅ Found {len(valid_passages)} valid clips in segment {segment_idx + 1}, attempt {attempt + 1}")
                    
                    # Add new clips to accumulated clips, avoiding duplicates/overlaps
                    new_clips_added = 0
                    for new_clip in valid_passages:
                        is_duplicate = False
                        new_start = new_clip["start_time"]
                        new_end = new_clip["end_time"]
                        
                        # Check if this clip overlaps significantly with any existing clip
                        for existing_clip in all_accumulated_clips:
                            existing_start = existing_clip["start_time"]
                            existing_end = existing_clip["end_time"]
                            
                            # Check for overlap (if clips share more than 5 seconds, consider duplicate)
                            overlap_start = max(new_start, existing_start)
                            overlap_end = min(new_end, existing_end)
                            overlap_duration = max(0, overlap_end - overlap_start)
                            
                            if overlap_duration > 5:  # More than 5 seconds overlap = duplicate
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            all_accumulated_clips.append(new_clip)
                            new_clips_added += 1
                    
                    if new_clips_added > 0:
                        print(f"➕ Added {new_clips_added} new unique clips")
                    
                    print(f"📊 Total accumulated clips so far: {len(all_accumulated_clips)}")
                        
                except (json.JSONDecodeError, ValueError) as e:
                    print(f"❌ Error parsing AI response for segment {segment_idx + 1}: {e}")
                    continue
        
        # Sort all accumulated clips by viral score and take top clip_count
        all_accumulated_clips.sort(key=lambda x: x.get("viral_score", 0), reverse=True)
        final_passages = all_accumulated_clips[:clip_count] if len(all_accumulated_clips) > clip_count else all_accumulated_clips
        
        print(f"\n{'='*60}")
        print(f"🎯 Final selection: {len(final_passages)} clips will be generated")
        print(f"{'='*60}\n")

        # 4. Cut Clips (Multi-threaded)
        print(f"\n[4/4] Cutting {len(final_passages)} clips with quality settings (multi-threaded, max 3 concurrent)...")
        
        fps = quality_settings.get("fps", 30)
        res_map = {
            "720p": (720, 1280),
            "1080p": (1080, 1920),
            "2k": (1440, 2560),
            "4k": (2160, 3840)
        }
        res_key = quality_settings.get("resolution", "720p")
        if res_key not in res_map: res_key = "720p"
        target_width, target_height = res_map[res_key]
        
        bitrate_map = {
            "720p": "2500k",
            "1080p": "5000k",
            "2k": "8000k",
            "4k": "15000k"
        }
        video_bitrate = bitrate_map.get(res_key, "2500k")

        # Detect GPU acceleration support
        def get_video_codec():
            """Detect available hardware acceleration codec"""
            try:
                # Try NVIDIA NVENC (most common for Windows/Linux)
                import subprocess
                result = subprocess.run(['ffmpeg', '-codecs'], capture_output=True, text=True, timeout=5)
                if 'h264_nvenc' in result.stdout:
                    return 'h264_nvenc', 'GPU (NVENC)'
                elif 'h264_qsv' in result.stdout:
                    return 'h264_qsv', 'GPU (Intel QSV)'
                elif 'h264_videotoolbox' in result.stdout:
                    return 'h264_videotoolbox', 'GPU (VideoToolbox)'
            except:
                pass
            return 'libx264', 'CPU'
        
        codec_to_use, acceleration_type = get_video_codec()
        print(f"🎨 Using {acceleration_type} acceleration (codec: {codec_to_use})")
        
        # Define a function to process a single clip
        def process_clip(i, passage, video_path, output_folder, video_id, plan):
            """Process a single clip - used for multi-threading"""
            try:
                start_time = passage["start_time"]
                end_time = passage["end_time"]
                
                # Open video for this thread
                clip_video = VideoFileClip(video_path)
                
                # Safety check
                if start_time < 0 or end_time > clip_video.duration:
                    clip_video.close()
                    return None
                
                print(f"✂️  [Thread {i+1}] Extracting subclip {i+1}...")
                clip = clip_video.subclip(start_time, end_time)
                
                # Resize logic for vertical crop (9:16)
                w, h = clip.size
                target_ratio = 9/16
                crop_w = h * target_ratio
                
                if crop_w > w:
                    crop_h = w / target_ratio
                    clip = clip.crop(x_center=w/2, y_center=h/2, width=w, height=crop_h)
                else:
                    clip = clip.crop(x_center=w/2, y_center=h/2, width=crop_w, height=h)
                
                clip = clip.resize(newsize=(target_width, target_height))

                # Apply watermark for free plan
                if plan == "free":
                    watermark_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "watermark.png")
                    if os.path.exists(watermark_path):
                        print(f"💧 [Thread {i+1}] Applying watermark for free user...")
                        try:
                            watermark = (ImageClip(watermark_path)
                                        .set_duration(clip.duration)
                                        .resize(width=target_width * 0.3) # 30% of width
                                        .margin(right=20, opacity=0)
                                        .set_pos(("right", "center")))
                            
                            clip = CompositeVideoClip([clip, watermark])
                        except Exception as e:
                            print(f"⚠️ [Thread {i+1}] Failed to apply watermark: {e}")
                
                output_filename = f"clip_{video_id}_{i+1}_score{passage.get('viral_score', 0)}_{int(time.time())}_{i}.mp4"
                output_path = os.path.join(output_folder, output_filename)
                
                print(f"🎬 [Thread {i+1}] Writing video file...")
                
                # Try GPU encoding first, fallback to CPU if it fails
                try:
                    if codec_to_use != 'libx264':
                        # GPU encoding
                        clip.write_videofile(
                            output_path,
                            fps=fps,
                            codec=codec_to_use,
                            audio_codec="aac",
                            bitrate=video_bitrate,
                            preset='fast',
                            threads=1,
                            logger=None
                        )
                    else:
                        raise Exception("Using CPU codec")
                except:
                    # Fallback to CPU encoding
                    clip.write_videofile(
                        output_path,
                        fps=fps,
                        codec="libx264",
                        audio_codec="aac",
                        bitrate=video_bitrate,
                        preset='superfast',  # Better compression than ultrafast, still very fast
                        threads=1,
                        logger=None
                    )
                
                clip_record = {
                    "video_id": video_id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "viral_score": passage.get("viral_score", 0),
                    "style": "vertical",
                    "transcript_segment": passage["text"],
                    "output_path": output_path,
                    "clip_metadata": {
                        "title": f"Viral Clip {passage.get('viral_score', 0)}%",
                        "reason": passage.get("reason", ""),
                        "topic": passage.get("topic", ""),
                        "resolution": res_key,
                        "fps": fps
                    }
                }
                
                # Close clips to release memory/handle
                clip.close()
                clip_video.close()
                
                print(f"✅ [Thread {i+1}] Clip {i+1} completed!")
                return clip_record
                
            except Exception as e:
                print(f"❌ [Thread {i+1}] Error processing clip {i+1}: {e}")
                import traceback
                traceback.print_exc()
                return None

        # Use ThreadPoolExecutor to process clips in parallel
        clips_generated = 0
        with ThreadPoolExecutor(max_workers=2) as executor:        ### MAX THREAD (6 workers for faster export)
            # Submit all clip processing tasks
            future_to_clip = {
                executor.submit(process_clip, i, passage, video_path, output_folder, video_id, plan): (i, passage)
                for i, passage in enumerate(final_passages)
            }
            
            # Process completed tasks as they finish
            for future in as_completed(future_to_clip):
                i, passage = future_to_clip[future]
                try:
                    clip_record = future.result()
                    if clip_record:
                        storage.create_clip(clip_record)
                        clips_generated += 1
                except Exception as e:
                    print(f"❌ Exception in thread for clip {i+1}: {e}")

        print(f"✅ Processing complete! Generated {clips_generated} clips.")
        storage.update_video_status(video_id, VideoStatus.FINISHED.value)
        
        # Cleanup original video and audio
        video.close()
        video = None # Explicitly release
        
        # Wait a bit for handles to release
        time.sleep(1)
        
        # Delete original video
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                print("🗑️  Original video deleted")
        except Exception as e:
            print(f"⚠️ Could not delete original video: {e}")
            
        # Delete audio
        try:
            if os.path.exists(audio_file):
                os.remove(audio_file)
                print("🗑️  Temporary audio deleted")
        except Exception as e:
            print(f"⚠️ Could not delete temp audio: {e}")

    except Exception as e:
        print(f"❌ Error processing video {video_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        storage.update_video_status(video_id, VideoStatus.ERROR.value)
        
    finally:
        if video:
            video.close()
