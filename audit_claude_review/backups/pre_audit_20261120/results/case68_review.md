# Case 68 review

kafka-connect-splunk updates Jackson Databind from 2.10.5.1 to 2.12.6.1. Only the root POM changes among the archived source and POM files. The affected test classpath retains Jackson Core 2.10.5 and resolves Jackson Annotations 2.12.6.

PRE passes all 143 tests. BREAKING runs 143 tests and reports 97 errors, zero failures and zero skips. Maven and fresh Surefire XML agree. Direct errors name com.fasterxml.jackson.core.util.JacksonFeature as missing. Subsequent errors include failed class initialization and JUnit expected-exception wrappers.

The resolved Databind JAR contains bytecode references to JacksonFeature. The resolved Core 2.10.5 JAR lacks the class, and the first missing-class exception in the log confirms the runtime failure. This is a non-behavioural binary incompatibility pending independent review.

Both original runs, source, reports and JAR inspection are archived. Explicit Maven output establishes the build outcome because the command pipes Maven through tee.
