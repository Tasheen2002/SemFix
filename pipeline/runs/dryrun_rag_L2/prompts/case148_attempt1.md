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
`org.slf4j:slf4j-api` was updated from `1.7.36` to `2.0.2`. The project compiles, but tests now fail.

## Failure (from the build log)
Failing test classes: net.jadler.JadlerMockerTest
Exception types: java.lang.ClassCastException
Error lines:
- java.lang.ClassCastException: class org.slf4j.helpers.NOPLoggerFactory cannot be cast to class ch.qos.logback.classic.LoggerContext (org.slf4j.helpers.NOPLoggerFactory and ch.qos.logback.classic.LoggerContext are in unnamed module of loader 'app')
SLF4J console output:
- SLF4J: No SLF4J providers were found.
- SLF4J: Defaulting to no-operation (NOP) logger implementation
- SLF4J: See https://www.slf4j.org/codes.html#noProviders for further details.
- SLF4J: Class path contains SLF4J bindings targeting slf4j-api versions 1.7.x or earlier.
- SLF4J: Ignoring binding found at [jar:file:/root/.m2/repository/ch/qos/logback/logback-classic/1.2.11/logback-classic-1.2.11.jar!/org/slf4j/impl/StaticLoggerBinder.class]
- SLF4J: See https://www.slf4j.org/codes.html#ignoredBindings for an explanation.
Project stack frames:
- net.jadler.JadlerMockerTest (JadlerMockerTest.java:1092)
- net.jadler.JadlerMockerTest (JadlerMockerTest.java:857)
- org.junit.runners.model.FrameworkMethod$1 (FrameworkMethod.java:59)
- org.junit.internal.runners.model.ReflectiveCallable (ReflectiveCallable.java:12)
- org.junit.runners.model.FrameworkMethod (FrameworkMethod.java:56)
- org.junit.internal.runners.statements.InvokeMethod (InvokeMethod.java:17)
- org.junit.runners.ParentRunner$3 (ParentRunner.java:306)
- org.junit.runners.BlockJUnit4ClassRunner$1 (BlockJUnit4ClassRunner.java:100)
- org.junit.runners.ParentRunner (ParentRunner.java:366)
- org.junit.runners.BlockJUnit4ClassRunner (BlockJUnit4ClassRunner.java:103)
- org.junit.runners.BlockJUnit4ClassRunner (BlockJUnit4ClassRunner.java:63)
- org.junit.runners.ParentRunner$4 (ParentRunner.java:331)

## Similar past breakages and their validated fixes (from the knowledge base)
They come from OTHER projects. Use them for the idea of the fix; adapt it to this project's files.

### Past case 1: org.slf4j:slf4j-api 1.7.36 -> 2.0.3 (retest/recheck)
Symptom: java.lang.ClassCastException
  java.lang.ClassCastException: class org.slf4j.helpers.NOPLogger cannot be cast to class ch.qos.logback.classic.Logger (org.slf4j.helpers.NOPLogger and ch.qos.logback.classic.Logger are in unnamed module of loader 'app')
Behavior change: Logger implementation returned by LoggerFactory changed from logback Logger to NOPLogger (provider-selection policy change; old binding present and explicitly ignored per SLF4J console)
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

### Past case 2: org.slf4j:slf4j-api 1.7.36 -> 2.0.5 (feedzai/pdb)
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

### Past case 3: org.slf4j:slf4j-api 1.7.36 -> 2.0.3 (alphagov/pay-adminusers)
Symptom: java.lang.ClassCastException; java.lang.ExceptionInInitializerError; java.lang.NoClassDefFoundError
  java.lang.ClassCastException: class org.slf4j.helpers.NOPLogger cannot be cast to class ch.qos.logback.classic.Logger (org.slf4j.helpers.NOPLogger and ch.qos.logback.classic.Logger are in unnamed module of loader 'app')
  java.lang.Exception: java.lang.ExceptionInInitializerError
Behavior change: Logger implementation selected for the same classpath changed logback -> NOP
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
Copyright (c) 2012 - 2016 Jadler contributors
This program is made available under the terms of the MIT License.
-->

