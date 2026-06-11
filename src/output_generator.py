import json
from pathlib import Path
from typing import List
from src.models import ProfessorCandidate, Recommendation, ShortlistOutput

def generate_output(candidates: List[ProfessorCandidate], output_path: str | Path):
    """
    Generates the final JSON output matching the required schema.
    """
    recommendations = []
    
    for c in candidates:
        # Determine fallback linked program
        linked_program = "Check department website for open positions"
        
        rec = Recommendation(
            name=c.name,
            institution=c.institution or "Unknown Institution",
            country=c.country_code or "Unknown",
            contact_email=None, # OpenAlex rarely provides email, requires scraping which is out of scope
            research_focus="Domain matched via " + (", ".join([p.title for p in c.recent_papers[:2]])),
            evidence=c.recent_papers,
            why_match=c.why_match or "Strong academic alignment.",
            tier=c.tier or "Target",
            linked_phd_program_or_open_position=linked_program,
            match_score=round(c.match_score, 1),
            pi_confidence=round(c.pi_confidence, 2),
            identity_confidence=round(c.identity_confidence, 2)
        )
        recommendations.append(rec)
        
    output = ShortlistOutput(recommendations=recommendations)
    
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(output.model_dump_json(indent=2))
        
    # Bonus: Generate CSV
    csv_path = path.with_suffix('.csv')
    import csv
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Institution", "Country", "Match Score", "Tier", "Why Match", "Top Paper Link"])
        for rec in recommendations:
            top_paper_link = rec.evidence[0].url if rec.evidence else ""
            writer.writerow([
                rec.name, 
                rec.institution, 
                rec.country, 
                rec.match_score, 
                rec.tier, 
                rec.why_match, 
                top_paper_link
            ])
    print(f"   Bonus CSV saved to {csv_path}")
