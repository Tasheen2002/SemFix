# Case 164 review

jcabi-simpledb updates hibernate-validator from 6.2.5.Final to 8.0.1.Final.

Hibernate Validator 8 registers under jakarta.validation, while MethodValidator still uses javax.validation. Both API namespaces are available, but the old API cannot discover a compatible provider.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 5 | 0 | 0 | 0 |
| BREAKING | FAILURE | 5 | 0 | 3 | 0 |

Recorded assessment is `NON_BEHAVIORAL`. Binary linkage flag is `NO`. Independent human review is pending.

Changed POMs in the image comparison are pom.xml. The affected report classpaths list hibernate-validator-6.2.5.Final.jar in PRE and hibernate-validator-8.0.1.Final.jar in BREAKING.

Original logs and archived reports are indexed in the evidence manifest.
