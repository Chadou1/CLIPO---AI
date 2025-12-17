from fastapi import APIRouter, Depends, HTTPException, status
from utils.auth import get_current_user
from utils.file_storage import get_storage
from utils.credits import deduct_credits
from pydantic import BaseModel
import os

router = APIRouter(prefix="/clips", tags=["Clips"])

class ExportClipRequest(BaseModel):
    style: str = "simple"  # simple, zoom, jumpcuts

class ExportClipResponse(BaseModel):
    download_url: str
    credits_remaining: int

@router.get("/{clip_id}/download")
async def download_clip(
    clip_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Download a clip (FREE - no credit cost)"""
    from fastapi.responses import FileResponse
    storage = get_storage()
    
    # Get clip and verify ownership
    clip = storage.get_clip_by_id(clip_id)
    if not clip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clip not found"
        )
    
    # Verify user owns the video
    video = storage.get_video_by_id(clip["video_id"])
    if not video or video["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to download this clip"
        )
    
    # Check if clip is ready
    if not clip.get("output_path") or not os.path.exists(clip["output_path"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Clip not ready yet or file not found"
        )
    
    # Return file for download (FREE!)
    return FileResponse(
        path=clip["output_path"],
        filename=f"clip_{clip_id}.mp4",
        media_type="video/mp4"
    )

@router.post("/{clip_id}/export", response_model=ExportClipResponse)
async def export_clip(
    clip_id: int,
    request: ExportClipRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get clip download URL (FREE - no credit cost)"""
    storage = get_storage()
    
    # Get clip and verify ownership
    clip = storage.get_clip_by_id(clip_id)
    if not clip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clip not found"
        )
    
    # Verify user owns the video
    video = storage.get_video_by_id(clip["video_id"])
    if not video or video["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to export this clip"
        )
    
    # Check if clip is ready
    if not clip.get("output_path"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Clip not ready yet"
        )
    
    # NO CREDIT DEDUCTION - Downloads are free!
    # Get current user credits for display
    updated_user = storage.get_user_by_id(current_user["id"])
    
    # Return download URL (use the new download endpoint)
    # Return download URL (use the new download endpoint)
    download_url = f"/api/clips/{clip_id}/download"
    
    return ExportClipResponse(
        download_url=download_url,
        credits_remaining=updated_user["credits"]
    )

@router.delete("/{clip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_clip(
    clip_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a clip"""
    storage = get_storage()
    
    clip = storage.get_clip_by_id(clip_id)
    if not clip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clip not found"
        )
    
    # Verify ownership
    video = storage.get_video_by_id(clip["video_id"])
    if not video or video["user_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this clip"
        )
    
    # Delete file
    if clip.get("output_path") and os.path.exists(clip["output_path"]):
        try:
            os.remove(clip["output_path"])
        except Exception as e:
            print(f"Failed to delete file: {str(e)}")
    
    # Delete from storage
    storage.delete_clip(clip_id)
    
    return None
