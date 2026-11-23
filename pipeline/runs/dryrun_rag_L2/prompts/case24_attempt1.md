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
`org.slf4j:slf4j-api` was updated from `1.7.36` to `2.0.4`. The project compiles, but tests now fail.

## Failure (from the build log)
Failing test classes: org.simplify4u.plugins.sign.SignMojoTest, org.simplify4u.plugins.sign.utils.EnvironmentTest
Exception types: java.lang.ClassCastException
Error lines:
- java.lang.ClassCastException: class org.slf4j.helpers.NOPLogger cannot be cast to class org.simplify4u.slf4jmock.internal.ProxyMock (org.slf4j.helpers.NOPLogger and org.simplify4u.slf4jmock.internal.ProxyMock are in unnamed module of loader 'app')
SLF4J console output:
- SLF4J: No SLF4J providers were found.
- SLF4J: Defaulting to no-operation (NOP) logger implementation
- SLF4J: See https://www.slf4j.org/codes.html#noProviders for further details.
- SLF4J: Class path contains SLF4J bindings targeting slf4j-api versions 1.7.x or earlier.
- SLF4J: Ignoring binding found at [jar:file:/root/.m2/repository/org/simplify4u/slf4j-mock/2.3.0/slf4j-mock-2.3.0.jar!/org/slf4j/impl/StaticLoggerBinder.class]
- SLF4J: See https://www.slf4j.org/codes.html#ignoredBindings for an explanation.

## Similar past breakages and their validated fixes (from the knowledge base)
They come from OTHER projects. Use them for the idea of the fix; adapt it to this project's files.

### Past case 1: org.slf4j:slf4j-api 1.7.36 -> 2.0.4 (retest/recheck)
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

### Past case 2: org.slf4j:slf4j-api 1.7.36 -> 2.0.4 (feedzai/pdb)
Symptom: java.lang.ClassCastException
  java.lang.ClassCastException: class org.slf4j.helpers.NOPLogger cannot be cast to class ch.qos.logback.classic.Logger (org.slf4j.helpers.NOPLogger and ch.qos.logback.classic.Logger are in unnamed module of loader 'app')
