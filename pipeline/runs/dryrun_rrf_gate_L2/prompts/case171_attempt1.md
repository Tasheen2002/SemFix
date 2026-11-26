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
`org.slf4j:slf4j-api` was updated from `1.7.30` to `2.0.0`. The project compiles, but tests now fail.

## Failure (from the build log)
Failing test classes: org.pac4j.dropwizard.e2e.EndToEndServletTest, org.pac4j.dropwizard.e2e.EndToEndTest, org.pac4j.dropwizard.bundle.BundleFactoryTest
Exception types: java.lang.RuntimeException, java.lang.reflect.InvocationTargetException, java.lang.IllegalStateException
Error lines:
- java.lang.RuntimeException: java.lang.reflect.InvocationTargetException
- Caused by: java.lang.reflect.InvocationTargetException
- Caused by: java.lang.IllegalStateException: Unable to acquire the logger context
SLF4J console output:
- SLF4J: No SLF4J providers were found.
- SLF4J: Defaulting to no-operation (NOP) logger implementation
- SLF4J: See http://www.slf4j.org/codes.html#noProviders for further details.
- SLF4J: Class path contains SLF4J bindings targeting slf4j-api versions prior to 1.8.
- SLF4J: Ignoring binding found at [jar:file:/root/.m2/repository/ch/qos/logback/logback-classic/1.2.3/logback-classic-1.2.3.jar!/org/slf4j/impl/StaticLoggerBinder.class]
- SLF4J: See http://www.slf4j.org/codes.html#ignoredBindings for an explanation.
Project stack frames:
- org.pac4j.dropwizard.AbstractApplicationTest (AbstractApplicationTest.java:31)
- org.pac4j.dropwizard.e2e.EndToEndServletTest (EndToEndServletTest.java:31)
- org.pac4j.dropwizard.e2e.EndToEndServletTest (EndToEndServletTest.java:54)
- org.pac4j.dropwizard.e2e.EndToEndServletTest (EndToEndServletTest.java:36)
- org.pac4j.dropwizard.e2e.EndToEndServletTest (EndToEndServletTest.java:69)
- org.pac4j.dropwizard.e2e.EndToEndTest (EndToEndTest.java:31)
- org.pac4j.dropwizard.e2e.EndToEndTest (EndToEndTest.java:54)
- org.pac4j.dropwizard.e2e.EndToEndTest (EndToEndTest.java:36)
- org.pac4j.dropwizard.e2e.EndToEndTest (EndToEndTest.java:69)
- org.pac4j.dropwizard.bundle.BundleFactoryTest (BundleFactoryTest.java:47)
- org.pac4j.dropwizard.bundle.BundleFactoryTest (BundleFactoryTest.java:83)
- org.pac4j.dropwizard.bundle.BundleFactoryTest (BundleFactoryTest.java:31)

## Similar past breakages and their validated fixes (from the knowledge base)
They come from OTHER projects. Use them for the idea of the fix; adapt it to this project's files.

### Past case 1: org.slf4j:slf4j-api 1.7.36 -> 2.0.0 (s4u/sign-maven-plugin)
Symptom: java.lang.ClassCastException
  java.lang.ClassCastException: class org.slf4j.helpers.NOPLogger cannot be cast to class org.simplify4u.slf4jmock.ProxyMock (org.slf4j.helpers.NOPLogger and org.simplify4u.slf4jmock.ProxyMock are in unnamed module of loader 'app')
