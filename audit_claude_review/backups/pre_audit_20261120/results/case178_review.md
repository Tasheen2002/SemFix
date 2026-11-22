# Case 178 review

lti-launch updates spring-webmvc from 4.1.6.RELEASE to 5.3.18.

The Spring context test aborts before its assertion because a Spring MVC runtime reference to PathPatternParser cannot resolve on the project's classpath. The stack reports ClassNotFoundException for that type.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 1 | 0 | 0 | 0 |
| BREAKING | FAILURE | 1 | 0 | 1 | 0 |

Recorded assessment is `NON_BEHAVIORAL`. Binary linkage flag is `YES`. Independent human review is pending.

Changed POMs in the image comparison are pom.xml. The affected report classpaths list no matching JAR path in PRE and no matching JAR path in BREAKING.

Original logs and archived reports are indexed in the evidence manifest.
