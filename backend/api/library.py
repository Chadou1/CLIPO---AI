"""
Library Generation API Routes
Handles library-based clip generation with credit deduction and tier restrictions
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
from utils.auth import get_current_user
from utils.file_storage import get_storage
from utils.credits import check_credits, deduct_credits
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/library", tags=["Library"])

# Base paths
LIBRARY_BASE_DIR = Path(__file__).parent.parent.parent / "clipo-bibliothèque" / "libraries"
FONT_DIR = Path(__file__).parent.parent.parent / "clipo-bibliothèque" / "Fonts"
OUTPUT_DIR = Path(__file__).parent.parent / "storage" / "library_output"
MUSIC_DIR = Path(__file__).parent.parent.parent / "clipo-bibliothèque" / "Werenoi_Musiques"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_available_libraries() -> List[str]:
    """Scan library directory for available libraries"""
    if not LIBRARY_BASE_DIR.exists():
        logger.warning(f"Library directory not found: {LIBRARY_BASE_DIR}")
        return []
    
    # All subdirectories in libraries/ are valid libraries
    libraries = [d.name for d in LIBRARY_BASE_DIR.iterdir() if d.is_dir()]
    logger.info(f"Found {len(libraries)} libraries: {libraries}")
    return libraries



def get_font_filename_by_id(font_id: int) -> str:
    """Convert numeric font ID to actual filename"""
    if not FONT_DIR.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Font directory not found: {FONT_DIR}"
        )
    
    # Get valid fonts sorted to ensure consistent IDs
    fonts = sorted(
        [f for f in FONT_DIR.iterdir() if f.suffix.lower() in ['.ttf', '.otf']]
    )
    
    if font_id < 1 or font_id > len(fonts):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid font ID {font_id}. Valid range: 1-{len(fonts)}"
        )
    
    return fonts[font_id - 1].name


class LibraryGenerateRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500, description="Text to display on video")
    library: str = Field(..., description="Library name (e.g., 'Keo')")
    font: int = Field(..., description="Font ID from /library/fonts")
    fps: int = Field(default=30, description="Frames per second (30 or 60)")
    resolution: str = Field(default="720p", description="Video resolution ('720p' or '1080p')")
    black_white_intensity: int = Field(default=0, ge=0, le=100, description="B&W filter intensity 0-100")
    speed: int = Field(default=4, ge=1, le=8, description="Clips per second (1-8)")
    font_size: int = Field(default=48, ge=30, le=80, description="Font size (30-80)")
    url_song: str = Field(..., description="YouTube URL for music (REQUIRED)")


class LibraryGenerateResponse(BaseModel):
    message: str
    video_id: Optional[int] = None
    output_url: Optional[str] = None
    credits_remaining: int


@router.get("/libraries")
async def list_libraries(current_user: dict = Depends(get_current_user)):
    """List available video libraries"""
    libraries = get_available_libraries()
    return {
        "libraries": libraries,
        "description": "Available video libraries for clip generation"
    }


@router.get("/libraries/{library_name}/videos")
async def list_library_videos(
    library_name: str,
    current_user: dict = Depends(get_current_user)
):
    """List videos in a specific library"""
    available_libs = get_available_libraries()
    if library_name not in available_libs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library '{library_name}' not found"
        )
    
    library_path = LIBRARY_BASE_DIR / library_name
    
    videos = [
        f for f in os.listdir(library_path)
        if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))
    ]
    
    return {
        "library": library_name,
        "video_count": len(videos),
        "videos": videos[:20]  # Return first 20 for preview
    }


@router.post("/generate", response_model=LibraryGenerateResponse)
async def generate_library_video(
    request: LibraryGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate video from library with text overlay
    Costs 1 credit per generation
    """
    storage = get_storage()
    
    # Refresh user data to ensure plan is up to date
    user_id = current_user.get("id")
    refreshed_user = storage.get_user_by_id(user_id)
    if not refreshed_user:
        raise HTTPException(status_code=401, detail="User not found")
        
    # Get plan - default to free only if not set AT ALL
    plan = refreshed_user.get("plan")
    if not plan:  # Only use default if plan is None or empty string
        plan = "free"
    logger.info(f"Generating video for user {refreshed_user.get('email')} (Plan: {plan})")

    
    # Validate library
    available_libs = get_available_libraries()
    if request.library not in available_libs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid library. Available: {available_libs}"
        )
    
    # Check if library directory exists
    video_dir = LIBRARY_BASE_DIR / request.library
    if not video_dir.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library directory not found: {video_dir}"
        )
    
    # Enforce tier-based quality restrictions
    fps = request.fps
    resolution = request.resolution
    
    if plan == "free":
        # Free: 720p @ 30fps only
        fps = 30
        resolution = "720p"
    elif plan == "starter":
        # Starter: 1080p@30fps OR 720p@60fps
        if not ((resolution == "1080p" and fps == 30) or (resolution == "720p" and fps == 60)):
            # Default to 1080p@30fps if invalid combination
            fps = 30
            resolution = "1080p"
    elif plan in ["pro", "agency"]:
        # Pro/Agency: Any combination 720p-1080p @ 30-60fps
        if resolution not in ["720p", "1080p"]:
            resolution = "1080p"
        if fps not in [30, 60]:
            fps = 30
    
    # Check credits (1 credit required)
    if not check_credits(refreshed_user, 1):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. You have {refreshed_user.get('credits', 0)} credits, need 1."
        )
    
    # Deduct 1 credit
    deduct_credits(user_id, 1, "Library video generation")
    
    # Get updated user info for remaining credits
    updated_user = storage.get_user_by_id(user_id)
    
    # Generate video in background
    try:
        from services.library_generation_module import LibraryVideoGenerator
        
        # Ensure font directory exists
        if not FONT_DIR.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Font directory not found: {FONT_DIR}"
            )
        
        # Convert font ID to filename
        try:
            font_filename = get_font_filename_by_id(request.font)
            logger.info(f"Using font #{request.font}: {font_filename}")
        except HTTPException as e:
            raise e

        # Initialize generator
        generator = LibraryVideoGenerator()
        
        # Download YouTube audio (REQUIRED)
        try:
            youtube_audio_path = generator.download_youtube_audio(request.url_song, str(OUTPUT_DIR))
            logger.info(f"Downloaded YouTube audio: {youtube_audio_path}")
            music_dir_to_use = youtube_audio_path
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to download YouTube audio: {str(e)}"
            )
        
        # Generate video
        output_path = generator.generate_video(
            text=request.text,
            video_dir=str(video_dir),
            music_dir=music_dir_to_use,
            font_dir=str(FONT_DIR),
            output_dir=str(OUTPUT_DIR),
            fps=fps,
            font_filename=font_filename,
            bw_intensity=request.black_white_intensity,
            speed=request.speed,
            font_size=request.font_size,
            resolution=resolution
        )
        
        # Delete YouTube audio if it was downloaded
        if youtube_audio_path and os.path.exists(youtube_audio_path):
            try:
                os.remove(youtube_audio_path)
                logger.info(f"Deleted temporary YouTube audio: {youtube_audio_path}")
            except Exception as e:
                logger.warning(f"Failed to delete YouTube audio: {e}")
        
        # Get filename for URL
        filename = os.path.basename(output_path)
        output_url = f"/library/output/{filename}"
        
        return LibraryGenerateResponse(
            message="Video generated successfully",
            output_url=output_url,
            credits_remaining=updated_user.get("credits", 0)
        )
        
    except Exception as e:
        # Refund credit on error
        from utils.credits import add_credits
        add_credits(user_id, 1, "Refund: Library video generation failed")
        logger.error(f"Video generation failed: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video generation failed: {str(e)}"
        )