Behavior change: LoggerFactory returns NOPLogger instead of logback Logger
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
### pom.xml  (build file (declares the updated dependency))
```
<?xml version='1.0' encoding='UTF-8'?>
<!--
  ~ Copyright 2020-2021 Slawomir Jaranowski
  ~
  ~ Licensed under the Apache License, Version 2.0 (the "License");
  ~ you may not use this file except in compliance with the License.
  ~ You may obtain a copy of the License at
  ~
  ~     http://www.apache.org/licenses/LICENSE-2.0
  ~
  ~ Unless required by applicable law or agreed to in writing, software
  ~ distributed under the License is distributed on an "AS IS" BASIS,
  ~ WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  ~ See the License for the specific language governing permissions and
  ~ limitations under the License.
  -->

<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.simplify4u</groupId>
        <artifactId>parent</artifactId>
        <version>2.17.0</version>
        <relativePath />
    </parent>

    <groupId>org.simplify4u.plugins</groupId>
    <artifactId>sign-maven-plugin</artifactId>
    <version>1.0.2-SNAPSHOT</version>
    <packaging>maven-plugin</packaging>

    <name>Sign Maven Plugin</name>
    <description>
        Creates Open PGP / GPG signatures for all of the project's artifacts
        without any external software
    </description>
    <url>https://www.simplify4u.org/sign-maven-plugin</url>
    <inceptionYear>2020</inceptionYear>

    <organization>
        <name>Simplify4U</name>
        <url>https://www.simplify4u.org</url>
    </organization>

    <licenses>
        <license>
            <name>The Apache Software License, Version 2.0</name>
            <url>https://www.apache.org/licenses/LICENSE-2.0</url>
            <distribution>repo</distribution>
        </license>
    </licenses>

    <developers>
        <!-- Join a team if you want to support, maintain project -->
        <developer>
            <id>sjaranowski</id>
            <name>Slawomir Jaranowski</name>
            <email>s.jaranowski@gmail.com</email>
            <url>https://github.com/slawekjaranowski</url>
            <timezone>Europe/Warsaw</timezone>
        </developer>

        <developer>
            <id>mkarg</id>
            <name>Markus Karg</name>
            <email>markus@headcrashing.eu</email>
            <url>https://github.com/mkarg</url>
            <timezone>Europe/Berlin</timezone>
        </developer>
    </developers>

    <contributors>
        <!-- Add yourself to list after contributions - if wish -->
    </contributors>

    <prerequisites>
        <maven>${maven.version}</maven>
    </prerequisites>

    <scm>
        <connection>scm:git:git@github.com:s4u/sign-maven-plugin.git</connection>
        <developerConnection>${project.scm.connection}</developerConnection>
        <url>https://github.com/s4u/sign-maven-plugin</url>
        <tag>HEAD</tag>
    </scm>

    <distributionManagement>
        <site>
            <id>github</id>
            <url>${project.scm.connection}</url>
        </site>
    </distributionManagement>

    <properties>

        <maven.version>3.6.0</maven.version>
        <mockito.version>4.9.0</mockito.version>
        <pgpverify-maven-plugin.version>1.16.0</pgpverify-maven-plugin.version>

        <project.build.outputTimestamp>2022-02-27T13:30:38Z</project.build.outputTimestamp>

        <!-- default value is needed when jacoco is not executed -->
        <argLine />
    </properties>

    <dependencyManagement>
        <dependencies>
            <!-- maven core -->
            <dependency>
                <groupId>org.apache.maven</groupId>
                <artifactId>maven-core</artifactId>
                <version>${maven.version}</version>
                <exclusions>
                    <exclusion>
                        <groupId>org.sonatype.plexus</groupId>
                        <artifactId>*</artifactId>
                    </exclusion>
                </exclusions>
            </dependency>
            <dependency>
                <groupId>org.apache.maven</groupId>
                <artifactId>maven-plugin-api</artifactId>
                <version>${maven.version}</version>
            </dependency>
            <dependency>
                <groupId>org.apache.maven.plugin-tools</groupId>
                <artifactId>maven-plugin-annotations</artifactId>
                <version>${maven-plugin-plugin.version}</version>
            </dependency>
            <dependency>
                <groupId>org.codehaus.plexus</groupId>
                <artifactId>plexus-sec-dispatcher</artifactId>
                <version>2.0</version>
            </dependency>
            <dependency>
                <groupId>javax.inject</groupId>
                <artifactId>javax.inject</artifactId>
                <version>1</version>
            </dependency>

            <!-- external library -->
            <dependency>
                <groupId>org.bouncycastle</groupId>
                <artifactId>bcpg-jdk15on</artifactId>
                <version>1.70</version>
            </dependency>
            <dependency>
                <groupId>org.projectlombok</groupId>
                <artifactId>lombok</artifactId>
                <version>1.18.24</version>
            </dependency>
            <dependency>
                <groupId>org.slf4j</groupId>
                <artifactId>slf4j-api</artifactId>
                <version>2.0.4</version>
            </dependency>
            <dependency>
                <groupId>io.vavr</groupId>
                <artifactId>vavr</artifactId>
                <version>0.10.4</version>
            </dependency>

            <!-- testing -->
            <dependency>
                <groupId>org.assertj</groupId>
                <artifactId>assertj-core</artifactId>
                <version>3.23.1</version>
            </dependency>
            <dependency>
                <groupId>org.junit</groupId>
                <artifactId>junit-bom</artifactId>
                <version>5.9.1</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
            <dependency>
                <groupId>org.mockito</groupId>
                <artifactId>mockito-junit-jupiter</artifactId>
                <version>${mockito.version}</version>
            </dependency>
            <dependency>
                <groupId>org.simplify4u</groupId>
                <artifactId>slf4j-mock</artifactId>
                <version>2.3.0</version>
            </dependency>

            <!-- dependency coverage -->
            <dependency>
                <groupId>org.apache.maven</groupId>
                <artifactId>maven-artifact</artifactId>
                <version>${maven.version}</version>
            </dependency>
            <dependency>
                <groupId>org.codehaus.plexus</groupId>
                <artifactId>plexus-component-annotations</artifactId>
                <version>2.1.1</version>
            </dependency>
            <dependency>
                <groupId>org.codehaus.plexus</groupId>
                <artifactId>plexus-utils</artifactId>
                <version>3.5.0</version>
            </dependency>
            <dependency>
                <!-- https://bugs.eclipse.org/bugs/show_bug.cgi?id=552642 -->
                <groupId>org.eclipse.sisu</groupId>
                <artifactId>org.eclipse.sisu.inject</artifactId>
                <version>0.3.5</version>
            </dependency>
            <dependency>
                <groupId>org.mockito</groupId>
                <artifactId>mockito-core</artifactId>
                <version>${mockito.version}</version>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <dependencies>
        <dependency>
            <groupId>org.apache.maven.plugin-tools</groupId>
            <artifactId>maven-plugin-annotations</artifactId>
            <scope>provided</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.maven</groupId>
            <artifactId>maven-core</artifactId>
            <scope>provided</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.maven</groupId>
            <artifactId>maven-plugin-api</artifactId>
            <scope>provided</scope>
        </dependency>

        <dependency>
            <groupId>org.codehaus.plexus</groupId>
            <artifactId>plexus-sec-dispatcher</artifactId>
        </dependency>

        <dependency>
            <groupId>javax.inject</groupId>
            <artifactId>javax.inject</artifactId>
            <scope>provided</scope>
        </dependency>

        <dependency>
            <groupId>org.bouncycastle</groupId>
            <artifactId>bcpg-jdk15on</artifactId>
        </dependency>
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <scope>provided</scope>
        </dependency>
        <dependency>
            <groupId>io.vavr</groupId>
            <artifactId>vavr</artifactId>
        </dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
        </dependency>

        <!-- testing -->
        <dependency>
            <groupId>org.assertj</groupId>
            <artifactId>assertj-core</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-junit-jupiter</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.simplify4u</groupId>
            <artifactId>slf4j-mock</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <repositories>
        <repository>
            <id>apache-snapshot</id>
            <url>https://repository.apache.org/content/repositories/snapshots/</url>
            <snapshots>
                <enabled>true</enabled>
            </snapshots>
            <releases>
                <enabled>false</enabled>
            </releases>
        </repository>
    </repositories>

    <build>
        <pluginManagement>
            <plugins>
                <plugin>
                    <groupId>org.simplify4u.plugins</groupId>
                    <artifactId>pgpverify-maven-plugin</artifactId>
                    <version>${pgpverify-maven-plugin.version}</version>
                </plugin>
            </plugins>
        </pluginManagement>

        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-plugin-plugin</artifactId>
                <executions>
                    <execution>
                        <id>generated-help-mojo</id>
                        <goals>
                            <goal>helpmojo</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>

    <reporting>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-plugin-plugin</artifactId>
            </plugin>
        </plugins>
    </reporting>

    <profiles>
        <profile>
            <id>ci-system</id>
            <activation>
                <property>
                    <name>env.CI</name>
                </property>
            </activation>
            <properties>
                <invoker.streamLogsOnFailures>true</invoker.streamLogsOnFailures>
            </properties>
        </profile>

        <profile>
            <!-- when maven.test.skip is set we skip integration tests -->
            <id>integration-testing</id>
            <activation>
                <property>
                    <name>maven.test.skip</name>
                    <value>!true</value>
                </property>
            </activation>

            <build>
                <plugins>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-surefire-plugin</artifactId>
                        <configuration>
                            <excludedEnvironmentVariables>
                                <!-- exclude configuration variable from test environment -->
                                <excludedVariable>SIGN_KEY</excludedVariable>
                                <excludedVariable>SIGN_KEY_ID</excludedVariable>
                                <excludedVariable>SIGN_KEY_PASS</excludedVariable>
                            </excludedEnvironmentVariables>
                        </configuration>
                    </plugin>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-dependency-plugin</artifactId>
                        <executions>
                            <execution>
                                <id>unpack-maven4</id>
                                <phase>pre-integration-test</phase>
                                <goals>
                                    <goal>unpack</goal>
                                </goals>
                                <configuration>
                                    <artifactItems>
                                        <!--
                                        https://repository.apache.org/content/groups/snapshots/org/apache/maven/maven/
                                        -->
                                        <artifactItem>
                                            <groupId>org.apache.maven</groupId>
                                            <artifactId>apache-maven</artifactId>
                                            <version>4.0.0-alpha-1-SNAPSHOT</version>
                                            <type>zip</type>
                                            <classifier>bin</classifier>
                                        </artifactItem>
                                    </artifactItems>
                                    <outputDirectory>${project.build.directory}/maven4</outputDirectory>
                                </configuration>
                            </execution>
                        </executions>
                    </plugin>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-resources-plugin</artifactId>
                        <executions>
                            <execution>
                                <id>it-tests-public-key</id>
                                <phase>pre-integration-test</phase>
                                <goals>
                                    <goal>copy-resources</goal>
                                </goals>
                                <configuration>
                                    <outputDirectory>${project.build.directory}/keys-cache</outputDirectory>
                                    <resources>
                                        <resource>
                                            <directory>src/test/resources/public-keys</directory>
                                        </resource>
                                    </resources>
                                </configuration>
                            </execution>
                        </executions>
                    </plugin>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-invoker-plugin</artifactId>
                        <configuration>
                            <pomIncludes>
                                <pomInclude>*/pom-test.xml</pomInclude>
                            </pomIncludes>
                            <settingsFile>src/it/settings.xml</settingsFile>
                            <showErrors>true</showErrors>
                            <showVersion>true</showVersion>
                            <environmentVariables>
                                <SIGN_KEY />
                                <SIGN_KEY_ID />
                                <SIGN_KEY_PASS />
                            </environmentVariables>
                        </configuration>
                        <executions>
                            <execution>
                                <id>invoker-tests-maven3</id>
                                <goals>
                                    <goal>install</goal>
                                    <goal>integration-test</goal>
                                    <goal>verify</goal>
                                </goals>
                                <configuration>
                                    <cloneProjectsTo>${project.build.directory}/it3</cloneProjectsTo>
                                    <localRepositoryPath>${project.build.directory}/it3-repo</localRepositoryPath>
                                    <reportsDirectory>${project.build.directory}/invoker-reports3</reportsDirectory>
                                </configuration>
                            </execution>
                            <execution>
                                <id>invoker-tests-maven4</id>
                                <goals>
                                    <goal>install</goal>
                                    <goal>integration-test</goal>
                                    <goal>verify</goal>
                                </goals>
                                <configuration>
                                    <cloneProjectsTo>${project.build.directory}/it4</cloneProjectsTo>
                                    <localRepositoryPath>${project.build.directory}/it4-repo</localRepositoryPath>
                                    <reportsDirectory>${project.build.directory}/invoker-reports4</reportsDirectory>
                                    <mavenHome>${project.build.directory}/maven4/apache-maven</mavenHome>
                                </configuration>
                            </execution>
                        </executions>
                    </plugin>
                </plugins>
            </build>
        </profile>
    </profiles>
</project>
```

