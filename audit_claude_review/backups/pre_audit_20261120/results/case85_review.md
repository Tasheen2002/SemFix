# Case 85 review

dependency-track-maven-plugin updates JAXB implementation 2.3.3 to 4.0.1. The root POM version is the sole archived source/POM change. The affected classpath retains javax JAXB API 2.3.1 and JAXB core 2.3.0.1.

PRE succeeds with 209 reported tests including three skips. BREAKING reports the same total and skips, with seven assertion failures and zero errors. Three tests expect XML report operations to succeed. Four tests expect findings or policy violation checks to raise a build exception. Report generation encounters the JAXB error in both paths. Maven and fresh Surefire XML agree.

The PRE implementation JAR has javax service descriptors. The upgraded JAR registers a Jakarta service and lacks the javax descriptors. The retained JAXB API cannot find a compatible implementation. Its fallback lookup fails with ClassNotFoundException for com.sun.xml.internal.bind.v2.ContextFactory. That fallback class is absent from both inspected implementation JARs. The evidence supports a non-behavioural runtime incompatibility assessment pending independent review.

Both original builds, Surefire reports and JAR inspection are archived. Explicit Maven output establishes the outcome because the image pipes Maven through tee.
