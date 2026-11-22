# Classification v1.0 (frozen 2026-11-20)

This is the final classification of the 188 BUMP TEST_FAILURE candidates. Do not edit these files; later changes should produce v1.1 or later with a change note.

| Label | Cases | % of 188 |
|---|---:|---:|
| BEHAVIORAL | 56 | 29.8% |
| NON_BEHAVIORAL | 132 | 70.2% |

## How the labels were established

1. **Codex first review:** provisional labels, 64 BEHAVIORAL and 124 NON_BEHAVIORAL.
2. **Claude AI second review:** blind, evidence-only pass. 56 BEHAVIORAL and 132 NON_BEHAVIORAL; labels frozen and hashed before comparison.
3. **Factual corrections:** Cases 9, 10, 12, 14 and 17 (counts and provenance), plus 11 targeted checks. Two of the checks were single-change controls (Cases 30 and 69).
4. **Rules approved by the researcher** (`decision_rules.md`): R5 SLF4J provider selection = BEHAVIORAL; R7 rejected configuration property = BEHAVIORAL; R8 ANTLR format alignment = NON_BEHAVIORAL; R3 javax/jakarta (including Case 109) = NON_BEHAVIORAL.
5. **Rerun verification:** the 47-case stratified sample, rerun from the original images; 47/47 reproduced.
6. **Human review:** the researcher manually reviewed Cases 1–20. All 20 agree with the final labels.

## Agreement (n = 188 unless stated)

| Pair | Agreement |
|---|---|
| Codex original vs Claude blind | 95.7% (κ = 0.902) |
| Codex original vs final | 95.7% (κ = 0.902) |
| Claude blind vs final | 100.0% (κ = 1.000) |
| Human (Cases 1–20) vs final | 100% |
| Human (Cases 1–20) vs Codex original | 100% |

## Limitations to report

- **Which agreement figure to report:** Codex original vs Claude blind (95.7%, κ = 0.90) is the inter-rater figure. Claude blind vs final is 100% only because the approved rules matched Claude's blind leanings, so it is not independent evidence; do not report it as agreement.

- The human review covers Cases 1–20. Cases 1–14 were recorded during the pilot; Cases 15–20 were recorded on 2026-11-20 from the researcher's statement.
- The 8 cases where Codex and Claude disagreed (49, 67, 69, 109, 112, 127, 140, 188) were settled by researcher-approved rules, not by per-case human review. Case 69 is also backed by a control run.
- The second review was done by an AI. `reviewer_2_label` is therefore empty, and the AI evidence is in `audit_claude_review/`.

## Files

| File | Contents |
|---|---|
| `behavioral_classification.csv` | Master file; `final_label` filled, `review_status=FINAL_V1` |
| `final_classification_rule_based.csv` | Per-case rule, behavior category, evidence basis, human-review flag, related group, duplicates |
| `decision_rules.md` | The approved rules |
| `rq1_classification_summary.md` | RQ1 results |
| `retrieval_exclusions.csv`, `evaluation_folds.csv`, `evaluation_split_design.md` | Leakage-safe splits for RQ2–RQ4 |
| `agreement_statistics.json` | Agreement statistics |
| `SHA256SUMS.txt` | Hashes of every frozen file |
