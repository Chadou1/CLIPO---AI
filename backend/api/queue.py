from fastapi import APIRouter, Depends
from utils.auth import get_current_user
from utils.video_process_manager import get_process_manager

router = APIRouter(prefix="/queue", tags=["Queue"])


@router.get("/status")
async def get_queue_status(current_user: dict = Depends(get_current_user)):
    """
    Get current queue status and active processes.
    
    Returns:
        - max_processes: Maximum concurrent processes (2)
        - active_processes: Number of currently processing videos
        - active_tasks: List of active tasks with details
        - queued_tasks: Number of tasks waiting in queue
        - available_slots: Number of available processing slots
        - statistics: Total submitted, completed, and failed tasks
    """
    manager = get_process_manager()
    status = manager.get_queue_status()
    
    return status
