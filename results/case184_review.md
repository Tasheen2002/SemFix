# Case 184 review

jadler updates slf4j-api from 1.7.36 to 2.0.1.

SLF4J 2.0.1 ignores the existing Logback 1.2.11 binder and returns NOPLoggerFactory. JadlerMockerTest casts the returned factory to LoggerContext. Its five casts now fail, and subsequent modules do not run. The same compiled logger probe reproduces the factory change.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 389 | 0 | 0 | 0 |
| BREAKING | FAILURE | 235 | 0 | 5 | 0 |

Assessment is `PROVISIONAL_BEHAVIORAL`. Binary linkage flag is `NO`. Independent human review is pending.

Changed POMs in the original archives are pom.xml. Original logs and archived reports are indexed in the evidence manifest.
