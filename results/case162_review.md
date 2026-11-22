# Case 162 review

pay-cardid updates dropwizard-sentry from 2.0.22 to 2.0.28-4.

The updated Sentry appender rejects the existing stacktraceAppPackages YAML field. The factory still loads, but its configuration properties changed. Eleven PRE integration tests became one class-level error.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 44 | 0 | 0 | 0 |
| BREAKING | FAILURE | 34 | 0 | 1 | 0 |

Recorded assessment is `PROVISIONAL_BEHAVIORAL`. Binary linkage flag is `NO`. Independent human review is pending.

Changed POMs in the image comparison are pom.xml. The affected report classpaths list dropwizard-sentry-2.0.22.jar in PRE and dropwizard-sentry-2.0.28-4.jar in BREAKING.

Original logs and archived reports are indexed in the evidence manifest.
