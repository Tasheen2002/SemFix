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
`org.mockito:mockito-core` was updated from `4.11.0` to `5.4.0`. The project compiles, but tests now fail.

## Failure (from the build log)
Failing test classes: com.pholser.junit.quickcheck.internal.generator.CompositeGeneratorTest
Exception types: java.lang.AssertionError
Error lines:
- java.lang.AssertionError: expected:<[3, 6]> but was:<[]>
Project stack frames:
- com.pholser.junit.quickcheck.internal.generator.CompositeGeneratorTest (CompositeGeneratorTest.java:90)

## Similar past breakages and their validated fixes (from the knowledge base)
They come from OTHER projects. Use them for the idea of the fix; adapt it to this project's files.

### Past case 1: org.mockito:mockito-core 4.11.0 -> 5.1.0 (googleapis/gax-java)
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

### Past case 2: org.apache.httpcomponents:httpclient 4.5.1 -> 4.5.13 (lookfirst/sardine)
Symptom: org.junit.ComparisonFailure
  org.junit.ComparisonFailure: expected:<[]m (400 response phra...> but was:<[status code: 400, reason phrase: ]m (400 response phra...>
Behavior change: Exception message format changed (status code and reason phrase prefixed)
Fix (TEST_EXPECTATION_UPDATE, the project's developers; validated: all tests pass): Developer updated the expected exception message in SardineExceptionTest to the new httpclient format (landed with 4.5.14).
```diff
diff --git a/src/test/java/com/github/sardine/impl/SardineExceptionTest.java b/src/test/java/com/github/sardine/impl/SardineExceptionTest.java
--- a/src/test/java/com/github/sardine/impl/SardineExceptionTest.java
+++ b/src/test/java/com/github/sardine/impl/SardineExceptionTest.java
@@ -11,7 +11,7 @@
 	public void testMessage()
 	{
 		final SardineException e = new SardineException("m", 400, "response phrase");
-		assertEquals("m (400 response phrase)", e.getMessage());
+		assertEquals("status code: 400, reason phrase: m (400 response phrase)", e.getMessage());
 		assertEquals("response phrase", e.getResponsePhrase());
 		assertEquals(400, e.getStatusCode());
 	}
```

### Past case 3: org.slf4j:slf4j-api 1.7.32 -> 2.0.5 (searls/jasmine-maven-plugin)
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


## Project files (at the breaking commit)
### pom.xml  (build file (declares the updated dependency))
```
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.pholser</groupId>
    <artifactId>junit-quickcheck</artifactId>
    <version>1.1-SNAPSHOT</version>
    <packaging>pom</packaging>
    <name>junit-quickcheck</name>
    <description>Property-based testing, JUnit-style</description>
    <url>http://github.com/pholser/junit-quickcheck</url>

    <parent>
        <groupId>org.sonatype.oss</groupId>
        <artifactId>oss-parent</artifactId>
        <version>9</version>
    </parent>

    <licenses>
        <license>
            <name>The MIT License</name>
            <url>http://www.opensource.org/licenses/mit-license.php</url>
            <distribution>repo</distribution>
        </license>
    </licenses>
    <scm>
        <connection>scm:git:git://github.com/pholser/junit-quickcheck.git</connection>
        <developerConnection>scm:git:ssh://git@github.com/pholser/junit-quickcheck.git</developerConnection>
        <url>http://github.com/pholser/junit-quickcheck</url>
      <tag>HEAD</tag>
  </scm>
    <issueManagement>
        <system>GitHub Issues</system>
        <url>https://github.com/pholser/junit-quickcheck/issues</url>
    </issueManagement>
    <developers>
        <developer>
            <id>pholser</id>
            <name>Paul Holser</name>
            <email>pholser@alumni.rice.edu</email>
            <url>http://www.pholser.com</url>
        </developer>
    </developers>
    <contributors>
        <contributor>
            <name>Javier Fernandez-Ivern</name>
            <roles><role>java.time.* generators</role></roles>
        </contributor>
        <contributor>
            <name>Michael S. Daines</name>
            <roles><role>examples</role></roles>
        </contributor>
        <contributor>
            <name>Florent Ramière</name>
            <roles><role>code highlighting in markdown</role></roles>
        </contributor>
        <contributor>
            <name>Thomas Heilbronner</name>
            <roles><role>markdown correction</role></roles>
        </contributor>
        <contributor>
            <name>Peter Kofler</name>
            <roles><role>examples corrections</role></roles>
        </contributor>
        <contributor>
            <name>davidhart82</name>
            <roles><role>several patches</role></roles>
        </contributor>
        <contributor>
            <name>Jason Hinch</name>
            <roles><role>Fixed lambda generator to produce pure functions</role></roles>
        </contributor>
        <contributor>
            <name>Philipp Classen</name>
            <roles><role>Sped up int/long generation</role></roles>
        </contributor>
        <contributor>
            <name>Brent Vukmer</name>
            <roles><role>Added Encoded override for PropertiesGenerator</role></roles>
        </contributor>
        <contributor>
            <name>Pablo Gonzalez Alonso</name>
            <roles><role>Added support for Kotlin annotations</role></roles>
        </contributor>
        <contributor>
            <name>ryu1.sakai</name>
            <roles><role>Added @Distinct config for aggregate types</role></roles>
        </contributor>
        <contributor>
            <name>Cameron Samak</name>
            <roles><role>Ignoring shrinks that are equal to the shrinkee</role></roles>
        </contributor>
        <contributor>
            <name>Diego Berrueta</name>
            <roles><role>Added support for generating null values</role></roles>
        </contributor>
        <contributor>
            <name>Julien Debon</name>
            <roles><role>Trying to improve stuff like shrinking</role></roles>
        </contributor>
    </contributors>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <github.global.server>github</github.global.server>
        <sonatypeOssDistMgmtSnapshotsUrl>https://oss.sonatype.org/content/repositories/snapshots/</sonatypeOssDistMgmtSnapshotsUrl>
        <arguments />
    </properties>

    <modules>
        <module>core</module>
        <module>generators</module>
        <module>guava</module>
        <module>examples</module>
    </modules>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>junit</groupId>
                <artifactId>junit</artifactId>
                <version>4.13.2</version>
            </dependency>

            <dependency>
                <groupId>org.hamcrest</groupId>
                <artifactId>hamcrest-core</artifactId>
                <version>2.2</version>
            </dependency>
            <dependency>
                <groupId>org.hamcrest</groupId>
                <artifactId>hamcrest-library</artifactId>
                <version>2.2</version>
            </dependency>
            <dependency>
                <groupId>org.slf4j</groupId>
                <artifactId>slf4j-api</artifactId>
                <version>2.0.7</version>
            </dependency>
            <dependency>
                <groupId>org.mockito</groupId>
                <artifactId>mockito-core</artifactId>
                <version>5.4.0</version>
            </dependency>
            <dependency>
                <groupId>com.google.guava</groupId>
                <artifactId>guava</artifactId>
                <version>31.1-jre</version>
            </dependency>
            <dependency>
                <groupId>com.google.guava</groupId>
                <artifactId>guava-testlib</artifactId>
                <version>31.1-jre</version>
            </dependency>
            <dependency>
                <groupId>ch.qos.logback</groupId>
                <artifactId>logback-classic</artifactId>
                <version>1.3.5</version>
            </dependency>

            <dependency>
                <groupId>com.github.spotbugs</groupId>
                <artifactId>spotbugs-annotations</artifactId>
                <version>4.7.2</version>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <build>
        <pluginManagement>
            <plugins>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-release-plugin</artifactId>
                    <version>3.0.0</version>
                    <configuration>
                        <mavenExecutorId>forked-path</mavenExecutorId>
                        <useReleaseProfile>false</useReleaseProfile>
                        <arguments>${arguments} -Psonatype-oss-release</arguments>
                    </configuration>
                </plugin>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-surefire-plugin</artifactId>
                    <version>3.1.0</version>
                    <dependencies>
                        <dependency>
                            <groupId>org.apache.maven.surefire</groupId>
                            <artifactId>surefire-junit47</artifactId>
                            <version>3.1.0</version>
                        </dependency>
                    </dependencies>
                    <configuration>
                        <includes>
                            <include>**/*.class</include>
                        </includes>
                        <excludedGroups>com.pholser.junit.quickcheck.LongRunning</excludedGroups>
                    </configuration>
                </plugin>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-compiler-plugin</artifactId>
                    <version>3.11.0</version>
                    <configuration>
                        <source>1.8</source>
                        <target>1.8</target>
                        <!--<compilerArgs><arg>-parameters</arg></compilerArgs>-->
                    </configuration>
                </plugin>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-jar-plugin</artifactId>
                    <version>3.3.0</version>
                    <executions>
                        <execution>
                            <goals>
                                <goal>test-jar</goal>
                            </goals>
                        </execution>
                    </executions>
                </plugin>
                <plugin>
                    <groupId>org.jacoco</groupId>
                    <artifactId>jacoco-maven-plugin</artifactId>
                    <version>0.8.8</version>
                    <executions>
                        <execution>
                            <id>default-prepare-agent</id>
                            <goals>
                                <goal>prepare-agent</goal>
                            </goals>
                        </execution>
                        <execution>
                            <id>default-report</id>
                            <phase>prepare-package</phase>
                            <goals>
                                <goal>report</goal>
                            </goals>
                        </execution>
                    </executions>
                    <configuration>
                        <rules>
                            <rule implementation="org.jacoco.maven.RuleConfiguration">
                                <element>BUNDLE</element>
                                <limits>
                                    <limit implementation="org.jacoco.report.check.Limit">
                                        <counter>INSTRUCTION</counter>
                                        <value>COVEREDRATIO</value>
                                        <minimum>0.98</minimum>
                                    </limit>
                                    <limit implementation="org.jacoco.report.check.Limit">
                                        <counter>CLASS</counter>
                                        <value>MISSEDCOUNT</value>
                                        <maximum>0</maximum>
                                    </limit>
                                </limits>
                            </rule>
                        </rules>
                    </configuration>
                </plugin>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-pmd-plugin</artifactId>
                    <version>3.21.0</version>
                    <configuration>
                        <minimumTokens>120</minimumTokens>
                        <targetJdk>1.8</targetJdk>
                    </configuration>
                    <executions>
                        <execution>
                            <phase>compile</phase>
                            <goals>
                                <goal>cpd-check</goal>
                            </goals>
                        </execution>
                    </executions>
                </plugin>
                <plugin>
                    <groupId>com.github.spotbugs</groupId>
                    <artifactId>spotbugs-maven-plugin</artifactId>
                    <version>4.7.2.1</version>
                    <configuration>
                        <effort>Max</effort>
                        <threshold>Low</threshold>
                        <xmlOutput>true</xmlOutput>
                    </configuration>
                    <executions>
                        <execution>
                            <phase>verify</phase>
                            <goals>
                                <goal>check</goal>
                            </goals>
                        </execution>
                    </executions>
                </plugin>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-site-plugin</artifactId>
                    <version>3.12.1</version>
                    <dependencies>
                        <dependency>
                            <groupId>org.apache.maven.doxia</groupId>
                            <artifactId>doxia-module-markdown</artifactId>
                            <version>1.12.0</version>
                        </dependency>
                    </dependencies>
                    <configuration>
                        <skipDeploy>true</skipDeploy>
                    </configuration>
                </plugin>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-project-info-reports-plugin</artifactId>
                    <version>3.4.5</version>
                </plugin>

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
                            <configuration>
                                <gpgArguments>
                                    <arg>--pinentry-mode</arg>
                                    <arg>loopback</arg>
                                </gpgArguments>
                            </configuration>
                        </execution>
                    </executions>
                </plugin>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-javadoc-plugin</artifactId>
                    <version>3.5.0</version>
                    <configuration>
                        <source>8</source>
                        <show>protected</show>
                        <nohelp>true</nohelp>
                        <header>junit-quickcheck ${project.version}</header>
                        <footer>junit-quickcheck ${project.version}</footer>
                        <doctitle>junit-quickcheck ${project.version}</doctitle>
                        <excludePackageNames>*.internal.*:org.junit.*</excludePackageNames>
                        <links>
                            <link>https://docs.oracle.com/javase/8/docs/api</link>
                            <link>http://junit.org/junit4/javadoc/latest/</link>
                            <link>https://guava.dev/releases/30.1-jre/api/docs/</link>
                        </links>
                        <bottom><![CDATA[<i>&copy; Copyright 2010-2021 Paul R. Holser, Jr.  All rights reserved. Licensed under The MIT License. pholser@alumni.rice.edu</i>]]></bottom>
                    </configuration>
                    <executions>
                        <execution>
                            <id>attach-javadocs</id>
                            <goals>
                                <goal>jar</goal>
                            </goals>
                        </execution>
                        <execution>
                            <goals>
                                <goal>javadoc</goal>
                            </goals>
                            <phase>site</phase>
                        </execution>
                    </executions>
                </plugin>

            </plugins>
        </pluginManagement>

        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-source-plugin</artifactId>
                <version>3.3.0</version>
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
                <groupId>com.github.github</groupId>
                <artifactId>site-maven-plugin</artifactId>
                <version>0.12</version>
                <configuration>
                    <message>Creating site for ${project.artifactId}, ${project.version}</message>
                    <path>${project.distributionManagement.site.url}</path>
                    <merge>true</merge>
                </configuration>
                <executions>
                    <execution>
                        <id>github-site</id>
                        <goals>
                            <goal>site</goal>
                        </goals>
                        <phase>site-deploy</phase>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>

    <reporting>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-project-info-reports-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-javadoc-plugin</artifactId>
                <reportSets>
                    <reportSet>
                        <id>default</id>
                        <reports>
                            <report>javadoc</report>
                        </reports>
                    </reportSet>
                </reportSets>
            </plugin>
            <plugin>
                <groupId>org.jacoco</groupId>
                <artifactId>jacoco-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-pmd-plugin</artifactId>
            </plugin>
        </plugins>
    </reporting>

    <profiles>
        <profile>
            <id>standard-jdk</id>
            <activation>
                <file>
                    <exists>${java.home}/../lib/tools.jar</exists>
                </file>
            </activation>
            <properties>
                <tools-jar>${java.home}/../lib/tools.jar</tools-jar>
            </properties>
        </profile>
    </profiles>

    <distributionManagement>
        <site>
            <id>github-pages-site</id>
            <url>site/${project.version}/</url>
        </site>

        <snapshotRepository>
            <id>sonatype-nexus-snapshots</id>
            <name>Sonatype Nexus Snapshots</name>
            <url>${sonatypeOssDistMgmtSnapshotsUrl}</url>
        </snapshotRepository>
        <repository>
            <id>sonatype-nexus-staging</id>
            <name>Nexus Release Repository</name>
            <url>https://oss.sonatype.org/service/local/staging/deploy/maven2/</url>
        </repository>

    </distributionManagement>
</project>
```

### core/pom.xml  (build file (declares the updated dependency))
```
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>com.pholser</groupId>
        <artifactId>junit-quickcheck</artifactId>
        <version>1.1-SNAPSHOT</version>
    </parent>

    <artifactId>junit-quickcheck-core</artifactId>
    <version>1.1-SNAPSHOT</version>
    <packaging>jar</packaging>
    <name>junit-quickcheck-core</name>
    <description>Property-based testing, JUnit-style: core functionality</description>
    <url>http://github.com/pholser/junit-quickcheck</url>

    <dependencies>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
        </dependency>
        <dependency>
            <groupId>org.hamcrest</groupId>
            <artifactId>hamcrest-core</artifactId>
        </dependency>
        <dependency>
            <groupId>org.javaruntype</groupId>
            <artifactId>javaruntype</artifactId>
            <version>1.3</version>
        </dependency>
        <dependency>
            <groupId>ognl</groupId>
            <artifactId>ognl</artifactId>
            <version>3.3.4</version>
        </dependency>
        <dependency>
            <groupId>ru.vyarus</groupId>
            <artifactId>generics-resolver</artifactId>
            <version>3.0.3</version>
        </dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
        </dependency>

        <dependency>
            <groupId>com.github.spotbugs</groupId>
            <artifactId>spotbugs-annotations</artifactId>
            <optional>true</optional>
        </dependency>

        <dependency>
            <groupId>org.hamcrest</groupId>
            <artifactId>hamcrest-library</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-core</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava-testlib</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>ch.qos.logback</groupId>
            <artifactId>logback-classic</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-release-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.jacoco</groupId>
                <artifactId>jacoco-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-pmd-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>com.github.spotbugs</groupId>
                <artifactId>spotbugs-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

### generators/pom.xml  (build file (declares the updated dependency))
```
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>com.pholser</groupId>
        <artifactId>junit-quickcheck</artifactId>
        <version>1.1-SNAPSHOT</version>
    </parent>

    <artifactId>junit-quickcheck-generators</artifactId>
    <version>1.1-SNAPSHOT</version>
    <packaging>jar</packaging>
    <name>junit-quickcheck-generators</name>
    <description>Property-based testing, JUnit-style: basic generators</description>
    <url>http://github.com/pholser/junit-quickcheck</url>

    <dependencies>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
        </dependency>
        <dependency>
            <groupId>com.pholser</groupId>
            <artifactId>junit-quickcheck-core</artifactId>
            <version>1.1-SNAPSHOT</version>
        </dependency>

        <dependency>
            <groupId>org.hamcrest</groupId>
            <artifactId>hamcrest-core</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.hamcrest</groupId>
            <artifactId>hamcrest-library</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-core</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava-testlib</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>ch.qos.logback</groupId>
            <artifactId>logback-classic</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.pholser</groupId>
            <artifactId>junit-quickcheck-core</artifactId>
            <version>1.1-SNAPSHOT</version>
            <scope>test</scope>
            <type>test-jar</type>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-release-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.jacoco</groupId>
                <artifactId>jacoco-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-pmd-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>com.github.spotbugs</groupId>
                <artifactId>spotbugs-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>eu.somatik.serviceloader-maven-plugin</groupId>
                <artifactId>serviceloader-maven-plugin</artifactId>
                <version>1.4.0</version>
                <configuration>
                    <services>
                        <param>com.pholser.junit.quickcheck.generator.Generator</param>
                    </services>
                </configuration>
                <executions>
                    <execution>
                        <goals>
                            <goal>generate</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

### guava/pom.xml  (build file (declares the updated dependency))
```
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>com.pholser</groupId>
        <artifactId>junit-quickcheck</artifactId>
        <version>1.1-SNAPSHOT</version>
    </parent>

    <artifactId>junit-quickcheck-guava</artifactId>
    <version>1.1-SNAPSHOT</version>
    <packaging>jar</packaging>
    <name>junit-quickcheck-guava</name>
    <description>Property-based testing, JUnit-style: generators for Guava types</description>
    <url>http://github.com/pholser/junit-quickcheck</url>

    <dependencies>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
        </dependency>
        <dependency>
            <groupId>com.pholser</groupId>
            <artifactId>junit-quickcheck-generators</artifactId>
            <version>1.1-SNAPSHOT</version>
        </dependency>
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava</artifactId>
            <scope>compile</scope>
        </dependency>

        <dependency>
            <groupId>org.hamcrest</groupId>
            <artifactId>hamcrest-core</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.hamcrest</groupId>
            <artifactId>hamcrest-library</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-core</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>ch.qos.logback</groupId>
            <artifactId>logback-classic</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.pholser</groupId>
            <artifactId>junit-quickcheck-core</artifactId>
            <version>1.1-SNAPSHOT</version>
            <scope>test</scope>
            <type>test-jar</type>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-release-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.jacoco</groupId>
                <artifactId>jacoco-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-pmd-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>com.github.spotbugs</groupId>
                <artifactId>spotbugs-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>eu.somatik.serviceloader-maven-plugin</groupId>
                <artifactId>serviceloader-maven-plugin</artifactId>
                <version>1.4.0</version>
                <configuration>
                    <services>
                        <param>com.pholser.junit.quickcheck.generator.Generator</param>
                    </services>
                </configuration>
                <executions>
                    <execution>
                        <goals>
                            <goal>generate</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

### core/src/test/java/com/pholser/junit/quickcheck/internal/generator/CompositeGeneratorTest.java  (failing test)
```
/*
 The MIT License

 Copyright (c) 2010-2021 Paul R. Holser, Jr.

 Permission is hereby granted, free of charge, to any person obtaining
 a copy of this software and associated documentation files (the
 "Software"), to deal in the Software without restriction, including
 without limitation the rights to use, copy, modify, merge, publish,
 distribute, sublicense, and/or sell copies of the Software, and to
 permit persons to whom the Software is furnished to do so, subject to
 the following conditions:

 The above copyright notice and this permission notice shall be
 included in all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

package com.pholser.junit.quickcheck.internal.generator;

import static java.util.Arrays.asList;
import static java.util.Collections.singletonList;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertTrue;
import static org.mockito.Mockito.atLeastOnce;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.pholser.junit.quickcheck.generator.Generator;
import com.pholser.junit.quickcheck.internal.Weighted;
import com.pholser.junit.quickcheck.random.SourceOfRandomness;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.mockito.Mock;
import org.mockito.junit.MockitoJUnit;
import org.mockito.junit.MockitoRule;

public class CompositeGeneratorTest {
    @Rule public final MockitoRule mockito = MockitoJUnit.rule();

    private CompositeGenerator composite;
    @Mock private Generator<Integer> first;
    @Mock private Generator<Integer> second;
    @Mock private Generator<Integer> third;
    @Mock private SourceOfRandomness random;

    @Before public void setUp() {
        composite =
            new CompositeGenerator(
                asList(
                    new Weighted<>(first, 2),
                    new Weighted<>(second, 5),
                    new Weighted<>(third, 7)));
    }

    @Test public void capabilityOfShrinkingDependsOnComponents() {
        when(first.canShrink(9)).thenReturn(true);
        when(second.canShrink(9)).thenReturn(false);
        when(third.canShrink(9)).thenReturn(true);

        assertTrue(composite.canShrink(9));
    }

    @Test public void
    capabilityOfShrinkingFalseIfNoComponentsCanShrinkAValue() {
        when(first.canShrink(8)).thenReturn(false);
        when(second.canShrink(8)).thenReturn(false);
        when(third.canShrink(8)).thenReturn(false);

        assertFalse(composite.canShrink(8));
    }

    @Test public void shrinkingChoosesAComponentCapableOfShrinkingTheValue() {
        when(first.canShrink(7)).thenReturn(true);
        when(second.canShrink(7)).thenReturn(false);
        when(third.canShrink(7)).thenReturn(true);
        when(first.types()).thenReturn(singletonList(Integer.class));
        when(first.doShrink(random, 7)).thenReturn(asList(3, 6));
        when(random.nextInt(9)).thenReturn(1);

        assertEquals(asList(3, 6), composite.shrink(random, 7));
        verify(first, atLeastOnce()).doShrink(random, 7);
    }
}
```


Now write the explanation and the single ```diff block.
