# Case 101 review

dddsample-core updates jakarta.xml.bind-api from 2.3.3 to 4.0.0. The root POM version is the only archived source/POM change. The classpath also changes the transitive activation API from 1.2.2 to 2.1.0; the old JAXB implementation 2.3.3 remains.

PRE succeeds with 132 reported tests, zero failures/errors and three skips. BREAKING fails with 132 reported tests, zero failures, 20 errors and two skips. Maven and 37 fresh Surefire reports per phase agree. The skip count changes; reported tests must not be described as all passed.

AdminAcceptanceTest and other Spring tests fail to load ApplicationContext. Nested Hibernate entity-manager initialization reports NoClassDefFoundError: javax/xml/bind/JAXBException, caused by ClassNotFoundException. Inspection of the actual resolved API JARs confirms this javax class exists in 2.3.3 and is absent in 4.0.0, which provides the jakarta equivalent. This establishes a missing-type binary incompatibility and supports a non-behavioral assessment.

Both original Docker images were run with their original Maven command. Its tee pipeline masks Maven failure in the container exit code; explicit Maven outcomes and fresh reports establish the result. This is an agent assessment pending independent human review. No repair or dependency substitution was attempted.
