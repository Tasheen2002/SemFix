# Case 176 review

dropwizard-pac4j updates jersey-server from 2.32 to 2.38.

The updated Jersey Server references DynamicFeatureConfigurator, which is absent from retained Jersey Common. Ten tests fail with a missing runtime class.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 16 | 0 | 0 | 0 |
| BREAKING | FAILURE | 16 | 0 | 10 | 0 |

Recorded assessment is `NON_BEHAVIORAL`. Binary linkage flag is `YES`. Independent human review is pending.

Changed POMs in the image comparison are pom.xml. The affected report classpaths list jersey-server-2.32.jar in PRE and jersey-server-2.38.jar in BREAKING.

Original logs and archived reports are indexed in the evidence manifest.
