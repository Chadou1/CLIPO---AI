from fastapi import APIRouter, Depends
from utils.auth import get_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/process", tags=["Processing"])

class ProcessStartRequest(BaseModel):
    video_id: int

class ProcessStartResponse(BaseModel):
    task_id: str = "pending"
    status: str

class ProcessStatusResponse(BaseModel):
    state: str
    status: str
    result: Optional[dict] = None

@router.post("/start", response_model=ProcessStartResponse)
async def start_processing(
    request: ProcessStartRequest,
    current_user: dict = Depends(get_current_user)
):
    """Start video processing task"""
    # Processing is already triggered by upload in the current local implementation
    # This endpoint just confirms the status
    
    return ProcessStartResponse(
        task_id=str(request.video_id),
        status="Processing started"
    )

@router.get("/status/{task_id}", response_model=ProcessStatusResponse)
async def get_processing_status(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get processing task status (task_id is video_id in local mode)"""
    from utils.file_storage import get_storage
    storage = get_storage()
    
    try:
        video_id = int(task_id)
        video = storage.get_video_by_id(video_id)
        
        if not video:
            return ProcessStatusResponse(
                state="FAILURE",
                status="Video not found"
            )
            
        status = video.get("status", "uploaded")
        
        if status == "uploaded":
            return ProcessStatusResponse(state="PENDING", status="Waiting to start...")
        elif status == "processing":
            return ProcessStatusResponse(state="PROCESSING", status="Analyzing video...")
        elif status == "finished":
            return ProcessStatusResponse(state="SUCCESS", status="Completed", result={"video_id": video_id})
        elif status == "error":
            return ProcessStatusResponse(state="FAILURE", status="Processing failed")
        else:
            return ProcessStatusResponse(state="PENDING", status=status)
            
    except ValueError:
        return ProcessStatusResponse(state="FAILURE", status="Invalid task ID")
