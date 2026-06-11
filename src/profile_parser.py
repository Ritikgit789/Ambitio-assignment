import json
from pathlib import Path
from src.models import StudentProfile

def load_student_profile(file_path: str | Path) -> StudentProfile:
    """
    Loads and validates a student profile from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing student data.
        
    Returns:
        A validated StudentProfile Pydantic object.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Student profile file not found at {path}")
        
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Pydantic will validate the schema automatically
    return StudentProfile(**data)

