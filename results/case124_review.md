# Case 124 review

camunda-platform-7-camel updates jakarta.xml.bind-api from 2.3.2 to 3.0.1 in camunda-bpm-camel-spring/pom.xml. This is the only changed archived source/POM. The existing Camel/Spring code still uses javax XML Bind types.

Both original images were run. PRE succeeds with 42 reactor tests and no failures, errors or skips. BREAKING reports 42 tests, zero failures, 16 errors and zero skips. Maven and ten fresh Surefire reports per phase agree. The errors wrap NoClassDefFoundError for javax/xml/bind/JAXBException while CamelNamespaceHandler loads the Spring application context. ClassNotFoundException confirms the missing type.

An unaffected module reports JAXB API 2.3.3 in its own classpath in both images. That initial all-reported-modules JAR inspection is preserved, but it is not used as evidence for the failing Spring module. Original Spring XML exposes only Maven's launcher classpath. Separate same-image diagnostics add/select one standalone resource-origin test in the Spring module, retaining original production source and dependency versions. PRE identifies API 2.3.2 and the javax JAXBException resource. BREAKING identifies API 3.0.1, the jakarta resource and no javax resource. Both resource-inspection diagnostics pass one test; they do not run or fix the failing Spring tests.

The affected_module_jar_inspection files archive those exact Spring-module API artifacts and confirm javax JAXBException/JAXBContext exist in 2.3.2 but not 3.0.1, which provides jakarta equivalents. The older runner captures diagnostic output in report text files; those original files, logs and initial extraction are retained. This independently establishes a missing-type namespace/binary incompatibility, supporting NON_BEHAVIORAL with binary_linkage_incompatibility=YES.

Independent human review remains pending, with reviewer/final labels blank. Automated screening is separate. Explicit Maven output establishes original outcomes because the tee pipeline masks Maven failures in Docker's exit code. No repair was attempted.
