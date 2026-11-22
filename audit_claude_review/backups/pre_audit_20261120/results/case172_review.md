# Case 172 review

recheck.cli updates logback-classic from 1.2.11 to 1.4.5.

Logback Classic 1.4.5 no longer includes StaticLoggerBinder, which retained SLF4J 1.7.36 directly calls. Its missing-class fallback suppresses warnings and prompts, leading to two assertions against empty output.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 12 | 0 | 0 | 0 |
| BREAKING | FAILURE | 12 | 2 | 0 | 0 |

Assessment is `NON_BEHAVIORAL`. Binary linkage flag is `YES`. Independent human review is pending.

Changed POMs in the original archives are pom.xml. Original logs and archived reports are indexed in the evidence manifest.
