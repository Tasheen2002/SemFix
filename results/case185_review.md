# Case 185 review

pay-adminusers updates slf4j-api from 1.7.36 to 2.0.0.

SLF4J 2.0.0 ignores the retained Logback 1.2.11 binder and selects NOP logging. Eight client logger casts fail and four Dropwizard resource-test classes cannot initialize the logger context. Those class-level reports account for the lower BREAKING test count.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 757 | 0 | 0 | 0 |
| BREAKING | FAILURE | 726 | 0 | 12 | 0 |

Assessment is `PROVISIONAL_BEHAVIORAL`. Binary linkage flag is `NO`. Independent human review is pending.

Changed POMs in the original archives are pom.xml. Original logs and archived reports are indexed in the evidence manifest.
