# Case 17 repair status

Case: `18102f7a87e7ab8308a86208d47696c060110d0c` (`ORCID-Source`).

Update: Jackson Databind 2.10.0 → 2.12.6.1.

Status: **NOT_ATTEMPTED_BASELINE_REPRODUCTION_PROBLEM**.

The unmodified PRE build fails a date-sensitive assertion. BREAKING exhibits a missing JacksonFeature linkage failure and was deliberately interrupted after repeated startup errors. Overall classification remains UNCERTAIN until baseline reproduction and human review are resolved. The observed update failure is a non-behavioural candidate.

No repair patch or verified-repair record was created. `results/verified_repairs.jsonl` still contains only Case 14. A future correction of the baseline fixture/clock would be reproduction maintenance, not a verified dependency-update repair.

See `results/case17_review.md`, `results/case17_assessment.json`, and `logs/case17_evidence/` for evidence and limitations.
