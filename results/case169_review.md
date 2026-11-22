# Case 169 review

html2pop3 updates logback-classic from 1.4.1 to 1.4.3.

Logback Classic 1.4.3 references SanityChecker during configuration. The retained Logback Core 1.4.1 lacks that class. The second error follows the failed initialization of FilterTest.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 5 | 0 | 0 | 0 |
| BREAKING | FAILURE | 5 | 0 | 2 | 0 |

Assessment is `NON_BEHAVIORAL`. Binary linkage flag is `YES`. Independent human review is pending.

Changed POMs in the original archives are pom.xml. Original logs and archived reports are indexed in the evidence manifest.
