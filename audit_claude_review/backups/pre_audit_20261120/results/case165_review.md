# Case 165 review

dropwizard-pac4j updates jackson-databind from 2.10.5.1 to 2.13.4.1.

Updated Jackson Databind requires JacksonFeature, which is absent from retained Jackson Core 2.10.5. ObjectMapper initialization fails in all 16 tests.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 16 | 0 | 0 | 0 |
| BREAKING | FAILURE | 16 | 0 | 16 | 0 |

Recorded assessment is `NON_BEHAVIORAL`. Binary linkage flag is `YES`. Independent human review is pending.

Changed POMs in the image comparison are pom.xml. The affected report classpaths list jackson-databind-2.10.5.1.jar in PRE and jackson-databind-2.13.4.1.jar in BREAKING.

Original logs and archived reports are indexed in the evidence manifest.