<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>net.jadler</groupId>
    <artifactId>jadler-pom</artifactId>
    <version>1.3.2-SNAPSHOT</version>
    <name>${project.artifactId}</name>
    <description>jadler - http services stubbing and mocking library</description>
    <url>https://github.com/jadler-mocking/jadler</url>
    <packaging>pom</packaging>

    <parent>
        <groupId>org.sonatype.oss</groupId>
        <artifactId>oss-parent</artifactId>
        <version>7</version>
    </parent>

    <developers>
        <developer>
            <name>Jan Dudek</name>
            <email>jan.dudek.jr@gmail.com</email>
        </developer>
        <developer>
            <name>Libor Ryšavý</name>
            <url>https://github.com/liry</url>
        </developer>
        <developer>
            <name>Lukáš Křečan</name>
            <url>https://github.com/lukas-krecan</url>
        </developer>
        <developer>
            <name>Richard Benkovský</name>
            <url>https://github.com/Benky</url>
        </developer>
    </developers>

    <licenses>
        <license>
            <name>MIT license</name>
            <url>https://github.com/jadler-mocking/jadler/blob/master/LICENSE</url>
        </license>
    </licenses>

    <scm>
        <connection>scm:git:https://github.com/jadler-mocking/jadler.git</connection>
        <developerConnection>scm:git:https://github.com/jadler-mocking/jadler.git</developerConnection>
        <url>https://github.com/jadler-mocking/jadler</url>
    </scm>

    <modules>
        <module>jadler-all</module>
        <module>jadler-core</module>
        <module>jadler-jetty</module>
        <module>jadler-jdk</module>
        <module>jadler-junit</module>
    </modules>


    <dependencyManagement>
        <dependencies>
            <!-- JADLER dependencies -->
            <dependency>
                <groupId>net.jadler</groupId>
                <artifactId>jadler-core</artifactId>
                <version>${project.version}</version>
            </dependency>
            <dependency>
                <groupId>net.jadler</groupId>
                <artifactId>jadler-jetty</artifactId>
                <version>${project.version}</version>
            </dependency>
            <dependency>
                <groupId>net.jadler</groupId>
                <artifactId>jadler-junit</artifactId>
                <version>${project.version}</version>
            </dependency>
            <dependency>
                <groupId>net.jadler</groupId>
                <artifactId>jadler-jdk</artifactId>
                <version>${project.version}</version>
            </dependency>

            <!-- MISC -->
            <dependency>
                <groupId>org.slf4j</groupId>
                <artifactId>slf4j-api</artifactId>
                <version>2.0.2</version>
            </dependency>
            <dependency>
                <groupId>org.hamcrest</groupId>
                <artifactId>hamcrest</artifactId>
                <version>2.2</version>
            </dependency>
            <dependency>
                <groupId>commons-io</groupId>
                <artifactId>commons-io</artifactId>
                <version>2.11.0</version>
            </dependency>
            <dependency>
                <groupId>commons-lang</groupId>
                <artifactId>commons-lang</artifactId>
                <version>2.6</version>
            </dependency>
            <dependency>
                <groupId>commons-collections</groupId>
                <artifactId>commons-collections</artifactId>
                <version>3.2.2</version>
            </dependency>
            <dependency>
                <groupId>org.eclipse.jetty</groupId>
                <artifactId>jetty-server</artifactId>
                <version>8.1.11.v20130520</version> <!-- Jetty 8 is the last JDK1.6 compatible version-->
            </dependency>
            <dependency>
                <groupId>org.eclipse.jetty.orbit</groupId>
                <artifactId>javax.servlet</artifactId>
                <version>3.0.0.v201112011016</version>
            </dependency>

            <!-- TEST dependencies -->
            <dependency>
                <groupId>ch.qos.logback</groupId>
                <artifactId>logback-classic</artifactId>
                <version>1.2.11</version>
                <scope>test</scope>
            </dependency>
            <dependency>
                <groupId>junit</groupId>
                <artifactId>junit</artifactId>
                <version>4.13.2</version>
                <scope>test</scope>
            </dependency>
            <dependency>
                <groupId>org.mockito</groupId>
                <artifactId>mockito-core</artifactId>
                <version>4.6.1</version>
                <scope>test</scope>
            </dependency>
            <dependency>
                <groupId>org.mockito</groupId>
                <artifactId>mockito-inline</artifactId>
                <version>4.6.1</version>
                <scope>test</scope>
            </dependency>
            <dependency>
                <groupId>org.springframework</groupId>
                <artifactId>spring-test</artifactId>
                <version>5.3.22</version>
                <scope>test</scope>
            </dependency>
            <dependency>
                <groupId>org.springframework</groupId>
                <artifactId>spring-core</artifactId>
                <version>5.3.22</version>
                <scope>test</scope>
            </dependency>
            <dependency>
                <groupId>org.springframework</groupId>
                <artifactId>spring-web</artifactId>
                <version>5.3.22</version>
                <scope>test</scope>
            </dependency>
            <dependency>
                <groupId>org.apache.httpcomponents</groupId>
                <artifactId>httpclient</artifactId>
                <version>4.5.13</version>
                <scope>test</scope>
            </dependency>
            <dependency>
                <groupId>org.apache.httpcomponents</groupId>
                <artifactId>fluent-hc</artifactId>
                <version>4.5.13</version>
                <scope>test</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>


    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.10.1</version>
                <configuration>
                    <source>1.6</source>
                    <target>1.6</target>
                    <showDeprecation>true</showDeprecation>
                    <showWarnings>true</showWarnings>
                    <fork>true</fork>
                </configuration>
            </plugin>

            <plugin>
                <groupId>org.codehaus.mojo</groupId>
                <artifactId>animal-sniffer-maven-plugin</artifactId>
                <version>1.21</version>
                <configuration>
                    <signature>
                        <groupId>org.codehaus.mojo.signature</groupId>
                        <artifactId>java16</artifactId>
                        <version>1.0</version>
                    </signature>
                    <ignores>
                        <!-- HttpServer is not part of Animal Sniffer signature -->
                        <ignore>com.sun.net.httpserver.*</ignore>
                    </ignores>
                </configuration>
                <executions>
                    <execution>
                        <goals>
                            <goal>check</goal>
                        </goals>
                        <phase>package</phase>
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
                            <goal>jar</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>

            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-javadoc-plugin</artifactId>
                <version>2.9</version>
                <executions>
                    <execution>
                        <id>attach-javadocs</id>
                        <goals>
                            <goal>jar</goal>
                        </goals>
                        <configuration>
                            <additionalparam>${javadoc.opts}</additionalparam>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <groupId>org.sonatype.plugins</groupId>
                <artifactId>nexus-staging-maven-plugin</artifactId>
                <version>1.6.13</version>
                <extensions>true</extensions>
                <configuration>
                    <serverId>sonatype-nexus-staging</serverId>
                    <nexusUrl>https://oss.sonatype.org/</nexusUrl>
                    <autoReleaseAfterClose>true</autoReleaseAfterClose>
                </configuration>
            </plugin>
        </plugins>
        <pluginManagement>
            <plugins>
                <plugin>
                    <groupId>org.pitest</groupId>
                    <artifactId>pitest-maven</artifactId>
                    <version>1.1.11</version>
                    <executions>
                        <execution>
                            <phase>verify</phase>
                            <goals>
                                <goal>mutationCoverage</goal>
                            </goals>
                        </execution>
                    </executions>
                </plugin>
            </plugins>
        </pluginManagement>
    </build>

    <profiles>
        <profile>
            <id>gpg</id>
            <build>
                <plugins>
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
                </plugins>
            </build>
        </profile>

        <profile>
            <!-- disables javadoc reference checks in doclint in Java 8-->
            <!--TODO fix the javadocs and remove this profile-->
            <id>doclint-java8-disable</id>
            <activation>
                <jdk>[1.8,)</jdk>
            </activation>
            <properties>
                <javadoc.opts>-Xdoclint:all -Xdoclint:-reference</javadoc.opts>
            </properties>
        </profile>
    </profiles>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