Behavior change: LoggerFactory returns NOPLogger instead of slf4j-mock logger
Fix (RESEARCHER_WRITTEN, written by the researchers (validated, but not the project's own fix); validated: all tests pass): Replace org.simplify4u:slf4j-mock 2.2.0 (SLF4J-1 binding) with org.simplify4u:slf4j2-mock 2.3.0 (same author and packages, SLF4J-2 provider).
```diff
diff --git a/pom.xml b/pom.xml
--- a/pom.xml
+++ b/pom.xml
@@ -181,8 +181,8 @@
             </dependency>
             <dependency>
                 <groupId>org.simplify4u</groupId>
-                <artifactId>slf4j-mock</artifactId>
-                <version>2.2.0</version>
+                <artifactId>slf4j2-mock</artifactId>
+                <version>2.3.0</version>
             </dependency>
 
             <!-- dependency coverage -->
@@ -279,7 +279,7 @@
         </dependency>
         <dependency>
             <groupId>org.simplify4u</groupId>
-            <artifactId>slf4j-mock</artifactId>
+            <artifactId>slf4j2-mock</artifactId>
             <scope>test</scope>
         </dependency>
     </dependencies>
```

### Past case 2: org.slf4j:slf4j-api 1.7.36 -> 2.0.0 (retest/recheck)
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

### Past case 3: org.slf4j:slf4j-api 1.7.36 -> 2.0.0 (alphagov/pay-adminusers)
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
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <parent>
    <groupId>org.sonatype.oss</groupId>
    <artifactId>oss-parent</artifactId>
    <version>9</version>
  </parent>

  <groupId>org.pac4j</groupId>
  <artifactId>dropwizard-pac4j</artifactId>
  <packaging>jar</packaging>
  <version>5.0.1-SNAPSHOT</version>
  <name>Dropwizard pac4j Support</name>
  <description>Dropwizard bundle adding support for the pac4j security engine</description>
  <url>https://github.com/pac4j/dropwizard-pac4j</url>

  <repositories>
    <repository>
      <id>sonatype-nexus-snapshots</id>
      <name>Sonatype Nexus Snapshots</name>
      <url>https://oss.sonatype.org/content/repositories/snapshots</url>
      <releases>
        <enabled>false</enabled>
      </releases>
      <snapshots>
        <enabled>true</enabled>
      </snapshots>
    </repository>
    <repository>
      <id>sonatype-nexus</id>
      <name>Sonatype Nexus</name>
      <url>https://oss.sonatype.org/content/repositories/releases</url>
      <releases>
        <enabled>true</enabled>
      </releases>
      <snapshots>
        <enabled>false</enabled>
      </snapshots>
    </repository>
  </repositories>

  <licenses>
    <license>
      <name>The Apache Software License, Version 2.0</name>
      <url>http://www.apache.org/licenses/LICENSE-2.0.txt</url>
      <distribution>repo</distribution>
    </license>
  </licenses>

  <organization>
    <name>pac4j</name>
    <url>http://www.pac4j.org/</url>
  </organization>

  <developers>
    <developer>
      <id>leleuj</id>
      <name>Jerome LELEU</name>
      <email>leleuj@gmail.com</email>
    </developer>
    <developer>
      <id>victornoel</id>
      <name>Victor NOEL</name>
      <url>https://github.com/victornoel</url>
    </developer>
    <developer>
      <id>evanm</id>
      <name>Evan Meagher</name>
      <email>evan.meagher@gmail.com</email>
      <organization>Dropwizard</organization>
      <organizationUrl>http://www.dropwizard.io</organizationUrl>
    </developer>
  </developers>

  <scm>
    <url>https://github.com/pac4j/dropwizard-pac4j.git</url>
    <connection>https://github.com/pac4j/dropwizard-pac4j.git</connection>
    <developerConnection>scm:git:git@github.com:pac4j/dropwizard-pac4j.git</developerConnection>
  </scm>

  <issueManagement>
    <system>GitHub Issues</system>
    <url>https://github.com/pac4j/dropwizard-pac4j/issues</url>
  </issueManagement>

  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
    <maven.compiler.source>11</maven.compiler.source>
    <maven.compiler.target>11</maven.compiler.target>
    <dropwizard.version>2.0.17</dropwizard.version>
    <pac4j.version>4.5.6</pac4j.version>
    <jax-rs-pac4j.version>4.0.0</jax-rs-pac4j.version>
    <jee-pac4j.version>5.0.0</jee-pac4j.version>
  </properties>

  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>io.dropwizard</groupId>
        <artifactId>dropwizard-bom</artifactId>
        <version>${dropwizard.version}</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>com.fasterxml</groupId>
        <artifactId>classmate</artifactId>
        <version>1.5.1</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>com.fasterxml.jackson.core</groupId>
        <artifactId>jackson-databind</artifactId>
        <version>2.10.5.1</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>com.google.errorprone</groupId>
        <artifactId>error_prone_annotations</artifactId>
        <version>2.15.0</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>com.google.guava</groupId>
        <artifactId>guava</artifactId>
        <version>31.1-jre</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>org.apache.commons</groupId>
        <artifactId>commons-lang3</artifactId>
        <version>3.11</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>joda-time</groupId>
        <artifactId>joda-time</artifactId>
        <version>2.11.0</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>org.checkerframework</groupId>
        <artifactId>checker-qual</artifactId>
        <version>3.24.0</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>org.eclipse.jetty</groupId>
        <artifactId>jetty-server</artifactId>
        <version>9.4.35.v20201120</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>org.glassfish</groupId>
        <artifactId>jakarta.el</artifactId>
        <version>3.0.3</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>jakarta.xml.bind</groupId>
        <artifactId>jakarta.xml.bind-api</artifactId>
        <version>2.3.3</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>jakarta.annotation</groupId>
        <artifactId>jakarta.annotation-api</artifactId>
        <version>1.3.5</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>jakarta.servlet</groupId>
        <artifactId>jakarta.servlet-api</artifactId>
        <version>4.0.4</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>jakarta.activation</groupId>
        <artifactId>jakarta.activation-api</artifactId>
        <version>2.0.0</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>org.glassfish.jersey.core</groupId>
        <artifactId>jersey-server</artifactId>
        <version>2.32</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>org.hibernate.validator</groupId>
        <artifactId>hibernate-validator</artifactId>
        <version>6.2.4.Final</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>org.javassist</groupId>
        <artifactId>javassist</artifactId>
        <version>3.29.1-GA</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>org.objenesis</groupId>
        <artifactId>objenesis</artifactId>
        <version>3.3</version>
      </dependency>
      <dependency>
        <groupId>org.pac4j</groupId>
        <artifactId>pac4j-core</artifactId>
        <version>${pac4j.version}</version>
      </dependency>
      <!-- Required for dependency convergence -->
      <dependency>
        <groupId>org.slf4j</groupId>
        <artifactId>slf4j-api</artifactId>
        <version>2.0.0</version>
      </dependency>
      <dependency>
        <groupId>org.assertj</groupId>
        <artifactId>assertj-core</artifactId>
        <version>3.18.1</version>
      </dependency>
      <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-core</artifactId>
        <version>3.12.4</version>
      </dependency>
    </dependencies>
  </dependencyManagement>

  <dependencies>
    <dependency>
      <groupId>io.dropwizard</groupId>
      <artifactId>dropwizard-core</artifactId>
      <scope>provided</scope>
    </dependency>
    <dependency>
      <groupId>org.pac4j</groupId>
      <artifactId>pac4j-core</artifactId>
    </dependency>
    <dependency>
      <groupId>org.pac4j</groupId>
      <artifactId>pac4j-config</artifactId>
      <version>${pac4j.version}</version>
    </dependency>
    <dependency>
      <groupId>org.pac4j</groupId>
      <artifactId>jersey-pac4j</artifactId>
      <version>${jax-rs-pac4j.version}</version>
      <exclusions>
        <exclusion>
          <groupId>org.pac4j</groupId>
          <artifactId>pac4j-core</artifactId>
        </exclusion>
      </exclusions>
    </dependency>
    <dependency>
      <groupId>org.pac4j</groupId>
      <artifactId>jee-pac4j</artifactId>
      <version>${jee-pac4j.version}</version>
      <exclusions>
        <exclusion>
          <groupId>org.pac4j</groupId>
          <artifactId>pac4j-core</artifactId>
        </exclusion>
      </exclusions>
    </dependency>
    <dependency>
      <groupId>org.pac4j</groupId>
      <artifactId>pac4j-http</artifactId>
      <version>${pac4j.version}</version>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.pac4j</groupId>
      <artifactId>pac4j-oauth</artifactId>
      <version>${pac4j.version}</version>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>io.dropwizard</groupId>
      <artifactId>dropwizard-testing</artifactId>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.assertj</groupId>
      <artifactId>assertj-core</artifactId>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.mockito</groupId>
      <artifactId>mockito-core</artifactId>
      <scope>test</scope>
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.10.1</version>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-source-plugin</artifactId>
        <version>3.2.1</version>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-javadoc-plugin</artifactId>
        <version>3.4.1</version>
      </plugin>
      <plugin>
        <groupId>com.github.spotbugs</groupId>
        <artifactId>spotbugs-maven-plugin</artifactId>
        <version>4.7.1.1</version>
        <dependencies>
          <!-- overwrite dependency on spotbugs if you want to specify the version of spotbugs -->
          <dependency>
            <groupId>com.github.spotbugs</groupId>
            <artifactId>spotbugs</artifactId>
            <version>4.7.1</version>
          </dependency>
        </dependencies>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-pmd-plugin</artifactId>
        <version>3.17.0</version>
        <configuration>
          <includeTests>true</includeTests>
          <printFailingErrors>true</printFailingErrors>
        </configuration>
        <executions>
          <execution>
            <id>run-pmd</id>
            <phase>compile</phase>
            <goals>
              <goal>check</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-enforcer-plugin</artifactId>
        <version>3.1.0</version>
        <executions>
          <execution>
            <id>dependency-convergence</id>
            <configuration>
              <rules>
                <dependencyConvergence />
              </rules>
            </configuration>
            <goals>
              <goal>enforce</goal>
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
        </plugins>
      </build>
    </profile>
  </profiles>

</project>
```

### src/test/java/org/pac4j/dropwizard/e2e/EndToEndServletTest.java  (failing test)
```
package org.pac4j.dropwizard.e2e;

import static org.assertj.core.api.Assertions.assertThat;

import javax.ws.rs.client.Entity;
import javax.ws.rs.core.Form;
import javax.ws.rs.core.HttpHeaders;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import org.junit.Test;
import org.pac4j.dropwizard.AbstractApplicationTest;
import org.pac4j.http.client.direct.DirectBasicAuthClient;
import org.pac4j.http.client.direct.DirectFormClient;

import io.dropwizard.setup.Environment;
import io.dropwizard.testing.ConfigOverride;

public class EndToEndServletTest extends AbstractApplicationTest {

    public static class App extends TestApplication<TestConfiguration> {

        @Override
        public void run(TestConfiguration configuration,
                Environment environment) throws Exception {
            environment.jersey().register(new DogsResource());
        }
    }

    private void setup(ConfigOverride config) throws Exception {
        super.setup(App.class, "end-to-end-servlet-test.yaml", config);
    }

    @Test
    public void grantsAccessToResourcesForm() throws Exception {
        setup(ConfigOverride.config("pac4j.servlet.security[0].clients",
                DirectFormClient.class.getSimpleName()));

        // username == password
        Form form = new Form();
        form.param("username", "rosebud");
        form.param("password", "rosebud");
        final String dogName = client.target(getUrlPrefix() + "/dogs/pierre")
                .request(MediaType.APPLICATION_JSON)
                .post(Entity.entity(form,
                        MediaType.APPLICATION_FORM_URLENCODED_TYPE),
                        String.class);

        assertThat(dogName).isEqualTo("pierre");
    }

    @Test
    public void grantsAccessToResources() throws Exception {
        setup(ConfigOverride.config("pac4j.servlet.security[0].clients",
                DirectBasicAuthClient.class.getSimpleName()));

        final String dogName = client.target(getUrlPrefix() + "/dogs/pierre")
                .request(MediaType.APPLICATION_JSON)
                // username == password
                .header(HttpHeaders.AUTHORIZATION,
                        mkAuthField("rosebud", "rosebud"))
                .get(String.class);

        assertThat(dogName).isEqualTo("pierre");
    }

    @Test
    public void restrictsAccessToResources() throws Exception {
        setup(ConfigOverride.config("pac4j.servlet.security[0].clients",
                DirectBasicAuthClient.class.getSimpleName()));

        final Response response = client.target(getUrlPrefix() + "/dogs/pierre")
                .request(MediaType.APPLICATION_JSON)
                // username != password
                .header(HttpHeaders.AUTHORIZATION, mkAuthField("boy", "howdy"))
                .get();

        assertThat(response.getStatusInfo())
                .isEqualTo(Response.Status.UNAUTHORIZED);
    }
}
```

### src/test/java/org/pac4j/dropwizard/e2e/EndToEndTest.java  (failing test)
```
package org.pac4j.dropwizard.e2e;

import static org.assertj.core.api.Assertions.assertThat;

import javax.ws.rs.client.Entity;
import javax.ws.rs.core.Form;
import javax.ws.rs.core.HttpHeaders;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import org.junit.Test;
import org.pac4j.dropwizard.AbstractApplicationTest;
import org.pac4j.http.client.direct.DirectBasicAuthClient;
import org.pac4j.http.client.direct.DirectFormClient;

import io.dropwizard.setup.Environment;
import io.dropwizard.testing.ConfigOverride;

public class EndToEndTest extends AbstractApplicationTest {

    public static class App extends TestApplication<TestConfiguration> {

        @Override
        public void run(TestConfiguration configuration,
                Environment environment) throws Exception {
            environment.jersey().register(new DogsResource());
        }
    }

    private void setup(ConfigOverride config) throws Exception {
        super.setup(App.class, "end-to-end-test.yaml", config);
    }

    @Test
    public void grantsAccessToResourcesForm() throws Exception {
        setup(ConfigOverride.config("pac4j.globalFilters[0].clients",
                DirectFormClient.class.getSimpleName()));

        // username == password
        Form form = new Form();
        form.param("username", "rosebud");
        form.param("password", "rosebud");
        final String dogName = client.target(getUrlPrefix() + "/dogs/pierre")
                .request(MediaType.APPLICATION_JSON)
                .post(Entity.entity(form,
                        MediaType.APPLICATION_FORM_URLENCODED_TYPE),
                        String.class);

        assertThat(dogName).isEqualTo("pierre");
    }

    @Test
    public void grantsAccessToResources() throws Exception {
        setup(ConfigOverride.config("pac4j.globalFilters[0].clients",
                DirectBasicAuthClient.class.getSimpleName()));

        final String dogName = client.target(getUrlPrefix() + "/dogs/pierre")
                .request(MediaType.APPLICATION_JSON)
                // username == password
                .header(HttpHeaders.AUTHORIZATION,
                        mkAuthField("rosebud", "rosebud"))
                .get(String.class);

        assertThat(dogName).isEqualTo("pierre");
    }

    @Test
    public void restrictsAccessToResources() throws Exception {
        setup(ConfigOverride.config("pac4j.globalFilters[0].clients",
                DirectBasicAuthClient.class.getSimpleName()));

        final Response response = client.target(getUrlPrefix() + "/dogs/pierre")
                .request(MediaType.APPLICATION_JSON)
                // username != password
                .header(HttpHeaders.AUTHORIZATION, mkAuthField("boy", "howdy"))
                .get();

        assertThat(response.getStatusInfo())
                .isEqualTo(Response.Status.UNAUTHORIZED);
    }
}
```

### src/test/java/org/pac4j/dropwizard/bundle/BundleFactoryTest.java  (failing test)
```
package org.pac4j.dropwizard.bundle;

import static org.assertj.core.api.Assertions.assertThat;

import org.assertj.core.api.Condition;
import org.eclipse.jetty.server.session.SessionHandler;
import org.junit.Test;
import org.pac4j.core.client.Client;
import org.pac4j.core.config.Config;
import org.pac4j.dropwizard.AbstractApplicationTest;
import org.pac4j.jax.rs.pac4j.JaxRsUrlResolver;
import org.pac4j.jax.rs.servlet.features.ServletJaxRsContextFactoryProvider;

import com.fasterxml.jackson.databind.ObjectMapper;

import io.dropwizard.setup.Environment;
import io.dropwizard.testing.ConfigOverride;

public class BundleFactoryTest extends AbstractApplicationTest {

    public static class App extends TestApplication<TestConfiguration> {

    }

    private static final Condition<Object> CONDSI = new Condition<>(
            s -> s instanceof ServletJaxRsContextFactoryProvider,
            "pac4j singleton");

    @Test
    public void noPac4jInConfig() throws Exception{
        setup(App.class, "no-pac4j.yaml");

        App app = dropwizardTestSupport.getApplication();
        ObjectMapper om = dropwizardTestSupport.getObjectMapper();
        Environment env = dropwizardTestSupport.getEnvironment();

        assertThat(app.bundle.getConfig()).isNull();
        // if one use the bundle with null pac4j, one will get the mixing
        // registered anyway
        assertThat(om.findMixInClassFor(Client.class)).isNotNull();
        assertThat(env.jersey().getResourceConfig().getSingletons())
                .doesNotHave(CONDSI);
    }

    @Test
    public void emptyPac4jInConfig() throws Exception{
        setup(App.class, "empty-pac4j.yaml");

        App app = dropwizardTestSupport.getApplication();
        ObjectMapper om = dropwizardTestSupport.getObjectMapper();
        Environment env = dropwizardTestSupport.getEnvironment();

        Config config = app.bundle.getConfig();
        assertThat(config).isNotNull();
        // this is the default url resolver!
        assertThat(config.getClients().getUrlResolver())
                .isInstanceOf(JaxRsUrlResolver.class);
        assertThat(om.findMixInClassFor(Client.class)).isNotNull();
        assertThat(env.jersey().getResourceConfig().getSingletons())
                .haveAtLeastOne(CONDSI);

        assertThat(env.getApplicationContext().getSessionHandler())
                .isInstanceOf(SessionHandler.class);
    }

    @Test
    public void sessionEnabledForced() throws Exception {
        setup(App.class, "empty-pac4j.yaml",
                ConfigOverride.config("pac4j.sessionEnabled", "true"));

        App app = dropwizardTestSupport.getApplication();
        Environment env = dropwizardTestSupport.getEnvironment();

        Config config = app.bundle.getConfig();
        assertThat(config).isNotNull();

        assertThat(env.getApplicationContext().getSessionHandler())
                .isInstanceOf(SessionHandler.class);
    }

    @Test
    public void sessiondisabledForced() throws Exception {
        setup(App.class, "empty-pac4j.yaml",
                ConfigOverride.config("pac4j.sessionEnabled", "false"));

        App app = dropwizardTestSupport.getApplication();
        Environment env = dropwizardTestSupport.getEnvironment();

        Config config = app.bundle.getConfig();
        assertThat(config).isNotNull();

        assertThat(env.getApplicationContext().getSessionHandler()).isNull();
    }

}
```

### src/test/resources/clients.yaml  (resource file named in the failing test)
```
clients:
  - org.pac4j.http.client.direct.DirectBasicAuthClient:
      authenticator:
        class: org.pac4j.http.credentials.authenticator.test.SimpleTestUsernamePasswordAuthenticator
  - org.pac4j.http.client.direct.DirectBasicAuthClient:
      name: basic
```

### src/test/resources/empty-pac4j.yaml  (resource file named in the failing test)
```
server:
  applicationConnectors:
    - type: http
      port: 0
  adminConnectors:
    - type: http
      port: 0

pac4j: {}
```

### src/test/resources/end-to-end-servlet-test.yaml  (resource file named in the failing test)
```
server:
  applicationConnectors:
    - type: http
      port: 0
  adminConnectors:
    - type: http
      port: 0

pac4j:
  clients:
    - org.pac4j.http.client.direct.DirectBasicAuthClient:
        authenticator:
          class: org.pac4j.http.credentials.authenticator.test.SimpleTestUsernamePasswordAuthenticator
    - org.pac4j.http.client.direct.DirectFormClient:
        authenticator:
          class: org.pac4j.http.credentials.authenticator.test.SimpleTestUsernamePasswordAuthenticator
  servlet:
    security:
      - clients: ""
        authorizers: "none"
```

### src/test/resources/end-to-end-test.yaml  (resource file named in the failing test)
```
server:
  applicationConnectors:
    - type: http
      port: 0
  adminConnectors:
    - type: http
      port: 0

pac4j:
  clients:
    - org.pac4j.http.client.direct.DirectBasicAuthClient:
        authenticator:
          class: org.pac4j.http.credentials.authenticator.test.SimpleTestUsernamePasswordAuthenticator
    - org.pac4j.http.client.direct.DirectFormClient:
        authenticator:
          class: org.pac4j.http.credentials.authenticator.test.SimpleTestUsernamePasswordAuthenticator
  globalFilters:
    - clients: ""
      authorizers: "none"
```

### src/test/resources/no-pac4j.yaml  (resource file named in the failing test)
```
server:
  applicationConnectors:
    - type: http
      port: 0
  adminConnectors:
    - type: http
      port: 0
```

### src/test/java/org/pac4j/dropwizard/AbstractApplicationTest.java  (class in the failing stack trace)
```
package org.pac4j.dropwizard;

import javax.ws.rs.client.Client;

import org.glassfish.jersey.client.JerseyClientBuilder;
import org.junit.After;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.google.common.base.Charsets;
import com.google.common.io.BaseEncoding;

import io.dropwizard.Application;
import io.dropwizard.Configuration;
import io.dropwizard.setup.Bootstrap;
import io.dropwizard.setup.Environment;
import io.dropwizard.testing.ConfigOverride;
import io.dropwizard.testing.DropwizardTestSupport;
import io.dropwizard.testing.ResourceHelpers;

public class AbstractApplicationTest {

    protected DropwizardTestSupport<TestConfiguration> dropwizardTestSupport;

    protected Client client = new JerseyClientBuilder().build();

    public void setup(
            Class<? extends Application<TestConfiguration>> applicationClass,
            String configPath, ConfigOverride... configOverrides) throws Exception{
        dropwizardTestSupport = new DropwizardTestSupport<>(applicationClass,
                ResourceHelpers.resourceFilePath(configPath), configOverrides);
        dropwizardTestSupport.before();
    }

    @After
    public void tearDown() {
        dropwizardTestSupport.after();
        client.close();
    }

    protected String getUrlPrefix() {
        return "http://localhost:" + dropwizardTestSupport.getLocalPort();
    }

    protected String mkAuthField(String username, String password) {
        final String encodedBasicAuthCreds = BaseEncoding.base64().encode(String
                .format("%s:%s", username, password).getBytes(Charsets.UTF_8));
        return String.format("Basic %s", encodedBasicAuthCreds);
    }

    public static class TestConfiguration extends Configuration {

        private Pac4jFactory pac4jFactory = null;

        @JsonProperty("pac4j")
        public Pac4jFactory getPac4jFactory() {
            return pac4jFactory;
        }

        @JsonProperty("pac4j")
        public void setPac4jFactory(Pac4jFactory pac4jFactory) {
            this.pac4jFactory = pac4jFactory;
        }
    }

    public static class TestApplication<C extends TestConfiguration>
            extends Application<C> {

        public final Pac4jBundle<C> bundle = new Pac4jBundle<C>() {
            @Override
            public Pac4jFactory getPac4jFactory(C configuration) {
                return configuration.getPac4jFactory();
            }
        };

        @Override
        public void initialize(Bootstrap<C> bootstrap) {
            bootstrap.addBundle(bundle);
        }

        @Override
        public void run(C configuration, Environment environment)
                throws Exception {
            // nothing by default
        }
    }

}
```


Now write the explanation and the single ```diff block.
