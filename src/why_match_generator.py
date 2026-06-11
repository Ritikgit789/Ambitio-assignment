import time
import json
from typing import List
from tenacity import retry, wait_exponential, stop_after_attempt
import groq
from src.config import GROQ_API_KEY, GROQ_MODEL_NAME
from src.models import ProfessorCandidate, StudentProfile

client = groq.Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

SLEEP_BETWEEN_CALLS = 5

@retry(wait=wait_exponential(multiplier=1, min=5, max=30), stop=stop_after_attempt(5))
def generate_why_match_batch(candidates: List[ProfessorCandidate], profile: StudentProfile) -> dict:
    time.sleep(SLEEP_BETWEEN_CALLS)
    
    if not client:
        return {}
        
    batch_data = {}
    for c in candidates:
        batch_data[c.openalex_id] = {
            "name": c.name,
            "papers": [f"{p.title} ({p.year})" for p in c.recent_papers[:2]]
        }
        
    prompt = f"""
    You are an academic advisor. Write a concise, 2-3 sentence personalized explanation
    of why each professor is a good PhD supervisor match for the student.
    
    Student Profile:
    Interests: {profile.research_interests}
    Skills: {profile.skills}
    Projects: {profile.projects}
    
    Professors: {json.dumps(batch_data)}
    
    Instructions:
    - Directly reference at least one of the professor's actual papers.
    - Connect it specifically to the student's background/projects.
    - No generic praise. Be highly specific and academic.
    
    Return ONLY a JSON dictionary mapping the professor's ID to the text explanation.
    Example:
    {{
       "https://api.openalex.org/A123": "Dr. Smith's recent work on..."
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Failed Groq request: {e}")
        return {}

def add_why_match(candidates: List[ProfessorCandidate], profile: StudentProfile) -> List[ProfessorCandidate]:
    """
    Generates the 'why_match' reasoning for top candidates using Groq Llama 3 in batches.
    """
    batch_size = 20
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i+batch_size]
        print(f"      Processing why_match batch {i//batch_size + 1}/{(len(candidates)+batch_size-1)//batch_size}...")
        
        reasons_dict = generate_why_match_batch(batch, profile)
        
        for candidate in batch:
            candidate.why_match = reasons_dict.get(candidate.openalex_id, "Strong academic alignment.")
            
    return candidates
