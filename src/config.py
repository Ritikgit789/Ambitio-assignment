import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# OpenAlex specific configuration
# Including an email puts you in the "polite pool" with much better rate limits.
OPENALEX_EMAIL = os.getenv("OPENALEX_EMAIL")
OPENALEX_BASE_URL = "https://api.openalex.org"

# Ensure API keys are present if required (can also handle gracefully)
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is not set. The Gemini calls will fail.")
if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY is not set. Groq calls will fail.")

# Models
GEMINI_MODEL_NAME = "gemini-2.5-flash-lite"
GROQ_MODEL_NAME = "llama-3.1-8b-instant"
