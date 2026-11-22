# Evaluation split design for the repair experiments (RQ2–RQ4)

**Scope:** the 56 BEHAVIORAL cases in `results/final_classification_rule_based.csv` are the repair targets. These files decide which cases may be retrieved for each target. No fixes have been searched for or generated yet.

**Rule from the brief:** a target case's own fix must never be retrieved. Some benchmark entries are the same breakage under another case ID, and some projects contribute several updates of one dependency. Excluding only the case ID would still let the identical fix leak, so three exclusion levels are defined.

| Level | What is excluded for a target | Purpose |
|---|---|---|
| L1 | Exact duplicates (same project, dependency, old and new version) | Minimum to stop identical fixes leaking |
| **L2 (primary)** | L1 + every case of the same project **and** dependency | The same client code is usually repaired the same way for a neighbouring version, so this is the realistic "unseen project-dependency pair" setting |
| L3 (strict, sensitivity) | L2 + every case in the same mechanism family | Tests transfer when no repair of the same mechanism is available |

Exclusions apply to the whole retrieval pool (all 188 cases), whether or not a case is behavioral, so they stay valid if non-behavioral repairs are added to the knowledge base.

## Facts the design accounts for

- **Exact-duplicate groups:** 4 23 60 121 177; 32 54; 65 169; 123 135; 163 168. Cases 32/54 and the five-case IDS junit-platform group were not flagged in the earlier audit.
- **Group sizes:** the 56 behavioral cases form 18 project-dependency groups. The largest are sign-maven-plugin/slf4j (8), recheck/slf4j, pay-adminusers/slf4j and jasmine/slf4j (7 each), and pay-cardid/dropwizard-sentry (5).
- **Cases with no same-mechanism example left under L2:** 15 (13, 14, 20, 28, 35, 39, 53, 70, 114, 158, 162, 163, 166, 168, 181). These are the one-off mechanisms, plus families confined to a single project-dependency group (dropwizard-sentry config, H2, json-smart). Retrieval can only help them through other mechanisms, so report them separately in RQ2.
- **Under L3,** the 36 SLF4J cases have no SLF4J example to retrieve. L3 is the cleanest test of whether retrieval generalises beyond near-copies.

## Grouped folds (`evaluation_folds.csv`)

Use these only if a method needs tuning, such as prompt or retrieval settings. Tune on two folds, evaluate on the third, and rotate. A project-dependency group never spans folds.

| Fold | Cases | Behavior categories |
|---|---:|---|
| 0 | 19 | PROVIDER_OR_IMPLEMENTATION_SELECTION 11, DEFAULT_SETTING_OR_POLICY 4, ACCEPTED_INPUT 2, EXCEPTION_TYPE_OR_CONDITION 1, OUTPUT_FORMAT 1 |
| 1 | 19 | PROVIDER_OR_IMPLEMENTATION_SELECTION 15, ACCEPTED_INPUT 2, DEFAULT_SETTING_OR_POLICY 2 |
| 2 | 18 | PROVIDER_OR_IMPLEMENTATION_SELECTION 10, ACCEPTED_INPUT 5, OUTPUT_FORMAT 1, RETURN_VALUE 1, EXCEPTION_TYPE_OR_CONDITION 1 |

The PROVIDER_OR_IMPLEMENTATION_SELECTION category (SLF4J) cannot be balanced across folds without splitting projects, because the groups are large. Report per-fold and pooled results.

## Reporting rules

1. Report every RQ2/RQ3 success rate for L2 (primary). Also report L1 and L3, so the effect of near-duplicate leakage is visible.
2. Report results per mechanism family as well as per behavior category, because SLF4J is 36 of 56 cases.
3. A repair counts as a success only if the required tests pass **with the updated dependency still resolved**. Record `mvn dependency:tree` for every successful repair; the Case 14 repair log lacks this.
