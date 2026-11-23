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
Failing test classes: com.feedzai.commons.sql.abstraction.engine.impl.abs.BatchUpdateTest, com.feedzai.commons.sql.abstraction.engine.impl.abs.EngineGeneralTest, com.feedzai.commons.sql.abstraction.engine.impl.abs.EngineCloseTest
Exception types: java.lang.ClassCastException
Error lines:
- java.lang.ClassCastException: class org.slf4j.helpers.NOPLogger cannot be cast to class ch.qos.logback.classic.Logger (org.slf4j.helpers.NOPLogger and ch.qos.logback.classic.Logger are in unnamed module of loader 'app')
SLF4J console output:
- SLF4J: No SLF4J providers were found.
- SLF4J: Defaulting to no-operation (NOP) logger implementation
- SLF4J: See https://www.slf4j.org/codes.html#noProviders for further details.
- SLF4J: Class path contains SLF4J bindings targeting slf4j-api versions 1.7.x or earlier.
- SLF4J: Ignoring binding found at [jar:file:/root/.m2/repository/ch/qos/logback/logback-classic/1.2.11/logback-classic-1.2.11.jar!/org/slf4j/impl/StaticLoggerBinder.class]
- SLF4J: See https://www.slf4j.org/codes.html#ignoredBindings for an explanation.
Project stack frames:
- com.feedzai.commons.sql.abstraction.engine.impl.abs.BatchUpdateTest (BatchUpdateTest.java:143)
- com.feedzai.commons.sql.abstraction.engine.impl.abs.EngineGeneralTest (EngineGeneralTest.java:181)
- com.feedzai.commons.sql.abstraction.engine.impl.abs.EngineCloseTest (EngineCloseTest.java:102)

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

### Past case 2: org.slf4j:slf4j-api 1.7.36 -> 2.0.4 (alphagov/pay-adminusers)
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

### Past case 3: org.slf4j:slf4j-api 1.7.36 -> 2.0.2 (s4u/sign-maven-plugin)
Symptom: java.lang.ClassCastException
  java.lang.ClassCastException: class org.slf4j.helpers.NOPLogger cannot be cast to class org.simplify4u.slf4jmock.ProxyMock (org.slf4j.helpers.NOPLogger and org.simplify4u.slf4jmock.ProxyMock are in unnamed module of loader 'app')
Behavior change: LoggerFactory returns NOPLogger instead of the slf4j-mock logger (provider selection)
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


