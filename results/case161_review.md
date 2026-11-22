# Case 161 review

polyglot-maven updates kotlin-stdlib from 1.3.31 to 1.6.0.

The expected XML fixture changed its Kotlin stdlib version to 1.6.0. The unchanged Kotlin input still generates 1.3.31. All 34 test classpaths match, and the Kotlin stdlib 1.4.10 JAR has the same hash in both images.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 302 | 0 | 0 | 7 |
| BREAKING | FAILURE | 302 | 1 | 0 | 7 |

Recorded assessment is `NON_BEHAVIORAL`. Binary linkage flag is `NO`. Independent human review is pending.

Changed POMs in the image comparison are polyglot-kotlin/src/test/resources/example/pom.xml. The affected report classpaths list no matching JAR path in PRE and kotlin-stdlib-1.4.10.jar in BREAKING.

Original logs and archived reports are indexed in the evidence manifest.
