import json
import time
from tenacity import retry, wait_exponential, stop_after_attempt
import groq
from src.config import GROQ_API_KEY, GROQ_MODEL_NAME
from src.models import StudentProfile

client = groq.Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

SLEEP_BETWEEN_CALLS = 2

@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
def extract_research_interests(profile: StudentProfile) -> dict:
    time.sleep(SLEEP_BETWEEN_CALLS)
    
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
    
    if not client:
        print("Groq client not initialized. Returning fallback.")
        return {"primary_areas": profile.research_interests, "secondary_areas": [], "keywords": profile.skills}
        
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        data = json.loads(response.choices[0].message.content)
        return {
            "primary_areas": data.get("primary_areas", []),
            "secondary_areas": data.get("secondary_areas", []),
            "keywords": data.get("keywords", [])
        }
    except Exception as e:
        print(f"Failed to decode JSON from Groq: {e}. Returning fallback.")
        return {
            "primary_areas": profile.research_interests,
            "secondary_areas": [],
            "keywords": profile.skills
        }
