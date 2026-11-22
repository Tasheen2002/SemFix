# Case 110 review

IDS-Messaging-Services updates spring-tx from 5.3.24 to 6.0.0 in messaging/pom.xml. This is the sole change across archived source/POM files and across all eight POMs. Only the spring-tx JAR changes on the affected test classpath.

Both original images were run. PRE succeeds with 32 reactor tests and no failures, errors or skips. BREAKING fails after 18 reactor tests across core and messaging, with five errors, zero failures and zero skips; downstream modules are skipped. Maven reactor summaries and fresh Surefire XML agree. Automated triage records only messaging's final-module count of 12, which is not the reactor total.

All five errors are BeanInstantiationException reports while initializing TransactionalTestExecutionListener. Their nested UnsupportedClassVersionError names TransactionDefinition, class file version 61, on a runtime accepting up to version 55. Inspection of the actual resolved class bytes confirms major version 52 in Spring TX 5.3.24 and 61 in 6.0.0. This establishes a Java platform incompatibility before test execution, supporting a non-behavioral assessment.

Independent human review remains pending, with reviewer/final labels blank. Explicit Maven output and fresh XML establish outcomes because the original tee pipeline masks Maven failure in the Docker exit code. No repair or substitution control was run.
