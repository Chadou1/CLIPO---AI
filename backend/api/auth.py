from fastapi import APIRouter, Depends, HTTPException, status
from models import User, PlanType
from utils.auth import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token, get_current_user
from utils.email_service import send_verification_email, send_password_reset_email, send_welcome_email, generate_code
from utils.credits import add_credits
from utils.file_storage import get_storage
from .schemas import UserRegister, UserLogin, Token, TokenRefresh, UserResponse
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])

class ActivateAccountRequest(BaseModel):
    activation_code: str

class ActivateAccountResponse(BaseModel):
    message: str
    expiry_date: str
    credits_added: int

class VerifyEmailRequest(BaseModel):
    email: str
    code: str

class ResendVerificationRequest(BaseModel):
    email: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    new_password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """Register new user and send verification email"""
    storage = get_storage()
    
    # Check if user exists
    existing_user = storage.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Create new user with FREE plan and email_verified=False
        hashed_password = get_password_hash(user_data.password)
        new_user_data = {
            "email": user_data.email,
            "password_hash": hashed_password,
            "credits": 3,  # 3 free credits
            "plan": PlanType.FREE.value,
            "email_verified": False  # Require verification
        }
        
        new_user = storage.create_user(new_user_data)
        
        # Generate and send verification code
        code = generate_code()
        storage.store_verification_code(user_data.email, code)
        send_verification_email(user_data.email, code)
        
        return {
            "message": "Registration successful! Please check your email for verification code.",
            "email": new_user["email"]
        }
        
    except Exception as e:
        print(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest):
    """Verify email with code"""
    storage = get_storage()
    
    # Verify the code
    if not storage.verify_email_code(request.email, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )
    
    # Send welcome email
    try:
        send_welcome_email(request.email)
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
    
    return {"message": "Email verified successfully! You can now login."}

@router.post("/resend-verification")
async def resend_verification(request: ResendVerificationRequest):
    """Resend verification code"""
    storage = get_storage()
    
    user = storage.get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Generate and send new code
    code = generate_code()
    storage.store_verification_code(request.email, code)
    send_verification_email(request.email, code)
    
    return {"message": "Verification code sent!"}

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user (requires verified email)"""
    storage = get_storage()
    
    # Find user
    user = storage.get_user_by_email(user_data.email)
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if email is verified
    if not user.get("email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user["email"]})
    refresh_token = create_refresh_token(data={"sub": user["email"]})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Request password reset code"""
    storage = get_storage()
    
    user = storage.get_user_by_email(request.email)
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If that email exists, a reset code has been sent"}
    
    # Generate and send reset code
    code = generate_code()
    storage.store_reset_code(request.email, code)
    send_password_reset_email(request.email, code)
    
    return {"message": "If that email exists, a reset code has been sent"}

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password with code"""
    storage = get_storage()
    
    # Verify reset code
    if not storage.verify_reset_code(request.email, request.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset code"
        )
    
    # Get user
    user = storage.get_user_by_email(request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    hashed_password = get_password_hash(request.new_password)
    storage.update_user(user["id"], {"password_hash": hashed_password})
    
    # Clear reset code
    storage.clear_reset_code(request.email)
    
    return {"message": "Password reset successfully! You can now login with your new password."}

@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh):
    """Refresh access token"""
    storage = get_storage()
    
    payload = decode_token(token_data.refresh_token)
    
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    email = payload.get("sub")
    user = storage.get_user_by_email(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": user["email"]})
    new_refresh_token = create_refresh_token(data={"sub": user["email"]})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

# Activation endpoint removed in favor of Stripe payment

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user
