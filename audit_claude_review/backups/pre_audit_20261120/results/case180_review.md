# Case 180 review

billy updates hibernate-validator from 6.1.7.Final to 7.0.2.Final.

Hibernate Validator 7.0.2.Final advertises a Jakarta Bean Validation provider. BillyValidator uses the retained javax Validation API and cannot discover a provider for that namespace. The initializer fails and later tests report the failed initialization. The reactor stops in billy-core.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 279 | 0 | 0 | 4 |
| BREAKING | FAILURE | 20 | 0 | 19 | 0 |

Assessment is `NON_BEHAVIORAL`. Binary linkage flag is `NO`. Independent human review is pending.

Changed POMs in the original archives are pom.xml. Original logs and archived reports are indexed in the evidence manifest.
