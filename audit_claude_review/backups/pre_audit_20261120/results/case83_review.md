# Case 83 review

billy upgrades Hibernate Validator 6.1.7.Final to 7.0.3.Final. The root POM version is the sole archived source/POM change.

PRE reports 279 tests with four skips and succeeds. BREAKING reports 20 tests with 19 errors in billy-core. The remaining modules are skipped. Maven and fresh Surefire XML agree.

BillyValidator calls javax.validation.Validation.buildDefaultValidatorFactory(). The retained Validation API 2.0.2 contains the javax interface. The old validator registers a javax provider, while the updated JAR registers only a Jakarta provider. Lookup raises NoProviderFoundException, followed by one initialization error and 18 failed-initialization reports. This is a non-behavioural missing compatible runtime provider assessment. The linkage flag is NO because the initiating failure is service lookup, with class initialization errors following it. Independent human review remains pending.

The resolved JARs and both Maven runs are archived. Explicit Maven output establishes the result because the image pipes Maven through tee.