</project>
```

### jadler-core/pom.xml  (build file (declares the updated dependency))
```
<?xml version="1.0" encoding="UTF-8"?>
<!--
Copyright (c) 2012 - 2016 Jadler contributors
This program is made available under the terms of the MIT License.
-->

<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <artifactId>jadler-core</artifactId>
    <name>${project.artifactId}</name>
    <description>Core of the Jadler library.</description>
    <packaging>jar</packaging>

    <parent>
        <groupId>net.jadler</groupId>
        <artifactId>jadler-pom</artifactId>
        <version>1.3.2-SNAPSHOT</version>
    </parent>

    <dependencies>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
        </dependency>
        <dependency>
            <groupId>org.hamcrest</groupId>
            <artifactId>hamcrest</artifactId>
        </dependency>
        <dependency>
            <groupId>commons-io</groupId>
            <artifactId>commons-io</artifactId>
        </dependency>
        <dependency>
            <groupId>commons-lang</groupId>
            <artifactId>commons-lang</artifactId>
        </dependency>
        <dependency>
            <groupId>commons-collections</groupId>
            <artifactId>commons-collections</artifactId>
        </dependency>

        <!-- TEST dependencies -->
        <dependency>
            <groupId>ch.qos.logback</groupId>
            <artifactId>logback-classic</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-core</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-inline</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.pitest</groupId>
                <artifactId>pitest-maven</artifactId>
                <configuration>
                    <mutationThreshold>70</mutationThreshold>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