## Project files (at the breaking commit)
### pom.xml  (build file (declares the updated dependency))
```
... (lines 0-0 omitted)
<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.feedzai</groupId>
    <artifactId>pdb</artifactId>
    <version>0.0.0-SNAPSHOT</version>
    <name>pdb</name>

    <parent>
        <groupId>org.sonatype.oss</groupId>
        <artifactId>oss-parent</artifactId>
        <version>9</version>
    </parent>

    <url>https://github.com/feedzai/pdb</url>
    <organization>
        <name>Feedzai</name>
        <url>http://www.feedzai.com</url>
    </organization>

    <scm>
        <connection>scm:git:git@github.com:feedzai/pdb.git</connection>
        <developerConnection>scm:git:git@github.com:feedzai/pdb.git</developerConnection>
        <url>git@github.com:feedzai/pdb.git</url>
        <tag>HEAD</tag>
    </scm>

    <licenses>
        <license>
            <name>The Apache Software License, Version 2.0</name>
            <url>http://www.apache.org/licenses/LICENSE-2.0.txt</url>
            <distribution>repo</distribution>
        </license>
    </licenses>

    <properties>
        <project.source>1.8</project.source>

        <default.test.cmdArgs>
            -javaagent:"${settings.localRepository}"/org/jmockit/jmockit/${jmockit.version}/jmockit-${jmockit.version}.jar
            -Djdk.attach.allowAttachSelf
        </default.test.cmdArgs>

        <jmockit.version>1.49</jmockit.version>

        <maven-source-plugin.version>3.2.1</maven-source-plugin.version>
        <maven-gpg-plugin.version>3.0.1</maven-gpg-plugin.version>
    </properties>

    <developers>
        <developer>
            <id>rpvilao</id>
            <name>Rui Vilao</name>
            <email>rui.vilao@feedzai.com</email>
        </developer>
    </developers>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>mysql</groupId>
                <artifactId>mysql-connector-java</artifactId>
                <version>5.1.49</version>
            </dependency>
            <dependency>
                <groupId>org.postgresql</groupId>
... (lines 67-78 omitted)
            </dependency>
            <dependency>
                <groupId>com.ibm.db2</groupId>
                <artifactId>jcc</artifactId>
                <version>11.5.8.0</version>
            </dependency>
            <dependency>
                <groupId>com.microsoft.sqlserver</groupId>
                <artifactId>mssql-jdbc</artifactId>
                <version>11.2.1.jre8</version>
            </dependency>
            <dependency>
                <groupId>org.jmockit</groupId>
                <artifactId>jmockit</artifactId>
                <version>${jmockit.version}</version>
            </dependency>
            <dependency>
                <groupId>junit</groupId>
                <artifactId>junit</artifactId>
                <version>4.13.2</version>
            </dependency>
            <dependency>
                <groupId>org.assertj</groupId>
                <artifactId>assertj-core</artifactId>
                <version>3.23.1</version>
            </dependency>
            <dependency>
                <groupId>org.awaitility</groupId>
                <artifactId>awaitility</artifactId>
                <version>4.2.0</version>
            </dependency>
            <dependency>
                <groupId>com.google.guava</groupId>
                <artifactId>guava</artifactId>
                <version>25.1-jre</version>
            </dependency>
            <dependency>
                <groupId>ch.qos.logback</groupId>
                <artifactId>logback-classic</artifactId>
                <version>1.2.11</version>
            </dependency>
            <dependency>
                <groupId>org.slf4j</groupId>
                <artifactId>slf4j-api</artifactId>
                <version>2.0.4</version>
            </dependency>
            <dependency>
                <groupId>org.apache.commons</groupId>
                <artifactId>commons-lang3</artifactId>
                <version>3.12.0</version>
            </dependency>
            <dependency>
                <groupId>commons-codec</groupId>
                <artifactId>commons-codec</artifactId>
                <version>1.15</version>
            </dependency>
... (lines 135-180 omitted)
            <groupId>com.microsoft.sqlserver</groupId>
            <artifactId>mssql-jdbc</artifactId>
            <scope>provided</scope>
        </dependency>
        <!-- IBM DB2 -->
        <dependency>
            <groupId>com.ibm.db2</groupId>
            <artifactId>jcc</artifactId>
            <scope>provided</scope>
        </dependency>
        <!-- JMockit -->
        <dependency>
            <groupId>org.jmockit</groupId>
            <artifactId>jmockit</artifactId>
            <scope>test</scope>
        </dependency>
        <!-- Junit + AssertJ -->
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.assertj</groupId>
            <artifactId>assertj-core</artifactId>
            <scope>test</scope>
        </dependency>
        <!-- Awaitility -->
        <dependency>
            <groupId>org.awaitility</groupId>
            <artifactId>awaitility</artifactId>
            <scope>test</scope>
        </dependency>
        <!-- Guava -->
        <dependency>
            <groupId>com.google.guava</groupId>
            <artifactId>guava</artifactId>
        </dependency>
        <!-- logback -->
        <dependency>
            <groupId>ch.qos.logback</groupId>
            <artifactId>logback-classic</artifactId>
            <scope>provided</scope>
        </dependency>
        <!-- SLF4J -->
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
        </dependency>
        <!-- Commons-lang 3 -->
        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-lang3</artifactId>
        </dependency>
        <!-- Commons-codec -->
        <dependency>
            <groupId>commons-codec</groupId>
            <artifactId>commons-codec</artifactId>
        </dependency>
        <!-- Guice -->
... (lines 241-280 omitted)
                    <artifactId>exec-maven-plugin</artifactId>
                    <version>3.1.0</version>
                </plugin>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-source-plugin</artifactId>
                    <version>${maven-source-plugin.version}</version>
                </plugin>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-javadoc-plugin</artifactId>
                    <version>3.4.1</version>
                    <configuration>
                        <tags>
                            <tag>
                                <name>apiNote</name>
                                <placement>a</placement>
                                <head>API Note:</head>
                            </tag>
                            <tag>
                                <name>implSpec</name>
                                <placement>a</placement>
                                <head>Implementation Requirements:</head>
                            </tag>
                            <tag>
                                <name>implNote</name>
                                <placement>a</placement>
                                <head>Implementation Note:</head>
                            </tag>
                        </tags>
                    </configuration>

                </plugin>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-deploy-plugin</artifactId>
                    <version>3.0.0</version>
                </plugin>
                <plugin>
                    <groupId>io.fabric8</groupId>
                    <artifactId>docker-maven-plugin</artifactId>
                    <version>0.40.2</version>
                    <executions>
... (lines 324-327 omitted)
                                <goal>stop</goal>
                                <goal>start</goal>
                            </goals>
                        </execution>
                        <execution>
                            <id>stop</id>
                            <phase>test</phase>
                            <goals>
                                <goal>stop</goal>
                            </goals>
                        </execution>
                    </executions>
                    <configuration>
                        <verbose>true</verbose>
                        <useColor>true</useColor>
                    </configuration>
                </plugin>
                <plugin>
                    <groupId>org.apache.maven.plugins</groupId>
                    <artifactId>maven-gpg-plugin</artifactId>
                    <version>${maven-gpg-plugin.version}</version>
                </plugin>
            </plugins>
        </pluginManagement>

        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <source>${project.source}</source>
                    <target>${project.source}</target>
                </configuration>
            </plugin>
            <!-- maven-surefire-plugin -->
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <configuration>
                    <!-- By default only run the H2 tests. -->
                    <failIfNoTests>false</failIfNoTests>
                    <systemProperties>
                        <instances>h2</instances>
                    </systemProperties>
                    <argLine>${default.test.cmdArgs}</argLine>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.codehaus.mojo</groupId>
                <artifactId>exec-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>com.mycila</groupId>
                <artifactId>license-maven-plugin</artifactId>
                <configuration>
                    <includes>
                        <include>src/main/**/*.java</include>
                        <include>src/test/**/*.java</include>
                    </includes>
                    <useDefaultExcludes>true</useDefaultExcludes>
                    <properties>
                        <year>2021</year>
                    </properties>
                    <mapping>
                        <java>SLASHSTAR_STYLE</java>
                    </mapping>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-release-plugin</artifactId>
                <configuration>
                    <localCheckout>true</localCheckout>
                    <pushChanges>false</pushChanges>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-source-plugin</artifactId>
                <executions>
                    <execution>
                        <id>attach-sources</id>
                        <phase>deploy</phase>
                        <goals>
                            <goal>jar</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-javadoc-plugin</artifactId>
                <configuration>
                    <doclint>none</doclint>
                </configuration>
                <executions>
                    <execution>
                        <id>attach-javadocs</id>
                        <phase>deploy</phase>
                        <goals>
                            <goal>jar</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
... (lines 435-465 omitted)
            <url>https://oss.sonatype.org/content/repositories/snapshots</url>
        </snapshotRepository>
    </distributionManagement>

    <profiles>
        <profile>
            <id>h2remote</id>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-surefire-plugin</artifactId>
                        <configuration>
                            <systemProperties>
                                <instances>h2remote</instances>
                            </systemProperties>
                        </configuration>
                    </plugin>

                    <plugin>
                        <groupId>org.codehaus.mojo</groupId>
                        <artifactId>exec-maven-plugin</artifactId>
                        <executions>
                            <execution>
                                <phase>test-compile</phase>
                                <goals>
                                    <goal>exec</goal>
                                </goals>
                            </execution>
                        </executions>
                        <configuration>
                            <executable>java</executable>
                            <!-- add test artifacts (UDFs) to server classpath -->
                            <classpathScope>test</classpathScope>
                            <arguments>
                                <argument>-classpath</argument>
                                <!-- automatically creates the classpath using all project dependencies,
                                     also adding the project build directory -->
                                <classpath />
                                <argument>org.h2.tools.Server</argument>
                                <!-- make db available via tcp -->
                                <argument>-tcp</argument>
                                <!-- set local file inside test output directory -->
                                <argument>-baseDir</argument>
                                <argument>${project.build.testOutputDirectory}/pdb-h2-remote</argument>
                                <!-- allows databases to be created when accessed -->
                                <argument>-ifNotExists</argument>
                            </arguments>
                            <async>true</async>
                            <asyncDestroyOnShutdown>true</asyncDestroyOnShutdown>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        </profile>

        <profile>
            <id>h2v2</id>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-surefire-plugin</artifactId>
                        <configuration>
                            <systemProperties>
                                <instances>h2v2</instances>
                            </systemProperties>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        </profile>

        <profile>
            <id>h2v2remote</id>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-surefire-plugin</artifactId>
                        <configuration>
                            <systemProperties>
                                <instances>h2v2remote</instances>
                            </systemProperties>
                        </configuration>
                    </plugin>

                    <plugin>
                        <groupId>org.codehaus.mojo</groupId>
                        <artifactId>exec-maven-plugin</artifactId>
                        <executions>
                            <execution>
                                <phase>test-compile</phase>
                                <goals>
                                    <goal>exec</goal>
                                </goals>
                            </execution>
                        </executions>
                        <configuration>
                            <executable>java</executable>
                            <!-- add test artifacts (UDFs) to server classpath -->
                            <classpathScope>test</classpathScope>
                            <arguments>
                                <argument>-classpath</argument>
                                <!-- automatically creates the classpath using all project dependencies,
                                     also adding the project build directory -->
                                <classpath />
                                <argument>org.h2.tools.Server</argument>
                                <!-- make db available via tcp -->
                                <argument>-tcp</argument>
                                <!-- use port 9093, different from the one used in h2remote profile (the default 9092) -->
                                <argument>-tcpPort</argument>
                                <argument>9093</argument>
                                <!-- set local file inside test output directory -->
                                <argument>-baseDir</argument>
                                <argument>${project.build.testOutputDirectory}/pdb-h2v2-remote</argument>
                                <!-- allows databases to be created when accessed -->
                                <argument>-ifNotExists</argument>
                            </arguments>
                            <async>true</async>
                            <asyncDestroyOnShutdown>true</asyncDestroyOnShutdown>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        </profile>

        <profile>
            <id>mysql</id>
            <properties>
                <image.mysql>mysql:5.7.22</image.mysql>
            </properties>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-surefire-plugin</artifactId>
                        <configuration>
                            <systemProperties>
                                <instances>mysql</instances>
                            </systemProperties>
                        </configuration>
                    </plugin>

                    <plugin>
                        <groupId>io.fabric8</groupId>
                        <artifactId>docker-maven-plugin</artifactId>
                        <configuration>
                            <images>
                                <image>
                                    <name>${image.mysql}</name>
                                    <alias>pdb-mysql</alias>
                                    <run>
                                        <namingStrategy>alias</namingStrategy>
                                        <hostname>pdb-mysql</hostname>
                                        <ports>
                                            <port>3306:3306</port>
                                        </ports>
                                        <env>
                                            <MYSQL_ROOT_PASSWORD>AaBb12.#</MYSQL_ROOT_PASSWORD>
                                        </env>
                                        <cmd>--max-allowed-packet=16000000 --innodb-log-file-size=160000000</cmd>
                                        <wait>
                                            <time>40000</time>
                                            <log>MySQL init process done. Ready for start up.</log>
                                        </wait>
                                    </run>
                                </image>
                            </images>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        </profile>

        <profile>
            <id>sqlserver</id>
            <properties>
                <image.sqlserver>mcr.microsoft.com/mssql/server:2019-CU15-ubuntu-20.04</image.sqlserver>
            </properties>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-surefire-plugin</artifactId>
                        <configuration>
                            <systemProperties>
                                <instances>sqlserver</instances>
                            </systemProperties>
                        </configuration>
                    </plugin>

                    <plugin>
                        <groupId>io.fabric8</groupId>
                        <artifactId>docker-maven-plugin</artifactId>
                        <configuration>
                            <images>
                                <image>
                                    <name>${image.sqlserver}</name>
                                    <alias>pdb-sqlserver</alias>
                                    <run>
                                        <namingStrategy>alias</namingStrategy>
                                        <hostname>pdb-sqlserver</hostname>
                                        <ports>
                                            <port>1433:1433</port>
                                        </ports>
                                        <env>
                                            <ACCEPT_EULA>Y</ACCEPT_EULA>
                                            <SA_PASSWORD>AaBb12.#</SA_PASSWORD>
                                        </env>
                                        <wait>
                                            <time>40000</time>
                                            <log>Service Broker manager has started</log>
                                            <exec>
                                                <!--
                                                Prepare a new "pdb" database for tests with READ_COMMITTED_SNAPSHOT enabled
                                                 (required for SQL server to have the same behavior as other DBs in READ_COMMITTED
                                                 isolation level) and ALLOW_SNAPSHOT_ISOLATION enabled to allow using the
                                                 TRANSACTION_SNAPSHOT level (equivalent to SERIALIZABLE in PostgreSQL and Oracle).
                                                A new database needs to be used because the flags can't be enabled on "master" database.
                                                -->
                                                <postStart>/opt/mssql-tools/bin/sqlcmd -l 45 -U sa -P AaBb12.# -Q CREATE\ DATABASE\ pdb;\ ALTER\ DATABASE\ pdb\ SET\ READ_COMMITTED_SNAPSHOT\ ON;\ ALTER\ DATABASE\ pdb\ SET\ ALLOW_SNAPSHOT_ISOLATION\ ON</postStart>
                                            </exec>
                                        </wait>
                                    </run>
                                </image>
                            </images>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        </profile>

        <profile>
            <id>postgresql</id>
            <properties>
                <image.postgresql>postgres:12.3</image.postgresql>
            </properties>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-surefire-plugin</artifactId>
                        <configuration>
                            <systemProperties>
                                <instances>postgresql</instances>
                            </systemProperties>
                        </configuration>
                    </plugin>

                    <plugin>
                        <groupId>io.fabric8</groupId>
                        <artifactId>docker-maven-plugin</artifactId>
                        <configuration>
                            <images>
                                <image>
                                    <name>${image.postgresql}</name>
                                    <alias>pdb-postgresql</alias>
                                    <run>
                                        <namingStrategy>alias</namingStrategy>
                                        <hostname>pdb-postgresql</hostname>
                                        <ports>
                                            <port>5432:5432</port>
                                        </ports>
                                        <env>
                                            <POSTGRES_PASSWORD>AaBb12.#</POSTGRES_PASSWORD>
                                        </env>
                                        <wait>
                                            <time>40000</time>
                                            <log>PostgreSQL init process complete; ready for start up</log>
                                        </wait>
                                    </run>
                                </image>
                            </images>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        </profile>

        <profile>
            <id>cockroach</id>
            <properties>
                <image.cockroach>cockroachdb/cockroach:v21.2.5</image.cockroach>
            </properties>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-surefire-plugin</artifactId>
                        <configuration>
                            <systemProperties>
                                <instances>cockroach</instances>
                            </systemProperties>
                            <excludedGroups>com.feedzai.commons.sql.abstraction.engine.impl.cockroach.SkipTestCockroachDB</excludedGroups>
                        </configuration>
                    </plugin>

                    <plugin>
                        <groupId>io.fabric8</groupId>
                        <artifactId>docker-maven-plugin</artifactId>
                        <configuration>
                            <images>
                                <image>
                                    <name>${image.cockroach}</name>
                                    <alias>pdb-cockroach</alias>
                                    <run>
                                        <namingStrategy>alias</namingStrategy>
                                        <hostname>pdb-cockroach</hostname>
                                        <ports>
                                            <port>8080:8080</port>
                                            <port>26257:26257</port>
                                        </ports>
                                        <cmd>start-single-node --insecure</cmd>
                                        <wait>
                                            <time>40000</time>
                                            <log>CockroachDB node starting</log>
                                        </wait>
                                    </run>
                                </image>
                            </images>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        </profile>

        <profile>
            <id>oracle</id>
            <properties>
                <image.oracle>iatebes/oracle_11g:latest</image.oracle>
            </properties>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-surefire-plugin</artifactId>
                        <configuration>
                            <!--
                             The following line is a workaround for "ORA-01882: timezone region not found"
                             that occurs when the Oracle DB server doesn't have the system timezone
                             -->
                            <argLine>${default.test.cmdArgs} -Doracle.jdbc.timezoneAsRegion=false</argLine>
                            <systemProperties>
                                <instances>oracle</instances>
                            </systemProperties>
                        </configuration>
                    </plugin>

                    <plugin>
                        <groupId>io.fabric8</groupId>
                        <artifactId>docker-maven-plugin</artifactId>
                        <configuration>
                            <images>
                                <image>
                                    <name>${image.oracle}</name>
                                    <alias>pdb-oracle</alias>
                                    <run>
                                        <namingStrategy>alias</namingStrategy>
                                        <hostname>pdb-oracle</hostname>
                                        <ports>
                                            <port>1521:1521</port>
                                        </ports>
                                        <wait>
                                            <time>360000</time>
                                            <log>Disconnected from Oracle Database 11g</log>
                                        </wait>
                                    </run>
                                </image>
                            </images>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        </profile>

        <profile>
            <id>db2</id>
            <properties>
                <image.db2>ibmcom/db2:11.5.7.0a</image.db2>
            </properties>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-surefire-plugin</artifactId>
                        <configuration>
                            <systemProperties>
                                <instances>db2</instances>
                            </systemProperties>
                        </configuration>
                    </plugin>

                    <plugin>
                        <groupId>io.fabric8</groupId>
                        <artifactId>docker-maven-plugin</artifactId>
                        <configuration>
                            <images>
                                <image>
                                    <name>${image.db2}</name>
                                    <alias>pdb-db2</alias>
                                    <run>
                                        <namingStrategy>alias</namingStrategy>
                                        <hostname>pdb-db2</hostname>
                                        <ports>
                                            <port>50000:50000</port>
                                        </ports>
                                        <capAdd>IPC_LOCK,IPC_OWNER</capAdd>
                                        <env>
... (lines 875-877 omitted)
                                            <ARCHIVE_LOGS>false</ARCHIVE_LOGS>
                                            <AUTOCONFIG>false</AUTOCONFIG>
                                            <SAMPLEDB>false</SAMPLEDB>
                                            <HADR_ENABLED>false</HADR_ENABLED>
                                        </env>
                                        <wait>
                                            <time>360000</time>
                                            <log>Setup has completed.</log>
                                        </wait>
                                    </run>
                                </image>
                            </images>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        </profile>

        <!-- Profile to compile and run tests with JDK 11 -->
        <profile>
            <id>java-11</id>
            <activation>
                <jdk>11</jdk>
            </activation>
            <properties>
                <project.source>11</project.source>
            </properties>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-compiler-plugin</artifactId>
                        <configuration>
                            <release>${project.source}</release>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        </profile>

        <!-- Profile to compile and run tests with JDK 17 -->
        <profile>
            <id>java-17</id>
            <activation>
                <jdk>17</jdk>
            </activation>
            <properties>
                <project.source>17</project.source>
            </properties>
            <build>
                <plugins>
                    <plugin>
                        <groupId>org.apache.maven.plugins</groupId>
                        <artifactId>maven-compiler-plugin</artifactId>
                        <configuration>
                            <release>${project.source}</release>
                        </configuration>
                    </plugin>
                </plugins>
            </build>
        </profile>
    </profiles>
</project>
```

