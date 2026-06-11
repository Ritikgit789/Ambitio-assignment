from pydantic import BaseModel, Field
from typing import List, Optional

class StudentProfile(BaseModel):
    name: Optional[str] = None
    education_history: List[dict] = []
    skills: List[str] = []
    projects: List[dict] = []
    publications: List[dict] = []
    research_interests: List[str] = []
    target_countries: List[str] = []
    target_intake: Optional[str] = None
    intro_call_summary: Optional[str] = None
    raw_resume_text: Optional[str] = None

class Paper(BaseModel):
    title: str
    url: Optional[str] = None
    year: Optional[int] = None

class Grant(BaseModel):
    title: str
    url: Optional[str] = None

class ProfessorCandidate(BaseModel):
    openalex_id: str
    name: str
    institution: Optional[str] = None
    country_code: Optional[str] = None
    concepts: List[str] = []
    recent_papers: List[Paper] = []
    grants: List[Grant] = []
    h_index: Optional[int] = None
    citations: Optional[int] = None
    
    # Computed metrics
    pi_confidence: float = 0.0
    identity_confidence: float = 1.0 # default to 1.0 if not disambiguated
    domain_relevance: float = 0.0
    match_score: float = 0.0
    why_match: Optional[str] = None
    tier: Optional[str] = None
    
    # Raw metadata from OpenAlex for identity/pi resolution
    raw_affiliations: List[str] = []

class Recommendation(BaseModel):
    name: str
    institution: str
    country: str
    contact_email: Optional[str] = None
    research_focus: str
    evidence: List[Paper] = []
    why_match: str
    tier: str
    linked_phd_program_or_open_position: str
    match_score: float
    pi_confidence: float
    identity_confidence: float

class ShortlistOutput(BaseModel):
    recommendations: List[Recommendation]
