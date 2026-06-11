from typing import List
from src.models import ProfessorCandidate

def generate_tiers(candidates: List[ProfessorCandidate]) -> List[ProfessorCandidate]:
    """
    Assigns a tier (Reach, Target, Safety) based on professor prestige (h-index)
    and match score.
    """
    for candidate in candidates:
        # Simple heuristic for tiers based on h-index and match score
        h_index = candidate.h_index or 0
        score = candidate.match_score
        
        if h_index > 40:
            candidate.tier = "Reach"
        elif h_index > 15:
            if score > 85:
                candidate.tier = "Target"
            else:
                candidate.tier = "Reach"
        else:
            if score > 80:
                candidate.tier = "Safety"
            else:
                candidate.tier = "Target"
                
    return candidates
