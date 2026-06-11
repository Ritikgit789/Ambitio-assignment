from typing import List
from src.models import ProfessorCandidate, StudentProfile

def calculate_scores(candidates: List[ProfessorCandidate], profile: StudentProfile) -> List[ProfessorCandidate]:
    """
    Generates a hybrid match_score (0-100) combining:
    - Domain Relevance (from Gemini)
    - Publication Quality (h_index, citations)
    - Identity & PI Confidence
    """
    for candidate in candidates:
        # Base score from domain relevance (0-100 scale)
        base_score = candidate.domain_relevance * 100
        
        # Bonus for high PI confidence
        pi_bonus = candidate.pi_confidence * 10
        
        # Penalty for low identity confidence
        identity_penalty = (1.0 - candidate.identity_confidence) * 20
        
        # Cap final score at 100
        final_score = base_score + pi_bonus - identity_penalty
        candidate.match_score = max(0.0, min(100.0, final_score))
        
    return candidates