def get_available_fonts() -> List[dict]:
    """Scan font directory for available fonts"""
    if not FONT_DIR.exists():
        logger.warning(f"Font directory not found: {FONT_DIR}")
        return []
        
    font_list = []
    # Sort to ensure consistent IDs
    for idx, font_file in enumerate(sorted(FONT_DIR.iterdir()), start=1):
        if font_file.suffix.lower() in ['.ttf', '.otf']:
            display_name = font_file.stem.replace('_', ' ')
            font_list.append({
                "id": idx,
                "filename": font_file.name,
                "name": display_name
            })
    return font_list


def preload_resources():
    """Load and display available resources on startup"""
    print("\n" + "="*50)
    print("      PRE-LOADING CLIP GENIUS RESOURCES")
    print("="*50)
    
    # Load Libraries
    print("\n[LIBRARIES]")
    libraries = get_available_libraries()
    if libraries:
        for lib in libraries:
            print(f"  [+] {lib}")
    else:
        print("  [!] No libraries found!")
        
    # Load Fonts
    print("\n[FONTS]")
    fonts = get_available_fonts()
    if fonts:
        for font in fonts:
            print(f"  [+] [{font['id']}] {font['name']} ({font['filename']})")
    else:
        print("  [!] No fonts found!")
        
    print("\n" + "="*50 + "\n")


@router.get("/fonts")
async def list_fonts(current_user: dict = Depends(get_current_user)):
    """List available fonts with numeric IDs for frontend"""
    fonts = get_available_fonts()
    logger.info(f"Returning {len(fonts)} fonts")
    return {"fonts": fonts}

