# Case 60 review

IDS-Messaging-Services updates junit-platform-surefire-provider from 1.0.3 to 1.3.2 in clearinghouse/pom.xml. The source/POM comparison identifies this as the sole change.

PRE passes 32 tests. BREAKING passes 18 tests across core and messaging, then fails when Maven Surefire 2.19.1 attempts to start the clearinghouse tests. Maven reports zero tests in clearinghouse and skips the downstream modules. The fresh Surefire reports and Maven reactor totals agree. The automated screen captures only the last module's zero tests.

The clearinghouse plugin classpath contains the upgraded provider and common-java5 2.22.0. Maven reports NoSuchMethodError for StringUtils.requireNonNull(Object). Disassembly of the resolved common-java5 JAR shows the class lacks that method. This is a non-behavioural binary incompatibility in the test runner, pending independent human review. Cases 4 and 23 exhibit the analogous failure in other modules.

The original command pipes Maven output through tee. The explicit Maven result and fresh reports establish the outcomes. The 4ef12d53 logs and case60_evidence directory contain the runs, source and dependency evidence.
