import json
import time
from tenacity import retry, wait_exponential, stop_after_attempt
import google.generativeai as genai
from src.config import GEMINI_API_KEY, GEMINI_MODEL_NAME
from src.models import StudentProfile

# Configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Using Explicit sleep as requested
SLEEP_BETWEEN_CALLS = 2

@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
def extract_research_interests(profile: StudentProfile) -> dict:
    """
    Uses Gemini to extract structured primary areas, secondary areas, and keywords
    from the student profile to seed the OpenAlex discovery phase.
    """
    time.sleep(SLEEP_BETWEEN_CALLS)  # Explicit rate limiting
    
    prompt = f"""
    You are an expert academic advisor. Analyze the following student profile and extract their research interests.
    Return ONLY a JSON object with this exact structure:
    {{
        "primary_areas": ["string"],
        "secondary_areas": ["string"],
        "keywords": ["string"]
    }}
    
    Student Profile:
    Research Interests: {profile.research_interests}
    Skills: {profile.skills}
    Projects: {profile.projects}
    Intro Call Summary: {profile.intro_call_summary}
    Resume Text: {profile.raw_resume_text}
    """
    
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    
    # We use response_mime_type="application/json" if supported, but to be safe across gemini versions,
    # we can also just parse the text. Let's use the standard text generation and parse.
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.1
        )
    )
    
    try:
        data = json.loads(response.text)
        # Validate structure loosely
        return {
            "primary_areas": data.get("primary_areas", []),
            "secondary_areas": data.get("secondary_areas", []),
            "keywords": data.get("keywords", [])
        }
    except json.JSONDecodeError:
        print("Failed to decode JSON from Gemini. Returning fallback.")
        return {
            "primary_areas": profile.research_interests,
            "secondary_areas": [],
            "keywords": profile.skills
        }
