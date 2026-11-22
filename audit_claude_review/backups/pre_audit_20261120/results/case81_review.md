# Case 81 review

dropwizard-pac4j updates Hibernate Validator 6.2.4.Final to 8.0.0.Final. The root POM version is the sole archived source/POM change. Only the validator JAR changes on the affected test classpath.

PRE passes all 16 tests. BREAKING reports errors in all 16 tests, with zero assertion failures or skips. Each error occurs during Dropwizard validator initialization and names jakarta.validation.spi.ValidationProvider. Maven and fresh Surefire XML agree.

The retained jakarta.validation-api 2.0.2 artifact contains the javax.validation provider interface. The old validator registers a javax.validation provider and the updated JAR registers a jakarta.validation provider. The class named by NoClassDefFoundError is absent from the retained API JAR. This is a non-behavioural binary incompatibility, pending independent review.

Both runs, resolved JARs and reports are archived. Explicit Maven output determines the outcome because the image pipes Maven through tee.