### src/test/java/com/feedzai/commons/sql/abstraction/engine/impl/abs/BatchUpdateTest.java  (failing test)
```
... (lines 0-0 omitted)
/*
 * Copyright 2014 Feedzai
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
package com.feedzai.commons.sql.abstraction.engine.impl.abs;

import ch.qos.logback.classic.Level;
import ch.qos.logback.classic.Logger;
import com.feedzai.commons.sql.abstraction.batch.AbstractBatch;
import com.feedzai.commons.sql.abstraction.batch.AbstractBatchConfig;
import com.feedzai.commons.sql.abstraction.batch.BatchEntry;
import com.feedzai.commons.sql.abstraction.batch.PdbBatch;
import com.feedzai.commons.sql.abstraction.batch.impl.DefaultBatch;
import com.feedzai.commons.sql.abstraction.batch.impl.DefaultBatchConfig;
import com.feedzai.commons.sql.abstraction.batch.impl.MultithreadedBatchConfig;
import com.feedzai.commons.sql.abstraction.ddl.DbEntity;
import com.feedzai.commons.sql.abstraction.dml.result.ResultColumn;
import com.feedzai.commons.sql.abstraction.engine.AbstractDatabaseEngine;
import com.feedzai.commons.sql.abstraction.engine.DatabaseEngine;
import com.feedzai.commons.sql.abstraction.engine.DatabaseEngineException;
import com.feedzai.commons.sql.abstraction.engine.DatabaseEngineRuntimeException;
import com.feedzai.commons.sql.abstraction.engine.DatabaseFactory;
import com.feedzai.commons.sql.abstraction.engine.DatabaseFactoryException;
import com.feedzai.commons.sql.abstraction.engine.testconfig.DatabaseConfiguration;
import com.feedzai.commons.sql.abstraction.engine.testconfig.DatabaseTestUtil;
import com.feedzai.commons.sql.abstraction.entry.EntityEntry;
import com.feedzai.commons.sql.abstraction.listeners.BatchListener;
import com.feedzai.commons.sql.abstraction.listeners.MetricsListener;
import com.google.common.collect.ImmutableList;
... (lines 41-102 omitted)
/**
 * Tests for {@link PdbBatch} implementations.
 *
 * @author Paulo Leitao (paulo.leitao@feedzai.com)
 * @since 2.1.4
 */
@RunWith(Parameterized.class)
public class BatchUpdateTest {

    protected DatabaseEngine engine;
    protected Properties properties;

    /**
     * The {@link PdbBatch} used in each test (extracted to a field so that it can be closed after the test).
     */
    protected PdbBatch batch;

    @Parameterized.Parameters
    public static List<Object[]> data() throws Exception {
        final Set<DatabaseConfiguration> databaseConfigurations = new HashSet<>(DatabaseTestUtil.loadConfigurations());
        final Set<Supplier<AbstractBatchConfig.Builder<?, ?, ?>>> batchConfigs = ImmutableSet.of(
                DefaultBatchConfig::builder,
                MultithreadedBatchConfig::builder,
                () -> MultithreadedBatchConfig.builder().withNumberOfThreads(3)
        );

        return Sets.cartesianProduct(databaseConfigurations, batchConfigs)
                .stream()
                .map(List::toArray)
                .collect(Collectors.toList());
    }

    @Parameterized.Parameter
    public DatabaseConfiguration dbConfig;

    @Parameterized.Parameter(1)
    public Supplier<AbstractBatchConfig.Builder<?, ?, ?>> batchConfigBuilderSupplier;

    @BeforeClass
    public static void initStatic() {
        ((Logger) LoggerFactory.getLogger(Logger.ROOT_LOGGER_NAME)).setLevel(Level.TRACE);
    }

    @Before
    public void init() throws DatabaseFactoryException {
        properties = new Properties() {

            {
                setProperty(JDBC, dbConfig.jdbc);
                setProperty(USERNAME, dbConfig.username);
                setProperty(PASSWORD, dbConfig.password);
                setProperty(ENGINE, dbConfig.engine);
                setProperty(SCHEMA_POLICY, "drop-create");
                setProperty(MAX_NUMBER_OF_RETRIES, "5");
                setProperty(RETRY_INTERVAL, "1000");
            }
        };

        engine = DatabaseFactory.getConnection(properties);
    }

    @After
    public void cleanup() throws Exception {
        engine.close();
        if (batch != null) {
            batch.close();
        }
    }

    /**
     * Checks that after creating a batch the connection is still usable.
     * <p>
     * This is a regression test for some issues that were detected previously after batch creation (see test comments).
     */
    @Test
    public void createBatchLeavesUsableConnectionTest() throws Exception {
        final AbstractBatchConfig<?, ?> batchConfig = batchConfigBuilderSupplier.get()
                .withName("createBatchLeavesUsableConnectionTest")
                .withMaxAwaitTimeShutdown(Duration.ofSeconds(10))
                .build();
```

