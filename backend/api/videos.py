from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from models import User, Video, VideoStatus, Clip
from utils.auth import get_current_user
from utils.file_storage import get_storage
from typing import List, Optional
from pydantic import BaseModel
import os
import shutil
import time
from pathlib import Path

router = APIRouter(prefix="/videos", tags=["Videos"])

ALLOWED_EXTENSIONS = ['mp4', 'mov', 'avi', 'mkv']
MAX_FILE_SIZE = int(os.getenv("MAX_VIDEO_SIZE_MB", "500")) * 1024 * 1024  # in bytes

class VideoResponse(BaseModel):
    id: int
    filename: str
    duration: Optional[float] = None
    status: str
    created_at: str
    clips_count: int = 0

class ClipResponse(BaseModel):
    id: int
    start_time: float
    end_time: float
    viral_score: Optional[float] = None
    style: str
    transcript_segment: Optional[str] = None
    created_at: str
    download_url: Optional[str] = None

class YouTubeVideoRequest(BaseModel):
    url: str
    clip_count: int = 12
    quality: Optional[str] = None  # "720p", "1080p", "2k"
    fps: Optional[int] = None # 30, 60

class RenameVideoRequest(BaseModel):
    filename: str
    
    @classmethod
    def __init__(cls, **data):
        if 'filename' in data and len(data['filename']) > 15:
            data['filename'] = data['filename'][:15]
        super().__init__(**data)

