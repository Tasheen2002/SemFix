# Case 136 review

Both original dropwizard-pac4j images ran. PRE passed all 16 tests. BREAKING reported 16 tests and ten errors with four fresh Surefire reports. Maven and XML totals agree. The root POM changes only Jersey Server from 2.32 to 2.39.1. The affected classpath retains Jersey Common 2.32 and drops the old Jersey media JAXB JAR.

All ten errors identify the missing DynamicFeatureConfigurator class during ApplicationHandler initialization. The updated Server disassembly instantiates that class, and the retained Common JAR lacks it. This establishes binary incompatibility and supports a NON_BEHAVIORAL assessment pending independent review.
