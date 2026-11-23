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
`org.apache.httpcomponents:httpclient` was updated from `4.5.1` to `4.5.13`. The project compiles, but tests now fail.

## Failure (from the build log)
Failing test classes: com.github.sardine.impl.SardineExceptionTest
Exception types: org.junit.ComparisonFailure
Error lines:
- org.junit.ComparisonFailure: expected:<[]m (400 response phra...> but was:<[status code: 400, reason phrase: ]m (400 response phra...>
Project stack frames:
- com.github.sardine.impl.SardineExceptionTest (SardineExceptionTest.java:14)

## Similar past breakages and their validated fixes (from the knowledge base)
They come from OTHER projects. Use them for the idea of the fix; adapt it to this project's files.

### Past case 1: org.mockito:mockito-core 4.11.0 -> 5.1.1 (pholser/junit-quickcheck)
Symptom: java.lang.AssertionError
  java.lang.AssertionError: expected:<[3, 6]> but was:<[]>
Behavior change: Mocked collaborator behaviour changed under the new default mock maker (inline mocks intercept methods that previously ran real code); observable as an empty shrink result
Fix (RESEARCHER_WRITTEN, written by the researchers (validated, but not the project's own fix); validated: all tests pass): Restore Mockito's pre-5 default mock maker for the tests (documented Mockito 5 migration option: mockito-extensions/org.mockito.plugins.MockMaker = mock-maker-subclass).
```diff
diff --git a/core/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker b/core/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker
new file mode 100644
--- /dev/null
+++ b/core/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker
@@ -0,0 +1,1 @@
+mock-maker-subclass
```

### Past case 2: com.thoughtworks.xstream:xstream 1.4.17 -> 1.4.19 (apache/logging-chainsaw)
Symptom: com.thoughtworks.xstream.security.ForbiddenClassException
  com.thoughtworks.xstream.security.ForbiddenClassException: org.apache.log4j.chainsaw.LogPanelPreferenceModel
Behavior change: Default deserialization security policy changed: types not explicitly allowed are now rejected
Fix (TEST_ADAPTATION_API_CONFIG, the project's developers; validated: all tests pass): Developer added XStream.allowTypes(LogPanelPreferenceModel.class) in the failing test: adapts to the new deny-by-default security policy.
```diff
diff --git a/src/test/java/org/apache/log4j/chainsaw/LogPanelPreferenceModelTest.java b/src/test/java/org/apache/log4j/chainsaw/LogPanelPreferenceModelTest.java
--- a/src/test/java/org/apache/log4j/chainsaw/LogPanelPreferenceModelTest.java
+++ b/src/test/java/org/apache/log4j/chainsaw/LogPanelPreferenceModelTest.java
@@ -41,6 +41,10 @@
         model.setToolTips(!model.isToolTips());
         
         XStream stream = new XStream(new DomDriver());
+        stream.allowTypes(new Class[]{
+            LogPanelPreferenceModel.class
+        });
+
         String xml = stream.toXML(model);
 //        System.out.println(xml);
```

### Past case 3: org.mockito:mockito-core 4.11.0 -> 5.1.0 (googleapis/gax-java)
Symptom: test failure
Behavior change: Default mock maker changed subclass -> inline; mocked final methods no longer run real delegation code, so a different interaction is recorded
Fix (RESEARCHER_WRITTEN, written by the researchers (validated, but not the project's own fix); validated: all tests pass): Restore Mockito's pre-5 default mock maker for the gax tests (mock-maker-subclass).
```diff
diff --git a/gax/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker b/gax/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker
new file mode 100644
--- /dev/null
+++ b/gax/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker
@@ -0,0 +1,1 @@
+mock-maker-subclass
```


## Project files (at the breaking commit)
### pom.xml  (build file (declares the updated dependency))
```
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.github.lookfirst</groupId>
    <artifactId>sardine</artifactId>
    <packaging>jar</packaging>
	<version>5.11-SNAPSHOT</version>
    <description>An easy to use WebDAV client for Java</description>
    <name>Sardine WebDAV client</name>
    <url>https://github.com/lookfirst/sardine</url>
    <parent>
        <groupId>org.sonatype.oss</groupId>
        <artifactId>oss-parent</artifactId>
        <version>9</version>
    </parent>
    <licenses>
        <license>
            <name>Apache 2.0</name>
            <url>http://www.apache.org/licenses/LICENSE-2.0</url>
        </license>
    </licenses>
    <scm>
        <connection>scm:git:git@github.com:lookfirst/sardine.git</connection>
        <developerConnection>scm:git:git@github.com:lookfirst/sardine.git</developerConnection>
        <url>git@github.com:lookfirst/sardine.git</url>
    </scm>
    <developers>
        <developer>
            <name>Jon Stevens</name>
            <id>lookfirst</id>
            <email>latchkey@gmail.com</email>
        </developer>
        <developer>
            <name>David Kocher</name>
            <id>iterate</id>
            <email>post@iterate.ch</email>
            <organization>iterate GmbH</organization>
        </developer>
    </developers>
    <distributionManagement>
        <repository>
            <id>sonatype-release</id>
            <name>Nexus Release Repository</name>
            <url>https://oss.sonatype.org/service/local/staging/deploy/maven2</url>
        </repository>
        <snapshotRepository>
            <id>sonatype-snapshot</id>
            <name>Nexus Snapshot Repository</name>
            <url>https://oss.sonatype.org/content/repositories/snapshots</url>
        </snapshotRepository>
    </distributionManagement>
    <build>
        <plugins>
            <plugin>
                <artifactId>maven-jar-plugin</artifactId>
                <version>2.6</version>
                <configuration>
                    <archive>
                        <manifest>
                            <mainClass>com.googlecode.sardine.Version</mainClass>
                            <addDefaultImplementationEntries>true</addDefaultImplementationEntries>
                            <addDefaultSpecificationEntries>true</addDefaultSpecificationEntries>
                        </manifest>
                    </archive>
                </configuration>
            </plugin>
            <plugin>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.3</version>
                <configuration>
                    <source>1.7</source>
                    <target>1.7</target>
                </configuration>
            </plugin>
            <plugin>
                <artifactId>maven-source-plugin</artifactId>
                <version>3.0.1</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>jar</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <artifactId>maven-javadoc-plugin</artifactId>
                <configuration>
                    <source>8</source>
                </configuration>
                <version>2.10.4</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>jar</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>2.19</version>
                <configuration>
                    <excludedGroups>com.github.sardine.IntegrationTest.class</excludedGroups>
                    <useFile>false</useFile>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-failsafe-plugin</artifactId>
                <version>2.19</version>
                <configuration>
                    <encoding>UTF-8</encoding>
                    <includes>
                        <include>**/*.java</include>
                    </includes>
                    <groups>com.github.sardine.IntegrationTest.class</groups>
                    <skipITs>${skipITs}</skipITs>
                </configuration>
                <executions>
                    <execution>
                        <goals>
                            <goal>integration-test</goal>
                            <goal>verify</goal>
                        </goals>
                    </execution>
                </executions>
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
                        <artifactId>maven-gpg-plugin</artifactId>
                        <version>1.6</version>
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
                        <version>1.6.8</version>
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
    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <!-- Skip integration tests by default with failsafe plugin -->
        <skipITs>true</skipITs>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.apache.httpcomponents</groupId>
            <artifactId>httpclient</artifactId>
            <version>4.5.13</version>
        </dependency>
        <!-- Sardine has a runtime dependency to JAXB. As this not part of JDK 11 anymore,
             we need a dependency on JAXB-->
        <dependency>
            <groupId>jakarta.xml.bind</groupId>
            <artifactId>jakarta.xml.bind-api</artifactId>
            <version>4.0.0</version>
        </dependency>
        <dependency>
            <groupId>org.glassfish.jaxb</groupId>
            <artifactId>jaxb-runtime</artifactId>
            <version>4.0.2</version>
            <scope>runtime</scope>
        </dependency>
        
        <dependency>
            <groupId>org.apache.ant</groupId>
            <artifactId>ant</artifactId>
            <version>1.10.11</version>
            <scope>provided</scope>
        </dependency>
        <!-- test utilities -->
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.1</version>
            <scope>test</scope>
        </dependency>
        
    </dependencies>
</project>
```

### src/test/java/com/github/sardine/impl/SardineExceptionTest.java  (failing test)
```
package com.github.sardine.impl;

import static org.junit.Assert.assertEquals;

import org.junit.Test;

public class SardineExceptionTest
{

	@Test
	public void testMessage()
	{
		final SardineException e = new SardineException("m", 400, "response phrase");
		assertEquals("m (400 response phrase)", e.getMessage());
		assertEquals("response phrase", e.getResponsePhrase());
		assertEquals(400, e.getStatusCode());
	}
}
```


Now write the explanation and the single ```diff block.
