# Case 174 review

webapp updates log4j-core from 2.16.0 to 2.18.0.

Log4j Core 2.18.0 requires ServiceLoaderUtil, which is absent from retained Log4j API 2.16.0. The initial runtime class failure breaks LoggerContext initialization and produces cascading errors.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 67 | 0 | 0 | 2 |
| BREAKING | FAILURE | 61 | 0 | 48 | 1 |

Assessment is `NON_BEHAVIORAL`. Binary linkage flag is `YES`. Independent human review is pending.

Changed POMs in the original archives are pom.xml. Original logs and archived reports are indexed in the evidence manifest.
