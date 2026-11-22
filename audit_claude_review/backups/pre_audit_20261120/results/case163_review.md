# Case 163 review

scheduler updates json-smart from 2.4.8 to 2.4.9.

JSON Smart applies a nesting limit to unchanged scheduler test data. The existing parser call reaches input validation and rejects data accepted in PRE. Surefire totals exclude duplicate TestNG XML exports.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 966 | 0 | 0 | 0 |
| BREAKING | FAILURE | 617 | 2 | 0 | 0 |

Recorded assessment is `PROVISIONAL_BEHAVIORAL`. Binary linkage flag is `NO`. Independent human review is pending.

Changed POMs in the image comparison are json/pom.xml. The affected report classpaths list no matching JAR path in PRE and json-smart-2.4.9.jar in BREAKING.

Original logs and archived reports are indexed in the evidence manifest.
