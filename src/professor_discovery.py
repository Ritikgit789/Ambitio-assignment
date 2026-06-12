import time
import requests
from typing import List, Dict
from tenacity import retry, wait_exponential, stop_after_attempt
from src.config import OPENALEX_BASE_URL, OPENALEX_EMAIL
from src.models import ProfessorCandidate, Paper

# Explicit rate limiting
SLEEP_BETWEEN_CALLS = 1

def get_headers() -> dict:
    headers = {}
    if OPENALEX_EMAIL:
        headers['mailto'] = OPENALEX_EMAIL
    return headers

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def search_works_by_concept(query: str, limit: int = 50) -> List[dict]:
    """
    Search OpenAlex works (papers) matching a specific concept or keyword query.
    We look for recent papers (e.g., from the last 3-5 years) to ensure freshness.
    """
    time.sleep(SLEEP_BETWEEN_CALLS)
    url = f"{OPENALEX_BASE_URL}/works"
    params = {
        "search": query,
        "filter": "publication_year:>2020",
        "per-page": limit,
        "sort": "cited_by_count:desc"
    }
    
    response = requests.get(url, params=params, headers=get_headers(), timeout=10)
    response.raise_for_status()
    return response.json().get('results', [])

def build_candidate_pool(interests: dict) -> List[ProfessorCandidate]:
    """
    Builds the initial candidate pool by:
    1. Searching for papers related to the primary areas and keywords.
    2. Extracting authors from those papers.
    """
    queries = interests.get("primary_areas", []) + interests.get("keywords", [])
    
    # Use a set to avoid duplicates based on OpenAlex ID
    candidate_dict: Dict[str, ProfessorCandidate] = {}
    
    for query in queries[:5]: # Increased from top 3 to top 5 queries to broaden the net
        works = search_works_by_concept(query, limit=40) # Increased from 20 to 40 papers per query
        
        for work in works:
            authorships = work.get("authorships", [])
            for authorship in authorships:
                author = authorship.get("author", {})
                author_id = author.get("id")
                
                if not author_id:
                    continue
                
                # Only keep authors if they aren't already in the pool
                if author_id not in candidate_dict:
                    institutions = authorship.get("institutions", [])
                    institution_name = institutions[0].get("display_name") if institutions else None
                    country_code = institutions[0].get("country_code") if institutions else None
                    
                    # Extract raw affiliations for later validation
                    raw_affiliations = [inst.get("display_name") for inst in institutions if inst.get("display_name")]
                    
                    candidate = ProfessorCandidate(
                        openalex_id=author_id,
                        name=author.get("display_name", "Unknown"),
                        institution=institution_name,
                        country_code=country_code,
                        raw_affiliations=raw_affiliations
                    )
                    candidate_dict[author_id] = candidate
                    
                # Append the paper to their recent_papers list
                paper_obj = Paper(
                    title=work.get("title", "Unknown Title"),
                    url=work.get("doi") or work.get("id"),
                    year=work.get("publication_year")
                )
                
                # Avoid adding the same paper twice if multiple queries yield the same paper
                existing_titles = [p.title for p in candidate_dict[author_id].recent_papers]
                if paper_obj.title not in existing_titles:
                    candidate_dict[author_id].recent_papers.append(paper_obj)
                    
            if len(candidate_dict) > 800:
                break # Hard cap to prevent hitting API rate limits during downstream processing
        if len(candidate_dict) > 800:
            break
            
    return list(candidate_dict.values())
