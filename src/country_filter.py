from typing import List
from src.models import ProfessorCandidate, StudentProfile

def filter_by_country(candidates: List[ProfessorCandidate], profile: StudentProfile) -> List[ProfessorCandidate]:
    """
    Hard filter to ensure candidates are affiliated with the target countries.
    Must guarantee 100% adherence.
    """
    if not profile.target_countries:
        return candidates # No filter applied if no countries specified
        
    # Convert to uppercase for matching (e.g. 'US', 'GB')
    target_countries = [c.upper() for c in profile.target_countries]
    
    filtered_candidates = []
    
    for candidate in candidates:
        if candidate.country_code and candidate.country_code.upper() in target_countries:
            filtered_candidates.append(candidate)
            
    return filtered_candidates
