# Architectural Decisions

This document outlines the core technical and architectural decisions made to fulfill the PhD Supervisor Recommendation Pipeline assignment requirements, balancing precision, latency, and API quotas.

## 1. Hybrid LLM Architecture (Cost & Quota Optimization)
We hit hard API rate limits (10 Requests Per Minute / 20 Per Day) using Gemini exclusively. To bypass this and guarantee reproducibility without failure:
- **Groq (Llama 3 8B):** Handled low-stakes, high-volume tasks like keyword extraction and the final `why_match` generation.
- **Google Gemini 2.5 Flash Lite:** Reserved exclusively for the most critical reasoning task: Domain Classification (preventing wrong-domain leakage).

## 2. API Batching & Multithreading (Latency Optimization)
To ensure the pipeline completes comfortably under the **15-minute** SLA limit:
- **OpenAlex Batching:** Instead of fetching authors one-by-one, we used OpenAlex's filter syntax (`filter=openalex_id:A1|A2...`) to fetch up to 50 author profiles in a single HTTP request, dropping step 4 latency from 15 minutes down to 3 seconds.
- **LLM Batching:** We passed 40 candidates at a time in a single LLM prompt, asking the model to return a JSON dictionary of scores. This reduced LLM network overhead by 95%.
- **Multithreading:** For fetching the evidence (recent papers), we utilized Python's `concurrent.futures.ThreadPoolExecutor` with 5 workers, maximizing throughput while remaining safely inside OpenAlex's "Polite Pool" 10 RPS limit.

## 3. Heuristic PI Validation (Data Reality Trade-off)
OpenAlex does not consistently provide explicit job titles (e.g., "PhD Student" or "Professor"). Scraping university websites would violate the latency SLA.
**Decision:** We used academic metrics as a proxy. We hard-coded a heuristic that assumes anyone with fewer than 5 lifetime papers or an h-index < 2 is a student/junior researcher and pruned them. A high `pi_confidence` score was assigned to those with 15+ papers and h-index > 5.

## 4. Resolving Name Collisions (Identity Validation)
Instead of searching for authors by string names (which causes the John Smith collision problem), our entire discovery mechanism started from *papers*. By pulling authors directly from top-cited works, we inherently extracted their unique `openalex_id`. Therefore, our `identity_confidence` is extremely high (usually 1.0) because we track individuals by their unique OpenAlex database node, not their name string.

## 5. Late-Stage Reasoning Generation
Generating a personalized 2-sentence explanation (`why_match`) for 200+ candidates wastes massive amounts of API tokens and time. 
**Decision:** We calculated match scores and ranked the list *first*, dropping the bottom-tier candidates. We then only generated the `why_match` text for the Top 50 surviving candidates just before exporting to JSON.

## 6. Output Formats
To satisfy the baseline and bonus requirements, the `output_generator` builds both a strictly-typed `.json` file and a human-readable `.csv` spreadsheet.
