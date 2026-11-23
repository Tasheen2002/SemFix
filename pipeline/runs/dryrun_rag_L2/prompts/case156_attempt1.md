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
`org.slf4j:slf4j-api` was updated from `1.7.32` to `2.0.5`. The project compiles, but tests now fail.

## Failure (from the build log)
Failing test classes: com.github.searls.jasmine.format.JasmineResultLoggerTest
Exception types: java.lang.AssertionError
Error lines:
- java.lang.AssertionError:
SLF4J console output:
- SLF4J: No SLF4J providers were found.
- SLF4J: Defaulting to no-operation (NOP) logger implementation
- SLF4J: See https://www.slf4j.org/codes.html#noProviders for further details.
- SLF4J: Class path contains SLF4J bindings targeting slf4j-api versions 1.7.x or earlier.
- SLF4J: Ignoring binding found at [jar:file:/root/.m2/repository/uk/org/lidalia/slf4j-test/1.2.0/slf4j-test-1.2.0.jar!/org/slf4j/impl/StaticLoggerBinder.class]
- SLF4J: See https://www.slf4j.org/codes.html#ignoredBindings for an explanation.
Project stack frames:
- com.github.searls.jasmine.format.JasmineResultLoggerTest (JasmineResultLoggerTest.java:91)
- com.github.searls.jasmine.format.JasmineResultLoggerTest (JasmineResultLoggerTest.java:78)
- com.github.searls.jasmine.format.JasmineResultLoggerTest (JasmineResultLoggerTest.java:68)

## Similar past breakages and their validated fixes (from the knowledge base)
They come from OTHER projects. Use them for the idea of the fix; adapt it to this project's files.

### Past case 1: org.slf4j:slf4j-api 1.7.36 -> 2.0.5 (feedzai/pdb)
Symptom: java.lang.ClassCastException
  java.lang.ClassCastException: class org.slf4j.helpers.NOPLogger cannot be cast to class ch.qos.logback.classic.Logger (org.slf4j.helpers.NOPLogger and ch.qos.logback.classic.Logger are in unnamed module of loader 'app')
