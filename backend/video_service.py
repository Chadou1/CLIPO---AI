from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

from api import videos, clips, processing, queue

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Video Service...")
    
    # Initialize ProcessPoolManager
    from utils.video_process_manager import get_process_manager
    manager = get_process_manager()
    print(f"✅ ProcessPoolManager ready: {manager.max_processes} concurrent processes")
    
    yield
    # Shutdown
    print("Shutting down Video Service...")

app = FastAPI(
    title="ClipGenius Video Service",
    description="Video Processing and Management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(videos.router)
app.include_router(clips.router)
app.include_router(processing.router)
app.include_router(queue.router)

# Mount static files (using new storage path)
# We need to serve uploads and clips from here
storage_dir = os.path.join(os.path.dirname(__file__), "storage")
uploads_dir = os.path.join(storage_dir, "uploads")
clips_dir = os.path.join(storage_dir, "clips")
os.makedirs(uploads_dir, exist_ok=True)
os.makedirs(clips_dir, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
app.mount("/clips", StaticFiles(directory=clips_dir), name="clips")

@app.get("/")
async def root():
    return {
        "service": "Video Service",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "video_service:app",
        host="0.0.0.0",
        port=32191,
        reload=True
    )
