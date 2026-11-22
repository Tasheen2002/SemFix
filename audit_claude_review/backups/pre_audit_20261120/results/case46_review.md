# Case 46 review

The recheck.cli upgrade of Logback Classic from 1.2.11 to 1.4.3 is provisionally **non-behavioural**, pending human review.

PRE passed all 12 tests. BREAKING reported 12 tests, two assertion failures, zero errors and zero skips. PreConditionTest and SystemInUtilTest expect warning text on captured standard output, but receive empty output. Their unchanged application code emits those warnings through SLF4J.

The resolved SLF4J API remains at 1.7.36. Its LoggerFactory directly calls StaticLoggerBinder.getSingleton and catches NoClassDefFoundError to select a no-operation logger. The actual Logback 1.2.11 JAR contains org/slf4j/impl/StaticLoggerBinder.class. Logback 1.4.3 lacks that binary binding class and instead publishes an SLF4JServiceProvider. The runtime prints Failed to load class org.slf4j.impl.StaticLoggerBinder and defaults to the no-operation logger. The missing runtime binding suppresses the warning output and produces the two downstream assertions.

The classification follows the study's exclusion of actual missing binary types. Human review should adjudicate this provider-transition case against the SLF4J API upgrade family, where a newer API deliberately ignores an older binding. Here the retained API directly requires a class removed by the updated binding.

Only the Logback Classic version changes in the project POM. Resolved Logback Core also changes from 1.2.11 to 1.4.3. Maven and fresh Surefire totals agree. The tee pipeline masks Maven's failing exit code. Logs have prefix `41164ec5` under `logs/batch_triage/`. Archives, both Logback JARs, the SLF4J JAR and disassembly are under `logs/case46_evidence/`.