### src/test/java/com/feedzai/commons/sql/abstraction/engine/impl/abs/EngineGeneralTest.java  (failing test)
```
... (lines 0-0 omitted)
/*
 * Copyright 2014 Feedzai
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
package com.feedzai.commons.sql.abstraction.engine.impl.abs;

import ch.qos.logback.classic.Level;
import ch.qos.logback.classic.Logger;
import com.feedzai.commons.sql.abstraction.ddl.AlterColumn;
import com.feedzai.commons.sql.abstraction.ddl.DbColumn;
import com.feedzai.commons.sql.abstraction.ddl.DbColumnConstraint;
import com.feedzai.commons.sql.abstraction.ddl.DbColumnType;
import com.feedzai.commons.sql.abstraction.ddl.DbEntity;
import com.feedzai.commons.sql.abstraction.ddl.Rename;
import com.feedzai.commons.sql.abstraction.dml.Expression;
import com.feedzai.commons.sql.abstraction.dml.K;
import com.feedzai.commons.sql.abstraction.dml.Query;
import com.feedzai.commons.sql.abstraction.dml.Truncate;
import com.feedzai.commons.sql.abstraction.dml.Update;
import com.feedzai.commons.sql.abstraction.dml.Values;
import com.feedzai.commons.sql.abstraction.dml.With;
import com.feedzai.commons.sql.abstraction.dml.dialect.Dialect;
import com.feedzai.commons.sql.abstraction.dml.dialect.SqlBuilder;
import com.feedzai.commons.sql.abstraction.dml.result.ResultColumn;
import com.feedzai.commons.sql.abstraction.dml.result.ResultIterator;
import com.feedzai.commons.sql.abstraction.engine.AbstractDatabaseEngine;
import com.feedzai.commons.sql.abstraction.engine.ConnectionResetException;
import com.feedzai.commons.sql.abstraction.engine.DatabaseEngine;
import com.feedzai.commons.sql.abstraction.engine.DatabaseEngineException;
... (lines 41-140 omitted)
import static com.feedzai.commons.sql.abstraction.engine.configuration.PdbProperties.JDBC;
import static com.feedzai.commons.sql.abstraction.engine.configuration.PdbProperties.PASSWORD;
import static com.feedzai.commons.sql.abstraction.engine.configuration.PdbProperties.SCHEMA_POLICY;
import static com.feedzai.commons.sql.abstraction.engine.configuration.PdbProperties.USERNAME;
import static com.feedzai.commons.sql.abstraction.util.StringUtils.quotize;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatCode;
import static org.junit.Assert.assertArrayEquals;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertNull;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;
import static org.junit.Assume.assumeFalse;
import static org.junit.Assume.assumeTrue;

/**
 * @author Rui Vilao (rui.vilao@feedzai.com)
 * @since 2.0.0
 */
@RunWith(Parameterized.class)
public class EngineGeneralTest {


    private static final double DELTA = 1e-7;

    protected DatabaseEngine engine;
    protected Properties properties;

    @Parameterized.Parameters
    public static Collection<DatabaseConfiguration> data() throws Exception {
        return DatabaseTestUtil.loadConfigurations();
    }

    @Parameterized.Parameter
    public DatabaseConfiguration config;

    @BeforeClass
    public static void initStatic() {
        ((Logger) LoggerFactory.getLogger(Logger.ROOT_LOGGER_NAME)).setLevel(Level.TRACE);
    }

    @Before
    public void init() throws DatabaseFactoryException {
        properties = new Properties() {
            {
                setProperty(JDBC, config.jdbc);
                setProperty(USERNAME, config.username);
                setProperty(PASSWORD, config.password);
                setProperty(ENGINE, config.engine);
                setProperty(SCHEMA_POLICY, "drop-create");
            }
        };

        engine = DatabaseFactory.getConnection(properties);
    }

    @After
    public void cleanup() {
        engine.close();
    }

    @Test
    public void createEntityTest() throws DatabaseEngineException {

        DbEntity entity = dbEntity()
                .name("TEST")
                .addColumn("COL1", INT)
                .addColumn("COL2", BOOLEAN)
                .addColumn("COL3", DOUBLE)
                .addColumn("COL4", LONG)
                .addColumn("COL5", STRING)
                .pkFields("COL1")
                .build();

        engine.addEntity(entity);
    }

    @Test
    public void createEntityWithTwoColumnsBeingPKTest() throws DatabaseEngineException {
```

