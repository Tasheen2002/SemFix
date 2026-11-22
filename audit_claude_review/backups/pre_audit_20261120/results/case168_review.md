# Case 168 review

scheduler updates json-smart from 2.4.8 to 2.4.9.

JSON Smart 2.4.9 rejects the existing scheduler fixtures under its parser nesting restriction. IssuesTest.testIssue100 and testIssue101 fail during parsing after the same fixtures passed in PRE. Counts reconcile duplicate TestNG report formats.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 966 | 0 | 0 | 0 |
| BREAKING | FAILURE | 617 | 2 | 0 | 0 |

Assessment is `PROVISIONAL_BEHAVIORAL`. Binary linkage flag is `NO`. Independent human review is pending.

Changed POMs in the original archives are json/pom.xml. Original logs and archived reports are indexed in the evidence manifest.
