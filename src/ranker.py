from typing import List
from src.models import ProfessorCandidate

def calculate_evidence_quality(candidate: ProfessorCandidate) -> float:
    # Cap at 5 papers, normalize to 0-1
    return min(len(candidate.recent_papers) / 5.0, 1.0)

def calculate_freshness(candidate: ProfessorCandidate) -> float:
    if not candidate.recent_papers:
        return 0.0
    years = [p.year for p in candidate.recent_papers if p.year is not None]
    if not years:
        return 0.0
    most_recent = max(years)
    # Assume current year is ~2024.
    if most_recent >= 2023:
        return 1.0
    elif most_recent == 2022:
        return 0.8
    elif most_recent == 2021:
        return 0.6
    else:
        return 0.3

def rank_candidates(candidates: List[ProfessorCandidate], top_k: int = 100) -> List[ProfessorCandidate]:
    """
    Final ranking formula:
    0.40 Match Score
    0.20 Evidence Quality
    0.15 PI Confidence
    0.15 Identity Confidence
    0.10 Freshness
    """
    
    def rank_score(c: ProfessorCandidate) -> float:
        # Normalize match score from 0-100 to 0-1
        normalized_match = c.match_score / 100.0
        
        evidence_quality = calculate_evidence_quality(c)
        freshness = calculate_freshness(c)
        
        score = (
            (0.40 * normalized_match) +
            (0.20 * evidence_quality) +
            (0.15 * c.pi_confidence) +
            (0.15 * c.identity_confidence) +
            (0.10 * freshness)
        )
        return score
        
    # Sort descending based on score
    candidates.sort(key=rank_score, reverse=True)
    
    return candidates[:top_k]
