# Case 55 review

The dropwizard-pac4j Jersey Server upgrade from 2.32 to 2.39 is assessed **non-behavioural**, pending independent human review, because server startup requires a class absent from the resolved dependencies.

PRE passed 16 reported tests with zero failures/errors/skips. BREAKING reported 16 tests, zero failures, ten errors and zero skips, with Maven BUILD FAILURE. Fresh XML agrees. All ten errors are NoClassDefFoundError for org/glassfish/jersey/internal/DynamicFeatureConfigurator; the logs also preserve the underlying ClassNotFoundException.

The upgraded Server 2.39 is resolved with Jersey Common 2.32. Inspection of the actual resolved JARs confirms ApplicationHandler references DynamicFeatureConfigurator and the Common 2.32 JAR does not contain it. JVM class loading therefore fails before these startup tests can exercise their intended behavior. The test classpath changes Server 2.32 to 2.39 and also loses the transitive jersey-media-jaxb 2.32 JAR. The root evidence is the explicitly named absent class in the retained Common version; no isolated JAR substitution experiment was run.

Only the Jersey Server version in root pom.xml changes among archived project source/POM files. The original classpaths, fresh reports, resolved Common/Server JARs and JAR inspection are retained under logs/case55_evidence/. Logs use prefix 474422dc. The image tee pipeline masks Maven's failing exit status, so the XML and BUILD FAILURE determine the outcome. Automated screening and this agent assessment are separate; independent human review and final labels remain pending. No repair was attempted.
