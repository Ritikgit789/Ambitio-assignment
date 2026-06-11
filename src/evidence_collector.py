import time
import requests
from typing import List
from tenacity import retry, wait_exponential, stop_after_attempt
from src.config import OPENALEX_BASE_URL
from src.models import ProfessorCandidate, Paper
from src.professor_discovery import get_headers

SLEEP_BETWEEN_CALLS = 0.5

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def fetch_recent_works(author_id: str, limit: int = 5) -> List[dict]:
    time.sleep(SLEEP_BETWEEN_CALLS)
    url = f"{OPENALEX_BASE_URL}/works"
    params = {
        "filter": f"author.id:{author_id},publication_year:>2019",
        "per-page": limit,
        "sort": "cited_by_count:desc"
    }
    response = requests.get(url, params=params, headers=get_headers(), timeout=10)
    response.raise_for_status()
    return response.json().get('results', [])

def collect_evidence(candidates: List[ProfessorCandidate]) -> List[ProfessorCandidate]:
    """
    For every surviving professor, collect top recent papers.
    Reject candidates without sufficient evidence.
    """
    evidenced_candidates = []
    
    for candidate in candidates:
        works = fetch_recent_works(candidate.openalex_id)
        
        papers = []
        for work in works:
            paper = Paper(
                title=work.get("title", "Unknown Title"),
                url=work.get("doi") or work.get("id"),
                year=work.get("publication_year")
            )
            papers.append(paper)
            
        # Combine with papers found during discovery (deduplicate)
        existing_urls = {p.url for p in candidate.recent_papers if p.url}
        for p in papers:
            if p.url not in existing_urls:
                candidate.recent_papers.append(p)
                existing_urls.add(p.url)
                
        # Must have at least 1 piece of evidence to survive
        if candidate.recent_papers:
            evidenced_candidates.append(candidate)
            
    return evidenced_candidates
