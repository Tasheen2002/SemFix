# Case 137 review

Both original recheck.cli images ran. PRE passed 12 tests. BREAKING reported 12 tests and two assertion failures. Maven and five fresh Surefire reports per phase agree. The root POM updates Logback Classic from 1.2.11 to 1.4.4. Logback Core changes transitively to 1.4.4, while the affected test classpath retains SLF4J API 1.7.36.

The baseline Classic JAR contains StaticLoggerBinder. The updated Classic JAR omits it. Retained LoggerFactory calls StaticLoggerBinder.getSingleton and catches NoClassDefFoundError. The original log records the missing binding and the no-operation fallback. Two PreConditionTest assertions receive empty warning text. The caught linkage failure initiates the cascade and supports NON_BEHAVIORAL pending independent review.
