from mailjet_rest import Client
import os
import random

# Configure MailJet with API credentials
MAILJET_API_KEY = os.getenv("MAILJET_API_KEY", "6ffee449330f1af58fa2271bdc87e931")
MAILJET_SECRET_KEY = os.getenv("MAILJET_SECRET_KEY", "e5b8bcd26f61feac60b4710d32390ef5")
FROM_EMAIL = os.getenv("FROM_EMAIL", "chadou.pro1@gmail.com")
FROM_NAME = "Clipo AI"

# Initialize MailJet client
mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_SECRET_KEY), version='v3.1')

def generate_code() -> str:
    """Generate 8-digit verification code"""
    return ''.join([str(random.randint(0, 9)) for _ in range(8)])

def send_verification_email(to_email: str, code: str):
    """Send email verification code"""
    try:
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": FROM_EMAIL,
                        "Name": FROM_NAME
                    },
                    "To": [
                        {
                            "Email": to_email
                        }
                    ],
                    "Subject": "Verify your Clipo account",
                    "HTMLPart": f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
                            .container {{ max-width: 600px; margin: 50px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                            h1 {{ color: #8b5cf6; margin-bottom: 20px; }}
                            .code {{ font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #8b5cf6; background: #f3f4f6; padding: 20px; text-align: center; border-radius: 8px; margin: 30px 0; }}
                            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 14px; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>🎬 Verify Your Email</h1>
                            <p>Welcome to Clipo AI! Please use the code below to verify your email address:</p>
                            <div class="code">{code}</div>
                            <p>This code will expire in 10 minutes.</p>
                            <p>If you didn't create an account, please ignore this email.</p>
                            <div class="footer">
                                <p>Best regards,<br>The Clipo Team</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                }
            ]
        }
        
        result = mailjet.send.create(data=data)
        if result.status_code == 200:
            print(f"✅ Verification email sent to {to_email}")
            return True
        else:
            print(f"❌ Failed to send verification email: {result.status_code} - {result.json()}")
            return False
    except Exception as e:
        print(f"❌ Failed to send verification email: {str(e)}")
        return False

def send_password_reset_email(to_email: str, code: str):
    """Send password reset code"""
    try:
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": FROM_EMAIL,
                        "Name": FROM_NAME
                    },
                    "To": [
                        {
                            "Email": to_email
                        }
                    ],
                    "Subject": "Reset your Clipo password",
                    "HTMLPart": f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
                            .container {{ max-width: 600px; margin: 50px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                            h1 {{ color: #8b5cf6; margin-bottom: 20px; }}
                            .code {{ font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #8b5cf6; background: #f3f4f6; padding: 20px; text-align: center; border-radius: 8px; margin: 30px 0; }}
                            .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; margin: 20px 0; }}
                            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 14px; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>🔐 Reset Your Password</h1>
                            <p>We received a request to reset your password. Use the code below:</p>
                            <div class="code">{code}</div>
                            <p>This code will expire in 10 minutes.</p>
                            <div class="warning">
                                <strong>⚠️ Security Notice:</strong> If you didn't request a password reset, please ignore this email. Your password will remain unchanged.
                            </div>
                            <div class="footer">
                                <p>Best regards,<br>The Clipo Team</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                }
            ]
        }
        
        result = mailjet.send.create(data=data)
        if result.status_code == 200:
            print(f"✅ Password reset email sent to {to_email}")
            return True
        else:
            print(f"❌ Failed to send password reset email: {result.status_code} - {result.json()}")
            return False
    except Exception as e:
        print(f"❌ Failed to send password reset email: {str(e)}")
        return False

def send_welcome_email(to_email: str, name: str = ""):
    """Send welcome email to verified user"""
    try:
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": FROM_EMAIL,
                        "Name": FROM_NAME
                    },
                    "To": [
                        {
                            "Email": to_email
                        }
                    ],
                    "Subject": "Welcome to Clipo AI! 🎬",
                    "HTMLPart": f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
                            .container {{ max-width: 600px; margin: 50px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                            h1 {{ color: #8b5cf6; margin-bottom: 20px; }}
                            .credits {{ background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%); color: white; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
                            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 14px; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>🎬 Welcome to Clipo AI!</h1>
                            <p>Hi{' ' + name if name else ''},</p>
                            <p>Your email has been verified! You're now ready to create viral clips with AI.</p>
                            <div class="credits">
                                <h2 style="margin: 0;">🎁 3 FREE Credits</h2>
                                <p style="margin: 10px 0 0 0;">Start creating your first viral clips now!</p>
                            </div>
                            <p>Upload your first video and let our AI find the best moments!</p>
                            <div class="footer">
                                <p>Best regards,<br>The Clipo Team</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                }
            ]
        }
        
        result = mailjet.send.create(data=data)
        if result.status_code == 200:
            print(f"✅ Welcome email sent to {to_email}")
            return True
        else:
            print(f"❌ Failed to send welcome email: {result.status_code} - {result.json()}")
            return False
    except Exception as e:
        print(f"❌ Failed to send welcome email: {str(e)}")
        return False
def send_payment_success_email(to_email: str, name: str = ""):
    """Send payment success email"""
    try:
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": FROM_EMAIL,
                        "Name": FROM_NAME
                    },
                    "To": [
                        {
                            "Email": to_email
                        }
                    ],
                    "Subject": "Payment Successful! Welcome to PRO 🚀",
                    "HTMLPart": f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
                            .container {{ max-width: 600px; margin: 50px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                            h1 {{ color: #8b5cf6; margin-bottom: 20px; }}
                            .success-box {{ background: #ecfdf5; border: 1px solid #10b981; color: #065f46; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
                            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 14px; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>🚀 You are now a PRO!</h1>
                            <p>Hi{{ ' ' + name if name else '' }},</p>
                            <p>Thank you for your purchase. Your account has been upgraded to the <strong>Agency Plan</strong>.</p>
                            <div class="success-box">
                                <h2 style="margin: 0;">✅ Payment Confirmed</h2>
                                <p style="margin: 10px 0 0 0;">You now have UNLIMITED credits!</p>
                            </div>
                            <p>Go to your dashboard and start creating viral clips without limits.</p>
                            <div class="footer">
                                <p>Best regards,<br>The Clipo Team</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                }
            ]
        }
        
        result = mailjet.send.create(data=data)
        if result.status_code == 200:
            print(f"✅ Payment success email sent to {to_email}")
            return True
        else:
            print(f"❌ Failed to send payment success email: {result.status_code} - {result.json()}")
            return False
    except Exception as e:
        print(f"❌ Failed to send payment success email: {str(e)}")
        return False

def send_payment_reminder_email(to_email: str, name: str = ""):
    """Send payment reminder email (abandoned cart)"""
    try:
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": FROM_EMAIL,
                        "Name": FROM_NAME
                    },
                    "To": [
                        {
                            "Email": to_email
                        }
                    ],
                    "Subject": "Don't miss out on PRO features! 🌟",
                    "HTMLPart": f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
                            .container {{ max-width: 600px; margin: 50px auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                            h1 {{ color: #8b5cf6; margin-bottom: 20px; }}
                            .btn {{ display: inline-block; background: #8b5cf6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; margin-top: 20px; }}
                            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #e5e7eb; color: #6b7280; font-size: 14px; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1>👋 Still interested in PRO?</h1>
                            <p>Hi{{ ' ' + name if name else '' }},</p>
                            <p>We noticed you started the checkout process but didn't finish.</p>
                            <p>Unlock unlimited clips, 1080p exports, and priority processing today!</p>
                            <center>
                                <a href="https://Clipo.ai/pricing" class="btn">Complete Your Upgrade</a>
                            </center>
                            <div class="footer">
                                <p>Best regards,<br>The Clipo Team</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                }
            ]
        }
        
        result = mailjet.send.create(data=data)
        if result.status_code == 200:
            print(f"✅ Payment reminder email sent to {to_email}")
            return True
        else:
            print(f"❌ Failed to send payment reminder email: {result.status_code} - {result.json()}")
            return False
    except Exception as e:
        print(f"❌ Failed to send payment reminder email: {str(e)}")
        return False
