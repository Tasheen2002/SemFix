# Case 100 review

jadler updates SLF4J API 1.7.36 to 2.0.0. The root POM version is the sole archived source/POM change. Only the API changes on the affected classpath.

PRE passes 389 tests. BREAKING stops in jadler-core after 235 tests with five errors. Maven and fresh Surefire XML agree. JadlerMockerTest.addAppenderToStream casts the logger factory to Logback LoggerContext. The new API returns NOPLoggerFactory instead, and the cast fails.

The resolved Logback 1.2.11 JAR still contains its legacy binder. The updated API logs that it ignores that binding and selects the no-operation implementation. This changed provider selection supports a provisional behavioural assessment pending independent review. Both builds, reports and JAR inspection are archived.
