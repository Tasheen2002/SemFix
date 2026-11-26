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
`org.slf4j:slf4j-api` was updated from `1.7.36` to `2.0.5`. The project compiles, but tests now fail.

## Failure (from the build log)
Failing test classes: uk.gov.pay.adminusers.queue.event.EventMessageHandlerTest, uk.gov.pay.adminusers.unit.service.ServiceResourceFindTest, uk.gov.pay.adminusers.unit.service.ServiceResourceCreateTest, uk.gov.pay.adminusers.unit.service.ServiceResourceSearchTest, uk.gov.pay.adminusers.unit.service.ServiceResourceUpdateTest
Exception types: java.lang.ClassCastException, java.lang.ExceptionInInitializerError, java.lang.NoClassDefFoundError, java.lang.IllegalStateException
Error lines:
- java.lang.ClassCastException: class org.slf4j.helpers.NOPLogger cannot be cast to class ch.qos.logback.classic.Logger (org.slf4j.helpers.NOPLogger and ch.qos.logback.classic.Logger are in unnamed module of loader 'app')
- java.lang.Exception: java.lang.ExceptionInInitializerError
- Caused by: java.lang.NoClassDefFoundError: Could not initialize class uk.gov.pay.adminusers.unit.service.ServiceResourceFindTest
- Caused by: java.lang.ExceptionInInitializerError
- Caused by: java.lang.IllegalStateException: Unable to acquire the logger context
- Caused by: java.lang.NoClassDefFoundError: Could not initialize class uk.gov.pay.adminusers.unit.service.ServiceResourceCreateTest
- Caused by: java.lang.NoClassDefFoundError: Could not initialize class uk.gov.pay.adminusers.unit.service.ServiceResourceSearchTest
- Caused by: java.lang.NoClassDefFoundError: Could not initialize class uk.gov.pay.adminusers.unit.service.ServiceResourceUpdateTest
SLF4J console output:
- SLF4J: No SLF4J providers were found.
- SLF4J: Defaulting to no-operation (NOP) logger implementation
- SLF4J: See https://www.slf4j.org/codes.html#noProviders for further details.
- SLF4J: Class path contains SLF4J bindings targeting slf4j-api versions 1.7.x or earlier.
- SLF4J: Ignoring binding found at [jar:file:/root/.m2/repository/ch/qos/logback/logback-classic/1.2.11/logback-classic-1.2.11.jar!/org/slf4j/impl/StaticLoggerBinder.class]
- SLF4J: See https://www.slf4j.org/codes.html#ignoredBindings for an explanation.
Project stack frames:
- uk.gov.pay.adminusers.queue.event.EventMessageHandlerTest (EventMessageHandlerTest.java:111)

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

### Past case 2: org.slf4j:slf4j-api 1.7.36 -> 2.0.1 (retest/recheck)
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

