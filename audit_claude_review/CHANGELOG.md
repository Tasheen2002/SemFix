# Changes made to original workspace files by the Claude AI second review (2026-11-20)

Backups of every file in `results/` and `scripts/` taken before any edit are in `audit_claude_review/backups/pre_audit_20261120/`, with hashes in `SHA256SUMS.txt`. Raw logs, evidence archives, JARs, probe outputs, `verified_repairs.jsonl`, the Case 14 patch, `batch_triage_results.csv` and the review markdown files were **not** modified.

## results/behavioral_classification.csv

The SHA-256 was `4648193e…70cb1` before the edits and `b2c96ec6…d9ff4` after. 13 rows were edited and all other lines are byte-identical; `scripts/apply_corrections.py` verifies this. Labels, `review_status`, `reviewer_1_label`, `reviewer_2_label` and `final_label` were not changed. Each edited row's `notes` ends with a note tagged `[AI second review (Claude), 2026-11-20]`. The machine-readable record is `corrections_applied.json`.

| Case | Field | Old | New | Evidence |
|---|---|---|---|---|
| 12 | pre_tests | 726 | 757 | `logs/batch_triage/1266a8c8_pre.log` line 423: `Tests run: 757 … BUILD SUCCESS`. 726 is the BREAKING count. |
| 12 | notes (text) | "complete PRE build runs 726 tests" | "… 757 tests" | same |
| 9 | pre_tests | 510 | 1114 | Whole-build PRE total (510 + 561 + 11 + 32); 510 was core-module only |
| 10 | pre_tests / breaking_tests | 12 / 12 | 32 / 18 | Whole-build totals; 12 was messaging-module only |
| 14 | pre_tests / breaking_tests | 32 / 32 | 190 / 52 | Whole-build totals; 32 was persistence-module only |
| 17 | notes (append) | – | provenance note | The row's logs and counts come from diagnostic runs (fixed-date PRE control, scoped BREAKING). In the original runs, PRE fails and BREAKING was stopped (exit 143). |
| 49, 67, 69, 109, 112, 127, 140, 188 | notes (append) | – | dispute note | The blind AI label differs; see `claude_audit.csv` |

Why Cases 9, 10 and 14 changed: 184 of the 188 rows record whole-build totals from the original logs. These three pilot rows recorded only the affected module, so the column mixed two definitions. The values recorded for the affected module are kept in the appended notes.

Consequence: Codex's earlier consistency checks, such as `results/cases161_188_completion_check.json` with its `previous_160_records_values_preserved` field, will now report changes for these rows. That is expected.

## scripts/append_case_{9,10,12,14}.py

The hardcoded counts (and the Case 12 notes sentence) were updated to match the corrected rows, and a header comment was added. CRLF line endings were preserved. These scripts skip rows that already exist, so re-running them does not change the CSV.

## Not changed, recorded as findings only

- `C:\Users\TASHEEN\Downloads\CODEX_RESEARCH_HANDOFF.md` lines 287–288 still say PRE 726 for Case 12. The file is outside the workspace and is the historical handoff.
- `results/batch_triage_results.csv` records `breaking_exit_code=0` for 173 rows whose Maven build failed. The cause is `mvn … | tee`, which hides Maven's exit status. The column is a correct container exit code, but it must not be read as a Maven outcome.
- `results/verified_repairs.jsonl` (Case 14) is accurate as written. The repair log actually shows a full-reactor BUILD SUCCESS with 190 tests and 36 skipped. The log does not print the resolved H2 JAR.

## Addendum: targeted checks (2026-11-20)

- 11 targeted checks ran in `--rm` containers from the original BREAKING images. Results are in `reruns/RESULTS.md` and per-run metadata in `reruns/runs.jsonl`.
- 5 BREAKING images were pulled for these runs, because they were not on the machine: Cases 3, 21, 30, 69 and 71, 0.5 to 0.8 GB each.
- `results/behavioral_classification.csv`: notes appended for Cases 30, 69 and 116, tagged `[AI second review (Claude), 2026-11-20, targeted rerun]`. A backup taken before this edit is at `backups/behavioral_classification.before_rerun_notes.csv`. Labels and human fields are unchanged.
- `verification_plan/control_plan.csv`, `claude_audit.csv`, `decision_rules.md` and `claude_audit_report.md` were updated with the results. In `claude_audit.csv`, confidence for 30, 69 and 116 is now HIGH.


## Option A: label correction for 8 cases (2026-11-20, approved by the researcher)

- `results/behavioral_classification.csv`: SHA-256 `b006276e9b98…` before and `1626b63b21d2…` after. Backup: `backups/before_option_A_20261120/`.
- For Cases 49, 67, 69, 109, 112, 127, 140, 188:
  - `behavioral_status` changed from PROVISIONAL_BEHAVIORAL to **NON_BEHAVIORAL**;
  - `behavior_change_type` changed from OTHER_BEHAVIORAL_CHANGE to empty;
  - a tagged note was appended to `behavior_description` and `notes`, recording the original label, the rule and the evidence.
  Only these 8 lines changed. `binary_linkage_incompatibility` (NO), `review_status`, `reviewer_*` and `final_label` are unchanged.
- Rules behind the change: R8 (ANTLR: 49, 67, 112, 127, 140, 188), R2 (69, confirmed by an alignment control run) and R3 (109).
- `scripts/append_case_{49,67,69,109,112,127,140,188}.py`: the same two values were changed, with comments; CRLF preserved.
- `results/case{N}_review.md` for the 8 cases: a dated "Label correction" addendum was appended. Codex's original text is unchanged.
- The file's counts are now 56 PROVISIONAL_BEHAVIORAL and 132 NON_BEHAVIORAL, which matches `results/final_classification_rule_based.csv` for all 188 cases.
- **For inter-rater agreement, use Codex's original labels** (64/124): they are in `claude_audit.csv` (`codex_label`) and in `backups/pre_audit_20261120/`. Comparing against the corrected file would overstate agreement.
- Machine-readable record: `option_a_changes.json`.

## Classification v1.0 frozen (2026-11-20, approved by the researcher)

- `results/behavioral_classification.csv`, all 188 rows:
  - `final_label` filled (56 BEHAVIORAL, 132 NON_BEHAVIORAL);
  - `review_status` set to `FINAL_V1`;
  - a tagged note added giving the rule and the basis for each label.
- `reviewer_1_label` for Cases 15–20 recorded from the researcher's statement that they reviewed those cases and agree; Cases 1–14 already had pilot labels. `reviewer_2_label` left empty, because the second review was an AI review. Backup: `backups/before_final_v1_20261120/`.
- `results/final_classification_rule_based.csv`: `human_reviewed` and `label_status` columns added. **Do not regenerate this file with `build_final_classification.py`**: that script predates these columns and would drop them.
- `results/classification_v1.0/`: frozen copies of the classification files, plus `README.md`, `agreement_statistics.json` and `SHA256SUMS.txt`.
- Inter-rater figure to report: Codex original vs Claude blind = 95.7%, κ = 0.90. Claude blind vs final is 100% only by construction, because the approved rules matched Claude's blind leanings.
