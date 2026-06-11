import time
import requests
from typing import List
from tenacity import retry, wait_exponential, stop_after_attempt
from src.config import OPENALEX_BASE_URL, OPENALEX_EMAIL
from src.models import ProfessorCandidate
from src.professor_discovery import get_headers

SLEEP_BETWEEN_CALLS = 1

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def fetch_authors_batch(author_ids: List[str]) -> List[dict]:
    time.sleep(SLEEP_BETWEEN_CALLS)
    
    # Extract the raw ID part (A123...)
    clean_ids = [aid.split('/')[-1] for aid in author_ids if aid]
    filter_str = "|".join(clean_ids)
    
    url = f"{OPENALEX_BASE_URL}/authors"
    params = {
        "filter": f"openalex_id:{filter_str}",
        "per-page": len(clean_ids)
    }
    
    response = requests.get(url, params=params, headers=get_headers(), timeout=10)
    response.raise_for_status()
    return response.json().get('results', [])

def validate_pis(candidates: List[ProfessorCandidate]) -> List[ProfessorCandidate]:
    """
    Validates whether candidates are likely PIs by fetching author profiles in batches.
    """
    validated = []
    batch_size = 50 # OpenAlex allows up to 50 filters
    
    for i in range(0, len(candidates), batch_size):
        batch = candidates[i:i+batch_size]
        author_ids = [c.openalex_id for c in batch]
        
        try:
            results = fetch_authors_batch(author_ids)
            # Map results by full OpenAlex URL ID
            author_map = {res.get("id"): res for res in results}
            
            for candidate in batch:
                author_data = author_map.get(candidate.openalex_id, {})
                
                # Extract metrics
                summary_stats = author_data.get("summary_stats", {})
                h_index = summary_stats.get("h_index", 0)
                works_count = author_data.get("works_count", 0)
                
                candidate.h_index = h_index
                candidate.citations = summary_stats.get("cited_by_count", 0)
                
                if works_count < 5 or h_index < 2:
                    candidate.pi_confidence = 0.1
                elif works_count >= 20 and h_index >= 10:
                    candidate.pi_confidence = 0.9
                elif works_count >= 10 and h_index >= 5:
                    candidate.pi_confidence = 0.6
                else:
                    candidate.pi_confidence = 0.3
                    
                if candidate.pi_confidence > 0.2:
                    validated.append(candidate)
                    
        except Exception as e:
            print(f"Error fetching batch: {e}")
            for c in batch:
                c.pi_confidence = 0.3
                validated.append(c)
            
    return validated