### jadler-jetty/pom.xml  (build file (declares the updated dependency))
```
<?xml version="1.0" encoding="UTF-8"?>
<!--
Copyright (c) 2012 - 2016 Jadler contributors
This program is made available under the terms of the MIT License.
-->

<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <artifactId>jadler-jetty</artifactId>
    <name>${project.artifactId}</name>
    <description>An implementation of the stub http server component using Jetty.</description>
    <packaging>jar</packaging>

    <parent>
        <groupId>net.jadler</groupId>
        <artifactId>jadler-pom</artifactId>
        <version>1.3.2-SNAPSHOT</version>
    </parent>


    <dependencies>
        <dependency>
            <groupId>net.jadler</groupId>
            <artifactId>jadler-core</artifactId>
        </dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
        </dependency>
        <dependency>
            <groupId>org.eclipse.jetty</groupId>
            <artifactId>jetty-server</artifactId>
        </dependency>
        <dependency>
            <groupId>org.eclipse.jetty.orbit</groupId>
            <artifactId>javax.servlet</artifactId>
        </dependency>
        <dependency>
            <groupId>commons-lang</groupId>
            <artifactId>commons-lang</artifactId>
        </dependency>
        <dependency>
            <groupId>commons-io</groupId>
            <artifactId>commons-io</artifactId>
        </dependency>

        <!-- TEST dependencies -->
        <dependency>
            <groupId>ch.qos.logback</groupId>
            <artifactId>logback-classic</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.hamcrest</groupId>
            <artifactId>hamcrest</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-web</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.pitest</groupId>
                <artifactId>pitest-maven</artifactId>
                <configuration>
                    <mutationThreshold>20</mutationThreshold>
                </configuration>
            </plugin>
        </plugins>
    </build>

</project>
```

