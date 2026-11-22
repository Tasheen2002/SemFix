# Case 187 review

wsdoc updates jackson-databind from 2.4.2 to 2.12.7.1.

Jackson Databind requires JsonMerge, which is missing from retained Jackson Annotations. The first ObjectMapper initialization fails, and later tests report the failed initialization as a downstream exception. Counts exclude duplicate TestNG exports.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 59 | 0 | 0 | 0 |
| BREAKING | FAILURE | 59 | 33 | 0 | 0 |

Assessment is `NON_BEHAVIORAL`. Binary linkage flag is `YES`. Independent human review is pending.

Changed POMs in the original archives are pom.xml. Original logs and archived reports are indexed in the evidence manifest.
