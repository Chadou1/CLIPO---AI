import stripe
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PRICE_IDS = {
    "starter": os.getenv("STRIPE_PRICE_ID_STARTER"),
    "pro": os.getenv("STRIPE_PRICE_ID_PRO"),
    "agency": os.getenv("STRIPE_PRICE_ID_AGENCY")
}

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

def create_checkout_session(user_email: str, plan: str, user_id: int):
    """Create Stripe checkout session"""
    
    if plan not in PRICE_IDS:
        raise ValueError(f"Invalid plan: {plan}")
    
    session = stripe.checkout.Session.create(
        customer_email=user_email,
        payment_method_types=['card'],
        line_items=[{
            'price': PRICE_IDS[plan],
            'quantity': 1,
        }],
        mode='subscription',
        success_url=f"{FRONTEND_URL}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{FRONTEND_URL}/pricing",
        metadata={
            'user_id': user_id,
            'plan': plan
        }
    )
    
    return session

def create_customer_portal_session(customer_id: str):
    """Create customer portal session for managing subscription"""
    
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=f"{FRONTEND_URL}/account"
    )
    
    return session

def get_subscription(subscription_id: str):
    """Get subscription details"""
    
    return stripe.Subscription.retrieve(subscription_id)

def cancel_subscription(subscription_id: str):
    """Cancel subscription"""
    
    return stripe.Subscription.delete(subscription_id)