### src/test/java/org/simplify4u/plugins/sign/SignMojoTest.java  (failing test)
```
/*
 * Copyright 2020 Slawomir Jaranowski
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.simplify4u.plugins.sign;

import java.io.File;
import java.util.Collections;

import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import org.apache.maven.artifact.Artifact;
import org.apache.maven.artifact.DefaultArtifact;
import org.apache.maven.artifact.handler.DefaultArtifactHandler;
import org.apache.maven.project.MavenProject;
import org.apache.maven.project.MavenProjectHelper;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Spy;
import org.mockito.junit.jupiter.MockitoExtension;
import org.simplify4u.plugins.sign.openpgp.PGPKeyInfo;
import org.slf4j.Logger;

@ExtendWith(MockitoExtension.class)
class SignMojoTest {

    @Mock
    private MavenProject project;

    @Mock
    private MavenProjectHelper projectHelper;

    @Mock
    private ArtifactSigner artifactSigner;

    @Mock
    private ArtifactSignerFactory artifactSignerFactory;

    @Mock
    private KeyInfoFactory keyInfoFactory;

    @Spy
    private Logger logger;

    @InjectMocks
    private SignMojo mojo;

    @Test
    void skipExecution() {

        //given
        mojo.setSkip(true);

        // when
        mojo.execute();

        // then
        verifyNoInteractions(artifactSignerFactory, artifactSigner, keyInfoFactory, project);
    }

    @Test
    void emptyKeyInfoShouldSkipExecution() {

        // given
        mojo.setSkipNoKey(true);
        when(keyInfoFactory.buildKeyInfo(any())).thenReturn(PGPKeyInfo.builder().build());

        // when
        mojo.execute();

        //then
        verifyNoInteractions(artifactSignerFactory, artifactSigner, project);
    }

    @Test
    void emptyKeyInfoShouldBreakExecution() {
        // given
        mojo.setSkipNoKey(false);
        when(keyInfoFactory.buildKeyInfo(any())).thenReturn(PGPKeyInfo.builder().build());

        // when - then
        assertThatThrownBy(() -> mojo.execute())
                .isExactlyInstanceOf(SignMojoException.class)
                .hasMessage("Required key for signing not found");

        verifyNoInteractions(artifactSignerFactory, artifactSigner, project);
    }

    @Test
    void standardFlow() {

        DefaultArtifact artifact = new DefaultArtifact("groupId", "artifactId", "1.0.0", null, "pom", null,
                new DefaultArtifactHandler("pom"));

        when(project.getGroupId()).thenReturn(artifact.getGroupId());
        when(project.getArtifactId()).thenReturn(artifact.getArtifactId());
        when(project.getVersion()).thenReturn(artifact.getVersion());
        when(project.getArtifact()).thenReturn(artifact);
        when(project.getFile()).thenReturn(new File("pom.xml"));
        when(project.getBasedir()).thenReturn(new File("."));

        when(keyInfoFactory.buildKeyInfo(any())).thenReturn(PGPKeyInfo.builder().key(new byte[]{1, 2, 3}).build());

        when(artifactSignerFactory.getSigner(any())).thenReturn(artifactSigner);

        when(artifactSigner.signArtifact(any())).thenReturn(Collections.singletonList(SignResult.builder().build()));

        mojo.execute();

        verify(artifactSigner).signArtifact(artifact);
        verify(projectHelper).attachArtifact(eq(project), any(), any(), any());

        verifyNoMoreInteractions(artifactSigner, projectHelper);
    }

    @Test
    void excludeArtifact() {

        DefaultArtifact artifact = new DefaultArtifact("groupId", "artifactId", "1.0.0", null, "pom", null,
                new DefaultArtifactHandler("pom"));

        when(project.getGroupId()).thenReturn(artifact.getGroupId());
        when(project.getArtifactId()).thenReturn(artifact.getArtifactId());
        when(project.getVersion()).thenReturn(artifact.getVersion());
        when(project.getArtifact()).thenReturn(artifact);
        when(project.getFile()).thenReturn(new File("pom.xml"));
        when(project.getBasedir()).thenReturn(new File("."));

        Artifact artifactMd5 = aArtifactWithFile("artifact2", "pom.xml.md5");

        when(project.getAttachedArtifacts()).thenReturn(Collections.singletonList(artifactMd5));

        when(keyInfoFactory.buildKeyInfo(any())).thenReturn(PGPKeyInfo.builder().key(new byte[]{1, 2, 3}).build());

        when(artifactSignerFactory.getSigner(any())).thenReturn(artifactSigner);

        when(artifactSigner.signArtifact(any())).thenReturn(Collections.singletonList(SignResult.builder().build()));

        mojo.setExcludes(Collections.singletonList("**/*.md5"));
        mojo.execute();

        verify(artifactSigner).signArtifact(artifact);
        verify(projectHelper).attachArtifact(eq(project), any(), any(), any());

        verifyNoMoreInteractions(artifactSigner, projectHelper);
    }

    private Artifact aArtifactWithFile(String artifactId, String fileName) {
        DefaultArtifact artifact = new DefaultArtifact("groupId", artifactId, "1.0.0", null, "pom", null,
                new DefaultArtifactHandler("pom"));
        artifact.setFile(new File(fileName));
        return artifact;
    }

}
```

