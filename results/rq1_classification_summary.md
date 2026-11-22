# RQ1: behavioral breakages among the 188 TEST_FAILURE candidates

**Basis:** these labels come from the decision rules the researcher approved on 2026-11-20 (`audit_claude_review/verification_plan/decision_rules.md`), applied to the evidence in `audit_claude_review/claude_audit.csv` and the targeted checks in `audit_claude_review/reruns/RESULTS.md`. **Status:** FINAL v1.0 (2026-11-20). The researcher manually reviewed Cases 1–20 (100% agreement), and a 47-case stratified sample was rerun from the original images (47/47 reproduced). All percentages are of 188.

## Headline

| Label | Cases |
|---|---:|
| BEHAVIORAL | 56 (29.8%) |
| NON_BEHAVIORAL | 132 (70.2%) |
| UNCERTAIN | 0 |

The behavioral cases come from 18 of the 58 projects.
8 cases differ from Codex's provisional labels: 49, 67, 69, 109, 112, 127, 140, 188. All 8 move from PROVISIONAL_BEHAVIORAL to NON_BEHAVIORAL under rules R8 (ANTLR), R2 (Case 69, confirmed by an alignment control) and R3 (Case 109).

## What kind of behavior changed (n = 56)

| Category | Cases | % of 188 | What changed | Cases (dependency) |
|---|---:|---:|---|---|
| PROVIDER_OR_IMPLEMENTATION_SELECTION | 36 | 19.1% | Library selects a different implementation for the same classpath | slf4j-api x36 |
| ACCEPTED_INPUT | 9 | 4.8% | Input previously accepted is now rejected (DDL precision, JSON depth, YAML property) | dropwizard-sentry x5, h2 x2, json-smart x2 |
| DEFAULT_SETTING_OR_POLICY | 6 | 3.2% | A default (mock maker, deserialization allow-list) changed | mockito-core x5, xstream x1 |
| EXCEPTION_TYPE_OR_CONDITION | 2 | 1.1% | Different exception type, or an exception where a value was returned | commons-io x1, json x1 |
| OUTPUT_FORMAT | 2 | 1.1% | Serialized/string output differs | httpclient x1, jsoup x1 |
| RETURN_VALUE | 1 | 0.5% | Same call returns a different value | plexus-io x1 |

**Concentration:** 36 of the 56 behavioral cases (64%) are one mechanism, SLF4J 2.x provider discovery ignoring a legacy binding. They span 7 projects and slf4j-api 2.0.0 to 2.0.7. In 18 of them a logger-selection probe shows the switch directly. RQ4 per-category comparisons need to account for this, for example by reporting results by mechanism family as well as by category.

## Why the other cases are non-behavioral (n = 132)

| Rule | Cases |
|---|---:|
| R1: Linkage or bytecode incompatibility | 92 |
| R3: javax/jakarta namespace migration | 13 |
| R10: Tooling or test-infrastructure failure | 9 |
| R6: Retained API references a removed binding class | 6 |
| R8: Generator/runtime serialized-format alignment (ANTLR) | 6 |
| R4: Framework-generation mismatch | 3 |
| R13: Packaging change removes a runtime provider | 1 |
| R2: Version skew within one library family | 1 |
| R11: Fixture-only edit | 1 |

## Evidence strength of the behavioral labels

| Basis | Cases |
|---|---:|
| DECISION_ONLY | 41 |
| COVERED | 11 |
| COVERED_BY_TRACE | 4 |

- **COVERED:** a probe or control isolates the change.
- **COVERED_BY_TRACE:** the exception originates inside the updated library on an input that passes in PRE.
- **DECISION_ONLY:** the mechanism is confirmed and the label follows from the approved rule (R5 or R7). For R5, 18 of the 36 cases also have a direct logger-selection probe.

## Before the repair phase

- Use `results/retrieval_exclusions.csv` (L2 primary) and `results/evaluation_folds.csv` so that retrieval cannot return a target case's own fix. Exact-duplicate groups: 4/23/60/121/177, 32/54, 65/169, 123/135, 163/168. See `results/evaluation_split_design.md`.
- `final_label` in `results/behavioral_classification.csv` is filled for all 188 cases (v1.0 frozen in `results/classification_v1.0/`).
