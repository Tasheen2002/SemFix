# Case 182 review

tamtam-bot-api updates jackson-databind from 2.9.10.3 to 2.13.4.1.

Updated Jackson Databind references JsonKey, which the retained Jackson Annotations JAR lacks. Direct serialization errors and HTTP failures from the embedded test server occur in the same run.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 108 | 0 | 0 | 1 |
| BREAKING | FAILURE | 108 | 0 | 46 | 1 |

Assessment is `NON_BEHAVIORAL`. Binary linkage flag is `YES`. Independent human review is pending.

Changed POMs in the original archives are pom.xml. Original logs and archived reports are indexed in the evidence manifest.