### src/test/java/com/feedzai/commons/sql/abstraction/engine/impl/abs/EngineCloseTest.java  (failing test)
```
/*
 * Copyright 2018 Feedzai
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
package com.feedzai.commons.sql.abstraction.engine.impl.abs;

import ch.qos.logback.classic.Level;
import ch.qos.logback.classic.Logger;
import com.feedzai.commons.sql.abstraction.ddl.DbEntity;
import com.feedzai.commons.sql.abstraction.engine.AbstractDatabaseEngine;
import com.feedzai.commons.sql.abstraction.engine.DatabaseEngine;
import com.feedzai.commons.sql.abstraction.engine.DatabaseEngineException;
import com.feedzai.commons.sql.abstraction.engine.DatabaseFactory;
import com.feedzai.commons.sql.abstraction.engine.DatabaseFactoryException;
import com.feedzai.commons.sql.abstraction.engine.NameAlreadyExistsException;
import com.feedzai.commons.sql.abstraction.engine.testconfig.DatabaseConfiguration;
import com.feedzai.commons.sql.abstraction.engine.testconfig.DatabaseTestUtil;
import mockit.Capturing;
import mockit.Expectations;
import mockit.Mock;
import mockit.MockUp;
import mockit.Verifications;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.Parameterized;
import org.slf4j.LoggerFactory;

import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Properties;

import static com.feedzai.commons.sql.abstraction.engine.EngineTestUtils.buildEntity;
import static com.feedzai.commons.sql.abstraction.engine.configuration.PdbProperties.ENGINE;
import static com.feedzai.commons.sql.abstraction.engine.configuration.PdbProperties.JDBC;
import static com.feedzai.commons.sql.abstraction.engine.configuration.PdbProperties.PASSWORD;
import static com.feedzai.commons.sql.abstraction.engine.configuration.PdbProperties.SCHEMA_POLICY;
import static com.feedzai.commons.sql.abstraction.engine.configuration.PdbProperties.USERNAME;


/**
 * Tests closing a {@link DatabaseEngine} to make sure all resources are cleaned up correctly.
 *
 * It tests with each schema policy.
 *
 * @author David Fialho (david.fialho@feedzai.com)
 * @since 2.1.13
 */
@RunWith(Parameterized.class)
public class EngineCloseTest {

    protected DatabaseEngine engine;
    protected Properties properties;

    // Parameters
    protected DatabaseConfiguration config;
    protected String schemaPolicy;

    @Parameterized.Parameters
    public static Collection<Object[]> data() throws Exception {

        final Collection<DatabaseConfiguration> configurations = DatabaseTestUtil.loadConfigurations();
        final Collection<String> schemaPolicies = Arrays.asList(
                "drop-create",
                "create-drop",
                "create",
                "none"
        );

        final ArrayList<Object[]> data = new ArrayList<>();
        for (final DatabaseConfiguration configuration : configurations) {
            for (final String schemaPolicy : schemaPolicies) {
                data.add(new Object[]{configuration, schemaPolicy});
            }
        }

        return data;
    }

    public EngineCloseTest(final DatabaseConfiguration config, final String schemaPolicy) {
        this.config = config;
        this.schemaPolicy = schemaPolicy;
    }

    @BeforeClass
    public static void initStatic() {
        ((Logger) LoggerFactory.getLogger(Logger.ROOT_LOGGER_NAME)).setLevel(Level.TRACE);
    }

    @Before
    public void setUp() throws DatabaseFactoryException {
        properties = new Properties() {{
            setProperty(JDBC, config.jdbc);
            setProperty(USERNAME, config.username);
            setProperty(PASSWORD, config.password);
            setProperty(ENGINE, config.engine);
            setProperty(SCHEMA_POLICY, schemaPolicy);
        }};

        engine = DatabaseFactory.getConnection(properties);
    }

    /**
     * Test that closing a database engine with multiple entities closes all insert statements associated with each
     * entity, regardless of the schema policy used.
     *
     * Each entity is associated with 3 prepared statements. This test ensures that 3 PSs per entity are closed.
     *
     * @param preparedStatementMock       The mock to check number of closed prepared statements.
     * @throws DatabaseEngineException    If something goes wrong while adding an entity to the engine.
     * @throws SQLException               If an error occurs while closing the DB engine.
     * @throws NameAlreadyExistsException If trying to create two statements with the same name.
     * @since 2.1.13
     */
    @Test
    public void closingAnEngineShouldFlushAndCloseInsertPSsAndCloseCachedPSs(@Capturing final Statement preparedStatementMock)
            throws DatabaseEngineException, SQLException, NameAlreadyExistsException {

        engine.addEntity(buildEntity("ENTITY-1"));
        engine.addEntity(buildEntity("ENTITY-2"));
        engine.createPreparedStatement("PS-1", "SELECT * FROM ENTITY-1");
        engine.createPreparedStatement("PS-2", "SELECT * FROM ENTITY-2");

        // Prevent the temporary statements, created while dropping entities, from affecting the
        // number of close() invocations
        new MockUp<AbstractDatabaseEngine>() {
            @Mock
            void dropEntity(final DbEntity entity) { }
        };

        // Force invocation counting to start here
        new Expectations() {{ }};

        engine.close();

        new Verifications() {{
            preparedStatementMock.close(); times = 2 * 3 + 2;   // {2 entities} x {PSs per entity} + {cached PSs}
            preparedStatementMock.executeBatch(); times = 2 * 3;   // {2 entities} x {PSs per entity}
        }};

    }

}
```

