# Case 41 review

The IDS-Messaging-Services upgrade of Spring TX from 5.3.24 to 6.0.2 is provisionally **non-behavioural**, pending human review.

PRE passed all 32 tests. BREAKING reported 18 tests and five errors, with zero failures or skips. The messaging module fails while instantiating Spring's transactional test listener. Every error wraps UnsupportedClassVersionError for TransactionDefinition. The actual class in Spring TX 6.0.2 has major version 61, which requires Java 17, while the test runtime is Java 11 and accepts up to version 55. The corresponding PRE class has major version 52.

Only the Spring TX version changes in messaging/pom.xml. The affected classpath paths differ only in Spring TX. Fresh Surefire reports agree with the reactor totals in Maven. The image command pipes Maven through tee, which masks its failing exit code. Case 37 shows the analogous failure against Spring TX 6.0.4.

Logs have prefix `38eb09eb` under `logs/batch_triage/`. Source archives, fresh reports, image provenance and both resolved JARs are under `logs/case41_evidence/`.
