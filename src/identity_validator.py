from typing import List
from src.models import ProfessorCandidate

def validate_identities(candidates: List[ProfessorCandidate]) -> List[ProfessorCandidate]:
    """
    Solves same-name collisions.
    Because our discovery pipeline uses OpenAlex author IDs directly from works, 
    we bypass the typical string-matching same-name collision problem.
    However, we calculate identity_confidence based on profile completeness.
    """
    validated = []
    
    for candidate in candidates:
        confidence = 0.5 # Base confidence
        
        # If they have a clear institution, confidence goes up
        if candidate.institution:
            confidence += 0.3
            
        # If they have affiliations listed
        if candidate.raw_affiliations:
            confidence += 0.1
            
        # If they have an OpenAlex ID, we are certain of the entity (though OpenAlex itself might merge authors)
        if candidate.openalex_id:
            confidence += 0.1
            
        candidate.identity_confidence = min(1.0, confidence)
        
        # Reject low confidence (e.g., profiles with no institution or affiliations)
        if candidate.identity_confidence >= 0.7:
            validated.append(candidate)
            
    return validated
