# Case 37 review

The `IDS-Messaging-Services` upgrade of Spring TX from 5.3.24 to 6.0.4 is a **non-behavioural runtime compatibility failure**, pending human review.

PRE passed all 32 tests. BREAKING reported 18 tests with five errors and zero failures or skips. The six tests in `core` pass, then five test classes in `messaging` fail during Spring listener setup. Maven skips downstream modules.

The five errors wrap an `UnsupportedClassVersionError` for `TransactionDefinition`. The actual class file in the Spring TX 6.0.4 JAR has major version 61, while the Java 11 runtime accepts class file versions up to 55. The PRE JAR's corresponding class has major version 52. The JVM rejects the class before the affected tests can exercise transaction behaviour.

The only archived POM change is the Spring TX version in `messaging/pom.xml`. The affected test classpath changes the Spring TX JAR path. Maven totals match fresh Surefire reports. The image command pipes Maven through `tee`, masking Maven's failing exit code. Logs have prefix `31a177fb` under `logs/batch_triage/`. Reports, archives and both JARs are under `logs/case37_evidence/`.
