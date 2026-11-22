# Case 133 review

Both original neqsim images ran. PRE succeeded with 180 tests and nine skips. BREAKING reported 134 tests, 131 errors and one skip. The Maven totals agree with 54 fresh Surefire reports per phase. The root POM and affected classpath replace Core 2.17.2 with 2.18.0, while Log4j API remains at 2.17.2.

The original log first shows NoClassDefFoundError for org/apache/logging/log4j/util/ServiceLoaderUtil during logging startup and identifies ClassNotFoundException as its cause. Later test reports mostly describe failed initialization of logging or application classes. The actual updated Core disassembly shows ThreadContextDataInjector calling ServiceLoaderUtil.loadServices. The retained API JAR lacks ServiceLoaderUtil. The initiating error is a binary incompatibility and supports NON_BEHAVIORAL pending independent review.
