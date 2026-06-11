# Input / Output Schema

## Input Schema (`StudentProfile`)

```json
{
  "name": "Jane Doe",
  "education_history": [
    {
      "degree": "MSc Computer Science",
      "institution": "University of Example",
      "year": 2024
    }
  ],
  "skills": ["Python", "Machine Learning", "NLP", "PyTorch"],
  "projects": [
    {
      "title": "LLM Fine-tuning for Domain Specific QA",
      "description": "Fine-tuned Gemini models for medical QA..."
    }
  ],
  "publications": [],
  "research_interests": ["Large Language Models", "Information Retrieval", "Agentic AI"],
  "target_countries": ["US", "UK", "Canada"],
  "target_intake": "Fall 2025",
  "intro_call_summary": "Student is highly motivated to work on agentic workflows and RLHF.",
  "raw_resume_text": "..."
}
```

## Output Schema (`ShortlistOutput`)

The output is a JSON file containing a list of `Recommendation` objects.

```json
[
  {
    "name": "Dr. John Smith",
    "institution": "Example University",
    "country": "US",
    "contact_email": "jsmith@example.edu",
    "research_focus": "Agentic AI and RLHF",
    "evidence": [
      {
        "title": "Scaling Agentic Workflows",
        "url": "https://doi.org/10.xxxx",
        "year": 2023
      }
    ],
    "why_match": "Dr. Smith's recent work on scaling agentic workflows directly aligns with your project on LLM fine-tuning and your interest in Agentic AI.",
    "tier": "Target",
    "linked_phd_program_or_open_position": "Computer Science PhD Program",
    "match_score": 92.5,
    "pi_confidence": 0.95,
    "identity_confidence": 0.98
  }
]
```
