from utils.file_storage import get_storage
from fastapi import HTTPException, status

def check_credits(user: dict, amount: int) -> bool:
    """Check if user has enough credits"""
    return user.get("credits", 0) >= amount

def deduct_credits(user_id: int, amount: int, reason: str):
    """Deduct credits from user account"""
    storage = get_storage()
    user = storage.get_user_by_id(user_id)
    
    if not user or not check_credits(user, amount):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient credits"
        )
    
    # Update credits
    new_credits = user["credits"] - amount
    storage.update_user(user_id, {"credits": new_credits})
    
    # Log the transaction
    storage.create_credit_log({
        "user_id": user_id,
        "amount": -amount,
        "reason": reason
    })

def add_credits(user_id: int, amount: int, reason: str):
    """Add credits to user account"""
    storage = get_storage()
    user = storage.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update credits
    new_credits = user["credits"] + amount
    storage.update_user(user_id, {"credits": new_credits})
    
    # Log the transaction
    storage.create_credit_log({
        "user_id": user_id,
        "amount": amount,
        "reason": reason
    })

def get_plan_credits(plan: str) -> int:
    """Get monthly credits (videos) based on plan"""
    credits_map = {
        "free": 1,       # 1 video/month
        "starter": 10,   # 10 videos/month
        "pro": 30,       # 30 videos/month
        "agency": 100    # 100 videos/month
    }
    return credits_map.get(plan, 1)


