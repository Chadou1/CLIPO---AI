import sys
from pathlib import Path

# Ensure backend directory is in Python path for utils imports
BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from api import library
from api.library import preload_resources

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Library Service...")
    preload_resources()
    yield
    # Shutdown
    print("Shutting down Library Service...")

app = FastAPI(
    title="ClipGenius Library Service",
    description="Library-based Video Generation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(library.router)

# Mount static files for library output
storage_dir = Path(__file__).parent / "storage"
library_output_dir = storage_dir / "library_output"
library_output_dir.mkdir(parents=True, exist_ok=True)

app.mount("/library/output", StaticFiles(directory=str(library_output_dir)), name="library_output")

@app.get("/")
async def root():
    return {
        "service": "Library Service",
        "status": "running",
        "description": "Generate custom videos from library clips"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "library_service:app",
        host="0.0.0.0",
        port=32189,
        reload=True
    )
