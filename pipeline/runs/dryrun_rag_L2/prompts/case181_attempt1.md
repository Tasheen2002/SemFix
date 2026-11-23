<!-- SYSTEM -->
You repair Java projects whose tests broke after a dependency update changed the dependency's behavior.

You receive: the dependency update, the build/test failure, the relevant project source files, and (when
available) fixes of similar past breakages from a knowledge base.

Your task: produce ONE patch that makes the failing tests pass while keeping the dependency update.

Hard rules (patches that break them are rejected automatically):
1. Keep the updated dependency at the new version or higher. Do not revert, downgrade, exclude or remove it.
2. Do not delete, disable, skip or weaken tests (no @Ignore/@Disabled, no removed assertions or test methods).
   Updating an expected value is allowed only when the new library behavior is the intended behavior.
3. Every test that passed before the update must still pass.
4. You may change source code, test code, configuration files, or build files; you may add or upgrade a
   companion dependency (for example a provider that matches the new version) when that is the right fix.
5. Prefer the smallest change that addresses the actual behavior change.

Output format:
- First, at most a few sentences explaining the behavior change and your fix.
- Then exactly one fenced code block with language `diff` containing a unified diff (git format) against the
  files as shown, with paths relative to the repository root:
  ```diff
  diff --git a/path/File.java b/path/File.java
  --- a/path/File.java
  +++ b/path/File.java
  @@ -10,7 +10,7 @@
   context line
  -old line
  +new line
   context line
  ```
- Context lines must match the given files exactly. Do not output anything after the diff block.

<!-- USER -->
## Dependency update
`org.jsoup:jsoup` was updated from `1.14.2` to `1.15.3`. The project compiles, but tests now fail.

## Failure (from the build log)
Failing test classes: com.github.sparqlanything.html.HTMLMicrodataTest, com.github.sparqlanything.html.HTMLMicrodataRemoteTest
Exception types: java.lang.AssertionError
Error lines:
- java.lang.AssertionError
Project stack frames:
- com.github.sparqlanything.testutils.TestUtils (TestUtils.java:144)
- com.github.sparqlanything.testutils.AbstractTriplifierTester (AbstractTriplifierTester.java:199)
- com.github.sparqlanything.html.HTMLMicrodataTest (HTMLMicrodataTest.java:33)
- com.github.sparqlanything.html.HTMLMicrodataRemoteTest (HTMLMicrodataRemoteTest.java:36)

## Similar past breakages and their validated fixes (from the knowledge base)
They come from OTHER projects. Use them for the idea of the fix; adapt it to this project's files.

### Past case 1: org.slf4j:slf4j-api 1.7.32 -> 2.0.3 (searls/jasmine-maven-plugin)
Symptom: java.lang.AssertionError
  java.lang.AssertionError:
