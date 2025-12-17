from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

from api import auth, billing, videos, clips, processing, payment, queue
from utils.init_premium_account import create_premium_account

load_dotenv()

# Initialize JSON storage and premium account on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Clipo Unified Service...")
    print("Initializing JSON storage...")
    # Storage will be created automatically when first accessed
    print("Creating premium account if not exists...")
    create_premium_account()
    print("Initializing ProcessPoolManager...")
    from utils.video_process_manager import get_process_manager
    manager = get_process_manager()
    print("Starting Video Service...")
    yield
    # Shutdown
    print("Shutting down Clipo Unified Service...")

app = FastAPI(
    title="Clipo Unified Service",
    description="Authentication, Billing, and Video Processing Service",
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
app.include_router(auth.router)
app.include_router(billing.router)
app.include_router(payment.router)
app.include_router(videos.router)
app.include_router(clips.router)
app.include_router(processing.router)
app.include_router(queue.router)

# Mount static files (using new storage path)
# We need to serve uploads from here
storage_dir = os.path.join(os.path.dirname(__file__), "storage")
uploads_dir = os.path.join(storage_dir, "uploads")
os.makedirs(uploads_dir, exist_ok=True)

app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

@app.get("/")
async def root():
    return {
        "service": "Clipo Unified Service",
        "status": "running",
        "port": 32190,
        "endpoints": {
            "auth": "/api/auth",
            "billing": "/api/billing",
            "videos": "/api/videos",
            "clips": "/api/clips",
            "processing": "/api/processing"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "unified"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=32190,
        reload=True
    )
