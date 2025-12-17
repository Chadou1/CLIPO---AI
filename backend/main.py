from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from api import auth, videos, clips, processing, billing, library
from utils.init_premium_account import create_premium_account

load_dotenv()

# Initialize JSON storage and premium account on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing JSON storage...")
    # Storage will be created automatically when first accessed
    print("Creating premium account if not exists...")
    create_premium_account()
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title="ClipGenius AI",
    description="AI-Powered TikTok/Reels Clip Generator",
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

@app.get("/")
async def root():
    return {
        "message": "ClipGenius AI API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Global exception handler
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

# Include routers
app.include_router(auth.router)
app.include_router(videos.router)
app.include_router(clips.router)
app.include_router(processing.router)
app.include_router(billing.router)
app.include_router(library.router)

# Mount static files for library output
from pathlib import Path
from fastapi.staticfiles import StaticFiles
storage_dir = Path(__file__).parent / "storage"
library_output_dir = storage_dir / "library_output"
library_output_dir.mkdir(parents=True, exist_ok=True)

app.mount("/library/output", StaticFiles(directory=str(library_output_dir)), name="library_output")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
