# PhD Shortlist Builder

A high-precision PhD supervisor recommendation pipeline that prioritizes data quality and contamination reduction. 

## Features
- Discovers potential supervisors using the OpenAlex API based on student research interests.
- Filters out students/RAs in favor of PIs.
- Hard filters by target countries.
- Collects evidence (recent papers) and evaluates alignment using Gemini `gemini-2.5-flash-lite`.
- Generates a personalized "why match" reasoning.
- Outputs a ranked JSON shortlist.

## Installation

1. Clone this repository.
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variables by copying `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Add your `GEMINI_API_KEY`. Optionally, add your `OPENALEX_EMAIL` to be placed in the OpenAlex polite pool.

## Usage

Run the pipeline using the provided sample student data:

```bash
python src/main.py --input data/sample_student.json
```

The output will be saved to `sample_output/student_001.json`.

## Architecture Details
See [DECISIONS.md](DECISIONS.md) for detailed architectural decisions regarding contamination reduction, PI validation, and country filtering.
See [schema.md](schema.md) for input/output specifications.