### Past case 3: org.slf4j:slf4j-api 1.7.36 -> 2.0.1 (jadler-mocking/jadler)
Symptom: java.lang.ClassCastException
  java.lang.ClassCastException: class org.slf4j.helpers.NOPLoggerFactory cannot be cast to class ch.qos.logback.classic.LoggerContext (org.slf4j.helpers.NOPLoggerFactory and ch.qos.logback.classic.LoggerContext are in unnamed module of loader
Behavior change: Logger factory changed LoggerContext -> NOPLoggerFactory
Fix (COMPANION_DEPENDENCY_UPGRADE, the project's developers; validated: all tests pass): slf4j 2.0.3 landed together with logback-classic 1.2.11 -> 1.3.4 (an SLF4J-2 provider), POM only. Fixes the R5 provider-selection change.
```diff
diff --git a/pom.xml b/pom.xml
--- a/pom.xml
+++ b/pom.xml
@@ -127,7 +127,7 @@
             <dependency>
                 <groupId>ch.qos.logback</groupId>
                 <artifactId>logback-classic</artifactId>
-                <version>1.2.11</version>
+                <version>1.3.4</version>
                 <scope>test</scope>
             </dependency>
             <dependency>
```


## Project files (at the breaking commit)
### pom.xml  (build file (declares the updated dependency))
```
... (lines 0-0 omitted)
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>uk.gov.pay</groupId>
    <version>0.1-SNAPSHOT</version>
    <artifactId>pay-adminusers</artifactId>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <dropwizard.version>2.1.4</dropwizard.version>
        <hamcrest.version>2.2</hamcrest.version>
        <eclipselink.version>2.7.11</eclipselink.version>
        <guice.version>5.1.0</guice.version>
        <guava.version>31.1-jre</guava.version>
        <jackson.version>2.14.1</jackson.version>
        <pact.version>3.6.15</pact.version>
        <pay-java-commons.version>1.0.20221121110222</pay-java-commons.version>
        <junit5.version>5.9.1</junit5.version>
        <swaggger-version>2.2.7</swaggger-version>
        <testcontainers.version>1.17.6</testcontainers.version>
        <wiremock.version>2.35.0</wiremock.version>
        <surefire.version>3.0.0-M7</surefire.version>
        <PACT_BROKER_URL/>
        <PACT_BROKER_USERNAME/>
        <PACT_BROKER_PASSWORD/>
        <PACT_CONSUMER_VERSION/>
        <PACT_CONSUMER_TAG/>
    </properties>
    <dependencies>
        <dependency>
            <groupId>uk.gov.service.payments</groupId>
            <artifactId>logging</artifactId>
            <version>${pay-java-commons.version}</version>
        </dependency>
        <dependency>
            <groupId>uk.gov.service.payments</groupId>
            <artifactId>model</artifactId>
            <version>${pay-java-commons.version}</version>
        </dependency>
        <dependency>
            <groupId>uk.gov.service.payments</groupId>
            <artifactId>queue</artifactId>
            <version>${pay-java-commons.version}</version>
        </dependency>
        <dependency>
            <groupId>io.dropwizard</groupId>
            <artifactId>dropwizard-core</artifactId>
            <version>${dropwizard.version}</version>
        </dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>2.0.5</version>
        </dependency>
        <dependency>
            <groupId>io.dropwizard</groupId>
            <artifactId>dropwizard-auth</artifactId>
            <version>${dropwizard.version}</version>
        </dependency>
        <dependency>
            <groupId>io.dropwizard</groupId>
            <artifactId>dropwizard-client</artifactId>
            <version>${dropwizard.version}</version>
        </dependency>
        <dependency>
            <groupId>io.dropwizard</groupId>
            <artifactId>dropwizard-json-logging</artifactId>
            <version>${dropwizard.version}</version>
        </dependency>
        <dependency>
            <groupId>io.dropwizard</groupId>
            <artifactId>dropwizard-migrations</artifactId>
            <version>${dropwizard.version}</version>
            <exclusions>
                <exclusion>
                    <groupId>org.liquibase</groupId>
                    <artifactId>liquibase-core</artifactId>
                </exclusion>
            </exclusions>
        </dependency>
        <dependency>
            <groupId>io.dropwizard.metrics</groupId>
            <artifactId>metrics-graphite</artifactId>
            <version>4.2.13</version>
        </dependency>
        <dependency>
            <groupId>org.liquibase</groupId>
            <artifactId>liquibase-core</artifactId>
            <version>4.17.2</version>
            <exclusions>
                <exclusion>
                    <groupId>javax.servlet</groupId>
                    <artifactId>jstl</artifactId>
                </exclusion>
            </exclusions>
        </dependency>
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <version>42.5.0</version>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-core</artifactId>
            <version>${jackson.version}</version>
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
            <groupId>com.fasterxml.jackson.datatype</groupId>
            <artifactId>jackson-datatype-jsr310</artifactId>
            <version>${jackson.version}</version>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.datatype</groupId>
            <artifactId>jackson-datatype-guava</artifactId>
            <version>${jackson.version}</version>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.jaxrs</groupId>
            <artifactId>jackson-jaxrs-base</artifactId>
            <version>${jackson.version}</version>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.jaxrs</groupId>
            <artifactId>jackson-jaxrs-json-provider</artifactId>
            <version>${jackson.version}</version>
        </dependency>
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava</artifactId>
            <version>${guava.version}</version>
        </dependency>
        <dependency>
            <groupId>org.eclipse.persistence</groupId>
            <artifactId>org.eclipse.persistence.jpa</artifactId>
            <version>${eclipselink.version}</version>
            <scope>compile</scope>
        </dependency>
        <dependency>
            <groupId>com.google.inject</groupId>
            <artifactId>guice</artifactId>
            <version>${guice.version}</version>
        </dependency>
        <dependency>
            <groupId>com.google.inject.extensions</groupId>
            <artifactId>guice-persist</artifactId>
            <version>${guice.version}</version>
        </dependency>
        <dependency>
            <groupId>com.google.inject.extensions</groupId>
            <artifactId>guice-assistedinject</artifactId>
            <version>${guice.version}</version>
        </dependency>
        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-lang3</artifactId>
            <version>3.12.0</version>
        </dependency>
        <dependency>
            <groupId>org.mindrot</groupId>
            <artifactId>jbcrypt</artifactId>
            <version>0.4</version>
        </dependency>
        <dependency>
            <groupId>com.warrenstrange</groupId>
            <artifactId>googleauth</artifactId>
            <version>1.5.0</version>
        </dependency>
        <dependency>
            <groupId>ch.qos.logback</groupId>
            <artifactId>logback-classic</artifactId>
            <version>1.2.11</version>
        </dependency>
        <dependency>
            <groupId>uk.gov.service.notify</groupId>
            <artifactId>notifications-java-client</artifactId>
            <version>3.19.0-RELEASE</version>
        </dependency>
        <dependency>
            <groupId>commons-validator</groupId>
            <artifactId>commons-validator</artifactId>
            <version>1.7</version>
        </dependency>
        <dependency>
            <groupId>com.googlecode.libphonenumber</groupId>
            <artifactId>libphonenumber</artifactId>
            <version>8.13.0</version>
        </dependency>
        <dependency>
            <groupId>uk.gov.service.payments</groupId>
            <artifactId>utils</artifactId>
            <version>${pay-java-commons.version}</version>
        </dependency>
        <dependency>
            <groupId>org.dhatim</groupId>
            <artifactId>dropwizard-sentry</artifactId>
            <version>2.1.2-4</version>
        </dependency>
        <dependency>
            <groupId>com.amazonaws</groupId>
            <artifactId>aws-java-sdk-sqs</artifactId>
            <version>1.12.344</version>
        </dependency>
        <dependency>
            <groupId>com.google.code.gson</groupId>
            <artifactId>gson</artifactId>
            <version>2.10</version>
        </dependency>

        <!-- testing -->
        <dependency>
            <groupId>io.dropwizard</groupId>
            <artifactId>dropwizard-testing</artifactId>
            <version>${dropwizard.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-junit-jupiter</artifactId>
            <version>4.9.0</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>io.rest-assured</groupId>
            <artifactId>rest-assured</artifactId>
            <version>5.3.0</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.hamcrest</groupId>
            <artifactId>hamcrest-core</artifactId>
... (lines 241-244 omitted)
            <groupId>org.hamcrest</groupId>
            <artifactId>hamcrest-library</artifactId>
            <version>${hamcrest.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.hamcrest</groupId>
            <artifactId>java-hamcrest</artifactId>
            <version>2.0.0.0</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>io.dropwizard</groupId>
            <artifactId>dropwizard-jdbi3</artifactId>
            <version>${dropwizard.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.exparity</groupId>
            <artifactId>hamcrest-date</artifactId>
            <version>2.0.8</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>au.com.dius</groupId>
            <artifactId>pact-jvm-provider-junit_2.12</artifactId>
            <version>${pact.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>au.com.dius</groupId>
            <artifactId>pact-jvm-consumer-junit_2.12</artifactId>
            <version>${pact.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>commons-beanutils</groupId>
            <artifactId>commons-beanutils</artifactId>
            <version>1.9.4</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>uk.gov.service.payments</groupId>
            <artifactId>testing</artifactId>
            <version>${pay-java-commons.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.jayway.jsonpath</groupId>
            <artifactId>json-path-assert</artifactId>
            <version>2.7.0</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>javax.activation</groupId>
            <artifactId>activation</artifactId>
            <version>1.1.1</version>
        </dependency>
        <dependency>
            <groupId>javax.xml.bind</groupId>
            <artifactId>jaxb-api</artifactId>
            <version>2.3.1</version>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-params</artifactId>
            <version>${junit5.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter-api</artifactId>
            <version>${junit5.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>io.swagger.core.v3</groupId>
            <artifactId>swagger-annotations</artifactId>
            <version>${swaggger-version}</version>
        </dependency>
        <dependency>
            <groupId>org.testcontainers</groupId>
            <artifactId>postgresql</artifactId>
            <version>${testcontainers.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.github.tomakehurst</groupId>
            <artifactId>wiremock-jre8</artifactId>
            <version>${wiremock.version}</version>
            <exclusions>
                <exclusion>
                    <groupId>org.mortbay.jetty</groupId>
                    <artifactId>servlet-api</artifactId>
                </exclusion>
                <exclusion>
                    <groupId>org.eclipse.jetty</groupId>
                    <artifactId>jetty-server</artifactId>
                </exclusion>
                <exclusion>
                    <groupId>org.eclipse.jetty</groupId>
                    <artifactId>jetty-servlet</artifactId>
... (lines 347-412 omitted)
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
                <version>3.3.0</version>
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
                <artifactId>maven-failsafe-plugin</artifactId>
                <version>3.0.0-M7</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>integration-test</goal>
                            <goal>verify</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-shade-plugin</artifactId>
                <version>3.4.1</version>
                <configuration>
                    <outputFile>target/${project.artifactId}-${project.version}-allinone.jar</outputFile>
                    <filters>
                        <filter>
... (lines 466-474 omitted)
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
                                    <mainClass>uk.gov.pay.adminusers.app.AdminUsersApp</mainClass>
                                </transformer>
                            </transformers>
                        </configuration>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <groupId>org.codehaus.mojo</groupId>
                <artifactId>exec-maven-plugin</artifactId>
                <version>3.1.0</version>
                <configuration>
                    <mainClass>uk.gov.pay.adminusers.app.AdminUsersApp</mainClass>
                    <arguments>
                        <argument>server</argument>
                        <argument>src/main/resources/config/config.yaml</argument>
                    </arguments>
                </configuration>
            </plugin>
            <plugin>
                <groupId>io.swagger.core.v3</groupId>
                <artifactId>swagger-maven-plugin</artifactId>
                <version>${swaggger-version}</version>
                <configuration>
                    <outputPath>openapi</outputPath>
                    <outputFileName>adminusers_spec</outputFileName>
                    <outputFormat>YAML</outputFormat>
                    <configurationFilePath>${basedir}/src/main/resources/openapi-config.yaml</configurationFilePath>
                </configuration>
                <executions>
                    <execution>
                        <phase>compile</phase>
                        <goals>
                            <goal>resolve</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
```

### src/test/java/uk/gov/pay/adminusers/queue/event/EventMessageHandlerTest.java  (failing test)
```
package uk.gov.pay.adminusers.queue.event;

import ch.qos.logback.classic.Level;
import ch.qos.logback.classic.Logger;
import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.Appender;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.gson.GsonBuilder;
import org.hamcrest.core.Is;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Captor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.slf4j.LoggerFactory;
import uk.gov.pay.adminusers.client.ledger.model.LedgerTransaction;
import uk.gov.pay.adminusers.client.ledger.service.LedgerService;
import uk.gov.pay.adminusers.model.MerchantDetails;
import uk.gov.pay.adminusers.model.Service;
import uk.gov.pay.adminusers.model.ServiceName;
import uk.gov.pay.adminusers.persistence.entity.UserEntity;
import uk.gov.pay.adminusers.queue.model.Event;
import uk.gov.pay.adminusers.queue.model.EventMessage;
import uk.gov.pay.adminusers.queue.model.EventType;
import uk.gov.pay.adminusers.service.NotificationService;
import uk.gov.pay.adminusers.service.ServiceFinder;
import uk.gov.pay.adminusers.service.UserServices;
import uk.gov.service.payments.commons.queue.exception.QueueException;
import uk.gov.service.payments.commons.queue.model.QueueMessage;

import java.time.Instant;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;

import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.hasItems;
import static org.hamcrest.Matchers.is;
import static org.hamcrest.Matchers.nullValue;
import static org.mockito.ArgumentMatchers.anyMap;
import static org.mockito.ArgumentMatchers.anySet;
import static org.mockito.Mockito.atMostOnce;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static uk.gov.pay.adminusers.app.util.RandomIdGenerator.randomInt;
import static uk.gov.pay.adminusers.app.util.RandomIdGenerator.randomUuid;
import static uk.gov.pay.adminusers.fixtures.EventFixture.anEventFixture;
import static uk.gov.pay.adminusers.fixtures.LedgerTransactionFixture.aLedgerTransactionFixture;
import static uk.gov.pay.adminusers.model.Service.DEFAULT_NAME_VALUE;
import static uk.gov.pay.adminusers.service.UserServicesTest.aUserEntityWithRoleForService;

@ExtendWith(MockitoExtension.class)
class EventMessageHandlerTest {

    @Mock
    private EventSubscriberQueue mockEventSubscriberQueue;

    @Mock
    private NotificationService mockNotificationService;

    @Mock
    private ServiceFinder mockServiceFinder;

    @Mock
    private UserServices mockUserServices;

    @Mock
    private LedgerService mockLedgerService;

    @Captor
    ArgumentCaptor<Set<String>> adminEmailsCaptor;

    @Captor
    ArgumentCaptor<Map<String, String>> personalisationCaptor;
    @Mock
    private Appender<ILoggingEvent> mockLogAppender;
    @Captor
    ArgumentCaptor<ILoggingEvent> loggingEventArgumentCaptor;

    private final ObjectMapper objectMapper = new ObjectMapper();
    private final String gatewayAccountId = "123";

    private EventMessageHandler eventMessageHandler;
    private Service service;
    private LedgerTransaction transaction;
    private List<UserEntity> users;
    private Event disputeEvent;

    @BeforeEach
    void setUp() {
        eventMessageHandler = new EventMessageHandler(mockEventSubscriberQueue, mockLedgerService, mockNotificationService, mockServiceFinder, mockUserServices, objectMapper);
        service = Service.from(randomInt(), randomUuid(), new ServiceName(DEFAULT_NAME_VALUE));
        service.setMerchantDetails(new MerchantDetails("Organisation Name", null, null, null, null, null, null, null, null));
        transaction = aLedgerTransactionFixture()
                .withTransactionId("456")
                .withReference("tx ref")
                .build();
        users = Arrays.asList(
                aUserEntityWithRoleForService(service, true, "admin1"),
                aUserEntityWithRoleForService(service, true, "admin2")
        );

        Logger logger = (Logger) LoggerFactory.getLogger(EventMessageHandler.class);
        logger.setLevel(Level.INFO);
        logger.addAppender(mockLogAppender);
    }

    @Test
    void shouldMarkMessageAsProcessed() throws Exception {
        disputeEvent = anEventFixture()
                .withEventType(EventType.DISPUTE_CREATED.name())
                .withEventDetails(objectMapper.valueToTree(Map.of("amount", 21000L, "evidence_due_date", "2022-03-07T13:00:00.001Z", "gateway_account_id", gatewayAccountId)))
                .withParentResourceExternalId("456")
                .build();
        when(mockServiceFinder.byGatewayAccountId(gatewayAccountId)).thenReturn(Optional.of(service));
        when(mockLedgerService.getTransaction(transaction.getTransactionId())).thenReturn(Optional.of(transaction));
        when(mockUserServices.getAdminUsersForService(service.getId())).thenReturn(users);

        var mockQueueMessage = mock(QueueMessage.class);
        var eventMessage = EventMessage.of(disputeEvent, mockQueueMessage);
        when(mockEventSubscriberQueue.retrieveEvents()).thenReturn(List.of(eventMessage));

        eventMessageHandler.processMessages();

        verify(mockEventSubscriberQueue).markMessageAsProcessed(mockQueueMessage);
    }

    @Test
    void shouldHandleDisputeCreatedEvent() throws QueueException {
        var mockQueueMessage = mock(QueueMessage.class);
        disputeEvent = anEventFixture()
                .withEventType(EventType.DISPUTE_CREATED.name())
                .withEventDetails(objectMapper.valueToTree(Map.of("amount", 21000L, "evidence_due_date", "2022-03-07T13:00:00.001Z", "gateway_account_id", gatewayAccountId, "reason", "fraudulent")))
                .withParentResourceExternalId("456")
                .build();
        var eventMessage = EventMessage.of(disputeEvent, mockQueueMessage);
        when(mockQueueMessage.getMessageId()).thenReturn("queue-message-id");
        when(mockEventSubscriberQueue.retrieveEvents()).thenReturn(List.of(eventMessage));

        when(mockServiceFinder.byGatewayAccountId(gatewayAccountId)).thenReturn(Optional.of(service));
        when(mockLedgerService.getTransaction(transaction.getTransactionId())).thenReturn(Optional.of(transaction));
        when(mockUserServices.getAdminUsersForService(service.getId())).thenReturn(users);

        eventMessageHandler.processMessages();

        verify(mockNotificationService, atMostOnce()).sendStripeDisputeCreatedEmail(adminEmailsCaptor.capture(), personalisationCaptor.capture());

        var emails = adminEmailsCaptor.getValue();
        var personalisation = personalisationCaptor.getValue();

        assertThat(emails.size(), is(2));
        assertThat(emails, hasItems("admin1@service.gov.uk", "admin2@service.gov.uk"));
        assertThat(personalisation.get("serviceName"), is(service.getName()));
        assertThat(personalisation.get("paymentExternalId"), is("456"));
        assertThat(personalisation.get("serviceReference"), is("tx ref"));
        assertThat(personalisation.get("sendEvidenceToPayDueDate"), is("4 March 2022"));
        assertThat(personalisation.get("disputedAmount"), is("210.00"));

        assertThat(personalisation.get("fraudulent"), is("yes"));
        assertThat(personalisation.get("duplicate"), is("no"));
        assertThat(personalisation.get("credit_not_processed"), is("no"));
        assertThat(personalisation.get("product_not_received"), is("no"));
        assertThat(personalisation.get("product_unacceptable"), is("no"));
        assertThat(personalisation.get("subscription_canceled"), is("no"));
        assertThat(personalisation.get("unrecognized"), is("no"));
        assertThat(personalisation.get("paymentAmount"), is(nullValue()));
        assertThat(personalisation.get("disputeEvidenceDueDate"), is(nullValue()));

        verify(mockLogAppender, times(2)).doAppend(loggingEventArgumentCaptor.capture());

        List<ILoggingEvent> logStatement = loggingEventArgumentCaptor.getAllValues();
        assertThat(logStatement.get(0).getFormattedMessage(), Is.is("Retrieved event queue message with id [queue-message-id] for resource external id [a-resource-external-id]"));
        assertThat(logStatement.get(1).getFormattedMessage(), Is.is("Processed notification email for disputed transaction"));
    }

    @Test
    void shouldHandleDisputeLostEvent() throws QueueException {
        var mockQueueMessage = mock(QueueMessage.class);
        disputeEvent = anEventFixture()
                .withEventType(EventType.DISPUTE_LOST.name())
                .withEventDetails(objectMapper.valueToTree(Map.of("net_amount", -4000L, "fee", 1500L, "amount", 2500L, "gateway_account_id", gatewayAccountId)))
                .withParentResourceExternalId("456")
                .withServiceId(service.getExternalId())
                .withLive(true)
                .build();
        var eventMessage = EventMessage.of(disputeEvent, mockQueueMessage);
        when(mockQueueMessage.getMessageId()).thenReturn("queue-message-id");
        when(mockEventSubscriberQueue.retrieveEvents()).thenReturn(List.of(eventMessage));
        when(mockServiceFinder.byGatewayAccountId(gatewayAccountId)).thenReturn(Optional.of(service));
        when(mockLedgerService.getTransaction(transaction.getTransactionId())).thenReturn(Optional.of(transaction));
        when(mockUserServices.getAdminUsersForService(service.getId())).thenReturn(users);

        eventMessageHandler.processMessages();

        verify(mockNotificationService, atMostOnce()).sendStripeDisputeLostEmail(adminEmailsCaptor.capture(), personalisationCaptor.capture());

        var emails = adminEmailsCaptor.getValue();
        var personalisation = personalisationCaptor.getValue();

        assertThat(emails.size(), is(2));
        assertThat(emails, hasItems("admin1@service.gov.uk", "admin2@service.gov.uk"));
        assertThat(personalisation.get("serviceName"), is(service.getName()));
        assertThat(personalisation.get("serviceReference"), is("tx ref"));
        assertThat(personalisation.get("organisationName"), is(service.getMerchantDetails().getName()));

        verify(mockLogAppender, times(2)).doAppend(loggingEventArgumentCaptor.capture());

        List<ILoggingEvent> logStatement = loggingEventArgumentCaptor.getAllValues();
        assertThat(logStatement.get(0).getFormattedMessage(), Is.is("Retrieved event queue message with id [queue-message-id] for resource external id [a-resource-external-id]"));
        assertThat(logStatement.get(1).getFormattedMessage(), Is.is("Processed notification email for disputed transaction"));
    }

    @Test
    void shouldHandleDisputeWonEvent() throws QueueException {
        var mockQueueMessage = mock(QueueMessage.class);
        disputeEvent = anEventFixture()
                .withEventType(EventType.DISPUTE_WON.name())
                .withEventDetails(objectMapper.valueToTree(Map.of("gateway_account_id", gatewayAccountId)))
                .withParentResourceExternalId("456")
                .withServiceId(service.getExternalId())
                .withLive(true)
                .build();
        var eventMessage = EventMessage.of(disputeEvent, mockQueueMessage);
        when(mockQueueMessage.getMessageId()).thenReturn("queue-message-id");
        when(mockEventSubscriberQueue.retrieveEvents()).thenReturn(List.of(eventMessage));
        when(mockServiceFinder.byGatewayAccountId(gatewayAccountId)).thenReturn(Optional.of(service));
        when(mockLedgerService.getTransaction(transaction.getTransactionId())).thenReturn(Optional.of(transaction));
        when(mockUserServices.getAdminUsersForService(service.getId())).thenReturn(users);

        eventMessageHandler.processMessages();

        verify(mockNotificationService, atMostOnce()).sendStripeDisputeWonEmail(adminEmailsCaptor.capture(), personalisationCaptor.capture());

        var emails = adminEmailsCaptor.getValue();
        var personalisation = personalisationCaptor.getValue();

        assertThat(emails.size(), is(2));
        assertThat(emails, hasItems("admin1@service.gov.uk", "admin2@service.gov.uk"));
        assertThat(personalisation.get("serviceName"), is(service.getName()));
        assertThat(personalisation.get("serviceReference"), is("tx ref"));
        assertThat(personalisation.get("organisationName"), is(service.getMerchantDetails().getName()));

        verify(mockLogAppender, times(2)).doAppend(loggingEventArgumentCaptor.capture());

        List<ILoggingEvent> logStatement = loggingEventArgumentCaptor.getAllValues();
        assertThat(logStatement.get(0).getFormattedMessage(), Is.is("Retrieved event queue message with id [queue-message-id] for resource external id [a-resource-external-id]"));
        assertThat(logStatement.get(1).getFormattedMessage(), Is.is("Processed notification email for disputed transaction"));
    }

    @Test
    void shouldHandleDisputeEvidenceSubmittedEvent() throws QueueException {
        var mockQueueMessage = mock(QueueMessage.class);
        disputeEvent = anEventFixture()
                .withEventType(EventType.DISPUTE_EVIDENCE_SUBMITTED.name())
                .withEventDetails(objectMapper.valueToTree(Map.of("gateway_account_id", gatewayAccountId)))
                .withParentResourceExternalId("456")
                .withServiceId(service.getExternalId())
                .withLive(true)
                .build();
        var eventMessage = EventMessage.of(disputeEvent, mockQueueMessage);
        when(mockQueueMessage.getMessageId()).thenReturn("queue-message-id");
        when(mockEventSubscriberQueue.retrieveEvents()).thenReturn(List.of(eventMessage));
        when(mockServiceFinder.byGatewayAccountId(gatewayAccountId)).thenReturn(Optional.of(service));
        when(mockLedgerService.getTransaction(transaction.getTransactionId())).thenReturn(Optional.of(transaction));
        when(mockUserServices.getAdminUsersForService(service.getId())).thenReturn(users);

        eventMessageHandler.processMessages();

        verify(mockNotificationService, atMostOnce()).sendStripeDisputeEvidenceSubmittedEmail(adminEmailsCaptor.capture(), personalisationCaptor.capture());

        var emails = adminEmailsCaptor.getValue();
        var personalisation = personalisationCaptor.getValue();

        assertThat(emails.size(), is(2));
        assertThat(emails, hasItems("admin1@service.gov.uk", "admin2@service.gov.uk"));
        assertThat(personalisation.get("serviceName"), is(service.getName()));
        assertThat(personalisation.get("serviceReference"), is("tx ref"));
        assertThat(personalisation.get("organisationName"), is(service.getMerchantDetails().getName()));

        verify(mockLogAppender, times(2)).doAppend(loggingEventArgumentCaptor.capture());

        List<ILoggingEvent> logStatement = loggingEventArgumentCaptor.getAllValues();
        assertThat(logStatement.get(0).getFormattedMessage(), Is.is("Retrieved event queue message with id [queue-message-id] for resource external id [a-resource-external-id]"));
        assertThat(logStatement.get(1).getFormattedMessage(), Is.is("Processed notification email for disputed transaction"));
    }

    @Test
    void shouldNotCallNotificationServiceWhenServiceDoesNotExist() throws QueueException {
        var mockQueueMessage = mock(QueueMessage.class);
        disputeEvent = anEventFixture()
                .withEventType(EventType.DISPUTE_CREATED.name())
                .withEventDetails(objectMapper.valueToTree(Map.of("amount", 21000L, "fee", 1500L, "evidence_due_date", "2022-03-07T13:00:00Z", "gateway_account_id", gatewayAccountId)))
                .withParentResourceExternalId("456")
                .build();
        var eventMessage = EventMessage.of(disputeEvent, mockQueueMessage);
        when(mockEventSubscriberQueue.retrieveEvents()).thenReturn(List.of(eventMessage));
        when(mockServiceFinder.byGatewayAccountId(gatewayAccountId)).thenReturn(Optional.empty());

        eventMessageHandler.processMessages();

        verify(mockNotificationService, never()).sendStripeDisputeCreatedEmail(anySet(), anyMap());
    }

    @Test
    void shouldNotCallNotificationServiceWhenTransactionDoesNotExist() throws QueueException {
        var mockQueueMessage = mock(QueueMessage.class);
        disputeEvent = anEventFixture()
                .withEventType(EventType.DISPUTE_CREATED.name())
                .withEventDetails(objectMapper.valueToTree(Map.of("amount", 21000L, "fee", 1500L, "evidence_due_date", "2022-03-07T13:00:00.001Z", "gateway_account_id", gatewayAccountId)))
                .withParentResourceExternalId("456")
                .build();
        var eventMessage = EventMessage.of(disputeEvent, mockQueueMessage);
        when(mockEventSubscriberQueue.retrieveEvents()).thenReturn(List.of(eventMessage));
        when(mockServiceFinder.byGatewayAccountId(gatewayAccountId)).thenReturn(Optional.of(service));
        when(mockLedgerService.getTransaction(transaction.getTransactionId())).thenReturn(Optional.empty());

        eventMessageHandler.processMessages();

        verify(mockNotificationService, never()).sendStripeDisputeCreatedEmail(anySet(), anyMap());
    }

    @Test
    void shouldNotCallNotificationServiceWhenNoAdminUsersExist() throws QueueException {
        var mockQueueMessage = mock(QueueMessage.class);
        disputeEvent = anEventFixture()
                .withEventType(EventType.DISPUTE_CREATED.name())
                .withEventDetails(objectMapper.valueToTree(Map.of("amount", 21000L, "fee", 1500L, "evidence_due_date", "2022-03-07T13:00:00.001Z", "gateway_account_id", gatewayAccountId)))
                .withParentResourceExternalId("456")
                .build();
        var eventMessage = EventMessage.of(disputeEvent, mockQueueMessage);
        when(mockEventSubscriberQueue.retrieveEvents()).thenReturn(List.of(eventMessage));

        when(mockServiceFinder.byGatewayAccountId(gatewayAccountId)).thenReturn(Optional.of(service));
        when(mockLedgerService.getTransaction(transaction.getTransactionId())).thenReturn(Optional.of(transaction));
        when(mockUserServices.getAdminUsersForService(service.getId())).thenReturn(Collections.emptyList());

        eventMessageHandler.processMessages();

        verify(mockNotificationService, never()).sendStripeDisputeCreatedEmail(anySet(), anyMap());
    }
}
```

### src/test/java/uk/gov/pay/adminusers/unit/service/ServiceResourceFindTest.java  (failing test)
```
package uk.gov.pay.adminusers.unit.service;

import io.dropwizard.testing.junit5.DropwizardExtensionsSupport;
import io.dropwizard.testing.junit5.ResourceExtension;
import io.restassured.path.json.JsonPath;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;
import uk.gov.pay.adminusers.persistence.dao.ServiceDao;
import uk.gov.pay.adminusers.persistence.dao.UserDao;
import uk.gov.pay.adminusers.persistence.entity.GatewayAccountIdEntity;
import uk.gov.pay.adminusers.persistence.entity.MerchantDetailsEntity;
import uk.gov.pay.adminusers.persistence.entity.ServiceEntity;
import uk.gov.pay.adminusers.fixtures.ServiceEntityFixture;
import uk.gov.pay.adminusers.resources.GovUkPayAgreementRequestValidator;
import uk.gov.pay.adminusers.resources.ServiceRequestValidator;
import uk.gov.pay.adminusers.resources.ServiceResource;
import uk.gov.pay.adminusers.service.GovUkPayAgreementService;
import uk.gov.pay.adminusers.service.SendLiveAccountCreatedEmailService;
import uk.gov.pay.adminusers.service.ServiceFinder;
import uk.gov.pay.adminusers.service.ServiceServicesFactory;
import uk.gov.pay.adminusers.service.StripeAgreementService;
import uk.gov.pay.adminusers.validations.RequestValidations;
import uk.gov.service.payments.commons.model.SupportedLanguage;

import javax.ws.rs.core.Response;
import java.time.ZonedDateTime;
import java.util.Collections;
import java.util.Optional;

import static java.lang.String.format;
import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.hasKey;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.core.Is.is;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.mock;
import static uk.gov.pay.adminusers.app.util.RandomIdGenerator.randomUuid;

@ExtendWith(MockitoExtension.class)
@ExtendWith(DropwizardExtensionsSupport.class)
public class ServiceResourceFindTest extends ServiceResourceBaseTest {

    private static ServiceDao mockedServiceDao = mock(ServiceDao.class);
    private static UserDao mockedUserDao = mock(UserDao.class);

    private static ServiceServicesFactory mockedServicesFactory = mock(ServiceServicesFactory.class);

    private static ServiceFinder serviceFinder = new ServiceFinder(mockedServiceDao, LINKS_BUILDER);
    private static ServiceRequestValidator serviceRequestValidator = new ServiceRequestValidator(new RequestValidations(), null);
    private static StripeAgreementService stripeAgreementService = mock(StripeAgreementService.class);
    private static GovUkPayAgreementRequestValidator payAgreementRequestValidator = new GovUkPayAgreementRequestValidator(new RequestValidations());
    private static GovUkPayAgreementService agreementService = mock(GovUkPayAgreementService.class);
    private static SendLiveAccountCreatedEmailService sendLiveAccountCreatedEmailService = mock(SendLiveAccountCreatedEmailService.class);

    public static final ResourceExtension RESOURCES = ResourceExtension.builder()
            .addResource(new ServiceResource(
                    mockedUserDao,
                    mockedServiceDao,
                    LINKS_BUILDER,
                    serviceRequestValidator,
                    mockedServicesFactory,
                    stripeAgreementService,
                    payAgreementRequestValidator,
                    agreementService,
                    sendLiveAccountCreatedEmailService))
            .build();

    @BeforeEach
    public void setUp() {
        given(mockedServicesFactory.serviceFinder()).willReturn(serviceFinder);
    }

    @Test
    public void shouldGet_existingServiceById_withDefaultEnNameVariant() {
        String serviceExternalId = randomUuid();
        ServiceEntity serviceEntity = ServiceEntityFixture.aServiceEntity().withExternalId(serviceExternalId).build();
        given(mockedServiceDao.findByExternalId(serviceExternalId)).willReturn(Optional.of(serviceEntity));

        Response response = RESOURCES.target(format("/v1/api/services/%s", serviceExternalId)).request().get();

        assertThat(response.getStatus(), is(200));

        String body = response.readEntity(String.class);
        JsonPath json = JsonPath.from(body);

        assertThat(json.get("name"), is(serviceEntity.getServiceNames().get(SupportedLanguage.ENGLISH).getName()));
        assertEnServiceNameJson(serviceEntity.getServiceNames().get(SupportedLanguage.ENGLISH).getName(), json);
        assertThat(json.getMap("service_name"), not(hasKey("cy")));
        assertMerchantDetails(serviceEntity.getMerchantDetailsEntity(), json);
        assertLinks(serviceExternalId, json);
        assertThat(json.get("redirect_to_service_immediately_on_terminal_state"), is(serviceEntity.isRedirectToServiceImmediatelyOnTerminalState()));
        assertThat(json.get("collect_billing_address"), is(serviceEntity.isCollectBillingAddress()));
        assertThat(json.get("default_billing_address_country"), is(serviceEntity.getDefaultBillingAddressCountry()));
        assertThat(json.get("current_go_live_stage"), is(String.valueOf(serviceEntity.getCurrentGoLiveStage())));
    }

    @Test
    public void shouldGetServiceById_withServiceNameVariantForCy() {
        String serviceExternalId = randomUuid();
        ServiceEntity serviceEntity = ServiceEntityFixture.aServiceEntity()
                .withExternalId(serviceExternalId)
                .withServiceNameEntity(SupportedLanguage.WELSH, CY_SERVICE_NAME)
                .build();
        given(mockedServiceDao.findByExternalId(serviceExternalId)).willReturn(Optional.of(serviceEntity));
        Response response = RESOURCES.target(format("/v1/api/services/%s", serviceExternalId)).request().get();

        assertThat(response.getStatus(), is(200));
        String body = response.readEntity(String.class);
        JsonPath json = JsonPath.from(body);

        assertThat(json.get("name"), is(serviceEntity.getServiceNames().get(SupportedLanguage.ENGLISH).getName()));
        assertEnServiceNameJson(serviceEntity.getServiceNames().get(SupportedLanguage.ENGLISH).getName(), json);
        assertCyServiceNameJson(CY_SERVICE_NAME, json);
        assertMerchantDetails(serviceEntity.getMerchantDetailsEntity(), json);
        assertLinks(serviceExternalId, json);
    }

    @Test
    public void shouldGetServiceById_withServiceNameVariantsForEn_andCy() {
        String serviceExternalId = randomUuid();
        ServiceEntity serviceEntity = ServiceEntityFixture.aServiceEntity()
                .withExternalId(serviceExternalId)
                .withServiceNameEntity(SupportedLanguage.ENGLISH, EN_SERVICE_NAME)
                .withServiceNameEntity(SupportedLanguage.WELSH, CY_SERVICE_NAME)
                .build();
        given(mockedServiceDao.findByExternalId(serviceExternalId)).willReturn(Optional.of(serviceEntity));
        Response response = RESOURCES.target(format("/v1/api/services/%s", serviceExternalId)).request().get();

        assertThat(response.getStatus(), is(200));

        String body = response.readEntity(String.class);
        JsonPath json = JsonPath.from(body);

        assertThat(json.get("name"), is(EN_SERVICE_NAME));
        assertEnServiceNameJson(EN_SERVICE_NAME, json);
        assertCyServiceNameJson(CY_SERVICE_NAME, json);
        assertMerchantDetails(serviceEntity.getMerchantDetailsEntity(), json);
        assertLinks(serviceExternalId, json);
    }

    @Test
    public void shouldFind_existingServiceByGatewayAccountId() {
        GatewayAccountIdEntity gatewayAccountIdEntity = new GatewayAccountIdEntity();
        String gatewayAccountId = randomUuid();
        gatewayAccountIdEntity.setGatewayAccountId(gatewayAccountId);
        ServiceEntity serviceEntity = ServiceEntityFixture.aServiceEntity()
                .withGatewayAccounts(Collections.singletonList(gatewayAccountIdEntity))
                .withRedirectToServiceImmediatelyOnTerminalState(true)
                .withCreatedDate(ZonedDateTime.parse("2020-01-31T12:30:00Z"))
                .withWentLiveDate(ZonedDateTime.parse("2020-02-01T09:00:00Z"))
                .withSector("police")
                .build();
        gatewayAccountIdEntity.setService(serviceEntity);

        given(mockedServiceDao.findByGatewayAccountId(gatewayAccountId)).willReturn(Optional.of(serviceEntity));

        Response response = RESOURCES.target("/v1/api/services")
                .queryParam("gatewayAccountId", gatewayAccountId)
                .request().get();
        assertThat(response.getStatus(), is(200));

        String body = response.readEntity(String.class);
        JsonPath json = JsonPath.from(body);

        assertThat(json.get("name"), is(serviceEntity.getServiceNames().get(SupportedLanguage.ENGLISH).getName()));
        assertEnServiceNameJson(serviceEntity.getServiceNames().get(SupportedLanguage.ENGLISH).getName(), json);
        assertMerchantDetails(serviceEntity.getMerchantDetailsEntity(), json);
        assertLinks(serviceEntity.getExternalId(), json);
        assertThat(json.get("redirect_to_service_immediately_on_terminal_state"), is(serviceEntity.isRedirectToServiceImmediatelyOnTerminalState()));
        assertThat(json.get("collect_billing_address"), is(serviceEntity.isCollectBillingAddress()));
        assertThat(json.get("default_billing_address_country"), is(serviceEntity.getDefaultBillingAddressCountry()));
        assertThat(json.get("current_go_live_stage"), is(String.valueOf(serviceEntity.getCurrentGoLiveStage())));
        assertThat(json.get("created_date"), is("2020-01-31T12:30:00.000Z"));
        assertThat(json.get("went_live_date"), is("2020-02-01T09:00:00.000Z"));
        assertThat(json.get("sector"), is("police"));
        assertThat(json.get("internal"), is(false));
        assertThat(json.get("archived"), is(false));
    }

    @Test
    public void shouldReturn404_whenFindByGatewayAccountId_ifNotFound() {
        String gatewayAccountId = randomUuid();
        given(mockedServiceDao.findByGatewayAccountId(gatewayAccountId)).willReturn(Optional.empty());

        Response response = RESOURCES.target("/v1/api/services")
                .queryParam("gatewayAccountId", gatewayAccountId)
                .request().get();
        assertThat(response.getStatus(), is(404));
    }

    @Test
    public void shouldReturn404_whenGetServiceById_ifNotFound() {
        String externalId = randomUuid();
        given(mockedServiceDao.findByExternalId(externalId)).willReturn(Optional.empty());
        Response response = RESOURCES.target(format("/v1/api/services/%s", externalId)).request().get();
        assertThat(response.getStatus(), is(404));
    }

    @Test
    public void shouldReturnBadRequest_whenGetByGatewayAccountId_isMissingQueryParam() {
        Response response = RESOURCES.target("/v1/api/services")
                .queryParam("gatewayAccountId", "")
                .request().get();
        assertThat(response.getStatus(), is(400));
        String body = response.readEntity(String.class);
        JsonPath jsonPath = JsonPath.from(body);
        assertThat(jsonPath.getList("errors"), hasSize(1));
        assertThat(jsonPath.getList("errors").get(0), is("Find services currently support only by gatewayAccountId"));
    }

    private void assertMerchantDetails(MerchantDetailsEntity merchantDetails, JsonPath jsonPath) {
        assertThat(jsonPath.get("merchant_details.address_line1"), is(merchantDetails.getAddressLine1()));
        assertThat(jsonPath.get("merchant_details.address_line2"), is(merchantDetails.getAddressLine2()));
        assertThat(jsonPath.get("merchant_details.address_country"), is(merchantDetails.getAddressCountryCode()));
        assertThat(jsonPath.get("merchant_details.address_postcode"), is(merchantDetails.getAddressPostcode()));
        assertThat(jsonPath.get("merchant_details.address_city"), is(merchantDetails.getAddressCity()));
        assertThat(jsonPath.get("merchant_details.telephone_number"), is(merchantDetails.getTelephoneNumber()));
        assertThat(jsonPath.get("merchant_details.email"), is(merchantDetails.getEmail()));
        assertThat(jsonPath.get("merchant_details.name"), is(merchantDetails.getName()));
    }
}
```

### src/test/java/uk/gov/pay/adminusers/unit/service/ServiceResourceCreateTest.java  (failing test)
```
package uk.gov.pay.adminusers.unit.service;

import io.dropwizard.testing.junit5.DropwizardExtensionsSupport;
import io.dropwizard.testing.junit5.ResourceExtension;
import io.restassured.path.json.JsonPath;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Captor;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;
import uk.gov.pay.adminusers.model.Service;
import uk.gov.pay.adminusers.persistence.dao.UserDao;
import uk.gov.pay.adminusers.persistence.entity.ServiceEntity;
import uk.gov.pay.adminusers.persistence.entity.service.ServiceNameEntity;
import uk.gov.pay.adminusers.resources.GovUkPayAgreementRequestValidator;
import uk.gov.pay.adminusers.resources.ServiceRequestValidator;
import uk.gov.pay.adminusers.resources.ServiceResource;
import uk.gov.pay.adminusers.resources.ServiceUpdateOperationValidator;
import uk.gov.pay.adminusers.service.GovUkPayAgreementService;
import uk.gov.pay.adminusers.service.SendLiveAccountCreatedEmailService;
import uk.gov.pay.adminusers.service.ServiceCreator;
import uk.gov.pay.adminusers.service.ServiceServicesFactory;
import uk.gov.pay.adminusers.service.StripeAgreementService;
import uk.gov.pay.adminusers.validations.RequestValidations;
import uk.gov.service.payments.commons.model.SupportedLanguage;

import javax.ws.rs.client.Entity;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static org.hamcrest.CoreMatchers.not;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.containsInAnyOrder;
import static org.hamcrest.Matchers.hasKey;
import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.notNullValue;
import static org.hamcrest.core.Is.is;
import static org.mockito.ArgumentMatchers.anyList;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static uk.gov.pay.adminusers.resources.ServiceResource.FIELD_NAME;
import static uk.gov.pay.adminusers.resources.ServiceResource.SERVICES_RESOURCE;
import static uk.gov.pay.adminusers.service.ServiceUpdater.FIELD_GATEWAY_ACCOUNT_IDS;

@ExtendWith(DropwizardExtensionsSupport.class)
@ExtendWith(MockitoExtension.class)
public class ServiceResourceCreateTest extends ServiceResourceBaseTest {

    private static final Map<String, Object> PAYLOAD_MAP = new HashMap<>();

    private static UserDao mockedUserDao = mock(UserDao.class);
    private static ServiceServicesFactory mockedServicesFactory = mock(ServiceServicesFactory.class);

    private static ServiceCreator serviceCreator = new ServiceCreator(mockedServiceDao, LINKS_BUILDER);
    private static ServiceCreator mockedServiceCreator = mock(ServiceCreator.class);

    private static RequestValidations requestValidations = new RequestValidations();
    private static ServiceRequestValidator serviceRequestValidator = new ServiceRequestValidator(requestValidations, new ServiceUpdateOperationValidator(requestValidations));
    private static StripeAgreementService stripeAgreementService = mock(StripeAgreementService.class);
    private static GovUkPayAgreementRequestValidator payAgreementRequestValidator = new GovUkPayAgreementRequestValidator(requestValidations);
    private static GovUkPayAgreementService agreementService = mock(GovUkPayAgreementService.class);
    private static SendLiveAccountCreatedEmailService sendLiveAccountCreatedEmailService = mock(SendLiveAccountCreatedEmailService.class);

    public static final ResourceExtension RESOURCES = ResourceExtension.builder()
            .addResource(new ServiceResource(
                    mockedUserDao,
                    mockedServiceDao,
                    LINKS_BUILDER,
                    serviceRequestValidator,
                    mockedServicesFactory,
                    stripeAgreementService,
                    payAgreementRequestValidator,
                    agreementService,
                    sendLiveAccountCreatedEmailService))
            .build();

    @Captor
    private ArgumentCaptor<ServiceEntity> serviceEntityArgumentCaptor;

    @BeforeEach
    public void setUp() {
        given(mockedServicesFactory.serviceCreator()).willReturn(mockedServiceCreator);
    }

    @AfterEach
    public void tearDown() {
        Mockito.reset(mockedServiceDao);
        Mockito.reset(mockedServiceCreator);
        PAYLOAD_MAP.clear();
    }

    @Test
    public void shouldSuccess_whenCreateAServiceWithoutParameters() {
        Service service = buildService(Collections.emptyList(), Collections.emptyMap());
        given(mockedServiceCreator.doCreate(Collections.emptyList(), Collections.emptyMap()))
                .willReturn(service);
        Response response = RESOURCES.target(SERVICES_RESOURCE)
                .request(MediaType.APPLICATION_JSON)
                .post(Entity.json(PAYLOAD_MAP), Response.class);

        assertThat(response.getStatus(), is(201));

        String body = response.readEntity(String.class);
        JsonPath json = JsonPath.from(body);

        assertThat(json.get("name"), is("System Generated"));
        assertThat(json.get("external_id"), is(notNullValue()));
        assertThat(json.get("redirect_to_service_immediately_on_terminal_state"), is(false));
        assertThat(json.get("collect_billing_address"), is(true));
        assertThat(json.get("default_billing_address_country"), is("GB"));
        assertThat(json.getMap("service_name"), not(hasKey("cy")));
        assertEnServiceNameJson("System Generated", json);
        assertLinks(json.get("external_id"), json);
    }

    @Test
    public void shouldSuccess_whenCreateAServiceWithNameOnly() {
        PAYLOAD_MAP.put("service_name", Map.of(SupportedLanguage.ENGLISH.toString(), EN_SERVICE_NAME));

        Service service = buildService(Collections.emptyList(), Map.of(SupportedLanguage.ENGLISH, EN_SERVICE_NAME));
        given(mockedServiceCreator.doCreate(Collections.emptyList(), Map.of(SupportedLanguage.ENGLISH, EN_SERVICE_NAME)))
                .willReturn(service);
        Response response = RESOURCES.target(SERVICES_RESOURCE)
                .request(MediaType.APPLICATION_JSON)
                .post(Entity.json(PAYLOAD_MAP), Response.class);

        assertThat(response.getStatus(), is(201));

        String body = response.readEntity(String.class);
        JsonPath json = JsonPath.from(body);

        assertThat(json.get("external_id"), is(notNullValue()));
        assertThat(json.get("name"), is(EN_SERVICE_NAME));
        assertEnServiceNameJson(EN_SERVICE_NAME, json);
        assertThat(json.getMap("service_name"), not(hasKey("cy")));
        assertLinks(json.get("external_id"), json);
    }

    @Test
    public void shouldSuccess_whenCreateAServiceWithEnglishNameOnly() {
        PAYLOAD_MAP.put("service_name", Map.of(SupportedLanguage.ENGLISH.toString(), EN_SERVICE_NAME));

        Service service = buildService(Collections.emptyList(), Map.of(SupportedLanguage.ENGLISH, EN_SERVICE_NAME));
        given(mockedServiceCreator.doCreate(Collections.emptyList(), Map.of(SupportedLanguage.ENGLISH, EN_SERVICE_NAME)))
                .willReturn(service);
        Response response = RESOURCES.target(SERVICES_RESOURCE)
                .request(MediaType.APPLICATION_JSON)
                .post(Entity.json(PAYLOAD_MAP), Response.class);

        assertThat(response.getStatus(), is(201));

        String body = response.readEntity(String.class);
        JsonPath json = JsonPath.from(body);

        assertThat(json.get("external_id"), is(notNullValue()));
        assertThat(json.get("name"), is(EN_SERVICE_NAME));
        assertEnServiceNameJson(EN_SERVICE_NAME, json);
        assertThat(json.getMap("service_name"), not(hasKey("cy")));
        assertLinks(json.get("external_id"), json);
    }

    @Test
    public void shouldSuccess_whenCreateAServiceWithName_andGatewayAccountIds() {
        PAYLOAD_MAP.put("service_name", Map.of(SupportedLanguage.ENGLISH.toString(), EN_SERVICE_NAME));
        String anotherGatewayAccountId = "another-gateway-account-id";
        List<String> gatewayAccounts = Arrays.asList(GATEWAY_ACCOUNT_ID, anotherGatewayAccountId);
        PAYLOAD_MAP.put(FIELD_GATEWAY_ACCOUNT_IDS, gatewayAccounts);

        Service service = buildService(gatewayAccounts, Map.of(SupportedLanguage.ENGLISH, EN_SERVICE_NAME));
        given(mockedServiceCreator.doCreate(gatewayAccounts, Map.of(SupportedLanguage.ENGLISH, EN_SERVICE_NAME)))
                .willReturn(service);

        Response response = RESOURCES.target(SERVICES_RESOURCE)
                .request(MediaType.APPLICATION_JSON)
                .post(Entity.json(PAYLOAD_MAP), Response.class);
        assertThat(response.getStatus(), is(201));

        String body = response.readEntity(String.class);
        JsonPath json = JsonPath.from(body);

        assertThat(json.get("name"), is(EN_SERVICE_NAME));
        assertThat(json.get("external_id"), is(notNullValue()));
        assertEnServiceNameJson(EN_SERVICE_NAME, json);
        assertThat(json.getMap("service_name"), not(hasKey("cy")));
        assertLinks(json.get("external_id"), json);
    }

    @Test
    public void shouldSuccess_whenCreateAServiceWithEnglishName_andGatewayAccountIds() {
        PAYLOAD_MAP.put("service_name", Map.of(SupportedLanguage.ENGLISH.toString(), EN_SERVICE_NAME));
        String anotherGatewayAccountId = "another-gateway-account-id";
        List<String> gatewayAccounts = List.of(GATEWAY_ACCOUNT_ID, anotherGatewayAccountId);
        PAYLOAD_MAP.put(FIELD_GATEWAY_ACCOUNT_IDS, gatewayAccounts);

        Service service = buildService(gatewayAccounts, Map.of(SupportedLanguage.ENGLISH, EN_SERVICE_NAME));
        given(mockedServiceCreator.doCreate(gatewayAccounts, Map.of(SupportedLanguage.ENGLISH, EN_SERVICE_NAME)))
                .willReturn(service);

        Response response = RESOURCES.target(SERVICES_RESOURCE)
                .request(MediaType.APPLICATION_JSON)
                .post(Entity.json(PAYLOAD_MAP), Response.class);
        assertThat(response.getStatus(), is(201));

        String body = response.readEntity(String.class);
        JsonPath json = JsonPath.from(body);

        assertThat(json.get("name"), is(EN_SERVICE_NAME));
        assertThat(json.get("external_id"), is(notNullValue()));
        assertEnServiceNameJson(EN_SERVICE_NAME, json);
        assertThat(json.getMap("service_name"), not(hasKey("cy")));
        assertLinks(json.get("external_id"), json);
    }

    @Test
    public void shouldSuccess_whenCreateAServiceWithName_andGatewayAccountIds_andServiceNameVariants_engl
... (truncated: context budget reached)
```

### src/test/java/uk/gov/pay/adminusers/unit/service/ServiceResourceSearchTest.java  (failing test)
```

... (truncated: context budget reached)
```

### src/test/java/uk/gov/pay/adminusers/unit/service/ServiceResourceUpdateTest.java  (failing test)
```

... (truncated: context budget reached)
```

### src/main/resources/META-INF/persistence.xml  (resource file named in the failing test)
```

... (truncated: context budget reached)
```

### src/test/resources/fixtures/resource/service/patch/array-add-gateway-account-ids.json  (resource file named in the failing test)
```

... (truncated: context budget reached)
```

### src/test/resources/fixtures/resource/service/patch/array-missing-op-service-name-en.json  (resource file named in the failing test)
```

... (truncated: context budget reached)
```

### src/test/resources/fixtures/resource/service/patch/array-replace-missing-path.json  (resource file named in the failing test)
```

... (truncated: context budget reached)
```

### src/test/resources/fixtures/resource/service/patch/array-replace-service-name-cy-blank.json  (resource file named in the failing test)
```

... (truncated: context budget reached)
```

### src/test/resources/fixtures/resource/service/patch/array-replace-service-name-cy.json  (resource file named in the failing test)
```

... (truncated: context budget reached)
```


Now write the explanation and the single ```diff block.
