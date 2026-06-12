# PhD Supervisor Recommendation Pipeline

## Overview
This project is an end-to-end, production-quality Python pipeline designed to generate a highly precise, zero-contamination shortlist of PhD supervisors based on a student's profile. It uses a hybrid LLM architecture combining Groq (Llama 3) for efficient text extraction/generation and Google Gemini for strict academic domain reasoning.

## Data Sources
- **OpenAlex API (https://openalex.org/):** The primary data source for discovering academic papers, extracting authorship networks, retrieving institutional affiliations, and verifying publication records. OpenAlex provides a fully open, global index of the research system.
- **Student Profile JSON:** The input data containing the student's background, skills, and target parameters.

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your environment variables. Create a `.env` file in the root directory (see `.env.example`):
   ```env
   GEMINI_API_KEY=your_gemini_key
   GROQ_API_KEY=your_groq_key
   OPENALEX_EMAIL=your_email@example.com
   ```
3. Run the pipeline with a single command:
   ```bash
   python src/main.py --input data/sample_student.json
   ```
The final results will be saved in the `sample_output/` directory as both a JSON and a bonus CSV file.

## Design Trade-offs
- **Hybrid LLM approach vs. Single LLM:** To avoid hitting strict daily/minute API rate limits on free tiers, the pipeline delegates simpler tasks (keyword extraction, explanation generation) to Groq's fast Llama 3 model, reserving Gemini's superior reasoning purely for critical domain classification.
- **Proxy Metrics vs. Web Scraping:** Because OpenAlex does not provide explicit job titles, the system uses proxy metrics (h-index > 5, lifetime papers > 10) to determine Principal Investigator (PI) status. Web scraping university directories would have been more accurate but would violate the < 15-minute latency SLA.
- **Precision over Recall:** When faced with ambiguous domain alignment, the LLM is instructed to score strictly. We prefer to drop a potentially valid candidate rather than risk "wrong-domain leakage" contaminating the shortlist.

## Known Limitations
- **Contact Emails:** OpenAlex rarely provides contact emails. Fetching them would require secondary web scraping, which is currently out of scope to maintain low latency.
- **Mega-Authorship Bias:** The candidate pool building phase occasionally hits internal API hard caps prematurely if the seed paper is a massive consortium paper (e.g., Genomics or High-Energy Physics) with hundreds of authors.
- **Dependency on OpenAlex Recency:** If a professor recently moved institutions, OpenAlex's affiliation data might lag, potentially causing a candidate to fail the strict country filter incorrectly.

## Bonus: Closing the Feedback Loop
**How to use outcome streams (ADMIT, REJECT, NO_REPLY) to automatically improve future shortlists:**

If this pipeline were deployed in production and we received outcome data mapping our recommendations to real-world results, we would implement a **Closed-Loop Feedback System** using the following architecture:

1. **Mentorship Propensity Score:** We would introduce a dynamic penalty variable. If a professor has a 99% match score but historically ignores 10 emails in a row (`NO_REPLY`) or frequently responds with `NOT_RECRUITING`, their *Mentorship Propensity* score drops. The Ranking algorithm would automatically demote them, surfacing hungrier, highly-responsive early-career PIs instead.
2. **Dynamic Weight Tuning (XGBoost):** Our current heuristics (e.g., `h_index > 5` for PI validation) are hard-coded. We would train a lightweight offline XGBoost model on the outcome CSV to learn hidden correlations (e.g., *"Professors with an h-index over 50 almost never reply, but those between 8-15 reply 40% of the time"*). The system would automatically adjust the scoring weights based on these historical probability metrics.
3. **Automated LLM Prompt Engineering (Few-Shot Injection):** By tracking which generated `why_match` blurbs result in an `ADMIT` or `INTERVIEW` outcome, we can programmatically extract the top 5 most successful blurbs. We would inject these as few-shot examples into the Groq/Llama 3 prompt, forcing the LLM to structurally mimic the highest-converting email strategies for all future students without human intervention.
