# Case 54 review

The html2pop3 Logback Classic upgrade from 1.2.11 to 1.4.0 is assessed **non-behavioural**, pending independent human review, because it introduces a binary method mismatch.

PRE passed five tests with zero failures/errors/skips. BREAKING reported five tests, zero failures, two errors and zero skips, with Maven BUILD FAILURE. Fresh Surefire XML agrees. FilterTest.testAdd fails with NoSuchMethodError for ch.qos.logback.core.util.EnvUtil.logbackVersion(). FilterTest.testIsAllow then reports Could not initialize class FilterTest, a consequence of the first initialization failure.

The resolved test classpath contains Classic 1.4.0 alongside Core 1.2.11 and SLF4J API 2.0.0. Only Classic changes between PRE and BREAKING. Archived JAR disassembly confirms ContextInitializer calls EnvUtil.logbackVersion(), while the actual Core 1.2.11 EnvUtil has no such method. This is a missing JVM method, supporting a binary incompatibility classification.

Only the Classic version in root pom.xml changes among archived source/POM files. Source, fresh reports, resolved Classic/Core JARs and disassembly are under logs/case54_evidence/. Original logs use prefix 471b0bd8. The image tee pipeline masks the failing Maven exit status; the XML and explicit BUILD FAILURE establish the outcome. Automated triage and agent assessment agree but remain distinct, with human labels blank. No repair was attempted.
