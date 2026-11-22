# Case 96 review

dropwizard-pac4j updates jakarta.xml.bind-api 2.3.3 to 4.0.0. The root POM and the JAXB API entry in the affected classpath are the sole changes in those comparisons.

PRE passes all 16 tests. BREAKING reports ten errors across 16 tests. Each is a ServletException during Jersey initialization and wraps NoClassDefFoundError for javax.xml.bind.JAXBException. The resolved PRE JAR contains the javax class. The updated JAR provides the jakarta class and lacks the legacy binary name. This supports a non-behavioural binary incompatibility assessment pending independent review.

Maven and fresh Surefire XML agree. Both runs and resolved JARs are archived. The explicit Maven outcome establishes failure because the image pipes Maven through tee.
