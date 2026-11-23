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
`net.minidev:json-smart` was updated from `2.4.8` to `2.4.9`. The project compiles, but tests now fail.

## Failure (from the build log)
Failing test classes: TestSuite
Exception types: java.lang.IllegalArgumentException, org.btrplace.json.JSONConverterException, net.minidev.json.parser.ParseException
Error lines:
- java.lang.IllegalArgumentException: org.btrplace.json.JSONConverterException: net.minidev.json.parser.ParseException: Malicious payload, having non natural depths, parsing stoped on { at position 141434.
- Caused by: org.btrplace.json.JSONConverterException: net.minidev.json.parser.ParseException: Malicious payload, having non natural depths, parsing stoped on { at position 141434.
- Caused by: net.minidev.json.parser.ParseException: Malicious payload, having non natural depths, parsing stoped on { at position 141434.
- java.lang.IllegalArgumentException: org.btrplace.json.JSONConverterException: net.minidev.json.parser.ParseException: Malicious payload, having non natural depths, parsing stoped on { at position 49876.
- Caused by: org.btrplace.json.JSONConverterException: net.minidev.json.parser.ParseException: Malicious payload, having non natural depths, parsing stoped on { at position 49876.
- Caused by: net.minidev.json.parser.ParseException: Malicious payload, having non natural depths, parsing stoped on { at position 49876.
SLF4J console output:
- SLF4J: No SLF4J providers were found.
- SLF4J: Defaulting to no-operation (NOP) logger implementation
- SLF4J: See https://www.slf4j.org/codes.html#noProviders for further details.
Project stack frames:
- org.btrplace.json.JSON (JSON.java:78)
- org.btrplace.json.JSON (JSON.java:60)
- org.btrplace.scheduler.choco.IssuesTest (IssuesTest.java:515)
- org.btrplace.scheduler.choco.IssuesTest (IssuesTest.java:535)
- org.testng.internal.invokers.MethodInvocationHelper (MethodInvocationHelper.java:135)
- org.testng.internal.invokers.TestInvoker (TestInvoker.java:673)
- org.testng.internal.invokers.TestInvoker (TestInvoker.java:220)
- org.testng.internal.invokers.MethodRunner (MethodRunner.java:50)
- org.testng.internal.invokers.TestInvoker$MethodInvocationAgent (TestInvoker.java:945)
- org.testng.internal.invokers.TestInvoker (TestInvoker.java:193)
- org.testng.internal.invokers.TestMethodWorker (TestMethodWorker.java:146)
- org.testng.internal.invokers.TestMethodWorker (TestMethodWorker.java:128)

## Similar past breakages and their validated fixes (from the knowledge base)
They come from OTHER projects. Use them for the idea of the fix; adapt it to this project's files.

### Past case 1: commons-io:commons-io 2.7 -> 2.11.0 (damianszczepanik/cucumber-reporting)
Symptom: java.lang.IllegalArgumentException
  java.lang.IllegalArgumentException: Parameter 'srcFile' is not a file: src/test/resources/js
Behavior change: Exception type for a directory passed as srcFile changed IOException -> IllegalArgumentException (input validation / exception contract)
Fix (CLIENT_CODE_ADAPTATION, the project's developers; validated: all tests pass): Developer widened the catch to IOException | IllegalArgumentException in ReportBuilder, the class under the failing test.
```diff
diff --git a/src/main/java/net/masterthought/cucumber/ReportBuilder.java b/src/main/java/net/masterthought/cucumber/ReportBuilder.java
--- a/src/main/java/net/masterthought/cucumber/ReportBuilder.java
+++ b/src/main/java/net/masterthought/cucumber/ReportBuilder.java
@@ -175,7 +175,7 @@
         } catch (FileNotFoundException e) {
             LOG.log(Level.WARNING, "File not found: {0}", srcFile.getAbsolutePath());
             LOG.log(Level.FINE, "", e);
-        } catch (IOException e) {
+        } catch (IOException | IllegalArgumentException e) {
             throw new ValidationException(e);
         }
     }
```

### Past case 2: org.slf4j:slf4j-api 1.7.30 -> 2.0.0 (pac4j/dropwizard-pac4j)
Symptom: java.lang.RuntimeException; java.lang.reflect.InvocationTargetException; java.lang.IllegalStateException
  java.lang.RuntimeException: java.lang.reflect.InvocationTargetException
  Caused by: java.lang.reflect.InvocationTargetException
Behavior change: Logger factory selected changed from logback LoggerContext to NOP
Fix (FRAMEWORK_MIGRATION, the project's developers; validated: all tests pass): Dropwizard 2 -> 4 and pac4j upgrade (#397). Validated by REPLAYING the developer commit onto the breaking commit: all Java changes applied cleanly (Java files identical between breaking commit and fix parent); 3 pom.xml conflicts resolved with the developer's side; slf4j-api kept at the case's 2.0.0 and jax-rs-pac4j 6.0.0-SNAPSHOT replaced by released 6.0.0. A minimal logback-only fix fails (logba
```diff
diff --git a/README.md b/README.md
index 826b0d0..217bbad 100644
--- a/README.md
+++ b/README.md
@@ -10,7 +10,12 @@
 A [Dropwizard](http://www.dropwizard.io/) bundle for securing REST endpoints
 using [pac4j](http://www.pac4j.org/).
 
-**The new version 5.0.0 is based on Dropwizard v2.x (JDK 11)** while previous versions were based on Dropwizard v1.x.
+| dropwizard-pac4j | JDK | pac4j | jax-rs-pac4j | Dropwizard |
+|------------------|-----|-------|--------------|------------|
+| version >= 6     | 11  | v5    | v6           | v4         |
+| version >= 5     | 11  | v4    | v4           | v2         |
+| version >= 4     | 8   | v4    | v4           | v1         |
+| version >= 3     | 8   | v3    | v3           | v1         |
 
 ## Usage
 
@@ -122,18 +127,18 @@ pac4j:
 ```
 
 - `globalFilters` to declare global filters: the `clients`, `authorizers`,
-`matchers`, `multiProfile` and `skipResponse` properties directly map to
+`matchers`, and `skipResponse` properties directly map to
 [the parameters](https://github.com/pac4j/jax-rs-pac4j/wiki/Apply-security)
 used by `org.pac4j.jax.rs.filter.SecurityFilter`.
 
 - `servlet` to declare servlet-level filters:
- - `security`: the `clients`, `authorizers`, `matchers` and `multiProfile`
+ - `security`: the `clients`, `authorizers`, and `matchers`
    properties directly map to
    [the parameters](https://github.com/pac4j/jee-pac4j/wiki/Apply-security)
    used by `org.pac4j.jee.filter.SecurityFilter`.
    The `mapping` property is used to optionally specify urls to which this
    filter will be applied to, defaulting to all urls (`/*`).
- - `callback`: the `defaultUrl`, `renewSession` and `multiProfile` properties
+ - `callback`: the `defaultUrl`, and `renewSession` properties
    directly map to
    [the parameters](https://github.com/pac4j/jee-pac4j/wiki/Callback-configuration)
    used by `org.pac4j.jee.filter.CallbackFilter`.
diff --git a/pom.xml b/pom.xml
index 914dcc8..7dbde1e 100644
--- a/pom.xml
+++ b/pom.xml
@@ -11,7 +11,7 @@
   <groupId>org.pac4j</groupId>
   <artifactId>dropwizard-pac4j</artifactId>
   <packaging>jar</packaging>
-  <version>5.0.1-SNAPSHOT</version>
+  <version>6.0.0-SNAPSHOT</version>
   <name>Dropwizard pac4j Support</name>
   <description>Dropwizard bundle adding support for the pac4j security engine</description>
   <url>https://github.com/pac4j/dropwizard-pac4j</url>
@@ -90,10 +90,11 @@
     <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
     <maven.compiler.source>11</maven.compiler.source>
     <maven.compiler.target>11</maven.compiler.target>
-    <dropwizard.version>2.0.17</dropwizard.version>
-    <pac4j.version>4.5.6</pac4j.version>
-    <jax-rs-pac4j.version>4.0.0</jax-rs-pac4j.version>
-    <jee-pac4j.version>5.0.0</jee-pac4j.version>
+    <dropwizard.version>4.0.0</dropwizard.version>
+    <pac4j.version>5.7.1</pac4j.version>
+    <jax-rs-pac4j.version>6.0.0</jax-rs-pac4j.version>
+    <jee-pac4j.version>7.1.0</jee-pac4j.version>
+    <junit5.version>5.9.3</junit5.version>
   </properties>
 
   <dependencyManagement>
@@ -105,107 +106,12 @@
         <type>pom</type>
         <scope>import</scope>
       </dependency>
-      <!-- Required for dependency convergence -->
-      <dependency>
-        <groupId>com.fasterxml</groupId>
-        <artifactId>classmate</artifactId>
-        <version>1.5.1</version>
-      </dependency>
-      <!-- Required for dependency convergence -->
-      <dependency>
-        <groupId>com.fasterxml.jackson.core</groupId>
-        <artifactId>jackson-databind</artifactId>
-        <version>2.10.5.1</version>
-      </dependency>
-      <!-- Required for dependency convergence -->
-      <dependency>
-        <groupId>com.google.errorprone</groupId>
-        <artifactId>error_prone_annotations</artifactId>
-        <version>2.15.0</version>
-      </dependency>
-      <!-- Required for dependency convergence -->
-      <dependency>
-        <groupId>com.google.guava</groupId>
-        <artifactId>guava</artifactId>
-        <version>31.1-jre</version>
-      </dependency>
-      <!-- Required for dependency convergence -->
-      <dependency>
-        <groupId>org.apache.commons</groupId>
-        <artifactId>commons-lang3</artifactId>
-        <version>3.11</version>
-      </dependency>
-      <!-- Required for dependency convergence -->
-      <dependency>
-        <groupId>joda-time</groupId>
-        <artifactId>joda-time</artifactId>
-        <version>2.11.0</version>
-      </dependency>
-      <!-- Required for dependency convergence -->
-      <dependency>
-        <groupId>org.checkerframework</groupId>
-        <artifactId>checker-qual</artifactId>
-        <version>3.24.0</version>
-      </dependency>
-      <!-- Required for dependency convergence -->
-      <dependency>
-        <groupId>org.eclipse.jetty</groupId>
-        <artifactId>jetty-server</artifactId>
-        <version>9.4.35.v20201120</version>
-      </dependency>
-      <!-- Required for dependency convergence -->
-      <dependency>
-        <groupId>org.glassfish</groupId>
-        <artifactId>jakarta.el</artifactId>
-        <version>3.0.3</version>
-      </dependency>
-      <!-- Required for dependency convergence -->
-      <dependency>
-        <groupId>jakarta.xml.bind</groupId>
-        <artifactId>jakarta.xml.bind-api</artifactId>
-        <version>2.3.3</version>
-      </dependency>
-      <!-- Required for dependency convergence -->
       <dependency>
-        <groupId>jakarta.annotation</groupId>
-        <artifactId>jakarta.annotation-api</artifactId>
-        <version>1.3.5</version>
-      </dependency>
-      <!-- Required for dependency convergence -->
-      <dependency>
-        <groupId>jakarta.servlet</groupId>
-        <artifactId>jakarta.servlet-api</artifactId>
-        <version>4.0.4</version>
-      </dependency>
-      <!-- Required for dependency convergence -->
-      <dependency>
-        <groupId>jakarta.activation</groupId>
-        <ar
... (patch truncated)
```

### Past case 3: org.slf4j:slf4j-api 1.7.36 -> 2.0.4 (alphagov/pay-adminusers)
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
### pom.xml  (root build file)
```
<?xml version="1.0" encoding="UTF-8"?>
<!--
  ~ Copyright  2022 The BtrPlace Authors. All rights reserved.
  ~ Use of this source code is governed by a LGPL-style
  ~ license that can be found in the LICENSE.txt file.
  -->

<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>org.btrplace</groupId>
    <artifactId>scheduler</artifactId>
    <version>1.12.9-SNAPSHOT</version>
    <name>scheduler</name>
    <description>A flexible VM scheduler for hosting platforms.</description>
    <packaging>pom</packaging>
    <url>http://www.btrplace.org</url>
    <developers>
        <developer>
            <name>Fabien Hermenier</name>
            <email>fabien.hermenier@unice.fr</email>
            <organization>University Nice Sophia Antipolis</organization>
        </developer>
    </developers>
    <modules>
        <module>choco</module>
        <module>json</module>
        <module>api</module>
        <module>examples</module>
        <module>btrpsl</module>
        <module>safeplace</module>
        <module>bench</module>
        <module>split</module>
    </modules>
    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <slf4j.version>2.0.6</slf4j.version>
        <testng.version>7.5</testng.version>
        <maven.compiler.source>1.8</maven.compiler.source>
        <maven.compiler.target>1.8</maven.compiler.target>
    </properties>
    <licenses>
        <license>
            <name>GNU Lesser General Public License v3</name>
            <url>LICENSE.txt</url>
            <distribution>repo</distribution>
        </license>
    </licenses>
    <dependencies>
        <dependency>
            <groupId>org.testng</groupId>
            <artifactId>testng</artifactId>
            <version>${testng.version}</version>
            <type>jar</type>
            <scope>test</scope>
            <optional>false</optional>
        </dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>${slf4j.version}</version>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-core</artifactId>
            <version>4.9.0</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.openjdk.jmh</groupId>
            <artifactId>jmh-core</artifactId>
            <version>1.36</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.openjdk.jmh</groupId>
            <artifactId>jmh-generator-annprocess</artifactId>
            <version>1.36</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <distributionManagement>
        <repository>
            <id>sonatype</id>
            <url>https://oss.sonatype.org/service/local/staging/deploy/maven2</url>
        </repository>
        <snapshotRepository>
            <id>sonatype</id>
            <uniqueVersion>true</uniqueVersion>
            <url>https://oss.sonatype.org/content/repositories/snapshots</url>
            <layout>default</layout>
        </snapshotRepository>
    </distributionManagement>

    <scm>
        <connection>scm:git:git://github.com/btrplace/scheduler.git</connection>
        <url>scm:git:git@github.com:btrplace/scheduler</url>
        <developerConnection>scm:git:git@github.com:btrplace/scheduler.git</developerConnection>
        <tag>HEAD</tag>
    </scm>

    <build>
        <plugins>
            <plugin>
                <groupId>org.jacoco</groupId>
                <artifactId>jacoco-maven-plugin</artifactId>
                <version>0.8.8</version>
                <configuration>
                    <excludes>
                        <exclude>org/btrplace/btrpsl/**/*</exclude>
                        <exclude>org/btrplace/safeplace/**/*</exclude>
                        <exclude>org/btrplace/bench/**/*</exclude>
                        <exclude>org/btrplace/scheduler/runner/disjoint/**/*</exclude>
                    </excludes>
                    <formats>
                        <format>XML</format>
                    </formats>
                </configuration>
                <executions>
                    <execution>
                        <goals>
                            <goal>prepare-agent</goal>
                        </goals>
                    </execution>
                    <execution>
                        <id>report</id>
                        <phase>test</phase>
                        <goals>
                            <goal>report</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-gpg-plugin</artifactId>
                <version>3.0.1</version>
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
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-source-plugin</artifactId>
                <version>3.2.1</version>
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
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.10.1</version>
                <configuration>
                    <excludes>
                        <exclude>**/package-info.java</exclude>
                    </excludes>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-javadoc-plugin</artifactId>
                <version>3.4.1</version>
                <configuration>
                    <doctitle>${project.groupId}-${project.artifactId} ${project.version} API</doctitle>
                    <windowtitle>${project.groupId}-${project.artifactId} ${project.version} API</windowtitle>
                    <bottom>Copyright © 2016 University of Nice-Sophia Antipolis. All Rights Reserved.</bottom>
                    <doclint>none</doclint>
                    <!-- weired duplication, but aggregate does not scan module configurations -->
                    <excludePackageNames>org.btrplace.btrpsl.antlr</excludePackageNames>
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
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.0.0-M7</version>
                <configuration>
                    <includes>
                        <include>**/*Test.java</include>
                    </includes>
                	<parallel>classes</parallel>
                    <threadCount>5</threadCount>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-failsafe-plugin</artifactId>
                <version>2.22.2</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>integration-test</goal>
                            <goal>verify</goal>
                        </goals>
                    </execution>
                </executions>
                <configuration>
                    <includes>
                        <include>**/*Integration.java</include>
                    </includes>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.sonatype.plugins</groupId>
                <artifactId>nexus-staging-maven-plugin</artifactId>
                <version>1.6.13</version>
                <extensions>true</extensions>
                <configuration>
                    <serverId>sonatype</serverId>
                    <nexusUrl>https://oss.sonatype.org/</nexusUrl>
                    <autoReleaseAfterClose>true</autoReleaseAfterClose>
                </configuration>
            </plugin>
        </plugins>
    </build>

    <repositories>
        <repository>
            <id>sonatype</id>
            <url>https://oss.sonatype.org/service/local/staging/deploy/maven2</url>
        </repository>
        <repository>
            <id>sonatype-snapshots</id>
            <url>https://oss.sonatype.org/content/repositories/snapshots</url>
            <layout>default</layout>
        </repository>
    </repositories>
</project>
```

### json/pom.xml  (build file (declares the updated dependency))
```
<?xml version="1.0" encoding="UTF-8"?>

<!--
  ~ Copyright  2020 The BtrPlace Authors. All rights reserved.
  ~ Use of this source code is governed by a LGPL-style
  ~ license that can be found in the LICENSE.txt file.
  -->

<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.btrplace</groupId>
        <artifactId>scheduler</artifactId>
        <version>1.12.9-SNAPSHOT</version>
    </parent>

    <artifactId>scheduler-json</artifactId>
    <name>scheduler-json</name>
    <description>Read and write model according to the JSON format</description>

    <dependencies>
        <dependency>
            <groupId>org.btrplace</groupId>
            <artifactId>scheduler-api</artifactId>
            <version>${project.version}</version>
        </dependency>
        <dependency>
            <groupId>net.minidev</groupId>
            <artifactId>json-smart</artifactId>
            <version>2.4.9</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-jar-plugin</artifactId>
                <version>3.2.2</version>
                <configuration>
                    <archive>
                        <manifestEntries>
                            <Automatic-Module-Name>org.btrplace.scheduler.json</Automatic-Module-Name>
                        </manifestEntries>
                    </archive>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

### json/src/main/java/org/btrplace/json/JSON.java  (class in the failing stack trace)
```
/*
 * Copyright  2020 The BtrPlace Authors. All rights reserved.
 * Use of this source code is governed by a LGPL-style
 * license that can be found in the LICENSE.txt file.
 */

package org.btrplace.json;

import org.btrplace.json.model.InstanceConverter;
import org.btrplace.json.plan.ReconfigurationPlanConverter;
import org.btrplace.model.Instance;
import org.btrplace.plan.ReconfigurationPlan;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.Reader;
import java.util.zip.GZIPInputStream;
import java.util.zip.GZIPOutputStream;

import static java.nio.charset.StandardCharsets.UTF_8;

/**
 * Utility class to ease the serialisation and the deserialisation of the main btrplace entities.
 *
 * @author Fabien Hermenier
 */
public class JSON {

    private JSON() {
    }

    private static InputStreamReader makeIn(File f) throws IOException {
        if (f.getName().endsWith(".gz")) {
            return new InputStreamReader(new GZIPInputStream(new FileInputStream(f)), UTF_8);
        }
        return new InputStreamReader(new FileInputStream(f), UTF_8);
    }

    private static OutputStreamWriter makeOut(File f) throws IOException {
        if (f.getName().endsWith(".gz")) {
            return new OutputStreamWriter(new GZIPOutputStream(new FileOutputStream(f)), UTF_8);
        }
        return new OutputStreamWriter(new FileOutputStream(f), UTF_8);
    }

    /**
     * Read an instance from a file.
     * A file ending with '.gz' is uncompressed first
     *
     * @param f the file to parse
     * @return the resulting instance
     * @throws IllegalArgumentException if an error occurred while reading the file
     */
    public static Instance readInstance(File f) {
        try (Reader in = makeIn(f)) {
            return readInstance(in);
        } catch (IOException e) {
            throw new IllegalArgumentException(e);
        }
    }

    /**
     * Read an instance.
     *
     * @param r the stream to read
     * @return the resulting instance
     * @throws IllegalArgumentException if an error occurred while reading the json
     */
    public static Instance readInstance(Reader r) {
        try {
            InstanceConverter c = new InstanceConverter();
            return c.fromJSON(r);
        } catch (JSONConverterException e) {
            throw new IllegalArgumentException(e);
        }
    }

    /**
     * Write an instance.
     *
     * @param instance the instance to write
     * @param f        the output file. If it ends with '.gz' it will be gzipped
     * @throws IllegalArgumentException if an error occurred while writing the json
     */
    public static void write(Instance instance, File f) {
        try (OutputStreamWriter out = makeOut(f)) {
            write(instance, out);
        } catch (IOException e) {
            throw new IllegalArgumentException(e);
        }
    }

    /**
     * Write an instance
     *
     * @param instance the instance to write
     * @param a        the stream to write on.
     * @throws IllegalArgumentException if an error occurred while writing the json
     */
    public static void write(Instance instance, Appendable a) {
        try {
            InstanceConverter c = new InstanceConverter();
            c.toJSON(instance).writeJSONString(a);
        } catch (IOException | JSONConverterException e) {
            throw new IllegalArgumentException(e);
        }
    }

    /**
     * Serialise a instance.
     *
     * @param instance the instance to write
     * @return the JSON string
     * @throws IllegalArgumentException if an error occurred while writing the json
     */
    public static String toString(Instance instance) {
        try {
            InstanceConverter c = new InstanceConverter();
            return c.toJSON(instance).toJSONString();
        } catch (JSONConverterException e) {
            throw new IllegalArgumentException(e);
        }
    }


    /**
     * Read a reconfiguration plan from a file.
     * A file ending with '.gz' is uncompressed first
     *
     * @param f the file to parse
     * @return the resulting plan
     * @throws IllegalArgumentException if an error occurred while reading the file
     */
    public static ReconfigurationPlan readReconfigurationPlan(File f) {
        try (Reader in = makeIn(f)) {
            return readReconfigurationPlan(in);
        } catch (IOException e) {
            throw new IllegalArgumentException(e);
        }
    }

    /**
     * Read a plan.
     *
     * @param r the stream to read
     * @return the resulting reconfiguration plan
     * @throws IllegalArgumentException if an error occurred while reading the json
     */
    public static ReconfigurationPlan readReconfigurationPlan(Reader r) {
        try {
            ReconfigurationPlanConverter c =
                ReconfigurationPlanConverter.newBundle();
            return c.fromJSON(r);
        } catch (JSONConverterException e) {
            throw new IllegalArgumentException(e);
        }
    }

    /**
     * Write a reconfiguration plan.
     *
     * @param plan the reconfiguration plan to write
     * @param f    the output file. If it ends with '.gz' it will be gzipped
     * @throws IllegalArgumentException if an error occurred while writing the json
     */
    public static void write(ReconfigurationPlan plan, File f) {
        try (OutputStreamWriter out = makeOut(f)) {
            write(plan, out);
        } catch (IOException e) {
            throw new IllegalArgumentException(e);
        }
    }

    /**
     * Write a reconfiguration plan.
     *
     * @param plan the plan to write
     * @param a    the stream to write on.
     * @throws IllegalArgumentException if an error occurred while writing the json
     */
    public static void write(ReconfigurationPlan plan, Appendable a) {
        try {
            ReconfigurationPlanConverter c =
                ReconfigurationPlanConverter.newBundle();
            c.toJSON(plan).writeJSONString(a);
        } catch (IOException | JSONConverterException e) {
            throw new IllegalArgumentException(e);
        }
    }

    /**
     * Serialise a reconfiguration plan.
     *
     * @param plan the plan to write
     * @return the JSON string
     * @throws IllegalArgumentException if an error occurred while writing the json
     */
    public static String toString(ReconfigurationPlan plan) {
        try {
            ReconfigurationPlanConverter c = new ReconfigurationPlanConverter();
            return c.toJSON(plan).toJSONString();
        } catch (JSONConverterException e) {
            throw new IllegalArgumentException(e);
        }
    }
}
```

### choco/src/test/java/org/btrplace/scheduler/choco/IssuesTest.java  (class in the failing stack trace)
```
... (lines 0-0 omitted)
/*
 * Copyright  2020 The BtrPlace Authors. All rights reserved.
 * Use of this source code is governed by a LGPL-style
 * license that can be found in the LICENSE.txt file.
 */

package org.btrplace.scheduler.choco;

import org.btrplace.json.JSON;
import org.btrplace.model.DefaultModel;
import org.btrplace.model.Instance;
import org.btrplace.model.Mapping;
import org.btrplace.model.Model;
import org.btrplace.model.Node;
import org.btrplace.model.VM;
import org.btrplace.model.constraint.Ban;
import org.btrplace.model.constraint.Fence;
import org.btrplace.model.constraint.Gather;
import org.btrplace.model.constraint.MinMTTR;
import org.btrplace.model.constraint.MinMigrations;
import org.btrplace.model.constraint.Offline;
import org.btrplace.model.constraint.Online;
import org.btrplace.model.constraint.OptConstraint;
import org.btrplace.model.constraint.Running;
import org.btrplace.model.constraint.RunningCapacity;
import org.btrplace.model.constraint.SatConstraint;
import org.btrplace.model.constraint.Spread;
import org.btrplace.model.view.ShareableResource;
import org.btrplace.model.view.network.Network;
import org.btrplace.plan.ReconfigurationPlan;
import org.btrplace.scheduler.SchedulerException;
import org.btrplace.scheduler.choco.constraint.mttr.CMinMTTR;
import org.btrplace.scheduler.choco.extensions.ChocoUtils;
import org.btrplace.scheduler.choco.transition.NodeTransition;
import org.btrplace.scheduler.choco.transition.VMTransition;
import org.chocosolver.solver.Cause;
import org.chocosolver.solver.constraints.Constraint;
import org.chocosolver.solver.exception.ContradictionException;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
... (lines 41-474 omitted)
        satConstraints.add(new Offline(node3));
        final OptConstraint optConstraint = new MinMTTR();
        DefaultChocoScheduler scheduler = new DefaultChocoScheduler();
        scheduler.doOptimize(false);
        scheduler.doRepair(true);
        scheduler.setTimeLimit(60000);
        ReconfigurationPlan plan = scheduler.solve(
                model, satConstraints, optConstraint);
        System.out.println(scheduler.getStatistics());
        Assert.assertTrue(plan.isApplyable());


        satConstraints.clear();
        // This is somewhat similar to making Node 3 going offline by ensuring that
        // all VMs can no longer get hosted on that node.
        satConstraints.addAll(mapping.getAllVMs().stream().map(vm -> new Ban(vm, Collections.singletonList(node3))).collect(Collectors.toList()));

        scheduler = new DefaultChocoScheduler();
        scheduler.doOptimize(false);
        scheduler.doRepair(true);
        plan = scheduler.solve(model, satConstraints, optConstraint);
        Assert.assertTrue(plan.isApplyable());
    }

    private static void populateNodeVm(final Model model,
                                       final Mapping mapping, final Node node, final int[] ids) {

        mapping.addOnlineNode(node);
        for (final int id : ids) {
            final VM vm = model.newVM(id);
            mapping.addRunningVM(vm, node);
        }
    }

    /**
     * A helper to check that an instance has a solution.
     *
     * @param file the serialised instance. Must be in 'src/test/resources/'
     */
    private static void computable(String file) {
        Instance i = JSON.readInstance(new File("src/test/resources/" + file));
        ChocoScheduler s = new DefaultChocoScheduler();
        ReconfigurationPlan p = s.solve(i);
        System.out.println(s.getStatistics());
        Assert.assertNotNull(p);
        System.out.println(p.getSize() + " action(s)");
    }

    @Test
    public void testIssue93() throws Exception {
        String buf = "{\"model\":{\"mapping\":{\"readyVMs\":[],\"onlineNodes\":{\"0\":{\"sleepingVMs\":[],\"runningVMs\":[0]},\"1\":{\"sleepingVMs\":[],\"runningVMs\":[1]},\"2\":{\"sleepingVMs\":[],\"runningVMs\":[2]}},\"offlineNodes\":[]},\"attributes\":{\"nodes\":{},\"vms\":{\"0\":{\"memUsed\":204},\"1\":{\"memUsed\":204},\"2\":{\"memUsed\":204}}},\"views\":[{\"defConsumption\":0,\"nodes\":{\"0\":8,\"1\":10,\"2\":10},\"rcId\":\"cpu\",\"id\":\"shareableResource\",\"defCapacity\":0,\"vms\":{\"0\":8,\"1\":1,\"2\":1}},{\"routing\":{\"type\":\"default\"},\"switches\":[{\"id\":0,\"capacity\":-1}],\"links\":[{\"physicalElement\":{\"id\":2,\"type\":\"node\"},\"id\":0,\"capacity\":1000,\"switch\":0},{\"physicalElement\":{\"id\":1,\"type\":\"node\"},\"id\":1,\"capacity\":1000,\"switch\":0},{\"physicalElement\":{\"id\":0,\"type\":\"node\"},\"id\":2,\"capacity\":1000,\"switch\":0}],\"id\":\"net\"}]},\"constraints\":[{\"rc\":\"cpu\",\"amount\":6,\"nodes\":[0],\"continuous\":false,\"id\":\"resourceCapacity\"}],\"objective\":{\"id\":\"minimizeMTTR\"}}\n";
        Instance i = JSON.readInstance(new StringReader(buf));
        ChocoScheduler s = new DefaultChocoScheduler();
        s.doOptimize(true);
        ReconfigurationPlan p = s.solve(i);
        Assert.assertNotNull(p);
    }

    @Test
    public void testIssue100() throws Exception {
        computable("issue-100.json.gz");
    }

    @Test
    public void testIssue101() throws Exception {
        computable("issue-101.json.gz");
    }

    @Test
    public void testFoo() throws Exception {
        String buf = "{\"model\":{\"mapping\":{\"readyVMs\":[],\"onlineNodes\":{\"0\":{\"sleepingVMs\":[],\"runningVMs\":[0]},\"1\":{\"sleepingVMs\":[],\"runningVMs\":[1]}},\"offlineNodes\":[]},\"attributes\":{\"nodes\":{},\"vms\":{}},\"views\":[{\"defConsumption\":2,\"nodes\":{},\"rcId\":\"CPU\",\"id\":\"shareableResource\",\"defCapacity\":7,\"vms\":{}}]},\"constraints\":[{\"nodes\":[0],\"vm\":0,\"continuous\":false,\"id\":\"ban\"},{\"nodes\":[1],\"vm\":1,\"continuous\":false,\"id\":\"ban\"},{\"rc\":\"CPU\",\"amount\":4,\"vm\":0,\"id\":\"preserve\"},{\"rc\":\"CPU\",\"amount\":4,\"vm\":1,\"id\":\"preserve\"}],\"objective\":{\"id\":\"minimizeMTTR\"}}";
        Instance i = JSON.readInstance(new StringReader(buf));
        ChocoScheduler s = new DefaultChocoScheduler();
        ReconfigurationPlan p = s.solve(i);
        Assert.assertNotNull(p);
    }

    @Test
    public void testIssue131() throws Exception {
        for (int id = 0; id <= 4; id++) {
            System.out.println("--- " + id + " ---");
            computable("issue-131-" + id + ".json.gz");
        }
    }

  @Test
  public void testIssue117() throws Exception {
    String buf = "{\"model\":{\"mapping\":{\"readyVMs\":[5,4],\"onlineNodes\":{\"0\":{\"sleepingVMs\":[],\"runningVMs\":[0]},\"1\":{\"sleepingVMs\":[],\"runningVMs\":[1]},\"2\":{\"sleepingVMs\":[],\"runningVMs\":[3,2]}},\"offlineNodes\":[]},\"attributes\":{\"nodes\":{},\"vms\":{\"4\":{\"placeHolder\":true},\"5\":{\"placeHolder\":true}}},\"views\":[{\"defConsumption\":2,\"nodes\":{},\"rcId\":\"mem\",\"id\":\"shareableResource\",\"defCapacity\":6,\"vms\":{\"1\":4,\"4\":4,\"5\":2}},{\"defConsumption\":2,\"nodes\":{},\"rcId\":\"cpu\",\"id\":\"shareableResource\",\"defCapacity\":6,\"vms\":{\"0\":4,\"1\":4,\"4\":4,\"5\":2}}]},\"constraints\":[{\"vm\":4,\"continuous\":false,\"id\":\"running\"},{\"continuous\":false,\"id\":\"spread\",\"vms\":[1,3,4]},{\"vm\":5,\"continuous\":false,\"id\":\"running\"}],\"objective\":{\"id\":\"minimizeMTTR\"}}";
    Instance i = JSON.readInstance(new StringReader(buf));
    ChocoScheduler s = new DefaultChocoScheduler();
    ReconfigurationPlan plan = s.solve(i);
    Assert.assertNotNull(plan);
  }

    @Test
    public void testIssue171() {
        String buf = "{\"model\":{\"mapping\":{\"readyVMs\":[3],\"onlineNodes\":{\"0\":{\"sleepingVMs\":[],\"runningVMs\":[2]},\"1\":{\"sleepingVMs\":[],\"runningVMs\":[1]},\"2\":{\"sleepingVMs\":[],\"runningVMs\":[0]},\"3\":{\"sleepingVMs\":[],\"runningVMs\":[]},\"4\":{\"sleepingVMs\":[],\"runningVMs\":[]},\"5\":{\"sleepingVMs\":[],\"runningVMs\":[]}},\"offlineNodes\":[]},\"attributes\":{\"nodes\":{},\"vms\":{}},\"views\":[{\"defConsumption\":0,\"nodes\":{\"0\":4,\"1\":4,\"2\":4,\"3\":4,\"4\":2147483,\"5\":2147483},\"rcId\":\"memory\",\"id\":\"shareableResource\",\"defCapacity\":0,\"vms\":{\"0\":4,\"1\":4,\"2\":4}}]},\"constraints\":[{\"vm\":0,\"id\":\"running\"},{\"vm\":1,\"id\":\"running\"},{\"vm\":2,\"id\":\"running\"},{\"node\":5,\"id\":\"online\"},{\"node\":4,\"id\":\"online\"},{\"node\":3,\"id\":\"online\"},{\"node\":2,\"id\":\"online\"},{\"node\":1,\"id\":\"online\"},{\"node\":0,\"id\":\"online\"},{\"continuous\":true,\"id\":\"spread\",\"vms\":[1,2]},{\"continuous\":false,\"id\":\"gather\",\"vms\":[2,3]},{\"vm\":3,\"id\":\"running\"}],\"objective\":{\"id\":\"minimizeMTTR\"}}";
        Instance i = JSON.readInstance(new StringReader(buf));
        i.getModel().getMapping().remove(new Node(3));
        ShareableResource mem = ShareableResource.get(i.getModel(), "memory");
        mem.unset(new Node(5));
        mem.unset(new Node(4));
        mem.unset(new Node(3));
        i.getSatConstraints().removeIf(Online.class::isInstance);
        i.getSatConstraints().removeIf(Spread.class::isInstance);
        i.getSatConstraints().removeIf(Gather.class::isInstance);
```

### json/src/main/java/org/btrplace/json/JSONObjectConverter.java  (class in the failing stack trace)
```
/*
 * Copyright  2020 The BtrPlace Authors. All rights reserved.
 * Use of this source code is governed by a LGPL-style
 * license that can be found in the LICENSE.txt file.
 */

package org.btrplace.json;

import net.minidev.json.JSONObject;
import net.minidev.json.parser.JSONParser;
import net.minidev.json.parser.ParseException;

import java.io.Reader;
import java.io.StringReader;

/**
 * Specify a converter between a JSON formatted message and a object.
 *
 * @author Fabien Hermenier
 */
public interface JSONObjectConverter<E> {

    /**
     * Un-serialize an object.
     *
     * @param in the json object
     * @return the conversion result
     * @throws JSONConverterException if an error occurred while converting the object
     */
    E fromJSON(JSONObject in) throws JSONConverterException;

    /**
     * Serialize an object.
     *
     * @param e the object to serialize
     * @return the conversion result
     * @throws JSONConverterException if an error occurred while converting the object
     */
    JSONObject toJSON(E e) throws JSONConverterException;

    /**
     * Un-serialize an object from a string.
     *
     * @param buf the string to parse
     * @return the resulting object
     * @throws JSONConverterException if the stream cannot be parsed
     */
    default E fromJSON(String buf) throws JSONConverterException {
        try (StringReader in = new StringReader(buf)) {
            return fromJSON(in);
        }
    }

    /**
     * Un-serialize an object from a stream.
     * The stream must be close afterward
     *
     * @param r the stream to read
     * @return the resulting object
     * @throws JSONConverterException if the stream cannot be parsed
     */
    default E fromJSON(Reader r) throws JSONConverterException {
        try {
            JSONParser p = new JSONParser(JSONParser.MODE_RFC4627);
            Object o = p.parse(r);
            if (!(o instanceof JSONObject)) {
                throw new JSONConverterException("Unable to parse a JSON object");
            }
            return fromJSON((JSONObject) o);
        } catch (ParseException ex) {
            throw new JSONConverterException(ex);
        }
    }

    /**
     * Serialize an object to a string.
     *
     * @param o the object to serialize
     * @return the JSON message
     * @throws JSONConverterException if an error occurred while converting the object
     */
    default String toJSONString(E o) throws JSONConverterException {
        return toJSON(o).toJSONString();
    }
}
```


Now write the explanation and the single ```diff block.
