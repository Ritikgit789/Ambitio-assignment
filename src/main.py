import argparse
import sys
import os

# Ensure src module can be found if running from root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.profile_parser import load_student_profile
from src.research_interest_extractor import extract_research_interests
from src.professor_discovery import build_candidate_pool
from src.pi_validator import validate_pis
from src.country_filter import filter_by_country
from src.identity_validator import validate_identities
from src.evidence_collector import collect_evidence
from src.domain_classifier import filter_by_domain
from src.match_scorer import calculate_scores
from src.tier_generator import generate_tiers
from src.why_match_generator import add_why_match
from src.ranker import rank_candidates
from src.output_generator import generate_output

def main():
    parser = argparse.ArgumentParser(description="PhD Shortlist Builder")
    parser.add_argument("--input", required=True, help="Path to input student profile JSON")
    parser.add_argument("--output", default="sample_output/student_001.json", help="Path to output JSON")
    args = parser.parse_args()

    print("1. Loading Profile...")
    profile = load_student_profile(args.input)
    
    print("2. Extracting Interests...")
    interests = extract_research_interests(profile)
    print(f"   Extracted Primary Areas: {interests.get('primary_areas')}")
    
    print("3. Discovering Candidates...")
    candidates = build_candidate_pool(interests)
    print(f"   Discovered {len(candidates)} initial candidates.")
    
    print("4. PI Validation...")
    candidates = validate_pis(candidates)
    print(f"   {len(candidates)} candidates remain after PI validation.")
    
    print("5. Country Filtering...")
    candidates = filter_by_country(candidates, profile)
    print(f"   {len(candidates)} candidates remain after country filtering.")
    
    print("6. Identity Validation...")
    candidates = validate_identities(candidates)
    print(f"   {len(candidates)} candidates remain after identity validation.")
    
    print("7. Evidence Collection...")
    candidates = collect_evidence(candidates)
    print(f"   {len(candidates)} candidates remain after evidence collection.")
    
    print("8. Domain Classification...")
    candidates = filter_by_domain(candidates, profile)
    print(f"   {len(candidates)} candidates remain after domain classification.")
    
    print("9. Match Scoring...")
    candidates = calculate_scores(candidates, profile)
    
    print("10. Tier Generation...")
    candidates = generate_tiers(candidates)
    
    print("11. Why Match Generation...")
    candidates = add_why_match(candidates, profile)
    
    print("12. Ranking...")
    candidates = rank_candidates(candidates, top_k=50) # Targeting 50 for max precision
    print(f"   Top {len(candidates)} candidates selected.")
    
    print("13. Generating Output...")
    generate_output(candidates, args.output)
    print(f"   Output saved to {args.output}")

if __name__ == "__main__":
    main()
