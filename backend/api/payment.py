from fastapi import APIRouter, Depends, HTTPException, Request, status
from datetime import datetime, timedelta
from pydantic import BaseModel
from fastapi.responses import RedirectResponse
from utils.auth import get_current_user
from utils.file_storage import get_storage
from utils.email_service import send_payment_success_email
import stripe
import os
import time

router = APIRouter(prefix="/payment", tags=["Payment"])

# Configure Stripe
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
stripe.api_key = STRIPE_SECRET_KEY

# Frontend URL for redirects
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Subscription Plans Configuration
SUBSCRIPTION_PLANS = {
    "starter": {
        "name": "Clipo Starter",
        "price": 900,  # $9.00
        "description": "10 vidéos/mois, 1080p 30fps",
        "credits": 10,
        "features": [
            "10 vidéos par mois",
            "Export 1080p 30fps",
            "Analyse de score viral",
            "Support standard"
        ]
    },
    "pro": {
        "name": "Clipo Pro",
        "price": 2900,  # $29.00
        "description": "50 vidéos/mois, 1080p 60fps",
        "credits": 50,
        "features": [
            "50 vidéos par mois",
            "Export 1080p 60fps",
            "Analyse de score viral",
            "Support prioritaire",
            "Pas de watermark"
        ]
    },
    "agency": {
        "name": "Clipo Agency",
        "price": 8900,  # $89.00
        "description": "200 vidéos/mois, 2K 60fps",
        "credits": 200,
        "features": [
            "200 vidéos par mois",
            "Export 2K/4K 60fps",
            "Traitement prioritaire",
            "Support dédié"
        ]
    }
}

class CheckoutRequest(BaseModel):
    plan: str  # "starter", "pro", or "agency"

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a Stripe Checkout URL for selected plan with prefilled email"""
    
    plan = request.plan.lower()
    
    if plan not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Choose from: {', '.join(SUBSCRIPTION_PLANS.keys())}"
        )
    
    # Direct Stripe checkout links with email prefill
    STRIPE_CHECKOUT_LINKS = {
        "starter": os.getenv("STRIPE_STARTER_LINK", "https://buy.stripe.com/test_14A00k83E9K66uwcaecZa00"),
        "pro": os.getenv("STRIPE_PRO_LINK", "https://buy.stripe.com/test_aFafZigAa3lI9GI7TYcZa01"),
        "agency": os.getenv("STRIPE_AGENCY_LINK", "https://buy.stripe.com/test_5kQ00kcjUe0m1acfmqcZa02")
    }
    
    plan_config = SUBSCRIPTION_PLANS[plan]
    user_email = current_user['email']
    
    # Build checkout URL with prefilled email
    checkout_url = f"{STRIPE_CHECKOUT_LINKS[plan]}?prefilled_email={user_email}"
    
    print(f"💳 Created checkout URL for user {current_user['id']}: {plan} plan (${plan_config['price']/100}) - Email: {user_email}")
    
    return {"url": checkout_url}

@router.get("/plans")
async def get_plans():
    """Get available subscription plans"""
    return {
        "plans": SUBSCRIPTION_PLANS
    }

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        if endpoint_secret:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        else:
            # Dev mode without webhook signature verification
            event = stripe.Event.construct_from(
                stripe.util.json.loads(payload), stripe.api_key
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session_completed(session)
    
    elif event['type'] == 'checkout.session.expired':
        session = event['data']['object']
        print(f"⚠️ Checkout session expired for user {session.get('client_reference_id')}")

    return {"status": "success"}

def handle_checkout_session_completed(session):
    """Fulfill the purchase"""
    user_id = session.get('client_reference_id')
    plan = session.get('metadata', {}).get('plan', 'pro')
    
    if not user_id:
        user_id = session.get('metadata', {}).get('user_id')
        
    if user_id and plan in SUBSCRIPTION_PLANS:
        print(f"✅ Payment successful for user {user_id} - Plan: {plan}")
        storage = get_storage()
        
        plan_config = SUBSCRIPTION_PLANS[plan]
        
        try:
            user_id = int(user_id)
            user = storage.get_user_by_id(user_id)
            
            if user:
                # Calculate subscription dates
                now = datetime.now()
                end_date = now + timedelta(days=30)

                # Update user with new plan and credits
                storage.update_user(user_id, {
                    "plan": plan,
                    "credits": plan_config['credits'],
                    "is_verified": True,
                    "subscription_start_date": now.isoformat(),
                    "subscription_end_date": end_date.isoformat()
                })
                
                print(f"🎉 User {user_id} upgraded to {plan} plan with {plan_config['credits']} credits")
                
                # Send success email
                try:
                    send_payment_success_email(user['email'], user.get('name', 'User'))
                except Exception as e:
                    print(f"Failed to send success email: {e}")
                    
        except Exception as e:
            print(f"Error upgrading user: {e}")
    else:
        print(f"❌ Invalid user_id or plan in webhook: user={user_id}, plan={plan}")
