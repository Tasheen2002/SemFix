# Case 177 review

IDS-Messaging-Services updates junit-platform-surefire-provider from 1.0.3 to 1.3.2.

The messaging module cannot start Surefire 2.19.1 with the updated JUnit provider. Its plugin realm selects common-java5 2.22.0, whose StringUtils lacks the required requireNonNull(Object) method. Six tests ran in an earlier module before the runner failed.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 32 | 0 | 0 | 0 |
| BREAKING | FAILURE | 6 | 0 | 0 | 0 |

Recorded assessment is `NON_BEHAVIORAL`. Binary linkage flag is `YES`. Independent human review is pending.

Changed POMs in the image comparison are messaging/pom.xml. The affected report classpaths list no matching JAR path in PRE and no matching JAR path in BREAKING.

Original logs and archived reports are indexed in the evidence manifest.
