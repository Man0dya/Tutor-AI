import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DB = os.getenv("MONGODB_DB", "tutor_ai")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

APP_NAME = "Tutor AI API"
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Billing / Stripe (optional; enable if provided)
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_STANDARD = os.getenv("STRIPE_PRICE_STANDARD", "")
STRIPE_PRICE_PREMIUM = os.getenv("STRIPE_PRICE_PREMIUM", "")

# Privacy and PII handling configuration
# PRIVACY_MODE: 'STRICT' (reject inputs with PII everywhere) or 'BALANCED' (reject for content; redact in answers)
PRIVACY_MODE = os.getenv("PRIVACY_MODE", "BALANCED").upper()
REDACT_FEEDBACK = os.getenv("REDACT_FEEDBACK", "true").lower() == "true"
REDACT_CONTENT = os.getenv("REDACT_CONTENT", "true").lower() == "true"
