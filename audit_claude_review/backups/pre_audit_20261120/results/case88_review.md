# Case 88 review

missinglink upgrades Plexus Utils 3.5.0 to 4.0.0 in maven-plugin/pom.xml. The version is the only archived source/POM change.

PRE succeeds with 68 reported tests including one skip. BREAKING reports 68 tests with 14 errors and one skip. All 14 errors occur in the Maven plugin module when MojoRule is constructed. The automated screen captures that module's 15 tests. Maven reactor totals agree with fresh Surefire XML.

The initiating NoClassDefFoundError names org.codehaus.plexus.util.xml.XmlStreamReader. Inspection confirms the class exists in the resolved PRE JAR and is absent in the upgraded JAR. The missing type prevents test setup, supporting a non-behavioural binary incompatibility assessment pending independent review.

The original logs, fresh reports and inspected JARs are archived. Explicit Maven output establishes the result because the image pipes Maven through tee.
