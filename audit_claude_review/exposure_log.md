# Claude second review: exposure log

| When | What was seen | Cases affected |
|---|---|---|
| Before blind pass | Aggregate Codex counts (64 PROVISIONAL_BEHAVIORAL / 124 NON_BEHAVIORAL) from the task brief. No per-case labels. | none (aggregate only) |
| Workspace survey | `head -60` of results/cases161_188_completion_check.json showed Codex assessments for Case 161 (NON_BEHAVIORAL, change limited to polyglot-kotlin/src/test/resources/example/pom.xml) and Case 162 (PROVISIONAL_BEHAVIORAL). | 161, 162 |
| Workspace survey | Header row of behavioral_classification.csv and batch_triage_results.csv (column names only), plus the first data row of batch_triage_results.csv up to `pre_all_test_summaries` (no labels in that span). | none |
| Workspace survey | logs/case150_evidence probe/JAR JSON excerpts (primary evidence, no labels). | 150 (evidence only) |

The blind pass reads only `audit_claude_review/digests/*`, produced by scripts/make_digests.py from primary evidence. The script removes label-like keys from evidence JSON. Raw logs and archives are opened where needed. Codex's review files, append scripts, the label/rationale columns, auto_triage and the original handoff are not read until the comparison pass.
| Blind pass end | Blind labels for all 188 cases frozen in claude_blind_labels.tsv (hash in claude_blind_labels.sha256) before any Codex label, rationale, review file, append script, auto_triage value or the original handoff was read. | all |
| Blind pass note | For 161 and 162 the earlier exposure is recorded in their rows. 162 was labelled by reference to the Case 28 mechanism, which was assessed blind. | 161, 162 |