Behavior change: LoggerFactory returns NOPLogger
Fix (COMPANION_DEPENDENCY_UPGRADE, the project's developers; validated: all tests pass): slf4j 2.0.17 landed together with logback-classic 1.2.13 -> 1.3.16 (an SLF4J-2 provider), POM only. Fixes the R5 provider-selection change.
```diff
diff --git a/pom.xml b/pom.xml
--- a/pom.xml
+++ b/pom.xml
@@ -115,7 +115,7 @@
             <dependency>
                 <groupId>ch.qos.logback</groupId>
                 <artifactId>logback-classic</artifactId>
-                <version>1.2.11</version>
+                <version>1.3.16</version>
             </dependency>
             <dependency>
                 <groupId>org.slf4j</groupId>
```

### Past case 2: org.slf4j:slf4j-api 1.7.36 -> 2.0.5 (retest/recheck)
Symptom: java.lang.ClassCastException
  java.lang.ClassCastException: class org.slf4j.helpers.NOPLogger cannot be cast to class ch.qos.logback.classic.Logger (org.slf4j.helpers.NOPLogger and ch.qos.logback.classic.Logger are in unnamed module of loader 'app')
Behavior change: LoggerFactory returns NOPLogger
Fix (RESEARCHER_WRITTEN, written by the researchers (validated, but not the project's own fix); validated: all tests pass): Companion upgrade: logback 1.2.11 -> 1.3.5 (an SLF4J-2 provider), as in the validated pdb/jadler developer fixes.
```diff
diff --git a/pom.xml b/pom.xml
--- a/pom.xml
+++ b/pom.xml
@@ -46,7 +46,7 @@
 		<project.resources.sourceEncoding>UTF-8</project.resources.sourceEncoding>
 		<project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
 		<maven.surefire.and.failsafe.version>3.0.0-M6</maven.surefire.and.failsafe.version>
-		<logback.version>1.2.11</logback.version>
+		<logback.version>1.3.5</logback.version>
 		<eclipse.persistence.version>2.5.2</eclipse.persistence.version>
 	</properties>
```

### Past case 3: org.slf4j:slf4j-api 1.7.36 -> 2.0.5 (alphagov/pay-adminusers)
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
... (lines 0-0 omitted)
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>com.github.searls</groupId>
  <artifactId>jasmine-maven-plugin</artifactId>
  <version>3.0-SNAPSHOT</version>
  <packaging>maven-plugin</packaging>

  <name>jasmine-maven-plugin</name>
  <description>A JavaScript unit test plugin that processes JavaScript sources and Jasmine specs, prepares test runner HTML files, executes Jasmine specs headlessly with Chrome, and produces JUnit XML reports</description>
  <url>https://github.com/searls/jasmine-maven-plugin</url>
  <licenses>
    <license>
      <distribution>repo</distribution>
      <name>The Apache Software License, Version 2.0</name>
      <url>http://www.apache.org/licenses/LICENSE-2.0</url>
      <comments>Copyright Justin Searls</comments>
    </license>
  </licenses>
  <organization>
    <name>Justin Searls</name>
    <url>https://twitter.com/searls</url>
  </organization>
  <inceptionYear>2010</inceptionYear>
  <developers>
    <developer>
      <id>searls</id>
      <name>Justin Searls</name>
      <email>searls@gmail.com</email>
      <url>http://about.me/searls</url>
      <organization>Test Double</organization>
      <organizationUrl>http://testdouble.com</organizationUrl>
    </developer>
    <developer>
      <id>klieber</id>
      <name>Kyle Lieber</name>
      <email>klieber.github@mailnull.com</email>
      <url>http://kylelieber.com</url>
    </developer>
  </developers>
  <contributors>
    <contributor>
... (lines 43-111 omitted)
      <url>https://github.com/tongant</url>
    </contributor>
    <contributor>
      <name>Todd Quessenberry</name>
      <url>https://github.com/toddq</url>
    </contributor>
    <contributor>
      <name>Sam Jones</name>
      <url>https://github.com/samjonester</url>
    </contributor>
  </contributors>
  <scm>
    <url>https://github.com/searls/jasmine-maven-plugin</url>
    <connection>scm:git:git@github.com:searls/jasmine-maven-plugin.git</connection>
    <developerConnection>scm:git:git@github.com:searls/jasmine-maven-plugin.git</developerConnection>
    <tag>HEAD</tag>
  </scm>
  <distributionManagement>
    <snapshotRepository>
      <id>ossrh</id>
      <url>https://oss.sonatype.org/content/repositories/snapshots</url>
    </snapshotRepository>
  </distributionManagement>
  <issueManagement>
    <system>github</system>
    <url>https://github.com/searls/jasmine-maven-plugin/issues</url>
  </issueManagement>
  <ciManagement>
    <system>travis-ci</system>
    <url>https://travis-ci.org/searls/jasmine-maven-plugin</url>
  </ciManagement>
  <properties>
    <jetty.version>9.4.48.v20220622</jetty.version>
    <selenium.version>3.141.59</selenium.version>
    <jasmine.version>3.8.0</jasmine.version>
    <mockito.version>4.8.0</mockito.version>
    <webdrivermanager.version>5.3.0</webdrivermanager.version>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
    <java.version>1.8</java.version>
    <maven.compiler.target>${java.version}</maven.compiler.target>
    <maven.compiler.source>${java.version}</maven.compiler.source>
  </properties>

  <prerequisites>
    <maven>3.5.4</maven>
  </prerequisites>
... (lines 159-268 omitted)
    <dependency>
      <groupId>backport-util-concurrent</groupId>
      <artifactId>backport-util-concurrent</artifactId>
      <version>3.1</version>
    </dependency>
    <dependency>
      <groupId>org.webjars</groupId>
      <artifactId>webjars-locator</artifactId>
      <version>0.45</version>
    </dependency>
    <dependency>
      <groupId>org.webjars.npm</groupId>
      <artifactId>jasmine</artifactId>
      <version>${jasmine.version}</version>
    </dependency>
    <dependency>
      <groupId>io.github.bonigarcia</groupId>
      <artifactId>webdrivermanager</artifactId>
      <version>${webdrivermanager.version}</version>
    </dependency>
    <dependency>
      <groupId>javax.inject</groupId>
      <artifactId>javax.inject</artifactId>
      <version>1</version>
    </dependency>
    <dependency>
      <groupId>org.slf4j</groupId>
      <artifactId>slf4j-api</artifactId>
      <version>2.0.5</version>
    </dependency>
    <dependency>
      <groupId>com.google.guava</groupId>
      <artifactId>guava</artifactId>
      <version>31.1-jre</version>
    </dependency>

    <dependency>
      <groupId>org.immutables</groupId>
      <artifactId>value</artifactId>
      <version>2.9.1</version>
      <scope>provided</scope>
    </dependency>

    <!-- Plugin test deps -->
    <dependency>
      <groupId>uk.org.lidalia</groupId>
      <artifactId>slf4j-test</artifactId>
      <version>1.2.0</version>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.assertj</groupId>
      <artifactId>assertj-core</artifactId>
      <version>3.23.1</version>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.assertj</groupId>
... (lines 327-386 omitted)
            </nonFilteredFileExtensions>
          </configuration>
        </plugin>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
          <artifactId>maven-site-plugin</artifactId>
          <version>3.12.1</version>
          <configuration>
            <skipDeploy>true</skipDeploy>
            <attributes>
              <!--suppress MavenModelInspection -->
              <currentStableVersion>${releasedVersion.version}</currentStableVersion>
              <jasmineVersion>${jasmine.version}</jasmineVersion>
            </attributes>
          </configuration>
          <dependencies>
            <dependency>
              <groupId>org.apache.maven.doxia</groupId>
              <artifactId>doxia-module-markdown</artifactId>
              <version>1.11.1</version>
            </dependency>
          </dependencies>
        </plugin>
        <plugin>
          <groupId>org.apache.maven.plugins</groupId>
... (lines 412-462 omitted)
              <include>**/*.java</include>
            </includes>
          </configuration>
        </plugin>
      </plugins>
    </pluginManagement>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-plugin-plugin</artifactId>
        <version>3.6.4</version>
        <configuration>
          <goalPrefix>jasmine</goalPrefix>
          <!-- see http://jira.codehaus.org/browse/MNG-5346 -->
          <skipErrorNoDescriptorsFound>true</skipErrorNoDescriptorsFound>
        </configuration>
        <executions>
          <execution>
            <id>mojo-descriptor</id>
            <goals>
              <goal>descriptor</goal>
            </goals>
          </execution>
          <execution>
            <id>generated-helpmojo</id>
... (lines 488-532 omitted)
      <plugin>
        <groupId>org.jacoco</groupId>
        <artifactId>jacoco-maven-plugin</artifactId>
        <executions>
          <execution>
            <goals>
              <goal>prepare-agent</goal>
            </goals>
          </execution>
        </executions>
        <configuration>
          <excludes>
            <exclude>com/github/searls/jasmine/mojo/HelpMojo*</exclude>
            <!-- prevent 'Method code too large' exception -->
            <!-- see http://goo.gl/5THrnt -->
            <exclude>**com.steadystate*</exclude>
          </excludes>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.eluder.coveralls</groupId>
        <artifactId>coveralls-maven-plugin</artifactId>
        <version>4.3.0</version>
      </plugin>
      <plugin>
... (lines 558-566 omitted)
          </execution>
        </executions>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-scm-publish-plugin</artifactId>
        <version>3.1.0</version>
        <configuration>
          <checkoutDirectory>${project.build.directory}/scmpublish</checkoutDirectory>
          <checkinComment>Generating site for ${project.version}</checkinComment>
          <content>${project.reporting.outputDirectory}</content>
          <skipDeletedFiles>true</skipDeletedFiles>
          <pubScmUrl>scm:git:git@github.com:searls/jasmine-maven-plugin.git</pubScmUrl>
          <scmBranch>gh-pages</scmBranch>
        </configuration>
        <executions>
          <execution>
            <goals>
              <goal>publish-scm</goal>
            </goals>
            <phase>site-deploy</phase>
          </execution>
        </executions>
      </plugin>
      <plugin>
        <groupId>org.sonatype.plugins</groupId>
        <artifactId>nexus-staging-maven-plugin</artifactId>
        <version>1.6.13</version>
        <extensions>true</extensions>
        <configuration>
          <serverId>ossrh</serverId>
          <nexusUrl>https://oss.sonatype.org/</nexusUrl>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.sonatype.plugins</groupId>
        <artifactId>sisu-maven-plugin</artifactId>
        <version>1.4</version>
        <executions>
          <execution>
            <id>generate-index</id>
... (lines 608-745 omitted)
                    <arg>--pinentry-mode</arg>
                    <arg>loopback</arg>
                  </gpgArguments>
                </configuration>
              </execution>
            </executions>
          </plugin>
        </plugins>
      </build>
    </profile>
    <profile>
      <id>quick</id>
      <properties>
        <skipTests>true</skipTests>
        <jacoco.skip>true</jacoco.skip>
        <maven.javadoc.skip>true</maven.javadoc.skip>
        <maven.jxr.skip>true</maven.jxr.skip>
        <pmd.skip>true</pmd.skip>
      </properties>
    </profile>
  </profiles>
</project>
```

### src/test/java/com/github/searls/jasmine/format/JasmineResultLoggerTest.java  (failing test)
```
/*-
 * #%L
 * jasmine-maven-plugin
 * %%
 * Copyright (C) 2010 - 2017 Justin Searls
 * %%
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
 * #L%
 */
package com.github.searls.jasmine.format;

import com.github.searls.jasmine.model.JasmineResult;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import uk.org.lidalia.slf4jtest.LoggingEvent;
import uk.org.lidalia.slf4jtest.TestLogger;
import uk.org.lidalia.slf4jtest.TestLoggerFactory;

import javax.annotation.Nullable;
import java.util.List;
import java.util.function.Function;
import java.util.stream.Collectors;

import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
public class JasmineResultLoggerTest {

  private static final Function<LoggingEvent, String> EVENT_MESSAGE_FUNCTION = new Function<LoggingEvent, String>() {
    @Nullable
    @Override
    public String apply(@Nullable LoggingEvent loggingEvent) {
      return loggingEvent != null ? loggingEvent.getMessage() : null;
    }
  };

  private TestLogger logger = TestLoggerFactory.getTestLogger(JasmineResultLogger.class);

  @Mock
  private JasmineResult jasmineResult;

  @InjectMocks
  private JasmineResultLogger subject = new JasmineResultLogger();

  @AfterEach
  public void clearLoggers() {
    TestLoggerFactory.clear();
  }

  @Test
  public void shouldLogHeader() {
    subject.log(jasmineResult);
    assertMessage(JasmineResultLogger.HEADER);
  }

  @Test
  public void shouldLogDetails() {
    String details = "Fake Details";
    when(jasmineResult.getDetails()).thenReturn(details);

    subject.log(jasmineResult);

    assertMessage(JasmineResultLogger.HEADER);
    assertMessage(details);
  }

  private void assertMessage(String ... expectedMessages) {
    List<String> messages = logger.getLoggingEvents()
      .stream()
      .map(loggingEvent -> loggingEvent != null ? loggingEvent.getMessage() : null)
      .collect(Collectors.toList());

    for (String expectedMessage : expectedMessages) {
      Assertions.assertThat(messages)
        .describedAs("Expected %s to be logged.", expectedMessage)
        .contains(expectedMessage);
    }
  }
}
```


Now write the explanation and the single ```diff block.
