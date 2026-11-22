# Case 170 review

IDS-Messaging-Services updates jackson-databind from 2.9.10.8 to 2.13.2.

Jackson Databind 2.13.2 references JsonKey, which is absent from the retained Jackson Annotations JAR. The messaging module reports five missing-class errors and one assertion failure wrapping the same exception. Later modules did not run.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 32 | 0 | 0 | 0 |
| BREAKING | FAILURE | 18 | 1 | 5 | 0 |

Assessment is `NON_BEHAVIORAL`. Binary linkage flag is `YES`. Independent human review is pending.

Changed POMs in the original archives are core/pom.xml. Original logs and archived reports are indexed in the evidence manifest.
