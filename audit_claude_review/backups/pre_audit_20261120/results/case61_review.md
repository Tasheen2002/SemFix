# Case 61 review

IDS-Messaging-Services updates Jackson Databind 2.13.4.2 to 2.14.0. The only archived source/POM change is in core/pom.xml. The affected messaging test classpath also upgrades Jackson Core to 2.14.0 and retains Jackson Annotations 2.13.4.

PRE passes 32 tests. BREAKING reports 18 tests across core and messaging, with five errors and one failure in messaging. Maven skips subsequent modules. The automated screen records the last module's 12 tests. The Maven reactor totals and fresh Surefire XML give 18.

The five errors are NoSuchMethodError for JsonSubTypes.failOnRepeatedNames(). IdsMessageUtilsTest.testUtils wraps the same error in an assertion. Disassembly shows Databind 2.14.0 calls that annotation method and the resolved Annotations 2.13.4 lacks it. This is a non-behavioural binary incompatibility, pending independent human review.

The 4fa4c3a1 logs and case61_evidence directory preserve both image runs, reports and resolved JARs. The explicit Maven result establishes failure because the tee pipeline masks the Maven exit code.
