import json
import time
from typing import List
from tenacity import retry, wait_exponential, stop_after_attempt
import google.generativeai as genai
from src.config import GEMINI_API_KEY, GEMINI_MODEL_NAME
from src.models import ProfessorCandidate, StudentProfile

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SLEEP_BETWEEN_CALLS = 5

@retry(wait=wait_exponential(multiplier=1, min=5, max=30), stop=stop_after_attempt(5))
def classify_domain_batch(candidates: List[ProfessorCandidate], profile: StudentProfile) -> dict:
    time.sleep(SLEEP_BETWEEN_CALLS)
    
    batch_data = {}
    for c in candidates:
        # Pass up to 3 papers to keep prompt size manageable
        batch_data[c.openalex_id] = [p.title for p in c.recent_papers[:3]]
        
    prompt = f"""
    You are a strict academic domain classifier. 
    Compare the student's research interests with each professor's recent publications.
    
    Student Interests: {profile.research_interests}
    Student Skills: {profile.skills}
    
    Professors and their papers: 
    {json.dumps(batch_data)}
    
    Assess if the professor's work tightly aligns with the student's subfield.
    Return ONLY a JSON object mapping the professor's ID to their relevance score (float 0.0 to 1.0).
    Example:
    {{
        "https://api.openalex.org/A123": 0.8,
        "https://api.openalex.org/A456": 0.2
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
        return json.loads(response.text)
    except (json.JSONDecodeError, ValueError):
        return {}

def filter_by_domain(candidates: List[ProfessorCandidate], profile: StudentProfile) -> List[ProfessorCandidate]:
    """
    Filters candidates by domain relevance using Gemini.
    Uses batching to avoid API rate limits.
    Reject candidates with a score < 0.6.
    """
    relevant_candidates = []
    batch_size = 40 # Batching 40 candidates per LLM call
    
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i+batch_size]
        print(f"      Processing domain batch {i//batch_size + 1}/{(len(candidates)+batch_size-1)//batch_size}...")
        
        scores_dict = classify_domain_batch(batch, profile)
        
        for candidate in batch:
            # Default to 0.5 if LLM fails to return a score for them
            score = float(scores_dict.get(candidate.openalex_id, 0.5))
            candidate.domain_relevance = score
            
            if score >= 0.6:
                relevant_candidates.append(candidate)
                
    return relevant_candidates