### src/test/resources/connections.properties  (resource file named in the failing test)
```
# default databases/schemas commented

###############################################################################################
# IMPORTANT!
# the ports specified in the JDBC URLs are the default ones and are used by the Timeouts test
###############################################################################################

h2.engine=com.feedzai.commons.sql.abstraction.engine.impl.H2Engine
h2.jdbc=jdbc:h2:./target/pdb_h2;AUTO_SERVER=FALSE
h2.username=pdb
h2.password=pdb

h2remote.engine=com.feedzai.commons.sql.abstraction.engine.impl.H2Engine
h2remote.jdbc=jdbc:h2:tcp://localhost:9092/public
h2remote.username=sa
h2remote.password=sa

h2v2.engine=com.feedzai.commons.sql.abstraction.engine.impl.H2EngineV2
h2v2.jdbc=jdbc:h2:./target/pdb_h2v2;AUTO_SERVER=FALSE
h2v2.username=pdb
h2v2.password=pdb

h2v2remote.engine=com.feedzai.commons.sql.abstraction.engine.impl.H2EngineV2
h2v2remote.jdbc=jdbc:h2:tcp://localhost:9093/public
h2v2remote.username=sa
h2v2remote.password=sa

mysql.engine=com.feedzai.commons.sql.abstraction.engine.impl.MySqlEngine
mysql.jdbc=jdbc:mysql://localhost:3306/mysql?useSSL=false&allowPublicKeyRetrieval=true
# appended "useSSL=false" to jdbc url to avoid a warning about not using SSL;
# appended "allowPublicKeyRetrieval=true" to jdbc url to avoid "key retrieval not allowed" error in newer MySQL versions
# for mysql, schema and database is the same thing
# default database/schema: none, it must be specified either in jdbc url or in schema property
# example when used in jdbc url: jdbc:mysql://localhost:3306/mysql
mysql.username=root
mysql.password=AaBb12.#
#mysql.schema=mysql


sqlserver.engine=com.feedzai.commons.sql.abstraction.engine.impl.SqlServerEngine
sqlserver.jdbc=jdbc:sqlserver://localhost:1433;databaseName=pdb;encrypt=false
# default database (not mandatory): master
# using "pdb" for tests because READ_COMMITTED_SNAPSHOT is required for SQL server to have the same behavior
# as other DBs in READ_COMMITTED isolation level and that flag can't be enabled on "master" database;
# the same applies to ALLOW_SNAPSHOT_ISOLATION, that makes available the TRANSACTION_SNAPSHOT level which is equivalent
# to SERIALIZABLE in PostgreSQL and Oracle
sqlserver.username=sa
sqlserver.password=AaBb12.#
#sqlserver.schema=dbo


postgresql.engine=com.feedzai.commons.sql.abstraction.engine.impl.PostgreSqlEngine
postgresql.jdbc=jdbc:postgresql://localhost:5432/postgres
# default database: postgres is used because it's mandatory in jdbc url and it's the only one in the test server
postgresql.username=postgres
postgresql.password=AaBb12.#
#postgresql.schema=public


oracle.engine=com.feedzai.commons.sql.abstraction.engine.impl.OracleEngine
oracle.jdbc=jdbc:oracle:thin:@localhost:1521:orcl
# alternate long jdbc URL
#       oracle.jdbc=jdbc:oracle:thin:@(DESCRIPTION=(ENABLE=broken)(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=localhost)(PORT=1521)))(CONNECT_DATA=(SID=orcl)))
# default database: orcl is used because it's mandatory in jdbc url and it's the only one in the test server
oracle.username=system
oracle.password=oracle
# for oracle, default schema is the same as user name
#oracle.schema=system


db2.engine=com.feedzai.commons.sql.abstraction.engine.impl.DB2Engine
db2.jdbc=jdbc:db2://localhost:50000/testdb
# default database: testdb is used because it's mandatory in jdbc url and it's the only one in the test server
db2.username=db2inst1
db2.password=AaBb12.#
# for DB2, default schema is the same as user name
#db2.schema=db2inst1

cockroach.engine=com.feedzai.commons.sql.abstraction.engine.impl.CockroachDBEngine
cockroach.jdbc=jdbc:postgresql://localhost:26257/postgres
# default database: postgres is used because it's mandatory
cockroach.username=root
cockroach.password=
#cockroach.schema=public
```


Now write the explanation and the single ```diff block.
