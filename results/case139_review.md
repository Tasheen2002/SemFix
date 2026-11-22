# Case 139 review

Both original wsdoc images ran. PRE passed all 59 tests. BREAKING reported 59 tests and 20 failures, with no errors or skips in Maven's summary. Nested TestNG JUnit-format XML repeats the 59 suite test identities and their statuses in each phase. Reconciliation preserves all XML and counts the executions once, matching Maven.

The root POM and the affected classpath change only SnakeYAML from 1.13 to 1.31. The failure stack points to RAML Parser 0.9-SNAPSHOT in TemplateResolver.ResourceTemplateMerger.cloneSequenceNode. The unchanged caller bytecode invokes SequenceNode.getFlowStyle:()Ljava/lang/Boolean;. The method is inherited from CollectionNode and returns Boolean in 1.13. The new method returns DumperOptions.FlowStyle, so the old JVM descriptor is absent. The original NoSuchMethodError confirms a binary incompatibility. The assessment is NON_BEHAVIORAL pending independent review.

Case 138 reproduces the same mechanism with SnakeYAML 1.32. Case 139 has its own original images, logs, reports and JAR inspection for 1.31.
