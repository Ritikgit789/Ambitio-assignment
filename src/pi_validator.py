import time
import requests
from typing import List
from tenacity import retry, wait_exponential, stop_after_attempt
from src.config import OPENALEX_BASE_URL, OPENALEX_EMAIL
from src.models import ProfessorCandidate
from src.professor_discovery import get_headers

SLEEP_BETWEEN_CALLS = 0.5

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def fetch_author_details(author_id: str) -> dict:
    time.sleep(SLEEP_BETWEEN_CALLS)
    response = requests.get(f"{author_id}", headers=get_headers(), timeout=10)
    response.raise_for_status()
    return response.json()

def validate_pis(candidates: List[ProfessorCandidate]) -> List[ProfessorCandidate]:
    """
    Validates whether candidates are likely PIs (Principal Investigators)
    rather than students or junior researchers.
    
    Since OpenAlex doesn't explicitly state "PhD Student" vs "Professor",
    we use heuristics based on publication history (h-index, works count, years active).
    """
    validated = []
    
    for candidate in candidates:
        try:
            author_data = fetch_author_details(candidate.openalex_id)
            
            # Extract metrics
            summary_stats = author_data.get("summary_stats", {})
            h_index = summary_stats.get("h_index", 0)
            works_count = author_data.get("works_count", 0)
            
            candidate.h_index = h_index
            candidate.citations = summary_stats.get("cited_by_count", 0)
            
            # Simple heuristic for PI Confidence
            # A PI typically has an h-index > 5 and > 10 papers.
            # If extremely low, likely a student or RA.
            if works_count < 5 or h_index < 2:
                candidate.pi_confidence = 0.1 # Likely a student/junior
            elif works_count >= 20 and h_index >= 10:
                candidate.pi_confidence = 0.9 # Likely a Professor
            elif works_count >= 10 and h_index >= 5:
                candidate.pi_confidence = 0.6 # Likely Assistant Prof / Postdoc
            else:
                candidate.pi_confidence = 0.3
                
            # Filter out obvious non-PIs
            if candidate.pi_confidence > 0.2:
                validated.append(candidate)
                
        except Exception as e:
            print(f"Error fetching details for {candidate.name}: {e}")
            # Keep them if we can't fetch, but with low confidence
            candidate.pi_confidence = 0.3
            validated.append(candidate)
            
    return validated
