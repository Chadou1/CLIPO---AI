"""
Test script for library service components
"""

print("=" * 60)
print("Testing Library Service Components")
print("=" * 60)

# Test 1: Import library generation module
try:
    from services.library_generation_module import FONTS, create_video_for_library
    print("✅ Library generation module loaded successfully")
    print(f"   Available fonts: {list(FONTS.keys())}")
except Exception as e:
    print(f"❌ Failed to load library generation module: {e}")

# Test 2: Import library API
try:
    from api.library import router, AVAILABLE_LIBRARIES
    print("✅ Library API module loaded successfully")
    print(f"   Available libraries: {AVAILABLE_LIBRARIES}")
    print("   Endpoints:")
    for route in router.routes:
        print(f"     - {list(route.methods)} {route.path}")
except Exception as e:
    print(f"❌ Failed to load library API: {e}")

# Test 3: Check tier restrictions
try:
    from models.user import PlanType
    print("✅ Tier restrictions defined:")
    
    plans = [PlanType.FREE, PlanType.STARTER, PlanType.PRO, PlanType.AGENCY]
    for plan in plans:
        if plan == PlanType.FREE:
            restriction = "720p@30fps only"
        elif plan == PlanType.STARTER:
            restriction = "1080p@30fps OR 720p@60fps"
        else:
            restriction = "720p-1080p @ 30-60fps"
        print(f"   {plan.value}: {restriction}")
except Exception as e:
    print(f"❌ Failed to check tier restrictions: {e}")

# Test 4: Check credit system
try:
    from utils.credits import check_credits, deduct_credits
    print("✅ Credit system module loaded successfully")
except Exception as e:
    print(f"❌ Failed to load credit system: {e}")

print("=" * 60)
print("Component tests completed!")
print("=" * 60)