Behavior change: LoggerFactory returns NOPLogger
Fix (RESEARCHER_WRITTEN, written by the researchers (validated, but not the project's own fix); validated: all tests pass): Replace the unmaintained SLF4J-1 test binding uk.org.lidalia:slf4j-test 1.2.0 with its SLF4J-2 fork com.github.valfirst:slf4j-test 3.0.1 (package rename in the test imports).
```diff
diff --git a/pom.xml b/pom.xml
--- a/pom.xml
+++ b/pom.xml
@@ -311,9 +311,9 @@
 
     <!-- Plugin test deps -->
     <dependency>
-      <groupId>uk.org.lidalia</groupId>
+      <groupId>com.github.valfirst</groupId>
       <artifactId>slf4j-test</artifactId>
-      <version>1.2.0</version>
+      <version>3.0.1</version>
       <scope>test</scope>
     </dependency>
     <dependency>
diff --git a/src/test/java/com/github/searls/jasmine/format/JasmineResultLoggerTest.java b/src/test/java/com/github/searls/jasmine/format/JasmineResultLoggerTest.java
--- a/src/test/java/com/github/searls/jasmine/format/JasmineResultLoggerTest.java
+++ b/src/test/java/com/github/searls/jasmine/format/JasmineResultLoggerTest.java
@@ -27,9 +27,9 @@
 import org.mockito.InjectMocks;
 import org.mockito.Mock;
 import org.mockito.junit.jupiter.MockitoExtension;
-import uk.org.lidalia.slf4jtest.LoggingEvent;
-import uk.org.lidalia.slf4jtest.TestLogger;
-import uk.org.lidalia.slf4jtest.TestLoggerFactory;
+import com.github.valfirst.slf4jtest.LoggingEvent;
+import com.github.valfirst.slf4jtest.TestLogger;
+import com.github.valfirst.slf4jtest.TestLoggerFactory;
 
 import javax.annotation.Nullable;
 import java.util.List;
```

### Past case 2: org.mockito:mockito-core 4.11.0 -> 5.3.1 (pholser/junit-quickcheck)
Symptom: java.lang.AssertionError
  java.lang.AssertionError: expected:<[3, 6]> but was:<[]>
Behavior change: Default mock maker changed subclass -> inline
Fix (RESEARCHER_WRITTEN, written by the researchers (validated, but not the project's own fix); validated: all tests pass): Restore Mockito's pre-5 default mock maker for the tests (documented Mockito 5 migration option: mockito-extensions/org.mockito.plugins.MockMaker = mock-maker-subclass).
```diff
diff --git a/core/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker b/core/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker
new file mode 100644
--- /dev/null
+++ b/core/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker
@@ -0,0 +1,1 @@
+mock-maker-subclass
```

### Past case 3: org.slf4j:slf4j-api 1.7.36 -> 2.0.6 (alphagov/pay-adminusers)
Symptom: java.lang.ClassCastException; java.lang.ExceptionInInitializerError; java.lang.NoClassDefFoundError
  java.lang.ClassCastException: class org.slf4j.helpers.NOPLogger cannot be cast to class ch.qos.logback.classic.Logger (org.slf4j.helpers.NOPLogger and ch.qos.logback.classic.Logger are in unnamed module of loader 'app')
  java.lang.Exception: java.lang.ExceptionInInitializerError
Behavior change: LoggerFactory returns NOP instead of logback
Fix (FRAMEWORK_MIGRATION, derived from the developers' fix; validated: all tests pass): logback-classic/core 1.3.5 under the existing Dropwizard 2. Developer fix was the Dropwizard 2->3 migration 70fffbc56f (#2049).
```diff
diff --git a/pom.xml b/pom.xml
--- a/pom.xml
+++ b/pom.xml
@@ -178,7 +178,12 @@
         <dependency>
             <groupId>ch.qos.logback</groupId>
             <artifactId>logback-classic</artifactId>
-            <version>1.2.11</version>
+            <version>1.3.5</version>
+        </dependency>
+        <dependency>
+            <groupId>ch.qos.logback</groupId>
+            <artifactId>logback-core</artifactId>
+            <version>1.3.5</version>
         </dependency>
         <dependency>
             <groupId>uk.gov.service.notify</groupId>
```


## Project files (at the breaking commit)
### pom.xml  (build file (declares the updated dependency))
```
<?xml version="1.0" encoding="UTF-8"?>
<!--
  ~ Copyright (c) 2022 SPARQL Anything Contributors @ http://github.com/sparql-anything
  ~
  ~ Licensed under the Apache License, Version 2.0 (the "License");
  ~ you may not use this file except in compliance with the License.
  ~ You may obtain a copy of the License at
  ~
  ~      http://www.apache.org/licenses/LICENSE-2.0
  ~
  ~ Unless required by applicable law or agreed to in writing, software
  ~ distributed under the License is distributed on an "AS IS" BASIS,
  ~ WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  ~ See the License for the specific language governing permissions and
  ~ limitations under the License.
  -->

<project xmlns="http://maven.apache.org/POM/4.0.0"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
	<modelVersion>4.0.0</modelVersion>

	<groupId>com.github.sparqlanything</groupId>
	<artifactId>sparql-anything-parent</artifactId>
	<version>0.8.0-SNAPSHOT</version>
	<packaging>pom</packaging>

	<name>sparql.anything</name>
	<description>An opinionated approach to SPARQL any file</description>
	<url>https://github.com/SPARQL-Anything/sparql.anything</url>

	<properties>
		<project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
		<project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
		<maven.compiler.source>11</maven.compiler.source>
		<maven.compiler.target>11</maven.compiler.target>
	</properties>

	<licenses>
		<license>
			<name>Apache License, Version 2.0</name>
			<url>https://github.com/SPARQL-Anything/sparql.anything/blob/HEAD/LICENSE</url>
			<distribution>repo</distribution>
		</license>
	</licenses>

	<developers>
		<developer>
			<name>Luigi Asprino</name>
			<email>luigi.asprino@unibo.it</email>
			<organization>FICLIT</organization>
			<organizationUrl>https://ficlit.unibo.it/it</organizationUrl>
		</developer>
		<developer>
			<name>Enrico Daga</name>
			<email>enrico.daga@open.ac.uk</email>
			<organization>The Open University</organization>
			<organizationUrl>https://kmi.open.ac.uk</organizationUrl>
		</developer>
	</developers>

	<scm>
		<connection>scm:git:git://github.com/SPARQL-Anything/sparql.anything.git</connection>
		<developerConnection>scm:git:ssh://github.com:SPARQL-Anything/sparql.anything.git</developerConnection>
		<url>https://github.com/SPARQL-Anything/sparql.anything/tree/v0.3-DEV</url>
	</scm>

	<distributionManagement>
		<snapshotRepository>
			<id>ossrh</id>
			<url>https://oss.sonatype.org/content/repositories/snapshots</url>
		</snapshotRepository>
	</distributionManagement>


	<repositories>
		<repository>
			<id>oss.sonatype.org-snapshot</id>
			<url>https://oss.sonatype.org/content/repositories/snapshots</url>
			<releases>
				<enabled>false</enabled>
			</releases>
			<snapshots>
				<enabled>true</enabled>
			</snapshots>
		</repository>
	</repositories>

	<modules>
		<module>sparql-anything-engine</module>
		<module>sparql-anything-model</module>
		<module>sparql-anything-parser</module>
		<module>sparql-anything-json</module>
		<module>sparql-anything-yaml</module>
		<module>sparql-anything-markdown</module>
		<module>sparql-anything-testutils</module>
		<module>sparql-anything-xml</module>
		<module>sparql-anything-csv</module>
		<module>sparql-anything-cli</module>
		<module>sparql-anything-metadata</module>
		<module>sparql-anything-binary</module>
		<module>sparql-anything-text</module>
		<module>sparql-anything-html</module>
		<module>sparql-anything-it</module>
		<module>sparql-anything-fuseki</module>
		<module>sparql-anything-spreadsheet</module>
		<module>sparql-anything-rdf</module>
		<module>sparql-anything-archive</module>
		<module>sparql-anything-docs</module>
		<module>sparql-anything-bib</module>
	</modules>

	<build>
		<sourceDirectory>src/main/java</sourceDirectory>
		<plugins>
			<plugin>
				<groupId>org.apache.maven.plugins</groupId>
				<artifactId>maven-compiler-plugin</artifactId>
				<version>3.8.0</version>
				<configuration>
					<source>11</source>
					<target>11</target>
				</configuration>
			</plugin>
			<plugin>
				<groupId>org.apache.maven.plugins</groupId>
				<artifactId>maven-jar-plugin</artifactId>
				<version>3.2.0</version>
				<configuration>
					<archive>
						<index>true</index>
						<manifest>
							<addClasspath>true</addClasspath>

							<addDefaultImplementationEntries/>
							<addDefaultSpecificationEntries/>
							<addBuildEnvironmentEntries/>

						</manifest>
						<manifestEntries>
							<Implementation-Title>${project.name}</Implementation-Title>
							<Implementation-Version>${project.version}</Implementation-Version>
							<url>${project.url}</url>
						</manifestEntries>

					</archive>
				</configuration>
			</plugin>
		</plugins>
	</build>

	<profiles>


		<profile>
			<id>release-sign-artifacts</id>
			<activation>
				<property>
					<name>performRelease</name>
					<value>true</value>
				</property>
			</activation>
			<build>
				<plugins>
					<plugin>
						<groupId>org.apache.maven.plugins</groupId>
						<artifactId>maven-compiler-plugin</artifactId>
						<version>3.8.0</version>
						<configuration>
							<release>11</release>
						</configuration>
					</plugin>

					<plugin>
						<groupId>org.apache.maven.plugins</groupId>
						<artifactId>maven-source-plugin</artifactId>
						<version>2.2.1</version>
						<executions>
							<execution>
								<id>attach-sources</id>
								<goals>
									<goal>jar-no-fork</goal>
								</goals>
							</execution>
						</executions>
					</plugin>
					<plugin>
						<groupId>org.apache.maven.plugins</groupId>
						<artifactId>maven-javadoc-plugin</artifactId>
						<version>2.9.1</version>
						<!-- https://bugs.openjdk.java.net/browse/JDK-8212233 -->
						<configuration>
							<source>8</source>
						</configuration>
						<executions>
							<execution>
								<id>attach-javadocs</id>
								<goals>
									<goal>jar</goal>
								</goals>
							</execution>
						</executions>
					</plugin>

					<plugin>
						<groupId>org.apache.maven.plugins</groupId>
						<artifactId>maven-gpg-plugin</artifactId>
						<version>1.5</version>
						<executions>
							<execution>
								<id>sign-artifacts</id>
								<phase>verify</phase>
								<goals>
									<goal>sign</goal>
								</goals>
							</execution>
						</executions>
					</plugin>
					<plugin>
						<groupId>org.sonatype.plugins</groupId>
						<artifactId>nexus-staging-maven-plugin</artifactId>
						<version>1.6.7</version>
						<extensions>true</extensions>
						<configuration>
							<serverId>ossrh</serverId>
							<nexusUrl>https://oss.sonatype.org/</nexusUrl>
							<autoReleaseAfterClose>true</autoReleaseAfterClose>
						</configuration>
					</plugin>
				</plugins>
			</build>
		</profile>
	</profiles>

	<dependencyManagement>
		<dependencies>

			<!-- https://mvnrepository.com/artifact/org.apache.jena/apache-jena-libs -->
			<dependency>
				<groupId>org.apache.jena</groupId>
				<artifactId>apache-jena-libs</artifactId>
				<version>4.2.0</version>
				<type>pom</type>
				<!-- <exclusions> -->
				<!-- <exclusion> -->
				<!-- <groupId>org.slf4j</groupId> -->
				<!-- <artifactId>jcl-over-slf4j</artifactId> -->
				<!-- </exclusion> -->
				<!-- </exclusions> -->
			</dependency>

			<dependency>
				<groupId>org.apache.jena</groupId>
				<artifactId>jena-fuseki-main</artifactId>
				<version>4.2.0</version>
			</dependency>

			<!-- Commons configuration -->
			<dependency>
				<groupId>org.apache.commons</groupId>
				<artifactId>commons-configuration2</artifactId>
				<version>2.1.1</version>
			</dependency>
			<dependency>
				<groupId>commons-beanutils</groupId>
				<artifactId>commons-beanutils</artifactId>
				<version>1.9.4</version>
			</dependency>

			<!-- https://mvnrepository.com/artifact/org.apache.commons/commons-text -->
			<dependency>
				<groupId>org.apache.commons</groupId>
				<artifactId>commons-text</artifactId>
				<version>1.9</version>
			</dependency>


			<dependency>
				<groupId>com.google.guava</groupId>
				<artifactId>guava</artifactId>
				<version>30.1-jre</version>
			</dependency>

			<dependency>
				<groupId>org.slf4j</groupId>
				<artifactId>slf4j-simple</artifactId>
				<version>1.7.7</version>
			</dependency>

			<dependency>
				<groupId>org.jsoup</groupId>
				<artifactId>jsoup</artifactId>
				<version>1.15.3</version>
			</dependency>

			<!-- https://mvnrepository.com/artifact/commons-io/commons-io -->
			<dependency>
				<groupId>commons-io</groupId>
				<artifactId>commons-io</artifactId>
				<version>2.8.0</version>
			</dependency>

			<!-- https://mvnrepository.com/artifact/org.apache.commons/commons-csv -->
			<dependency>
				<groupId>org.apache.commons</groupId>
				<artifactId>commons-csv</artifactId>
				<version>1.8</version>
			</dependency>

			<dependency>
				<groupId>com.drewnoakes</groupId>
				<artifactId>metadata-extractor</artifactId>
				<version>2.15.0</version>
			</dependency>

			<dependency>
				<groupId>org.antlr</groupId>
				<artifactId>antlr4-runtime</artifactId>
				<version>4.7</version>
			</dependency>

			<!-- https://mvnrepository.com/artifact/org.json/json -->
			<dependency>
				<groupId>org.json</groupId>
				<artifactId>json</artifactId>
				<version>20200518</version>
			</dependency>
			<!-- dependency> <groupId>com.jsoniter</groupId> <artifactId>jsoniter</artifactId> 
				<version>0.9.19</version> </dependency -->
			<!-- https://mvnrepository.com/artifact/com.fasterxml.jackson.core/jackson-core -->
			<dependency>
				<groupId>com.fasterxml.jackson.core</groupId>
				<artifactId>jackson-core</artifactId>
				<version>2.12.4</version>
			</dependency>
			<!-- https://mvnrepository.com/artifact/org.snakeyaml/snakeyaml-engine -->
			<dependency>
				<groupId>org.snakeyaml</groupId>
				<artifactId>snakeyaml-engine</artifactId>
				<version>2.3</version>
			</dependency>
			<dependency>
				<groupId>org.javassist</groupId>
				<artifactId>javassist</artifactId>
				<version>3.21.0-GA</version>
			</dependency>
			<!-- https://mvnrepository.com/artifact/org.apache.commons/commons-compress -->
			<dependency>
				<groupId>org.apache.commons</groupId>
				<artifactId>commons-compress</artifactId>
				<version>1.21</version>
			</dependency>

			<!-- https://mvnrepository.com/artifact/org.apache.poi/poi-ooxml -->
			<dependency>
				<groupId>org.apache.poi</groupId>
				<artifactId>poi-ooxml</artifactId>
				<version>5.0.0</version>
			</dependency>

			<dependency>
				<groupId>io.github.basilapi</groupId>
				<artifactId>sparql</artifactId>
				<version>0.8.3</version>
				<exclusions>
					<exclusion>
						<groupId>org.apache.jena</groupId>
						<artifactId>jena-core</artifactId>
					</exclusion>
					<exclusion>
						<groupId>org.apache.jena</groupId>
						<artifactId>jena-arq</artifactId>
					</exclusion>
				</exclusions>
			</dependency>

			<!-- https://mvnrepository.com/artifact/commons-cli/commons-cli -->
			<dependency>
				<groupId>commons-cli</groupId>
				<artifactId>commons-cli</artifactId>
				<version>1.4</version>
			</dependency>

			<dependency>
				<groupId>junit</groupId>
				<artifactId>junit</artifactId>
				<version>4.13.1</version>
				<scope>test</scope>
			</dependency>

			<dependency>
				<groupId>org.freemarker</groupId>
				<artifactId>freemarker</artifactId>
				<version>2.3.28</version>
			</dependency>

			<dependency>
				<groupId>com.github.jsurfer</groupId>
				<artifactId>jsurfer-jackson</artifactId>
				<version>1.6.3</version>
			</dependency>

			<!-- https://mvnrepository.com/artifact/com.ximpleware/vtd-xml -->
			<dependency>
				<groupId>com.ximpleware</groupId>
				<artifactId>vtd-xml</artifactId>
				<version>2.13.4</version>
			</dependency>


		</dependencies>
	</dependencyManagement>

	<dependencies>
		<dependency>
			<groupId>org.slf4j</groupId>
			<artifactId>slf4j-api</artifactId>
			<version>1.7.7</version>
		</dependency>

		<dependency>
			<groupId>org.slf4j</groupId>
			<artifactId>slf4j-simple</artifactId>
			<version>1.7.7</version>
		</dependency>
	</dependencies>
</project>
```

### sparql-anything-html/pom.xml  (build file (declares the updated dependency))
```
<!--
  ~ Copyright (c) 2022 SPARQL Anything Contributors @ http://github.com/sparql-anything
  ~
  ~ Licensed under the Apache License, Version 2.0 (the "License");
  ~ you may not use this file except in compliance with the License.
  ~ You may obtain a copy of the License at
  ~
  ~      http://www.apache.org/licenses/LICENSE-2.0
  ~
  ~ Unless required by applicable law or agreed to in writing, software
  ~ distributed under the License is distributed on an "AS IS" BASIS,
  ~ WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  ~ See the License for the specific language governing permissions and
  ~ limitations under the License.
  -->

<project
	xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd"
	xmlns="http://maven.apache.org/POM/4.0.0"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	<modelVersion>4.0.0</modelVersion>
	<parent>
		<groupId>com.github.sparqlanything</groupId>
		<artifactId>sparql-anything-parent</artifactId>
		<version>0.8.0-SNAPSHOT</version>
		<relativePath>..</relativePath>
	</parent>
	<artifactId>sparql-anything-html</artifactId>
	<dependencies>
		<dependency>
			<groupId>com.microsoft.playwright</groupId>
			<artifactId>playwright</artifactId>
			<version>1.17.0</version>
		</dependency>
		<dependency>
			<groupId>com.github.sparqlanything</groupId>
			<artifactId>sparql-anything-model</artifactId>
			<version>${project.version}</version>
		</dependency>
		<dependency>
			<groupId>junit</groupId>
			<artifactId>junit</artifactId>
			<scope>test</scope>
		</dependency>
		<dependency>
			<groupId>org.jsoup</groupId>
			<artifactId>jsoup</artifactId>
		</dependency>
		<dependency>
			<groupId>com.github.sparqlanything</groupId>
			<artifactId>sparql-anything-testutils</artifactId>
			<version>${project.version}</version>
			<scope>test</scope>
		</dependency>

		<!-- https://mvnrepository.com/artifact/org.apache.any23/apache-any23-core -->
		<dependency>
			<groupId>org.apache.any23</groupId>
			<artifactId>apache-any23-core</artifactId>
			<version>2.5</version>
		</dependency>


		<!-- <dependency> -->
		<!-- <groupId>commons-httpclient</groupId> -->
		<!-- <artifactId>commons-httpclient</artifactId> -->
		<!-- <exclusions> -->
		<!-- <exclusion> -->
		<!-- <groupId>commons-codec</groupId> -->
		<!-- <artifactId>commons-codec</artifactId> -->
		<!-- </exclusion> -->
		<!-- </exclusions> -->
		<!-- </dependency> -->
	</dependencies>
</project>
```

### sparql-anything-html/src/test/java/com/github/sparqlanything/html/HTMLMicrodataTest.java  (failing test)
```
/*
 * Copyright (c) 2022 SPARQL Anything Contributors @ http://github.com/sparql-anything
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.github.sparqlanything.html;

import com.github.sparqlanything.testutils.AbstractTriplifierTester;
import org.junit.Test;

import java.util.Properties;

public class HTMLMicrodataTest extends AbstractTriplifierTester {

	public HTMLMicrodataTest() {
		super(new HTMLTriplifier(), new Properties(), "html", "nq");
		this.setPrintWholeGraph(true);
	}

	@Test
	public void testMicrodata1() {
		this.assertResultIsIsomorphicWithExpected();
	}
	
	protected void properties(Properties properties) {
		properties.setProperty(HTMLTriplifier.PROPERTY_METADATA, "true");
	}

}
```

### sparql-anything-html/src/test/java/com/github/sparqlanything/html/HTMLMicrodataRemoteTest.java  (failing test)
```
/*
 * Copyright (c) 2022 SPARQL Anything Contributors @ http://github.com/sparql-anything
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package com.github.sparqlanything.html;

import com.github.sparqlanything.testutils.AbstractTriplifierTester;
import org.apache.jena.riot.RDFDataMgr;
import org.junit.Test;

import java.net.MalformedURLException;
import java.net.URISyntaxException;
import java.net.URL;
import java.util.Properties;

public class HTMLMicrodataRemoteTest extends AbstractTriplifierTester {

	public HTMLMicrodataRemoteTest() {
		super(new HTMLTriplifier(), new Properties(), "html", "nq");
		this.setPrintWholeGraph(true);
	}

	@Test
	public void testMicrodata1() {
		this.assertResultIsIsomorphicWithExpected();
	}

	protected void properties(Properties properties) {
		properties.setProperty(HTMLTriplifier.PROPERTY_METADATA, "true");
	}

	protected void prepare() throws URISyntaxException {
		logger.debug("{} (prepare)", name.getMethodName());
		// Root is Document
		try {
			url = new URL(
					"https://raw.githubusercontent.com/SPARQL-Anything/sparql-anything.cc-site/main/examples/Microdata1.html");
		} catch (MalformedURLException e) {
			e.printStackTrace();
		}
		logger.debug("Input filename: {}", url.toString());
		properties.setProperty("location", url.toURI().toString());
		properties.setProperty("blank-nodes", "false");
		logger.debug("Input location: {}", url.toURI().toString());
		properties.setProperty("root", "http://www.example.org/document");
		//
		// RDF file name
		String rdfFileName = name.getMethodName().substring(4) + "." + expectedExtension;
		if (!useDatasetGraph) {
			expected = RDFDataMgr.loadModel(getClass().getClassLoader().getResource(rdfFileName).toURI().toString())
					.getGraph();
		} else {
			expectedDatasetGraph = super.replaceLocation(RDFDataMgr
					.loadDatasetGraph(getClass().getClassLoader().getResource(rdfFileName).toURI().toString()));
		}

	}

}
```

### sparql-anything-html/src/test/resources/Microdata1.html  (resource file named in the failing test)
```
<!--
  ~ Copyright (c) 2022 SPARQL Anything Contributors @ http://github.com/sparql-anything
  ~
  ~ Licensed under the Apache License, Version 2.0 (the "License");
  ~ you may not use this file except in compliance with the License.
  ~ You may obtain a copy of the License at
  ~
  ~      http://www.apache.org/licenses/LICENSE-2.0
  ~
  ~ Unless required by applicable law or agreed to in writing, software
  ~ distributed under the License is distributed on an "AS IS" BASIS,
  ~ WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  ~ See the License for the specific language governing permissions and
  ~ limitations under the License.
  -->

<!DOCTYPE html>
<html>

<body>

	<div itemscope itemtype="https://schema.org/Movie">
		<h1 itemprop="name">Avatar</h1>
		<span>Director: James Cameron (born August 16, 1954)</span>
	</div>

</body>

</html>
```

### sparql-anything-html/src/test/resources/Microdata1.nq  (resource file named in the failing test)
```
<html/body> <https://html.spec.whatwg.org/#innerHTML> "<div itemscope itemtype=\"https://schema.org/Movie\"> \n <h1 itemprop=\"name\">Avatar</h1> <span>Director: James Cameron (born August 16, 1954)</span> \n</div>" .
<html/body> <https://html.spec.whatwg.org/#innerText> "Avatar Director: James Cameron (born August 16, 1954) Avatar Director: James Cameron (born August 16, 1954) Avatar Director: James Cameron (born August 16, 1954)" .
<html/body> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/xhtml#body> .
<html/body> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_1> <html/body/div> .
<html/body/div/span> <https://html.spec.whatwg.org/#innerHTML> "Director: James Cameron (born August 16, 1954)" .
<html/body/div/span> <https://html.spec.whatwg.org/#innerText> "Director: James Cameron (born August 16, 1954)" .
<html/body/div/span> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/xhtml#span> .
<html/body/div/span> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_1> "Director: James Cameron (born August 16, 1954)" .
_:Bnode1fmiunljfx2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://schema.org/Movie> .
_:Bnode1fmiunljfx2 <https://schema.org/name> "Avatar" .
<html/body/div/h1> <https://html.spec.whatwg.org/#innerHTML> "Avatar" .
<html/body/div/h1> <https://html.spec.whatwg.org/#innerText> "Avatar" .
<html/body/div/h1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/xhtml#h1> .
<html/body/div/h1> <http://www.w3.org/1999/xhtml#itemprop> "name" .
<html/body/div/h1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_1> "Avatar" .
<html/head> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/xhtml#head> .
<html> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://sparql.xyz/facade-x/ns/root> .
<html> <https://html.spec.whatwg.org/#innerHTML> "<head></head>\n<body> \n <div itemscope itemtype=\"https://schema.org/Movie\"> \n  <h1 itemprop=\"name\">Avatar</h1> <span>Director: James Cameron (born August 16, 1954)</span> \n </div>  \n</body>" .
<html> <https://html.spec.whatwg.org/#innerText> "Avatar Director: James Cameron (born August 16, 1954)  Avatar Director: James Cameron (born August 16, 1954) Avatar Director: James Cameron (born August 16, 1954) Avatar Director: James Cameron (born August 16, 1954)" .
<html> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/xhtml#html> .
<html> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_1> <html/head> .
<html> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_2> <html/body> .
<html/body/div> <https://html.spec.whatwg.org/#innerHTML> "<h1 itemprop=\"name\">Avatar</h1> <span>Director: James Cameron (born August 16, 1954)</span>" .
<html/body/div> <https://html.spec.whatwg.org/#innerText> "Avatar Director: James Cameron (born August 16, 1954) Avatar Director: James Cameron (born August 16, 1954)" .
<html/body/div> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/xhtml#div> .
<html/body/div> <http://www.w3.org/1999/xhtml#itemscope> "" .
<html/body/div> <http://www.w3.org/1999/xhtml#itemtype> "https://schema.org/Movie" .
<html/body/div> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_1> <html/body/div/h1> .
<html/body/div> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_2> <html/body/div/span> .
<location> <http://www.w3.org/1999/xhtml/microdata#item> _:Bnode1fmiunljfx2 .
<html/body> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_1> <html/body/div> <location> .
<html/body> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/xhtml#body> <location> .
<html/body> <https://html.spec.whatwg.org/#innerText> "Avatar Director: James Cameron (born August 16, 1954) Avatar Director: James Cameron (born August 16, 1954) Avatar Director: James Cameron (born August 16, 1954)" <location> .
<html/body> <https://html.spec.whatwg.org/#innerHTML> "<div itemscope itemtype=\"https://schema.org/Movie\"> \n <h1 itemprop=\"name\">Avatar</h1> <span>Director: James Cameron (born August 16, 1954)</span> \n</div>" <location> .
<html/body/div/span> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_1> "Director: James Cameron (born August 16, 1954)" <location> .
<html/body/div/span> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/xhtml#span> <location> .
<html/body/div/span> <https://html.spec.whatwg.org/#innerText> "Director: James Cameron (born August 16, 1954)" <location> .
<html/body/div/span> <https://html.spec.whatwg.org/#innerHTML> "Director: James Cameron (born August 16, 1954)" <location> .
_:Bnode1fmiunljfx2 <https://schema.org/name> "Avatar" <location> .
_:Bnode1fmiunljfx2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <https://schema.org/Movie> <location> .
<html/body/div/h1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_1> "Avatar" <location> .
<html/body/div/h1> <http://www.w3.org/1999/xhtml#itemprop> "name" <location> .
<html/body/div/h1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/xhtml#h1> <location> .
<html/body/div/h1> <https://html.spec.whatwg.org/#innerText> "Avatar" <location> .
<html/body/div/h1> <https://html.spec.whatwg.org/#innerHTML> "Avatar" <location> .
<html/head> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/xhtml#head> <location> .
<html/body/div> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_2> <html/body/div/span> <location> .
<html/body/div> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_1> <html/body/div/h1> <location> .
<html/body/div> <http://www.w3.org/1999/xhtml#itemtype> "https://schema.org/Movie" <location> .
<html/body/div> <http://www.w3.org/1999/xhtml#itemscope> "" <location> .
<html/body/div> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/xhtml#div> <location> .
<html/body/div> <https://html.spec.whatwg.org/#innerText> "Avatar Director: James Cameron (born August 16, 1954) Avatar Director: James Cameron (born August 16, 1954)" <location> .
<html/body/div> <https://html.spec.whatwg.org/#innerHTML> "<h1 itemprop=\"name\">Avatar</h1> <span>Director: James Cameron (born August 16, 1954)</span>" <location> .
<html> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_2> <html/body> <location> .
<html> <http://www.w3.org/1999/02/22-rdf-syntax-ns#_1> <html/head> <location> .
<html> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/1999/xhtml#html> <location> .
<html> <https://html.spec.whatwg.org/#innerText> "Avatar Director: James Cameron (born August 16, 1954)  Avatar Director: James Cameron (born August 16, 1954) Avatar Director: James Cameron (born August 16, 1954) Avatar Director: James Cameron (born August 16, 1954)" <location> .
<html> <https://html.spec.whatwg.org/#innerHTML> "<head></head>\n<body> \n <div itemscope itemtype=\"https://schema.org/Movie\"> \n  <h1 itemprop=\"name\">Avatar</h1> <span>Director: James Cameron (born August 16, 1954)</span> \n </div>  \n</body>" <location> .
<html> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://sparql.xyz/facade-x/ns/root> <location> .
<location> <http://www.w3.org/1999/xhtml/microdata#item> _:Bnode1fmiunljfx2 <location> .
```

### sparql-anything-markdown/src/test/resources/Document.ttl  (resource file named in the failing test)
```
@prefix fx: <http://sparql.xyz/facade-x/ns/> .
@prefix xyz: <http://sparql.xyz/facade-x/data/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#>.

<http://www.example.org/document> a fx:root .
<http://www.example.org/document> a xyz:Document .
<http://www.example.org/document> rdf:_1 <http://www.example.org/document/paragraph/1> .
<http://www.example.org/document/paragraph/1> a xyz:Paragraph .
<http://www.example.org/document/paragraph/1> rdf:_1 "A document with some text."^^xsd:string .
```

### sparql-anything-testutils/src/main/java/com/github/sparqlanything/testutils/TestUtils.java  (class in the failing stack trace)
```
/*
 * Copyright (c) 2022 SPARQL Anything Contributors @ http://github.com/sparql-anything
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.github.sparqlanything.testutils;

import org.apache.jena.graph.Graph;
import org.apache.jena.graph.Node;
import org.apache.jena.graph.Triple;
import org.apache.jena.riot.Lang;
import org.apache.jena.riot.RDFDataMgr;
import org.apache.jena.sparql.core.DatasetGraph;
import org.apache.jena.sparql.core.Quad;
import org.apache.jena.util.iterator.ExtendedIterator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.ByteArrayOutputStream;
import java.util.HashSet;
import java.util.Iterator;
import java.util.Set;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

public class TestUtils {

	protected static final Logger logger = LoggerFactory.getLogger(TestUtils.class);

	public static final void printDebugDiff(Graph left, Graph right){
		if (logger.isDebugEnabled()) {
			ExtendedIterator<Triple> it = left.find();
			logger.debug(">> Test left items are also in right");
			while (it.hasNext()) {
				Triple t = it.next();
				logger.trace(">> {}", t);

				if (!right.contains(t)) {
					logger.debug(">> {} not found in right", t);
					logger.debug(">> (T) {} {} {} {}", t.getSubject().getClass().getSimpleName(),
							t.getPredicate().getClass().getSimpleName(), t.getObject().getClass().getSimpleName(),
							(t.getObject().isLiteral() && t.getObject().getLiteralDatatypeURI() != null)
									? t.getObject().getLiteralDatatypeURI()
									: "");
				}
			}
			it = right.find();
			logger.debug(">> Test right items are also in left");
			while (it.hasNext()) {
				Triple t = it.next();
				logger.trace("<< {}", t);
				if (!left.contains(t)) {
					logger.debug("<< {} not found in left", t);
					logger.debug("<< (T) {} {} {} {}", t.getSubject().getClass().getSimpleName(),
							t.getPredicate().getClass().getSimpleName(), t.getObject().getClass().getSimpleName(),
							(t.getObject().isLiteral() && t.getObject().getLiteralDatatypeURI() != null)
									? t.getObject().getLiteralDatatypeURI()
									: "");
				}
			}
		}
	}

	public static final void printDebugDiff(DatasetGraph left, DatasetGraph right){
		if (logger.isDebugEnabled()) {
			Iterator<Quad> it = left.find();
			while (it.hasNext()) {
				Quad q = it.next();
				logger.trace(">> {}", q);

				if (!right.contains(q)) {
					logger.debug(">> {} not found in right", q);
					logger.debug(">> (T) {} {} {} {} {}", q.getSubject().getClass().getSimpleName(),
							q.getPredicate().getClass().getSimpleName(), q.getObject().getClass().getSimpleName(),
							(q.getObject().isLiteral() && q.getObject().getLiteralDatatypeURI() != null)
									? q.getObject().getLiteralDatatypeURI()
									: "",
							q.getGraph().getClass().getSimpleName());
				}
			}
			it = right.find();
			while (it.hasNext()) {
				Quad t = it.next();
				logger.trace("<< {}", t);
				if (!left.contains(t)) {
					logger.debug("<< {} not found in left", t);
					logger.debug("<< (T) {} {} {} {} {}", t.getSubject().getClass().getSimpleName(),
							t.getPredicate().getClass().getSimpleName(), t.getObject().getClass().getSimpleName(),
							(t.getObject().isLiteral() && t.getObject().getLiteralDatatypeURI() != null)
									? t.getObject().getLiteralDatatypeURI()
									: "",
							t.getGraph().getClass().getSimpleName());
				}
			}
		}
	}

	public static final void printWholeGraph(Graph expected, Graph obtained){
		ByteArrayOutputStream baosExpected = new ByteArrayOutputStream();
		RDFDataMgr.write(baosExpected, expected, Lang.TTL);
		ByteArrayOutputStream baosResult = new ByteArrayOutputStream();
		RDFDataMgr.write(baosResult, obtained, Lang.TTL);
		logger.warn("Whole files\n\nExpected\n\n{}\n\n--------\n\nResult\n\n{}", baosExpected.toString(),
				baosResult.toString());

	}

	public static final void printWholeGraph(DatasetGraph expected, DatasetGraph obtained){
		ByteArrayOutputStream baosExpected = new ByteArrayOutputStream();
		RDFDataMgr.write(baosExpected, expected, Lang.NQ);
		ByteArrayOutputStream baosResult = new ByteArrayOutputStream();
		RDFDataMgr.write(baosResult, obtained, Lang.NQ);
		logger.warn("Whole files\n\nExpected\n\n{}\n\n--------\n\nObtained\n\n{}", baosExpected.toString(),
				baosResult.toString());
	}

	public static void assertIsomorphic(DatasetGraph expected, DatasetGraph got){

		Iterator<Node> it = expected.listGraphNodes();
		Set<String> expectedGraphUris = new HashSet<>();
		while (it.hasNext()) {
			expectedGraphUris.add(it.next().getURI());
		}

		it = got.listGraphNodes();
		Set<String> resultGraphUris = new HashSet<>();

		while (it.hasNext()) {
			resultGraphUris.add(it.next().getURI());
		}

		assertTrue((expected.getDefaultGraph()
				.isIsomorphicWith(got.getDefaultGraph())));
		assertEquals(expectedGraphUris, resultGraphUris);

		it = expected.listGraphNodes();
		while (it.hasNext()) {
			Node g = (Node) it.next();
			assertTrue(got.containsGraph(g));
			assertTrue(expected.getGraph(g).isIsomorphicWith(got.getGraph(g)));
		}
	}
}
```

### sparql-anything-testutils/src/main/java/com/github/sparqlanything/testutils/AbstractTriplifierTester.java  (class in the failing stack trace)
```
/*
 * Copyright (c) 2022 SPARQL Anything Contributors @ http://github.com/sparql-anything
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.github.sparqlanything.testutils;

import com.github.sparqlanything.model.BaseFacadeXGraphBuilder;
import com.github.sparqlanything.model.FacadeXGraphBuilder;
import com.github.sparqlanything.model.Slice;
import com.github.sparqlanything.model.Slicer;
import com.github.sparqlanything.model.Triplifier;
import com.github.sparqlanything.model.TriplifierHTTPException;
import org.apache.jena.graph.Graph;
import org.apache.jena.graph.Node;
import org.apache.jena.graph.NodeFactory;
import org.apache.jena.graph.Triple;
import org.apache.jena.riot.RDFDataMgr;
import org.apache.jena.sparql.core.DatasetGraph;
import org.apache.jena.sparql.core.DatasetGraphFactory;
import org.apache.jena.sparql.core.Quad;
import org.junit.Before;
import org.junit.Rule;
import org.junit.rules.TestName;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.URISyntaxException;
import java.net.URL;
import java.util.Iterator;
import java.util.Properties;

import static org.junit.Assert.assertTrue;

public class AbstractTriplifierTester {
	protected static final Logger logger = LoggerFactory.getLogger(AbstractTriplifierTester.class);

	protected Triplifier triplifier;
	protected Properties properties;
	protected URL url;
	protected String extension = null;

	protected Graph result;
	protected Graph expected;

	protected DatasetGraph expectedDatasetGraph;
	protected DatasetGraph resultDatasetGraph;

	protected Exception resultException = null;

	private boolean printWholeGraph = false;
	protected boolean useDatasetGraph = false;
	protected boolean throwsException = false;

	protected String expectedExtension;
	private static final String locationUriGraph = "location";

	public AbstractTriplifierTester(Triplifier t, Properties p, String extension, String expectedExtension) {
		this.triplifier = t;
		this.properties = p;
		this.extension = extension;
		this.expectedExtension = expectedExtension;
		if (expectedExtension.equals("nq")) {
			useDatasetGraph = true;
		}
	}

	public AbstractTriplifierTester(Triplifier t, Properties p, String extension) {
		this(t, p, extension, "ttl");
	}

	public void setPrintWholeGraph(boolean printWholeGraph) {
		this.printWholeGraph = printWholeGraph;
	}

	@Rule
	public TestName name = new TestName();

	protected void prepare() throws URISyntaxException {
		logger.debug("{} (prepare)", name.getMethodName());
		// Root is Document
		// Ignore content after '$', to allow multiple methods to reuse the same files
		String fileName;
		if(name.getMethodName().contains("$")){
			fileName = name.getMethodName().substring(4);
			fileName = fileName.substring(0, fileName.indexOf('$'));
			fileName = fileName + "." + extension;
		}else{
			fileName = name.getMethodName().substring(4) + "." + extension;
		}
		logger.debug("Input filename: {}", fileName);
		url = getClass().getClassLoader().getResource(fileName);
		properties.setProperty("location", url.toURI().toString());
		properties.setProperty("blank-nodes", "false");
		logger.debug("Input location: {}", url.toURI().toString());
		properties.setProperty("root", "http://www.example.org/document");
		//
		// RDF file name
		String rdfFileName;
		if(name.getMethodName().contains("$")){
			rdfFileName = name.getMethodName().substring(4);
			rdfFileName = rdfFileName.substring(0, rdfFileName.indexOf('$'));
			rdfFileName = rdfFileName + "." + expectedExtension;
		}else{
			rdfFileName = name.getMethodName().substring(4) + "." + expectedExtension;
		}
		if (!useDatasetGraph) {
			expected = RDFDataMgr.loadModel(getClass().getClassLoader().getResource(rdfFileName).toURI().toString())
					.getGraph();
		} else {
			expectedDatasetGraph = replaceLocation(RDFDataMgr
					.loadDatasetGraph(getClass().getClassLoader().getResource(rdfFileName).toURI().toString()));
		}

	}

	protected void properties(Properties properties) {
	}

	@Before
	public void run() throws URISyntaxException, TriplifierHTTPException, IOException {
		logger.info("{} (run)", name.getMethodName());

		try {
			// Template method
			prepare();
			//
			properties(properties);
			//
			perform();
			//
			inspect();
		}catch(Exception e){
			if (throwsException) {
				resultException = e;
			} else {
				throw e;
			}
		}
	}

	protected void inspect() {
		logger.debug("{} (inspect)", name.getMethodName());
		logger.debug("Expected (left) VS Result (right)");
		if (!useDatasetGraph) {
			TestUtils.printDebugDiff(expected, result);
			if (printWholeGraph) {
				TestUtils.printWholeGraph(expected, result);
			}
		} else {
			TestUtils.printDebugDiff(this.expectedDatasetGraph, this.resultDatasetGraph);
			if (printWholeGraph) {
				TestUtils.printWholeGraph(replaceLocation(this.expectedDatasetGraph), this.resultDatasetGraph);
			}
		}
	}

	protected void perform() throws TriplifierHTTPException, IOException, URISyntaxException {
		logger.debug("{} (perform)", name.getMethodName());
		logger.info("{}", properties);
		String graphName = Triplifier.getRootArgument(properties);
		logger.debug("Graph name: {}", graphName);
		FacadeXGraphBuilder b = new BaseFacadeXGraphBuilder(graphName, properties);
		if(properties.containsKey("slice")){
			final Slicer slicer = (Slicer) triplifier;
			final Iterable<Slice> it = slicer.slice(properties);
			final Iterator<Slice> iterator = it.iterator();
			while(iterator.hasNext()) {
				Slice slice = iterator.next();
				slicer.triplify(slice, properties, b);
			}
		}else{
			triplifier.triplify(properties, b);
		}
		if (!useDatasetGraph) {
			this.result = b.getDatasetGraph().getGraph(NodeFactory.createURI(graphName));
		} else {
			this.resultDatasetGraph = b.getDatasetGraph();
		}
	}


	protected void assertResultIsIsomorphicWithExpected() {
		if (!useDatasetGraph) {
			assertTrue(this.result.isIsomorphicWith(expected));
		} else {
			TestUtils.assertIsomorphic(this.expectedDatasetGraph, this.resultDatasetGraph);
		}
	}

	protected DatasetGraph replaceLocation(DatasetGraph g) {
		DatasetGraph dg = DatasetGraphFactory.create();
		g.find().forEachRemaining(q -> {
			dg.add(new Quad(resolveNode(q.getGraph()), new Triple(resolveNode(q.getSubject()),
					resolveNode(q.getPredicate()), resolveNode(q.getObject()))));
		});
		return dg;
	}

	private Node resolveNode(Node n) {
		if (n.isURI() && n.getURI().equals(locationUriGraph)) {
			try {
				return NodeFactory.createURI(url.toURI().toString());
			} catch (URISyntaxException e) {
				e.printStackTrace();
			}
		}
		return n;
	}

}
```


Now write the explanation and the single ```diff block.
