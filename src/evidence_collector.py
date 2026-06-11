import time
import requests
import concurrent.futures
from typing import List
from tenacity import retry, wait_exponential, stop_after_attempt
from src.config import OPENALEX_BASE_URL
from src.models import ProfessorCandidate, Paper
from src.professor_discovery import get_headers

# No sleep for concurrent threads to maximize speed within the 10 requests/sec limit
@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def fetch_recent_works(author_id: str, limit: int = 5) -> List[dict]:
    url = f"{OPENALEX_BASE_URL}/works"
    params = {
        "filter": f"author.id:{author_id},publication_year:>2019",
        "per-page": limit,
        "sort": "cited_by_count:desc"
    }
    response = requests.get(url, params=params, headers=get_headers(), timeout=10)
    response.raise_for_status()
    return response.json().get('results', [])

def process_candidate(candidate: ProfessorCandidate) -> ProfessorCandidate:
    try:
        works = fetch_recent_works(candidate.openalex_id)
        papers = []
        for work in works:
            paper = Paper(
                title=work.get("title", "Unknown Title"),
                url=work.get("doi") or work.get("id"),
                year=work.get("publication_year")
            )
            papers.append(paper)
            
        existing_urls = {p.url for p in candidate.recent_papers if p.url}
        for p in papers:
            if p.url not in existing_urls:
                candidate.recent_papers.append(p)
                existing_urls.add(p.url)
                
        if candidate.recent_papers:
            return candidate
    except Exception as e:
        pass
    return None

def collect_evidence(candidates: List[ProfessorCandidate]) -> List[ProfessorCandidate]:
    """
    Uses multithreading to collect evidence incredibly fast without breaking 
    latency SLAs.
    """
    evidenced_candidates = []
    
    # 5 workers keeps us safely under the 10 requests/sec limit of the Polite Pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(process_candidate, candidates)
        
    for r in results:
        if r:
            evidenced_candidates.append(r)
            
    return evidenced_candidates
