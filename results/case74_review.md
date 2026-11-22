# Case 74 review

IDS-Messaging-Services updates Spring TX 5.3.24 to 6.0.3 in messaging/pom.xml. This is the only archived source/POM change and the only dependency difference in the affected test classpath.

PRE passes 32 tests. BREAKING reports 18 tests across core and messaging, with five errors and zero failures or skips before downstream modules are skipped. Maven reactor summaries match the fresh Surefire XML. Automated triage reports the last module's 12 tests.

All five errors are BeanInstantiationException reports during Spring transactional test listener initialization, with nested UnsupportedClassVersionError for TransactionDefinition. Inspection of the resolved JARs shows major class file version 52 in Spring TX 5.3.24 and 61 in 6.0.3. The Java 11 runtime supports up to major version 55 and rejects the class before the affected tests can execute. This supports a non-behavioural platform incompatibility assessment, pending independent review.

Both original runs, reports and inspected JARs are archived. Explicit Maven output establishes failure because the image pipes Maven through tee.
