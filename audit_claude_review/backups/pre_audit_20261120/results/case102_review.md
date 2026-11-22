# Case 102 review

dependency-track-maven-plugin updates jaxb-impl from 2.3.3 to 4.0.2. The root POM version is the only archived source/POM change. Both phases retain javax jaxb-api 2.3.1 and jaxb-core 2.3.0.1. The old implementation's transitive jakarta.xml.bind-api 2.3.3 and activation 1.2.2 disappear from the affected classpath.

PRE succeeds with 210 reported tests, zero failures/errors and three skips. BREAKING fails with 210 tests, seven assertion failures, zero errors and three skips. Maven and 42 fresh Surefire reports per phase agree. Four assertions say Exception expected, and three say Exception not expected. These are consequences of report-generation failure, not sufficient evidence of a behavioral API change.

FindingsReportMarshallerService and PolicyViolationsReportMarshallerService call javax.xml.bind.JAXBContext.newInstance. The log reports that no JAXB implementation was found, with ClassNotFoundException for com.sun.xml.internal.bind.v2.ContextFactory. The resolved 2.3.3 implementation registers javax service descriptors and contains com.sun.xml.bind.v2.ContextFactory. Version 4.0.2 instead registers jakarta.xml.bind.JAXBContextFactory and contains org.glassfish.jaxb.runtime.v2.ContextFactory. The fallback internal class is absent from BOTH implementation JARs; it was not removed by this update. The incompatible API/provider namespaces establish a provider/type compatibility break and support a non-behavioral assessment.

Both original images were run. The tee pipeline masks Maven failure in Docker's exit code, so outcomes use Maven and fresh reports. This is an agent assessment pending independent human review. No repair or substitution control was run.
