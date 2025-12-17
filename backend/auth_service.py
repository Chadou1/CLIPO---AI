from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from api import auth, billing
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
    print("Shutting down Auth Service...")

app = FastAPI(
    title="ClipGenius Auth Service",
    description="Authentication and Billing Service",
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
app.include_router(billing.payment_router)

@app.get("/")
async def root():
    return {
        "service": "Auth Service",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "auth_service:app",
        host="0.0.0.0",
        port=32190,
        reload=True
    )