@router.post("/upload", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def create_video_from_url(
    request: YouTubeVideoRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create video from YouTube URL (Free)"""
    # from utils.credits import check_credits, deduct_credits # Credits no longer used
    
    storage = get_storage()
    
    # Credit check removed - Service is free
    
    # Create video record (initially without file path)
    # Truncate filename to 15 characters max
    default_name = f"YT{int(time.time())}"
    video_data = {
        "user_id": current_user["id"],
        "file_path": "", # Will be updated after download
        "filename": default_name[:15],  # Limit to 15 chars
        "status": VideoStatus.UPLOADED.value
    }
    
    
    video = storage.create_video(video_data)
    
    # Credit deduction removed
    
    # Determine quality settings based on plan and user choice
    plan = current_user.get("plan", "free")
    
    # Default settings
    quality = "720p"
    fps = 30
    
    if plan == "free":
        # Free users locked to 720p 30fps
        quality = "720p"
        fps = 30
    else:
        # Paid users logic
        # Allow user choice if provided, otherwise default based on plan
        if request.quality:
            quality = request.quality
        elif plan == "agency":
            quality = "2k"
        elif plan in ["pro", "starter"]:
            quality = "1080p"
            
        if request.fps:
            fps = request.fps
        elif plan == "agency":
            fps = 60
        else:
            fps = 30
            
        # Enforce limits just in case
        if plan != "agency" and quality == "2k":
            quality = "1080p" # Downgrade if not agency
            
    quality_settings = {"resolution": quality, "fps": fps}
    
    print(f"📋 User plan '{plan}' → Quality: {quality_settings} (user selected: {request.quality}/{request.fps})")
        
    # Submit to ProcessPoolManager for concurrent processing with queue support
    from utils.video_process_manager import get_process_manager
    
    manager = get_process_manager()
    result = manager.submit_video_task(
        video_id=video["id"],
        url=request.url,
        quality_settings=quality_settings,
        clip_count=request.clip_count,
        plan=plan
    )
    
    # Log queue status
    if result["status"] == "queued":
        print(f"📋 Video {video['id']} queued at position {result['queue_position']}")
    else:
        print(f"🎬 Video {video['id']} started processing in slot {result['slot_id']}")
    
    return VideoResponse(
        id=video["id"],
        filename=video["filename"],
        duration=video.get("duration"),
        status=video["status"],
        created_at=video["created_at"],
        clips_count=0
    )


def process_video_wrapper(video_id, url, quality_settings, clip_count=12, plan="free"):
    # Helper to download then process
    try:
        from utils.video_processor import process_video_groq, download_youtube_video
        from utils.file_storage import get_storage
        
        storage = get_storage()
        
        print(f"⬇️ Downloading video for {video_id}...")
        # Use new storage paths
        storage_base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "storage")
        uploads_dir = os.path.join(storage_base, "uploads")
        clips_dir = os.path.join(storage_base, "clips")
        
        # Ensure directories exist
        os.makedirs(uploads_dir, exist_ok=True)
        os.makedirs(clips_dir, exist_ok=True)
            
        video_filename = f"video_{video_id}.mp4"
        video_path = os.path.join(uploads_dir, video_filename)
        
        # Download - this now returns the actual file path or None
        downloaded_path = download_youtube_video(url, video_path)
        
        # Check if download succeeded
        if not downloaded_path or not os.path.exists(downloaded_path):
            print(f"❌ Download failed for video {video_id}. File does not exist.")
            storage.update_video_status(video_id, VideoStatus.ERROR.value)
            return
        
        # Use the actual downloaded path (might be .part file)
        actual_video_path = downloaded_path
        print(f"✅ Using video file: {actual_video_path}")
        
        # Update video record with actual path
        storage.update_video(video_id, {"file_path": actual_video_path})
        
        # Process with clip_count parameter - use clips_dir for output
        process_video_groq(video_id, actual_video_path, clips_dir, quality_settings, clip_count=clip_count, plan=plan)
        
    except Exception as e:
        print(f"❌ Error in wrapper: {e}")
        import traceback
        traceback.print_exc()
        # Ensure status is updated to error if something fails here
        try:
            storage = get_storage()
            storage.update_video_status(video_id, VideoStatus.ERROR.value)
        except:
            pass

@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get video details"""
    storage = get_storage()
    
    video = storage.get_video_by_id(video_id)
    
    if not video or video["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    clips = storage.get_clips_by_video(video_id)
    
    return VideoResponse(
        id=video["id"],
        filename=video["filename"],
        duration=video.get("duration"),
        status=video["status"],
        created_at=video["created_at"],
        clips_count=len(clips)
    )

@router.put("/{video_id}/rename", response_model=VideoResponse)
async def rename_video(
    video_id: int,
    request: RenameVideoRequest,
    current_user: dict = Depends(get_current_user)
):
    """Rename a video"""
    storage = get_storage()
    
    video = storage.get_video_by_id(video_id)
    
    if not video or video["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Truncate filename to 15 characters max
    new_filename = request.filename[:15]
    updated_video = storage.update_video(video_id, {"filename": new_filename})
    clips = storage.get_clips_by_video(video_id)
    
    return VideoResponse(
        id=updated_video["id"],
        filename=updated_video["filename"],
        duration=updated_video.get("duration"),
        status=updated_video["status"],
        created_at=updated_video["created_at"],
        clips_count=len(clips)
    )

@router.get("/{video_id}/clips", response_model=List[ClipResponse])
async def get_video_clips(
    video_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get all clips for a video"""
    storage = get_storage()
    
    # Verify ownership
    video = storage.get_video_by_id(video_id)
    
    if not video or video["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Get clips for this video (THIS WAS THE MISSING LINE!)
    clips = storage.get_clips_by_video(video_id)
    
    # Generate file URLs (local paths)
    clip_responses = []
    
    for clip in clips:
        # Convert file path to URL
        if clip.get("output_path"):
            filename = os.path.basename(clip["output_path"])
            # Clips are served from /clips/ not /uploads/
            download_url = f"/api/clips/{filename}"
        else:
            download_url = None
        
        clip_responses.append(ClipResponse(
            id=clip["id"],
            start_time=clip["start_time"],
            end_time=clip["end_time"],
            viral_score=clip.get("viral_score"),
            style=clip.get("style", "simple"),
            transcript_segment=clip.get("transcript_segment"),
            created_at=clip["created_at"],
            download_url=download_url
        ))
    
    return clip_responses

@router.get("", response_model=List[VideoResponse])
async def get_videos(
    current_user: dict = Depends(get_current_user)
):
    """Get all videos for current user"""
    storage = get_storage()
    
    videos = storage.get_videos_by_user(current_user["id"])
    
    response = []
    for video in videos:
        clips = storage.get_clips_by_video(video["id"])
        response.append(VideoResponse(
            id=video["id"],
            filename=video["filename"],
            duration=video.get("duration"),
            status=video["status"],
            created_at=video["created_at"],
            clips_count=len(clips)
        ))
        
    # Sort by created_at desc
    response.sort(key=lambda x: x.created_at, reverse=True)
    
    return response

@router.delete("/{video_id}")
async def delete_video(
    video_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a video"""
    storage = get_storage()
    
    video = storage.get_video_by_id(video_id)
    
    if not video or video["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found"
        )
    
    # Delete the video file
    try:
        if os.path.exists(video["file_path"]):
            os.remove(video["file_path"])
    except Exception as e:
        print(f"Error deleting file: {e}")
    
    # Delete from storage
    storage.delete_video(video_id)
    
    return {"message": "Video deleted successfully"}
