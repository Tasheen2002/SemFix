# Case 40 review

The `IDS-Messaging-Services` upgrade of Jackson Databind from 2.9.10.8 to 2.13.2.2 is a **non-behavioural binary linkage incompatibility**, pending human review.

PRE passed all 32 tests. BREAKING reported 18 tests with one assertion failure, five errors and zero skips. Six tests in `core` passed before the `messaging` module failed. Its five errors report `NoClassDefFoundError` for `com.fasterxml.jackson.annotation.JsonKey`. The sixth affected test uses an assertion that wraps the same missing class.

The change is in `core/pom.xml` and affects `messaging` through the reactor dependency. The original Surefire XML lacks the expanded test classpath. The offline Maven dependency-tree goal was unavailable in the image, so a focused debug run of `MessageControllerTest` captured the actual test classpath and reproduced the error. It contains Databind 2.13.2.2, Core 2.13.2 and Annotations 2.11.2. Inspection of the resolved JARs confirms that Databind's `JacksonAnnotationIntrospector` references `JsonKey`, while Annotations 2.11.2 lacks that class.

The original reactor totals come from the Maven summaries and fresh Surefire reports. The image command pipes Maven through `tee`, masking Maven's failing exit code. The raw logs have prefix `36fd224b` under `logs/batch_triage/`. Archives, diagnostic output and inspected JARs are under `logs/case40_evidence/`.
