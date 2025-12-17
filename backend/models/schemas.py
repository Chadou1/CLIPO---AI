from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

# Enums
class PlanType(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    AGENCY = "agency"

class VideoStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    FINISHED = "finished"
    ERROR = "error"

# User Model
class User(BaseModel):
    id: Optional[int] = None
    email: str
    password_hash: str
    credits: int = 3
    plan: PlanType = PlanType.FREE
    created_at: Optional[str] = None

# Video Model
class Video(BaseModel):
    id: Optional[int] = None
    user_id: int
    file_path: str
    filename: str
    duration: Optional[float] = None
    status: VideoStatus = VideoStatus.UPLOADED
    error_message: Optional[str] = None
    created_at: Optional[str] = None

# Clip Model
class Clip(BaseModel):
    id: Optional[int] = None
    video_id: int
    start_time: float
    end_time: float
    viral_score: Optional[float] = None
    style: str = "simple"
    output_path: Optional[str] = None
    transcript_segment: Optional[str] = None
    clip_metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

# Subscription Model
class Subscription(BaseModel):
    id: Optional[int] = None
    user_id: int
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    plan: PlanType
    renew_date: Optional[str] = None
    created_at: Optional[str] = None

# Credit Log Model
class CreditLog(BaseModel):
    id: Optional[int] = None
    user_id: int
    amount: int
    reason: str
    created_at: Optional[str] = None
