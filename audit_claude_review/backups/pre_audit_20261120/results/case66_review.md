# Case 66 review

recheck.cli upgrades Logback Classic 1.2.11 to 1.4.6. Only the root POM changes among the archived source and POM files. The test classpath also upgrades Logback Core and retains SLF4J API 1.7.36.

PRE passes all 12 tests. BREAKING reports 12 tests with two failures and zero errors or skips. PreConditionTest and SystemInUtilTest expect warning text but observe empty output. Maven and fresh Surefire XML agree.

The old Classic JAR supplies StaticLoggerBinder. The updated JAR supplies a service provider descriptor and omits the binder. Disassembly of the retained SLF4J LoggerFactory shows a direct call to StaticLoggerBinder.getSingleton and a NoClassDefFoundError handler. The updated run logs the failed binder load and fallback to a no-operation logger. The missing binary type causes the assertion failures, supporting a non-behavioural assessment pending independent review. The automated screen flags the downstream assertions as potentially behavioural. Case 46 shows a similar mechanism with a different Logback version.

Both original runs, reports, source and resolved JARs are archived. Maven output establishes the outcome because the image pipes Maven through tee.
