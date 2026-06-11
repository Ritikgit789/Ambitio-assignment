# Architectural Decisions

This document outlines the core technical and architectural decisions for the PhD Supervisor Recommendation Pipeline.

## 1. Quality over Quantity & Explicit Rate Limiting
To ensure we do not hit API rate limits with OpenAlex and Gemini, explicit `time.sleep()` calls and exponential backoff strategies via the `tenacity` library are implemented. We prioritize generating high-quality recommendations, even if the latency target is stretched towards the 15-minute upper limit.

## 2. Gemini 2.5 Flash Lite Model Selection
Based on requirements, we use the `gemini-2.5-flash-lite` model for all reasoning and extraction steps (interest extraction, domain classification, why-match generation) to maintain high throughput and minimize costs while retaining strong precision in text analysis tasks.

## 3. Handling Same-Name Collisions
OpenAlex frequently aggregates authors with the same names. To prevent conflation:
- We rely on `OpenAlex ID` as the primary key.
- We validate identities using the author's most recent institution affiliations and compare it to known domain characteristics.

## 4. Preventing Non-PI Contamination
The pipeline includes a dedicated `pi_validator` module.
- We reject profiles with titles hinting at student or postdoc status ("PhD Student", "Research Assistant", "Postdoctoral Researcher").
- We prefer profiles with titles such as "Professor", "Associate Professor", "Assistant Professor", and "Principal Investigator".

## 5. Preventing Wrong-Domain Leakage
Discovery is seeded from concepts and works rather than generic author name searches. 
The `domain_classifier` acts as a strict gatekeeper. It leverages LLM reasoning to check if the candidate's core subfield aligns tightly with the student's primary research interests.

## 6. Guaranteeing Country Adherence
Country filtering is treated as a hard constraint. The `country_filter` checks the OpenAlex affiliation records of the candidate against `student.target_countries`. If no matching country is found in recent affiliations, the candidate is immediately pruned.

## 7. Evidence Verification
We rely on OpenAlex works metadata. Only candidates with verified recent publications matching the student's domain pass the `evidence_collector` stage.

## 8. Precision over Recall
At every filtering stage, when there is ambiguity, we drop the candidate rather than risk a low-quality recommendation. This ensures the final output contains high-precision matches suitable for a mentor-eye audit.
