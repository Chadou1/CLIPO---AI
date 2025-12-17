from fastapi import APIRouter, Depends
from utils.auth import get_current_user
from utils.file_storage import get_storage
from utils.credits import add_credits, get_plan_credits
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/billing", tags=["Billing"])

class BillingInfoResponse(BaseModel):
    plan: str
    credits: int
    stripe_customer_id: Optional[str] = None
    next_renewal: Optional[str] = None

@router.get("/info", response_model=BillingInfoResponse)
async def get_billing_info(
    current_user: dict = Depends(get_current_user)
):
    """Get user's billing information"""
    storage = get_storage()
    
    # Get active subscription
    subscription = storage.get_subscription_by_user(current_user["id"])
    
    return BillingInfoResponse(
        plan=current_user["plan"],
        credits=current_user["credits"],
        stripe_customer_id=subscription.get("stripe_customer_id") if subscription else None,
        next_renewal=subscription.get("renew_date") if subscription else None
    )

# Note: Stripe functionality removed as per user request
# The system now uses activation codes instead of Stripe payments

# Payment router for backwards compatibility
payment_router = APIRouter(prefix="/payment", tags=["Payment"])

class PlanInfo(BaseModel):
    id: str
    name: str
    price: float
    credits: int
    features: list[str]

@payment_router.get("/plans")
async def get_plans():
    """Get available plans"""
    return {
        "plans": [
            {
                "id": "free",
                "name": "Free",
                "price": 0,
                "credits": 3,
                "features": ["3 free credits", "Basic features"]
            },
            {
                "id": "agency",
                "name": "Agency",
                "price": 97,
                "credits": -1,  # Unlimited
                "features": ["Unlimited credits", "Premium features", "1080p export"]
            }
        ]
    }

@payment_router.post("/create-checkout-session")
async def create_checkout_session(current_user: dict = Depends(get_current_user)):
    """Create checkout session - disabled, use activation codes instead"""
    return {
        "error": "Payment system disabled. Please use activation codes instead.",
        "message": "Contact support for activation codes"
    }

# Include payment router in the module
__all__ = ['router', 'payment_router']