### src/test/java/org/simplify4u/plugins/sign/utils/EnvironmentTest.java  (failing test)
```
/*
 * Copyright 2021 Slawomir Jaranowski
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.simplify4u.plugins.sign.utils;

import java.util.Optional;
import java.util.function.UnaryOperator;
import java.util.stream.Stream;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.params.provider.Arguments.arguments;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoMoreInteractions;
import static org.mockito.Mockito.when;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.slf4j.Logger;

@ExtendWith(MockitoExtension.class)
class EnvironmentTest {

    public static final String TEST_ENV_NAME = "TEST";

    @Mock
    private UnaryOperator<String> envGetter;

    @Mock
    private Logger logger;

    @InjectMocks
    private Environment environment;

    public static Stream<Arguments> shouldReadProperEnvironmentVariable() {
        return Stream.of(
                arguments(null, null),
                arguments("null", null),
                arguments("", null),
                arguments("  ", null),
                arguments(" trim value ", "trim value")
        );
    }

    @ParameterizedTest
    @MethodSource
    void shouldReadProperEnvironmentVariable(String envVariableValue, String result) {

        when(envGetter.apply(TEST_ENV_NAME)).thenReturn(envVariableValue);

        Optional<String> test = environment.getEnv(TEST_ENV_NAME);
        assertThat(test).isEqualTo(Optional.ofNullable(result));

        verify(envGetter).apply(TEST_ENV_NAME);
        verifyNoMoreInteractions(envGetter);
    }

    @Test
    void debugLogForEmptyValue() {

        when(envGetter.apply(TEST_ENV_NAME)).thenReturn(null);

        Optional<String> test = environment.getEnv(TEST_ENV_NAME);

        assertThat(test).isEmpty();

        verify(logger).debug("No {} set as environment variable", TEST_ENV_NAME);
        verifyNoMoreInteractions(logger);
    }

    @Test
    void debugLogForNotEmptyValue() {

        when(envGetter.apply(TEST_ENV_NAME)).thenReturn("Test");

        Optional<String> test = environment.getEnv(TEST_ENV_NAME);

        assertThat(test).hasValue("Test");

        verify(logger).debug("Retrieved {} configuration from environment variable", TEST_ENV_NAME);
        verifyNoMoreInteractions(logger);
    }

}
```


Now write the explanation and the single ```diff block.
