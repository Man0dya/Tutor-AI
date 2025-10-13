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
REDACT_QUESTIONS = os.getenv("REDACT_QUESTIONS", "true").lower() == "true"

# Question generation performance tuning
QS_BATCH_MODE = os.getenv("QS_BATCH_MODE", "true").lower() == "true"  # Use single-call batch generation
QS_SUMMARIZE_INPUT = os.getenv("QS_SUMMARIZE_INPUT", "true").lower() == "true"  # Summarize content before sending
QS_MAX_EXPLANATION_SENTENCES = int(os.getenv("QS_MAX_EXPLANATION_SENTENCES", "1"))  # Keep explanations short
QS_DEFAULT_MODEL = os.getenv("QS_DEFAULT_MODEL", "gemini-2.5-flash")  # Fast model variant

# Analytics toggle
ENABLE_ANALYTICS = os.getenv("ENABLE_ANALYTICS", "true").lower() == "true"
