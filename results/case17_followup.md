# Case 17 follow-up

**Provisional classification — non-behavioural binary linkage incompatibility, pending human review.**

In disposable containers from the original PRE and BREAKING images, the reproduction script pins the affiliation date comparison to 31 December 2024. This date keeps the fixture's 2025 affiliations current and its older affiliations past. The one-line source adjustment applies equally to both containers and serves as a baseline control.

| Run | Scope | Tests | Failures | Errors | Skipped | Maven result |
|---|---|---:|---:|---:|---:|---|
| PRE | Full 14-module reactor | 4,104 | 0 | 0 | 0 | BUILD SUCCESS |
| BREAKING | `SourceInActivitiesTest` in `orcid-core`, built with prerequisite modules | 11 | 0 | 11 | 0 | BUILD FAILURE |

The previously failing `OrcidRecordToSolrDocumentTest.convertTest` passed in PRE. The same core test class reported 11 passes in PRE and 11 errors in BREAKING. Every BREAKING error has a nested `ClassNotFoundException` for `com.fasterxml.jackson.core.util.JacksonFeature`. The reported test classpath paths differ only in Jackson Databind, which moves from 2.10.0 to 2.12.6.1. Jackson Core remains at 2.10.1 and lacks the required class. The linkage failure occurs during Spring bean construction, before application behaviour can be compared.

The classification row uses the full adjusted PRE count and the focused BREAKING count. The earlier review, assessment and automated triage row document the original runs, including the failing unmodified baseline and the interrupted BREAKING reactor. This follow-up records the revised assessment. The full BREAKING reactor has only partial evidence from the original run. A dependency repair was outside the scope of these experiments.

The reproduction command is in `scripts/reproduce_case_17_fixed_date.sh`. The logs, three selected Surefire reports and machine-readable verification are under `logs/case17_evidence/fixed_date/`.
