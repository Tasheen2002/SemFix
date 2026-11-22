# Case 134 review

Both original sign-maven-plugin images ran. PRE passed 38 tests. BREAKING reported 38 tests and 12 errors. Maven and six fresh reports per phase agree. The root POM and affected classpath change only SLF4J API from 1.7.36 to 2.0.6. Both images retain the legacy binder in slf4j-mock 2.3.0.

The same compiled LoggerFactory probe returns a mock proxy in PRE and NOPLogger in BREAKING. The updated runtime reports that it ignored the legacy binder. Fresh test reports identify LoggerAnnotationEngine.findLoggersMocks casting the returned logger to org.simplify4u.slf4jmock.internal.ProxyMock during Mockito setup. The retained mock library disassembly corroborates the cast. The cause is changed logger selection through a compatible API call, supporting PROVISIONAL_BEHAVIORAL pending independent review.
