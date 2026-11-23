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
`org.dhatim:dropwizard-sentry` was updated from `2.0.22` to `2.0.26-3`. The project compiles, but tests now fail.

## Failure (from the build log)
Failing test classes: uk.gov.pay.card.it.resources.CardIdResourceITest
Exception types: io.dropwizard.configuration.ConfigurationParsingException, com.fasterxml.jackson.databind.exc.UnrecognizedPropertyException
Error lines:
- io.dropwizard.configuration.ConfigurationParsingException:
- Caused by: com.fasterxml.jackson.databind.exc.UnrecognizedPropertyException:

## Similar past breakages and their validated fixes (from the knowledge base)
They come from OTHER projects. Use them for the idea of the fix; adapt it to this project's files.

### Past case 1: org.slf4j:slf4j-api 1.7.36 -> 2.0.3 (alphagov/pay-adminusers)
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

### Past case 2: org.codehaus.plexus:plexus-io 3.2.0 -> 3.3.0 (codehaus-plexus/plexus-archiver)
Symptom: org.codehaus.plexus.archiver.ArchiverException
  org.codehaus.plexus.archiver.ArchiverException: Not a directory: test/resources/symlinks/src/symLinkToDirOnTheOutside
  org.codehaus.plexus.archiver.ArchiverException: Not a directory: bzz/symLinkToDirOnTheOutside
