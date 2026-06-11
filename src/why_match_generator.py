import time
from typing import List
from tenacity import retry, wait_exponential, stop_after_attempt
import google.generativeai as genai
from src.config import GEMINI_API_KEY, GEMINI_MODEL_NAME
from src.models import ProfessorCandidate, StudentProfile

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SLEEP_BETWEEN_CALLS = 2

@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
def generate_why_match(candidate: ProfessorCandidate, profile: StudentProfile) -> str:
    time.sleep(SLEEP_BETWEEN_CALLS)
    
    paper_titles = [f"{p.title} ({p.year})" for p in candidate.recent_papers]
    
    prompt = f"""
    You are an academic advisor. Write a concise, 2-3 sentence personalized explanation
    of why {candidate.name} is a good PhD supervisor match for the student.
    
    Student Profile:
    Interests: {profile.research_interests}
    Skills: {profile.skills}
    Projects: {profile.projects}
    
    Professor's Recent Papers: {paper_titles}
    
    Instructions:
    - Directly reference at least one of the professor's actual papers.
    - Connect it specifically to the student's background/projects.
    - No generic praise. Be highly specific and academic.
    """
    
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0.3
        )
    )
    
    return response.text.strip()

def add_why_match(candidates: List[ProfessorCandidate], profile: StudentProfile) -> List[ProfessorCandidate]:
    """
    Generates the 'why_match' reasoning for top candidates.
    To save API costs and time, we assume candidates are already filtered.
    """
    for candidate in candidates:
        candidate.why_match = generate_why_match(candidate, profile)
        
    return candidates