### jadler-core/src/test/java/net/jadler/JadlerMockerTest.java  (failing test)
```
... (lines 0-0 omitted)
/*
 * Copyright (c) 2012 - 2022 Jadler contributors
 * This program is made available under the terms of the MIT License.
 */
package net.jadler;

import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.LoggerContext;
import ch.qos.logback.classic.encoder.PatternLayoutEncoder;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.OutputStreamAppender;
import net.jadler.exception.JadlerException;
import net.jadler.mocking.VerificationException;
import net.jadler.mocking.Verifying;
import net.jadler.stubbing.HttpStub;
import net.jadler.stubbing.StubResponse;
import net.jadler.stubbing.Stubbing;
import net.jadler.stubbing.StubbingFactory;
import net.jadler.stubbing.server.StubHttpServer;
import net.jadler.stubbing.server.StubHttpServerManager;
import org.apache.commons.collections.MultiMap;
import org.apache.commons.collections.map.MultiValueMap;
import org.hamcrest.Description;
import org.hamcrest.Matcher;
import org.junit.Test;
import org.mockito.invocation.InvocationOnMock;
import org.mockito.stubbing.Answer;
import org.slf4j.LoggerFactory;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.net.URI;
import java.nio.charset.Charset;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;

import static java.lang.String.format;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.is;
... (lines 41-816 omitted)
                            "Request #2: %s\n" +
                            "  matching predicates:\n" +
                            "    %s\n" +
                            "  clashing predicates:\n" +
                            "    %s\n" +
                            "Request #3: %s\n" +
                            "  matching predicates:\n" +
                            "    %s\n" +
                            "  clashing predicates:\n" +
                            "    %s\n" +
                            "Request #4: %s\n" +
                            "  matching predicates:\n" +
                            "    %s\n" +
                            "  clashing predicates:\n" +
                            "    %s\n" +
                            "Request #5: %s\n" +
                            "  matching predicates:\n" +
                            "    %s\n" +
                            "  clashing predicates:\n" +
                            "    %s",
                    REQUESTS[0], MATCHER1_MISMATCH, MATCHER2_MISMATCH,
                    REQUESTS[1], MATCHER2_DESCRIPTION, MATCHER1_MISMATCH,
                    REQUESTS[2], MATCHER2_DESCRIPTION, MATCHER1_MISMATCH,
                    REQUESTS[3], MATCHER1_DESCRIPTION, MATCHER2_MISMATCH,
                    REQUESTS[4], MATCHER1_DESCRIPTION, MATCHER2_MISMATCH)));
        } finally {
            resetLoggerContext();
            os.close();
        }
    }


    @Test
    public void evaluateVerification_0_predicates_5_matching_negative() throws IOException {
        final JadlerMocker mocker = this.createMockerWithRequests();

        //5 requests matching (=received in this case), 4 expected          
        final Matcher<Integer> countMatcher = this.createCountMatcherFor(4, 5, COUNT_MATCHER_DESCRIPTION,
                COUNT_MATCHER_MISMATCH);

        final ByteArrayOutputStream os = addAppenderToStream();
        try {
            mocker.evaluateVerification(Collections.<Matcher<? super Request>>emptySet(), countMatcher);
            fail("VerificationException is supposed to be thrown here");
        } catch (final VerificationException e) {
            assertThat(e.getMessage(), is(format("The number of http requests was expected to be %s, but %s",
                    COUNT_MATCHER_DESCRIPTION, COUNT_MATCHER_MISMATCH)));

            assertThat(os.toString("UTF-8"), is(format(
                    "[INFO] Verification failed, here is a list of requests received so far:\n" +
                            "Request #1: %s\n" +
                            "  matching predicates: <none>\n" +
                            "  clashing predicates: <none>\n" +
                            "Request #2: %s\n" +
                            "  matching predicates: <none>\n" +
                            "  clashing predicates: <none>\n" +
                            "Request #3: %s\n" +
                            "  matching predicates: <none>\n" +
                            "  clashing predicates: <none>\n" +
                            "Request #4: %s\n" +
                            "  matching predicates: <none>\n" +
                            "  clashing predicates: <none>\n" +
                            "Request #5: %s\n" +
                            "  matching predicates: <none>\n" +
                            "  clashing predicates: <none>",
                    REQUESTS[0], REQUESTS[1], REQUESTS[2], REQUESTS[3], REQUESTS[4])));
        } finally {
            resetLoggerContext();
            os.close();
        }
    }


    @Test
    public void evaluateVerification_0_requests_0_matching_negative() {
        final JadlerMocker mocker = new JadlerMocker(mock(StubHttpServer.class));
        final Matcher<Request> m1 = this.createRequestMatcher(MATCHER1_DESCRIPTION, MATCHER1_MISMATCH);
        final Matcher<Request> m2 = this.createRequestMatcher(MATCHER2_DESCRIPTION, MATCHER2_MISMATCH);

        //0 requests matching (=received in this case), 0 expected
        final Matcher<Integer> countMatcher = this.createCountMatcherFor(1, 0, COUNT_MATCHER_DESCRIPTION,
... (lines 898-1051 omitted)
        //register all requests
        for (final Request r : REQUESTS) {
            mocker.provideStubResponseFor(r);
        }

        return mocker;
    }


    private void addDescriptionTo(final Matcher<?> m, final String desc) {
        doAnswer(new Answer<Void>() {
            @Override
            public Void answer(final InvocationOnMock invocation) {
                final Description d = (Description) invocation.getArguments()[0];

                d.appendText(desc);

                return null;
            }
        }).when(m).describeTo(any(Description.class));
    }


    private Collection<Matcher<? super Request>> collectionOf(Matcher<? super Request> m1,
                                                              Matcher<? super Request> m2) {
        return Arrays.<Matcher<? super Request>>asList(m1, m2);
    }


    private String expectedMessage() {
        return format("The number of http requests having %s AND %s was expected to be %s, but %s",
                MATCHER1_DESCRIPTION, MATCHER2_DESCRIPTION, COUNT_MATCHER_DESCRIPTION, COUNT_MATCHER_MISMATCH);
    }

    /**
     * Do not forget to close returned OutputStream.
     */
    private ByteArrayOutputStream addAppenderToStream() {
        final ByteArrayOutputStream os = new ByteArrayOutputStream();

        LoggerContext lc = (LoggerContext) LoggerFactory.getILoggerFactory();
        PatternLayoutEncoder ple = new PatternLayoutEncoder();
        ple.setPattern("[%level] %msg");
        ple.setContext(lc);
        ple.start();

        final OutputStreamAppender<ILoggingEvent> osAppender = new OutputStreamAppender<ILoggingEvent>();
        osAppender.setContext(lc);
        osAppender.setEncoder(ple);
        osAppender.setOutputStream(os);
        osAppender.start();

        Logger logbackLogger = (Logger) LoggerFactory.getLogger(Logger.ROOT_LOGGER_NAME);
        logbackLogger.addAppender(osAppender);

        return os;
    }

    private void resetLoggerContext() {
        LoggerContext lc = (LoggerContext) LoggerFactory.getILoggerFactory();
        lc.reset();
    }
}
```

