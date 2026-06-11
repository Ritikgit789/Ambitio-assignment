import csv
import json
from pathlib import Path
from collections import defaultdict

class FeedbackLoop:
    def __init__(self, feedback_db_path: str = "data/feedback_db.json"):
        self.feedback_db_path = Path(feedback_db_path)
        self.outcomes = self._load_db()
        
    def _load_db(self) -> dict:
        if self.feedback_db_path.exists():
            with open(self.feedback_db_path, 'r') as f:
                return json.load(f)
        return {
            "supervisor_scores": defaultdict(float), # Positive outcomes increase score, negative decrease
            "blacklisted_supervisors": [], # e.g. NOT_RECRUITING
            "wrong_domain_flags": defaultdict(int)
        }
        
    def save_db(self):
        # Convert defaultdict to dict for JSON serialization
        db_to_save = {
            "supervisor_scores": dict(self.outcomes["supervisor_scores"]),
            "blacklisted_supervisors": list(set(self.outcomes["blacklisted_supervisors"])),
            "wrong_domain_flags": dict(self.outcomes["wrong_domain_flags"])
        }
        with open(self.feedback_db_path, 'w') as f:
            json.dump(db_to_save, f, indent=2)

    def ingest_csv(self, csv_path: str):
        """
        Ingests the outcome stream CSV and updates the feedback database.
        Expected columns: student_id, supervisor_id, institution, area, sent_at, outcome
        """
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Map column names, handling potential whitespace
            fieldnames = [name.strip() for name in reader.fieldnames or []]
            reader.fieldnames = fieldnames
            
            for row in reader:
                supervisor_id = row.get("supervisor_id", "").strip()
                outcome = row.get("outcome", "").strip().upper()
                
                if not supervisor_id or not outcome:
                    continue
                    
                # Process the outcome and update weights
                if outcome in ["ADMIT", "INTERVIEW", "POSITIVE_REPLY"]:
                    # Positive signals heavily boost this supervisor's ranking in the future
                    self.outcomes["supervisor_scores"][supervisor_id] = self.outcomes["supervisor_scores"].get(supervisor_id, 0.0) + 1.0
                elif outcome == "REJECT":
                    # Rejections slightly penalize, but not severely (could be capacity or student profile)
                    self.outcomes["supervisor_scores"][supervisor_id] = self.outcomes["supervisor_scores"].get(supervisor_id, 0.0) - 0.2
                elif outcome == "NOT_RECRUITING":
                    # Critical signal: Blacklist them for the current cycle
                    self.outcomes["blacklisted_supervisors"].append(supervisor_id)
                elif outcome == "WRONG_PERSON":
                    # Critical signal: Penalize heavily or flag to improve identity validation
                    self.outcomes["supervisor_scores"][supervisor_id] = self.outcomes["supervisor_scores"].get(supervisor_id, 0.0) - 2.0
                    self.outcomes["wrong_domain_flags"][supervisor_id] = self.outcomes["wrong_domain_flags"].get(supervisor_id, 0) + 1
                    
        self.save_db()
        print(f"Ingested CSV and updated feedback database at {self.feedback_db_path}")

    def apply_feedback_to_candidates(self, candidates):
        """
        Adjusts candidate match_scores and removes blacklisted candidates
        based on historical outcome data.
        """
        filtered_candidates = []
        for c in candidates:
            if c.openalex_id in self.outcomes["blacklisted_supervisors"]:
                print(f"Dropping {c.name} ({c.openalex_id}) due to previous NOT_RECRUITING status.")
                continue
                
            # Apply historical score boost/penalty
            historical_adjustment = self.outcomes["supervisor_scores"].get(c.openalex_id, 0.0)
            
            # Scale adjustment (e.g., each point is worth 5 match score points)
            c.match_score += (historical_adjustment * 5.0)
            
            # Cap at 100 and floor at 0
            c.match_score = max(0.0, min(100.0, c.match_score))
            
            filtered_candidates.append(c)
            
        return filtered_candidates

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingest Feedback CSV")
    parser.add_argument("--csv", required=True, help="Path to outcomes CSV")
    args = parser.parse_args()
    
    loop = FeedbackLoop()
    loop.ingest_csv(args.csv)
