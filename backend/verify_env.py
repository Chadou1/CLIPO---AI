import sys
import moviepy
import groq
import yt_dlp

print(f"Python Version: {sys.version}")
print(f"MoviePy Version: {moviepy.__version__}")
print(f"Groq Version: {groq.__version__}")
print(f"yt-dlp Version: {yt_dlp.version.__version__}")

try:
    from moviepy.editor import VideoFileClip
    print("MoviePy VideoFileClip import successful")
except ImportError as e:
    print(f"MoviePy VideoFileClip import failed: {e}")