Behavior change: Return value of PlexusIoResource.isDirectory() for symbolic links to directories changed true -> false
Fix (VERSION_SKIP, the project's developers; validated: all tests pass): 3.3.0 never landed; 3.3.1 landed POM-only. Validated: plexus-io 3.3.1 alone makes all tests pass, so the library undid the symlink isDirectory change.
```diff
diff --git a/pom.xml b/pom.xml
--- a/pom.xml
+++ b/pom.xml
@@ -64,7 +64,7 @@
     <dependency>
       <groupId>org.codehaus.plexus</groupId>
       <artifactId>plexus-io</artifactId>
-      <version>3.3.0</version>
+      <version>3.3.1</version>
     </dependency>
     <!-- Apache Commons dependencies -->
     <dependency>
```

### Past case 3: org.slf4j:slf4j-api 1.7.30 -> 2.0.0 (pac4j/dropwizard-pac4j)
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


## Project files (at the breaking commit)
### pom.xml  (build file (declares the updated dependency))
```
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>uk.gov.pay</groupId>
    <version>0.1-SNAPSHOT</version>
    <artifactId>pay-cardid</artifactId>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <dropwizard.version>2.0.26</dropwizard.version>
        <hamcrest.version>2.2</hamcrest.version>
        <jmh.version>1.33</jmh.version>
        <jackson.version>2.13.0</jackson.version>
        <mockito.version>4.1.0</mockito.version>
        <pay-java-commons.version>1.0.20211213094914</pay-java-commons.version>
    </properties>

    <parent>
        <groupId>io.dropwizard</groupId>
        <artifactId>dropwizard-dependencies</artifactId>
        <version>2.0.26</version>
    </parent>

    <dependencies>
        <dependency>
            <groupId>uk.gov.service.payments</groupId>
            <artifactId>logging</artifactId>
            <version>${pay-java-commons.version}</version>
        </dependency>
        <dependency>
            <groupId>io.dropwizard</groupId>
            <artifactId>dropwizard-core</artifactId>
            <version>${dropwizard.version}</version>
        </dependency>
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava</artifactId>
            <version>31.0.1-jre</version>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
            <version>${jackson.version}</version>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-annotations</artifactId>
            <version>${jackson.version}</version>
        </dependency>
        <dependency>
            <groupId>org.dhatim</groupId>
            <artifactId>dropwizard-sentry</artifactId>
            <version>2.0.26-3</version>
        </dependency>
        <dependency>
            <groupId>io.dropwizard</groupId>
            <artifactId>dropwizard-json-logging</artifactId>
            <version>${dropwizard.version}</version>
        </dependency>

        <!-- testing -->
        <dependency>
            <groupId>org.hamcrest</groupId>
            <artifactId>hamcrest</artifactId>
            <version>${hamcrest.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.hamcrest</groupId>
            <artifactId>hamcrest-library</artifactId>
            <version>${hamcrest.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>io.dropwizard</groupId>
            <artifactId>dropwizard-testing</artifactId>
            <version>${dropwizard.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-core</artifactId>
            <version>${mockito.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>io.rest-assured</groupId>
            <artifactId>rest-assured</artifactId>
            <version>4.4.0</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.openjdk.jmh</groupId>
            <artifactId>jmh-core</artifactId>
            <version>${jmh.version}</version>
        </dependency>
        <dependency>
            <groupId>org.openjdk.jmh</groupId>
            <artifactId>jmh-generator-annprocess</artifactId>
            <version>${jmh.version}</version>
            <scope>provided</scope>
        </dependency>
        <dependency>
            <groupId>io.dropwizard.metrics</groupId>
            <artifactId>metrics-graphite</artifactId>
            <version>4.2.5</version>
        </dependency>
        <dependency>
            <groupId>com.jayway.jsonpath</groupId>
            <artifactId>json-path-assert</artifactId>
            <version>2.6.0</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <version>5.8.2</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-junit-jupiter</artifactId>
            <version>${mockito.version}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
                <configuration>
                    <release>11</release>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-jar-plugin</artifactId>
                <version>3.2.0</version>
                <configuration>
                    <archive>
                        <manifest>
                            <addDefaultImplementationEntries>true</addDefaultImplementationEntries>
                        </manifest>
                    </archive>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-dependency-plugin</artifactId>
                <version>3.2.0</version>
                <executions>
                    <execution>
                        <id>analyze</id>
                        <goals>
                            <goal>analyze-only</goal>
                        </goals>
                        <configuration>
                            <failOnWarning>false</failOnWarning>
                        </configuration>
                    </execution>
                    <execution>
                        <id>copy-dependencies</id>
                        <phase>package</phase>
                        <goals>
                            <goal>copy-dependencies</goal>
                        </goals>
                        <configuration>
                            <stripVersion>true</stripVersion>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-resources-plugin</artifactId>
                <version>3.2.0</version>
                <executions>
                    <execution>
                        <id>copy-resources</id>
                        <phase>validate</phase>
                        <goals>
                            <goal>copy-resources</goal>
                        </goals>
                        <configuration>
                            <outputDirectory>${basedir}/target</outputDirectory>
                            <resources>
                                <resource>
                                    <directory>src/main/resources/config</directory>
                                </resource>
                            </resources>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-shade-plugin</artifactId>
                <version>3.2.4</version>
                <configuration>
                    <outputFile>target/${project.artifactId}-${project.version}-allinone.jar</outputFile>
                    <filters>
                        <filter>
                            <artifact>*:*</artifact>
                            <excludes>
                                <exclude>META-INF/*.SF</exclude>
                                <exclude>META-INF/*.DSA</exclude>
                                <exclude>META-INF/*.RSA</exclude>
                            </excludes>
                        </filter>
                    </filters>
                </configuration>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals>
                            <goal>shade</goal>
                        </goals>
                        <configuration>
                            <transformers>
                                <transformer
                                        implementation="org.apache.maven.plugins.shade.resource.ServicesResourceTransformer"/>
                                <transformer
                                        implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                                    <mainClass>uk.gov.pay.card.app.CardApi</mainClass>
                                </transformer>
                            </transformers>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <groupId>org.codehaus.mojo</groupId>
                <artifactId>exec-maven-plugin</artifactId>
                <version>3.0.0</version>
                <configuration>
                    <mainClass>uk.gov.pay.card.app.CardApi</mainClass>
                    <arguments>
                        <argument>server</argument>
                        <argument>src/main/resources/config/config.yaml</argument>
                    </arguments>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
```

### src/test/java/uk/gov/pay/card/it/resources/CardIdResourceITest.java  (failing test)
```
package uk.gov.pay.card.it.resources;

import io.dropwizard.testing.junit5.DropwizardAppExtension;
import io.dropwizard.testing.junit5.DropwizardExtensionsSupport;
import io.restassured.response.ValidatableResponse;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import uk.gov.pay.card.app.CardApi;
import uk.gov.pay.card.app.config.CardConfiguration;

import static io.dropwizard.testing.ConfigOverride.config;
import static io.dropwizard.testing.ResourceHelpers.resourceFilePath;
import static io.restassured.RestAssured.given;
import static io.restassured.http.ContentType.JSON;
import static org.hamcrest.core.Is.is;

/**
 * @deprecated The usefulness of many of these tests is unclear - move them to pay-cardid-data?
 * <p>
 * These tests used to make assertions about data in pay-cardid-data, but that lives in a private repo.
 * <p>
 * We want to be able to test pay-cardid in a CI system that doesn't have access to private repos,
 * so the data needed for the tests to pass has been redacted to reduce its sensitivity and inlined
 * in src/test/resources/card-id-resource-integration-test
 * <p>
 * The overall effect is that a lot of these tests are now just checking that "the tests do what the tests do",
 * whereas they used to make some (fairly loose) assertions that the bin data in pay-cardid-data was correct.
 * <p>
 * If we care about testing pay-cardid-data we should set up CI for that repo separately in a system that
 * has access to private repos and move the tests that use card data there.
 * <p>
 * A test that checks the general success case and the tests for the error conditions without relying on specific
 * card details are probably still valid and should stay.
 */
@ExtendWith(DropwizardExtensionsSupport.class)
public class CardIdResourceITest {

    private static final DropwizardAppExtension<CardConfiguration> app = new DropwizardAppExtension<>(
            CardApi.class
            , resourceFilePath("config/config.yaml")
            , config("server.applicationConnectors[0].port", "0")
            , config("server.adminConnectors[0].port", "0")
            , config("worldpayDataLocation", "file://" + resourceFilePath("card-id-resource-integration-test/worldpay-bin-ranges.csv"))
            , config("discoverDataLocation", "file://" + resourceFilePath("card-id-resource-integration-test/discover-bin-ranges.csv"))
            , config("testCardDataLocation", "file://" + resourceFilePath("card-id-resource-integration-test/test-bin-ranges.csv")));

    @Test
    public void shouldFindDiscoverCardInformation() {
        getCardInformation("6221267457963485")
                .statusCode(200)
                .contentType(JSON)
                .body("brand", is("unionpay"))
                .body("label", is("UNIONPAY"))
                .body("type", is("CD"))
                .body("prepaid", is("NOT_PREPAID"))
                .body("corporate", is(false));
    }

    @Test
    public void shouldFindTestCardInformation() {
        getCardInformation("2221000000000009")
                .statusCode(200)
                .contentType(JSON)
                .body("brand", is("master-card"))
                .body("label", is("MC"))
                .body("type", is("C"))
                .body("prepaid", is("NOT_PREPAID"))
                .body("corporate", is(false));
    }

    @Test
    public void shouldFindWorldpayCardInformation() {
        getCardInformation("2225670000000000")
                .statusCode(200)
                .contentType(JSON)
                .body("brand", is("master-card"))
                .body("label", is("DEBIT MASTERCARD"))
                .body("type", is("D"))
                .body("prepaid", is("NOT_PREPAID"))
                .body("corporate", is(false));
    }

    @Test
    public void shouldFindAmexCardInformation() {
        getCardInformation("3714496353984311")
                .statusCode(200)
                .contentType(JSON)
                .body("brand", is("american-express"))
                .body("label", is("AMEX"))
                .body("type", is("C"))
                .body("prepaid", is("NOT_PREPAID"))
                .body("corporate", is(false));
    }

    @Test
    public void shouldFindMastercardCreditCorporateCardInformation() {
        getCardInformation("2223451044300001")
                .statusCode(200)
                .contentType(JSON)
                .body("brand", is("master-card"))
                .body("label", is("MASTERCARD CREDIT"))
                .body("type", is("C"))
                .body("prepaid", is("NOT_PREPAID"))
                .body("corporate", is(true));
    }

    @Test
    public void shouldFindPrepaidCard() {
        getCardInformation("4208933330200001")
                .statusCode(200)
                .contentType(JSON)
                .body("brand", is("visa"))
                .body("label", is("VISA CREDIT"))
                .body("type", is("D"))
                .body("prepaid", is("PREPAID"))
                .body("corporate", is(false));
    }

    @Test
    public void shouldReturn404WhenCardInformationNotFound() {
        getCardInformation("8282382383829393")
                .statusCode(404);
    }

    @Test
    public void shouldReturn422WhenCardNumberIsTooSmall() {
        getCardInformation("8")
                .statusCode(422);
    }

    @Test
    public void shouldReturn422WhenCardNumberIsTooBig() {
        getCardInformation("12345678901234567890")
                .statusCode(422);
    }

    @Test
    public void shouldReturn422WhenJSONIsEmpty() {
        given().port(app.getLocalPort())
                .contentType(JSON)
                .body("{}")
                .when()
                .post("/v1/api/card")
                .then().statusCode(422);
    }

    @Test
    public void shouldReturn422WhenJSONIsMissing() {
        given().port(app.getLocalPort())
                .contentType(JSON)
                .body("")
                .when()
                .post("/v1/api/card")
                .then().statusCode(422);
    }

    private ValidatableResponse getCardInformation(String cardNumber) {
        return given().port(app.getLocalPort())
                .contentType(JSON)
                .body(String.format("{\"cardNumber\":%s}", cardNumber))
                .when()
                .post("/v1/api/card")
                .then();
    }
}
```

### src/main/resources/config/config.yaml  (resource file named in the failing test)
```
server:
  applicationConnectors:
    - type: http
      port: ${PORT:-8080}
  adminConnectors:
    - type: http
      port: ${ADMIN_PORT:-8081}
  requestLog:
    appenders:
      - type: console
        layout:
          type: govuk-pay-access-json
          additionalFields:
            container: "cardid"
            environment: ${ENVIRONMENT}

logging:
  level: INFO
  appenders:
    - type: logstash-console
      threshold: ALL
      target: stdout
      customFields:
        container: "cardid"
        environment: ${ENVIRONMENT}
    - type: sentry
      threshold: ERROR
      dsn: ${SENTRY_DSN:-https://example.com@dummy/1}
      environment: ${ENVIRONMENT}
      stacktraceAppPackages: ["uk.gov.pay"]

worldpayDataLocation: ${WORLDPAY_DATA_LOCATION:-file:///app/data/worldpay/GENERIC2ISOCPTISSUERPREPAID.CSV}
discoverDataLocation: ${DISCOVER_DATA_LOCATION:-file:///app/data/discover/Merchant_Marketing.csv}
testCardDataLocation: ${TEST_CARD_DATA_LOCATION:-file:///app/data/test-cards/test-card-bin-ranges.csv}

graphiteHost: ${METRICS_HOST:-localhost}
graphitePort: ${METRICS_PORT:-8092}
```

### src/test/resources/card-id-resource-integration-test/discover-bin-ranges.csv  (resource file named in the failing test)
```
01,START,END,TYPE,BRAND
02,62212600,62212700,CD,UNIONPAY
```

### src/test/resources/card-id-resource-integration-test/test-bin-ranges.csv  (resource file named in the failing test)
```
01,START,END,TYPE,BRAND
02,71221111,71221400,CD,DISCOVER
02,371449635,371449635,C,AMERICAN EXPRESS
02,222100000,222100000,C,MC
```

### src/test/resources/card-id-resource-integration-test/worldpay-bin-ranges.csv  (resource file named in the failing test)
```
00,20210419,451354,,,,,,,,,,,,
01,222345000000000000,222345009999999999,CP,DEBIT MASTERCARD,UNKNOWN,GBR,826,UNITED KINGDOM,D,USD,DCC allowed,VPMCX,N,,,,,,,,,,,
01,222345100000000000,222345509999999999,CP,MASTERCARD CREDIT,UNKNOWN,GBR,826,UNITED KINGDOM,C,USD,DCC allowed,VPMCX,N,,,,,,,,,,,
01,222567000000000000,222567999999999999,CN,DEBIT MASTERCARD,UNKNOWN,NPL,524,NEPAL,D,USD,DCC allowed,DM000,N,,,,,,,,,,,
01,370000000000000000,389999999999999999,CN,AMEX,UNKNOWN,NPL,524,NEPAL,C,USD,DCC allowed,AX000,N,,,,,,,,,,,
01,410873333000000000,410873333999999999,CN,VISA DEBIT,UNKNOWN,USA,840,UNITED STATES,D,,DCC allowed,DE000,U,N,,,,,,,,,,
01,420893333000000000,420903333999999999,CN,VISA CREDIT,UNKNOWN,USA,840,UNITED STATES,P,,DCC allowed,DE000,U,N,,,,,,,,,,
99,451355,,,,,,,,,,,,,
```

### src/test/resources/discover/discover-bin-ranges.csv  (resource file named in the failing test)
```
01,START,END,TYPE,BRAND
02,71221111,71221400,CD,DISCOVER
02,71231111,71241400,CD,DISCOVER
02,71241111,71251400,CD,DISCOVER
09
```

### src/test/resources/worldpay/worldpay-bin-ranges.csv  (resource file named in the failing test)
```
00,20210419,451354,,,,,,,,,,,,
01,222345000000000000,222345009999999999,CP,MASTERCARD CREDIT,UNKNOWN,GBR,826,UNITED KINGDOM,D,USD,DCC allowed,VPMCX,N,,,,,,,,,,,
01,222567000000000000,222567999999999999,CN,DEBIT MASTERCARD,UNKNOWN,NPL,524,NEPAL,D,USD,DCC allowed,DM000,N,,,,,,,,,,,
01,222890000000000000,222895999999999999,CN,AMEX,UNKNOWN,NPL,524,NEPAL,D,USD,DCC allowed,AX000,N,,,,,,,,,,,
01,410873333000000000,410873333999999999,CN,VISA DEBIT,UNKNOWN,USA,840,UNITED STATES,D,,DCC allowed,DE000,U,N,,,,,,,,,,
99,451355,,,,,,,,,,,,,
```


Now write the explanation and the single ```diff block.
