# Case 42 review

The camunda-platform-7-camel upgrade of Jakarta XML Bind API from 2.3.2 to 4.0.0 is provisionally **non-behavioural**, pending human review.

PRE passed all 42 tests. BREAKING reported 42 tests with 16 errors, zero assertion failures and zero skips. The first 25 tests pass in the common test module. Sixteen Spring tests then fail to load the application context because CamelNamespaceHandler requires `javax.xml.bind.JAXBException`. Its nested exceptions identify NoClassDefFoundError and ClassNotFoundException for that type.

The actual API 2.3.2 JAR contains the javax class. The API 4.0.0 JAR contains `jakarta.xml.bind.JAXBException` and lacks its javax counterpart. The existing Camel and JAXB implementation classes still require the javax namespace. The classpath also changes the transitive Jakarta Activation API version. Only the XML Bind API version changes in camunda-bpm-camel-spring/pom.xml.

Maven module summaries agree with the fresh Surefire totals. The image command pipes Maven through tee, masking the failing exit code. Logs have prefix `3b26e047` under `logs/batch_triage/`. The source archives, reports, image provenance and inspected API JARs are under `logs/case42_evidence/`.
