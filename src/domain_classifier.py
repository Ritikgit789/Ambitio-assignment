import json
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
def classify_domain(candidate: ProfessorCandidate, profile: StudentProfile) -> float:
    time.sleep(SLEEP_BETWEEN_CALLS)
    
    paper_titles = [p.title for p in candidate.recent_papers]
    
    prompt = f"""
    You are a strict academic domain classifier. 
    Compare the student's research interests with the professor's recent publications.
    
    Student Interests: {profile.research_interests}
    Student Skills: {profile.skills}
    
    Professor's Recent Papers: {paper_titles}
    
    Assess if the professor's work tightly aligns with the student's subfield.
    Return ONLY a JSON object with this exact structure:
    {{
        "relevance_score": float # 0.0 to 1.0
    }}
    Be strict. If the domain is broadly similar but the subfield is wrong, score < 0.5.
    """
    
    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            temperature=0.0
        )
    )
    
    try:
        data = json.loads(response.text)
        return float(data.get("relevance_score", 0.0))
    except (json.JSONDecodeError, ValueError):
        return 0.5

def filter_by_domain(candidates: List[ProfessorCandidate], profile: StudentProfile) -> List[ProfessorCandidate]:
    """
    Filters candidates by domain relevance using Gemini.
    Reject candidates with a score < 0.6.
    """
    relevant_candidates = []
    
    for candidate in candidates:
        score = classify_domain(candidate, profile)
        candidate.domain_relevance = score
        
        if score >= 0.6:
            relevant_candidates.append(candidate)
            
    return relevant_candidates
