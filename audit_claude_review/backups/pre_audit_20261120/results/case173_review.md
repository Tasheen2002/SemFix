# Case 173 review

dropwizard-pac4j updates jetty-server from 9.4.35.v20201120 to 10.0.10.

Jetty Server 10.0.10 references AbstractLifeCycle.StopException, which the retained Jetty Util JAR lacks. One test reports the missing type and nine report the resulting failure to initialize MutableServletContextHandler.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 16 | 0 | 0 | 0 |
| BREAKING | FAILURE | 16 | 0 | 10 | 0 |

Assessment is `NON_BEHAVIORAL`. Binary linkage flag is `YES`. Independent human review is pending.

Changed POMs in the original archives are pom.xml. Original logs and archived reports are indexed in the evidence manifest.
