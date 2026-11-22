# Case 47 review

The IDS-Messaging-Services Spring TX upgrade from 5.3.24 to 6.0.5 is provisionally **non-behavioural**, pending human review.

PRE passed all 32 tests. BREAKING reported 18 tests with five errors and zero failures or skips. The messaging module fails when Spring instantiates its transactional test listener. Every error wraps UnsupportedClassVersionError for TransactionDefinition. Its resolved class-file header changes from major version 52 to 61, requiring Java 17, while the test runtime is Java 11 and supports at most major version 55.

Only the Spring TX version changes in messaging/pom.xml. The affected classpath changes only the Spring TX path. Maven reactor summaries agree with the fresh Surefire totals. Both image commands pipe Maven through tee, masking the failing Maven exit code.

Logs have prefix `414c42fd` under `logs/batch_triage/`. Source archives, reports, image provenance and both Spring TX JARs are under `logs/case47_evidence/`.