### jadler-all/src/test/resources/logback.xml  (resource file named in the failing test)
```
<?xml version="1.0" encoding="UTF-8"?>
<!--
  ~ Copyright (c) 2022 Jadler contributors
  ~ This program is made available under the terms of the MIT License.
  -->

<configuration>
    <appender name="console" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>[%thread] %-5level %file\(%line\): %msg%n</pattern>
        </encoder>
    </appender>
    <logger name="org.eclipse" level="WARN"/>
    <root level="INFO">
        <appender-ref ref="console"/>
    </root>
</configuration>
```

### jadler-core/src/test/resources/logback.xml  (resource file named in the failing test)
```
<?xml version="1.0" encoding="UTF-8"?>
<!--
  ~ Copyright (c) 2022 Jadler contributors
  ~ This program is made available under the terms of the MIT License.
  -->

<configuration>
    <appender name="console" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>[%thread] %-5level %file\(%line\): %msg%n</pattern>
        </encoder>
    </appender>
    <logger name="org.eclipse" level="WARN"/>
    <root level="INFO">
        <appender-ref ref="console"/>
    </root>
</configuration>
```

### jadler-jdk/src/test/resources/logback.xml  (resource file named in the failing test)
```
<?xml version="1.0" encoding="UTF-8"?>
<!--
  ~ Copyright (c) 2022 Jadler contributors
  ~ This program is made available under the terms of the MIT License.
  -->

<configuration>
    <appender name="console" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>[%thread] %-5level %file\(%line\): %msg%n</pattern>
        </encoder>
    </appender>
    <logger name="org.eclipse" level="WARN"/>
    <root level="INFO">
        <appender-ref ref="console"/>
    </root>
</configuration>
```

### jadler-jetty/src/test/resources/logback.xml  (resource file named in the failing test)
```
<?xml version="1.0" encoding="UTF-8"?>
<!--
  ~ Copyright (c) 2022 Jadler contributors
  ~ This program is made available under the terms of the MIT License.
  -->

<configuration>
    <appender name="console" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>[%thread] %-5level %file\(%line\): %msg%n</pattern>
        </encoder>
    </appender>
    <logger name="org.eclipse" level="WARN"/>
    <root level="INFO">
        <appender-ref ref="console"/>
    </root>
</configuration>
```

### jadler-junit/src/test/resources/logback.xml  (resource file named in the failing test)
```
<?xml version="1.0" encoding="UTF-8"?>
<!--
  ~ Copyright (c) 2022 Jadler contributors
  ~ This program is made available under the terms of the MIT License.
  -->

<configuration>
    <appender name="console" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>[%thread] %-5level %file\(%line\): %msg%n</pattern>
        </encoder>
    </appender>
    <logger name="org.eclipse" level="WARN"/>
    <root level="INFO">
        <appender-ref ref="console"/>
    </root>
</configuration>
```


Now write the explanation and the single ```diff block.
