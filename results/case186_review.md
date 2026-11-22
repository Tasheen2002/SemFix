# Case 186 review

pay-adminusers updates slf4j-api from 1.7.36 to 2.0.2.

SLF4J 2.0.2 ignores the retained Logback binding and selects NOP logging. Eight logger casts fail and four Dropwizard resource-test classes cannot initialize their logger context. The class-level errors account for the lower reported BREAKING test count.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 757 | 0 | 0 | 0 |
| BREAKING | FAILURE | 726 | 0 | 12 | 0 |

Assessment is `PROVISIONAL_BEHAVIORAL`. Binary linkage flag is `NO`. Independent human review is pending.

Changed POMs in the original archives are pom.xml. Original logs and archived reports are indexed in the evidence manifest.
