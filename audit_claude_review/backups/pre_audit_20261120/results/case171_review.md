# Case 171 review

dropwizard-pac4j updates slf4j-api from 1.7.30 to 2.0.0.

SLF4J 2.0.0 ignores the present legacy Logback 1.2.3 binding and selects NOP logging. Dropwizard cannot obtain the expected logger context during test server startup, leading to ten setup errors. The original runtime pair and logger probe show the provider selection change.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 16 | 0 | 0 | 0 |
| BREAKING | FAILURE | 16 | 0 | 10 | 0 |

Assessment is `PROVISIONAL_BEHAVIORAL`. Binary linkage flag is `NO`. Independent human review is pending.

Changed POMs in the original archives are pom.xml. Original logs and archived reports are indexed in the evidence manifest.
