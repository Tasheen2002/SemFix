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
`com.h2database:h2` was updated from `1.3.175` to `2.1.210`. The project compiles, but tests now fail.

## Failure (from the build log)
Failing test classes: (not named in the log)
Exception types: org.h2.jdbc.JdbcSQLSyntaxErrorException
Error lines:
- Caused by: org.h2.jdbc.JdbcSQLSyntaxErrorException: Precision ("10000000") must be between "1" and "1048576" inclusive; SQL statement:
- Caused by: org.h2.jdbc.JdbcSQLSyntaxErrorException: Table "GS_STORED_DATA" not found; SQL statement:

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

### Past case 3: org.dhatim:dropwizard-sentry 2.0.22 -> 2.0.26-3 (alphagov/pay-cardid)
Symptom: io.dropwizard.configuration.ConfigurationParsingException; com.fasterxml.jackson.databind.exc.UnrecognizedPropertyException
  io.dropwizard.configuration.ConfigurationParsingException:
  Caused by: com.fasterxml.jackson.databind.exc.UnrecognizedPropertyException:
Behavior change: Accepted configuration input changed
Fix (CONFIGURATION_ADAPTATION, the project's developers; validated: all tests pass): Developer renamed the rejected Sentry appender property stacktraceAppPackages -> inAppIncludes in config.yaml (PR #732, landed with 2.0.28-8).
```diff
diff --git a/src/main/resources/config/config.yaml b/src/main/resources/config/config.yaml
--- a/src/main/resources/config/config.yaml
+++ b/src/main/resources/config/config.yaml
@@ -27,7 +27,7 @@
       threshold: ERROR
       dsn: ${SENTRY_DSN:-https://example.com@dummy/1}
       environment: ${ENVIRONMENT}
-      stacktraceAppPackages: ["uk.gov.pay"]
+      inAppIncludes: ["uk.gov.pay"]
 
 worldpayDataLocation: ${WORLDPAY_DATA_LOCATION:-file:///app/data/worldpay/GENERIC2ISOCPTISSUERPREPAID.CSV}
 discoverDataLocation: ${DISCOVER_DATA_LOCATION:-file:///app/data/discover/Merchant_Marketing.csv}
```


## Project files (at the breaking commit)
### pom.xml  (root build file)
```
<?xml version="1.0" encoding="ISO-8859-1"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>it.geosolutions</groupId>
    <artifactId>geostore</artifactId>
    <version>1.8-SNAPSHOT</version>

    <packaging>pom</packaging>

    <name>Master GeoStore POM</name>
    <description>
        GeoStore is an open source Java enterprise application for storing, searching and retrieving data on the fly.
    </description>

    <url>https://github.com/geosolutions-it/geostore</url>
    <inceptionYear>2011</inceptionYear>

    <organization>
        <name>GeoSolutions</name>
        <url>http://www.geo-solutions.it</url>
    </organization>

    <developers>
        <developer>
            <id>etj</id>
            <name>Emanuele Tajariol</name>
            <email>etj AT geosolutions.it</email>
            <organization>GeoSolutions</organization>
            <organizationUrl>http://www.geo-solutions.it</organizationUrl>
            <roles>
                <role>architect</role>
                <role>developer</role>
            </roles>
            <timezone>+1</timezone>
        </developer>
        <developer>
            <id>tobaro</id>
            <name>Tobia Di Pisa</name>
            <email>tobia.dipisa AT geosolutions.it</email>
            <organization>GeoSolutions</organization>
            <organizationUrl>http://www.geo-solutions.it</organizationUrl>
            <roles>
                <role>developer</role>
            </roles>
            <timezone>+1</timezone>
        </developer>
    </developers>

    <licenses>
        <license>
            <name>GPL-3-0</name>
            <url>http://opensource.org/licenses/GPL-3.0</url>
            <distribution>repo</distribution>
        </license>
    </licenses>

    <issueManagement>
        <system>github</system>
        <url>https://github.com/geosolutions-it/geostore/issues</url>
    </issueManagement>

    <scm>
        <url>https://github.com/geosolutions-it/geostore</url>
        <connection>scm:git:git@github.com:geosolutions-it/geostore.git</connection>
      <tag>HEAD</tag>
  </scm>

    <ciManagement>
        <system>jenkins</system>
        <url>http://build.geo-solutions.it/jenkins/view/GeoStore/</url>
    </ciManagement>

    <distributionManagement>
        <!-- use the following if you're not using a snapshot version. -->
        <repository>
            <uniqueVersion>false</uniqueVersion>
            <id>geosolutions</id>
            <url>ftp://maven.geo-solutions.it/</url>
        </repository>
        <!-- use the following if you ARE using a snapshot version. -->
        <snapshotRepository>
            <uniqueVersion>false</uniqueVersion>
            <id>geosolutions</id>
            <url>ftp://maven.geo-solutions.it/</url>
        </snapshotRepository>
        <site>
            <id>demo.geosolutions</id>
            <url>scp://demo.geo-solutions.it/var/www/share/javadoc/geostore/${project.version}</url>
        </site>
    </distributionManagement>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>2.0.2</version>
                <configuration>
                    <source>1.8</source>
                    <target>1.8</target>
                </configuration>
            </plugin>

            <!-- ======================================================= -->
            <!-- Source packaging. -->

            <plugin>
                <inherited>true</inherited>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-source-plugin</artifactId>
                <version>3.0.1</version>
                <configuration>
                    <attach>true</attach>
                </configuration>
                <executions>
                    <execution>
                        <id>attach-sources</id>
                        <goals>
                            <goal>jar</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>

            <!-- ======================================================= -->
            <!-- versioning -->

            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-release-plugin</artifactId>
                <version>2.5.2</version>
                <configuration>
                    <tagNameFormat>v@{project.version}</tagNameFormat>
                </configuration>
            </plugin>

            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-jar-plugin</artifactId>
                <version>2.4</version>
                <executions>
                    <execution>
                        <goals>
                            <goal>test-jar</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>

            <plugin>
                <groupId>org.eluder.coveralls</groupId>
                <artifactId>coveralls-maven-plugin</artifactId>
                <version>4.1.0</version>
            </plugin>

            <plugin>
                <groupId>org.codehaus.mojo</groupId>
                <artifactId>cobertura-maven-plugin</artifactId>
                <version>2.7</version>
                <configuration>
                    <format>xml</format>
                    <maxmem>256m</maxmem>
                    <!-- aggregated reports for multi-module projects -->
                    <aggregate>true</aggregate>
                </configuration>
            </plugin>

        </plugins>

        <extensions>
            <extension>
                <groupId>org.apache.maven.wagon</groupId>
                <artifactId>wagon-ftp</artifactId>
                <version>2.10</version>
            </extension>
        </extensions>

    </build>

    <reporting>
        <plugins>

            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-javadoc-plugin</artifactId>
                <configuration>
                    <links>
                        <link>http://commons.apache.org/lang/api</link>
                        <link>http://java.sun.com/j2se/1.5.0/docs/api</link>
                        <link>http://www.jdom.org/docs/apidocs</link>
                    </links>
                </configuration>
            </plugin>

            <plugin>
                <groupId>org.codehaus.mojo</groupId>
                <artifactId>cobertura-maven-plugin</artifactId>
                <version>2.7</version>
            </plugin>
        </plugins>
    </reporting>


    <modules>
        <module>src</module>
    </modules>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

</project>
```

### src/cli/pom.xml  (build file (declares the updated dependency))
```
<?xml version="1.0" encoding="UTF-8"?>
<!--
 Copyright (C) 2007 - 2010 GeoSolutions S.A.S.
 http://www.geo-solutions.it

 GPLv3 + Classpath exception

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses />.
 -->
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>it.geosolutions.geostore</groupId>
        <artifactId>geostore-root</artifactId>
        <version>1.8-SNAPSHOT</version>
    </parent>

    <artifactId>geostore-cli</artifactId>
    <packaging>jar</packaging>
    <name>GeoStore - Command Line Interface</name>

    <dependencies>

        <!-- H2 -->
        <dependency>
            <groupId>com.h2database</groupId>
            <artifactId>h2</artifactId>
            <version>1.3.175</version>
        </dependency>

   	    <!-- Apache Commons -->
        <dependency>
            <groupId>commons-beanutils</groupId>
            <artifactId>commons-beanutils</artifactId>
        </dependency>

        <dependency>
            <groupId>jdom</groupId>
            <artifactId>jdom</artifactId>
        </dependency>
        
        <dependency>
            <groupId>info.picocli</groupId>
            <artifactId>picocli</artifactId>
            <version>4.6.1</version>
        </dependency>
        <dependency>
            <groupId>commons-lang</groupId>
            <artifactId>commons-lang</artifactId>
        </dependency>

        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>

        <plugins>
            <!-- Attach sources ============================================ -->
            <plugin>
                <inherited>true</inherited>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-source-plugin</artifactId>
                <configuration>
                    <attach>true</attach>
                </configuration>
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
                <artifactId>maven-assembly-plugin</artifactId>
                <version>2.2</version>
                <configuration>
                    <finalName>H2ToPgSQLExport</finalName>
                        <appendAssemblyId>false</appendAssemblyId>
                    <archive>
                        <manifest>
                            <mainClass>it.geosolutions.geostore.cli.H2ToPgSQLExportCLI</mainClass>
                        </manifest>
                    </archive>
                    <descriptorRefs>
                    <descriptorRef>jar-with-dependencies</descriptorRef>
                    </descriptorRefs>
                </configuration>
                <executions>
                    <execution>
                    <id>make-assembly</id> <!-- this is used for inheritance merges -->
                    <phase>package</phase> <!-- bind to the packaging phase -->
                    <goals>
                        <goal>single</goal>
                    </goals>
                    </execution>
                </executions>
                </plugin>
        </plugins>
    </build>

</project>
```

### src/core/persistence/pom.xml  (build file (declares the updated dependency))
```
<?xml version="1.0" encoding="UTF-8"?>
<!--
 Copyright (C) 2007 - 2010 GeoSolutions S.A.S.
 http://www.geo-solutions.it

 GPLv3 + Classpath exception

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses />.
 -->
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">

    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>it.geosolutions.geostore</groupId>
        <artifactId>geostore-core</artifactId>
        <version>1.8-SNAPSHOT</version>
    </parent>

    <artifactId>geostore-persistence</artifactId>
    <packaging>jar</packaging>
    <name>GeoStore - Core - Persistence</name>

    <dependencies>

        <!-- ================================================================-->
        <!-- GeoStore -->
        <!-- ================================================================-->
        <dependency>
            <groupId>it.geosolutions.geostore</groupId>
            <artifactId>geostore-model</artifactId>
        </dependency>
         <dependency>
            <groupId>it.geosolutions.geostore</groupId>
            <artifactId>geostore-security</artifactId>
        </dependency>


        <!-- ================================================================-->
       	<!-- APACHE COMMONS -->
        <!-- ================================================================-->
        <dependency>
            <groupId>commons-lang</groupId>
            <artifactId>commons-lang</artifactId>
        </dependency>
        <dependency>
            <groupId>commons-collections</groupId>
            <artifactId>commons-collections</artifactId>
        </dependency>

        <dependency>
            <groupId>commons-codec</groupId>
            <artifactId>commons-codec</artifactId>
        </dependency>

        <dependency>
            <groupId>commons-dbcp</groupId>
            <artifactId>commons-dbcp</artifactId>
        </dependency>

        <!-- ================================================================-->
        <!-- 4J UTILS -->
        <!-- ================================================================-->
        <dependency>
            <groupId>dom4j</groupId>
            <artifactId>dom4j</artifactId>
        </dependency>
        <dependency>
            <groupId>log4j</groupId>
            <artifactId>log4j</artifactId>
        </dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-log4j12</artifactId>
        </dependency>

        <!-- ================================================================-->
        <!-- Spring -->
        <!-- ================================================================-->
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-aop</artifactId>
            <scope>test</scope>
        </dependency>

        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-context</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-orm</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-jdbc</artifactId>
        </dependency>

        <dependency>
             <groupId>org.springframework.security</groupId>
             <artifactId>spring-security-ldap</artifactId>
       </dependency>

		<!-- =========================================================== -->
		<!--     SPRING SECURITY                                         -->
		<!-- =========================================================== -->
<!--		<dependency>
		    <groupId>org.springframework.security</groupId>
		    <artifactId>spring-security-core</artifactId>
		</dependency>
        <dependency>
            <groupId>javax.persistence</groupId>
            <artifactId>persistence-api</artifactId>
        </dependency>-->

        <!-- https://mvnrepository.com/artifact/org.hibernate.javax.persistence/hibernate-jpa-2.1-api -->
        <dependency>
            <groupId>org.hibernate.javax.persistence</groupId>
            <artifactId>hibernate-jpa-2.1-api</artifactId>
        </dependency>


		<!-- HIBERNATE-GENERIC-DAO -->
        <dependency>
            <groupId>com.googlecode.genericdao</groupId>
            <artifactId>dao-hibernate</artifactId>
<!--            <groupId>com.trg</groupId>
            <artifactId>trg-dao</artifactId>-->
        </dependency>
        <dependency>
            <groupId>com.googlecode.genericdao</groupId>
            <artifactId>search-jpa-hibernate</artifactId>
<!--            <groupId>com.trg</groupId>
            <artifactId>trg-search-jpa-hibernate</artifactId>-->
        </dependency>

		<!-- H2 -->
        <dependency>
		    <groupId>com.h2database</groupId>
		    <artifactId>h2</artifactId>
		    <version>2.1.210</version>
		</dependency>

		<!-- HIBERNATE -->
        
<!--        <dependency>
            <groupId>org.hibernate</groupId>
            <artifactId>hibernate-validator</artifactId>
        </dependency>-->
        <dependency>
            <groupId>org.hibernate</groupId>
            <artifactId>hibernate-core</artifactId>
            <exclusions>
                <exclusion>
                    <groupId>asm</groupId>
                    <artifactId>asm</artifactId>
                </exclusion>
                <exclusion>
                    <groupId>asm</groupId>
                    <artifactId>asm-attrs</artifactId>
                </exclusion>
                <exclusion>
                    <groupId>cglib</groupId>
                    <artifactId>cglib</artifactId>
                </exclusion>
            </exclusions>
        </dependency>
        <dependency>
            <groupId>org.hibernate</groupId>
            <artifactId>hibernate-ehcache</artifactId>
        </dependency>

  	<!-- CGLIB -->
        <dependency>
            <groupId>asm</groupId>
            <artifactId>asm</artifactId>
        </dependency>
        <dependency>
            <groupId>cglib</groupId>
            <artifactId>cglib-nodep</artifactId>
        </dependency>

    <!-- HTTP UTILS -->
<!--        <dependency>
            <groupId>org.codehaus.jettison</groupId>
            <artifactId>jettison</artifactId>
        </dependency>    -->
        <dependency>
            <groupId>org.aspectj</groupId>
            <artifactId>aspectjrt</artifactId>
        </dependency>
        <dependency>
            <groupId>org.aspectj</groupId>
            <artifactId>aspectjweaver</artifactId>
        </dependency>

<!--        <dependency>
            <groupId>javax.servlet</groupId>
            <artifactId>servlet-api</artifactId>
            <scope>provided</scope>
        </dependency>-->

    <!-- JUnit -->
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <scope>test</scope>
        </dependency>

    </dependencies>

    <!-- if you want to create a new profile for support another DB create a profile including -->
	<!-- JDBC dependency and right esclusion/inclusion rule for load the right override file -->
	<!-- Profile for supporting Postgres -->
	<profiles>
		<profile>
			<id>postgres</id>
		    <dependencies>
			    <!-- POSTGRESQL database driver -->
		        <dependency>
		            <groupId>org.postgresql</groupId>
		            <artifactId>postgresql</artifactId>
		        </dependency>
	        </dependencies>
	    </profile>

		<profile>
			<id>oracle</id>
			<dependencies>
				<!-- ORACLE database driver -->
				<dependency>
					<groupId>com.oracle</groupId>
					<artifactId>ojdbc6</artifactId>
					<version>11.2.0</version>
				</dependency>
			</dependencies>
		</profile>
	</profiles>

    <build>

        <plugins>
            <plugin>
                <groupId>org.codehaus.mojo</groupId>
                <artifactId>hibernate3-maven-plugin</artifactId>
                <version>2.2</version>
                <executions>
                    <execution>
                        <phase>process-classes</phase>
                        <goals>
                            <goal>hbm2ddl</goal>
                        </goals>
                    </execution>
                </executions>
                <configuration>
                    <components>
                        <component>
                            <name>hbm2ddl</name>
                            <implementation>annotationconfiguration</implementation>
                            <outputDirectory>target/classes</outputDirectory>
                        </component>
                        <component>
                            <name>hbmdoc</name>
                        </component>
                    </components>
                    <componentProperties>
                        <configurationfile>/src/test/resources/hibernate.cfg.xml</configurationfile>
                        <outputfilename>geostore.ddl</outputfilename>

                        <drop>false</drop> <!-- -->
                        <create>true</create>
                        <export>false</export>
                        <format>true</format>
                    </componentProperties>
                </configuration>
            </plugin>
        </plugins>

    </build>
</project>
```

### src/pom.xml  (build file (declares the updated dependency))
```
... (lines 0-0 omitted)
<?xml version="1.0" encoding="UTF-8"?>
<!--
 Copyright (C) 2007 - 2016 GeoSolutions S.A.S.
 http://www.geo-solutions.it

 GPLv3 + Classpath exception

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <http://www.gnu.org/licenses />.
-->
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>it.geosolutions</groupId>
        <artifactId>geostore</artifactId>
        <version>1.8-SNAPSHOT</version>
    </parent>

    <groupId>it.geosolutions.geostore</groupId>
    <artifactId>geostore-root</artifactId>
    <packaging>pom</packaging>

    <name>GeoStore - 0 Server Root</name>

    <profiles>
        <profile>
            <id>default</id>
            <activation>
                <activeByDefault>true</activeByDefault>
... (lines 41-52 omitted)
                <module>web</module>
                <module>cli</module>
            </modules>
        </profile>
        <profile>
            <id>cli</id>
            <modules>
                <module>cli</module>
            </modules>
        </profile>
    </profiles>

    <properties>
        <geostore-version>1.8-SNAPSHOT</geostore-version>
        <main-prefix>geostore</main-prefix>

        <cxf-version>3.4.4</cxf-version>
        <activemq-version>5.3.0.4-fuse</activemq-version>

        <jersey-version>2.5.1</jersey-version>
        <!--
        spring-security-core 3.0.4 requires spring-core 3.x, otherwise we'd normally use 2.5.6, which
        is what the rest of the app uses
        -->
        <spring-version>5.3.9</spring-version>
... (lines 78-109 omitted)

        <maven-assembly-plugin-version>2.2-beta-5</maven-assembly-plugin-version>

        <xbean-version>3.1.0.2-fuse</xbean-version>

        <spring-support>2.0.8</spring-support>
        <spring-ws-version>1.0.1</spring-ws-version>
        <aspectj-version>1.5.4</aspectj-version>
        <ubl-version>2.0</ubl-version>
        <jetty-version>6.1.0.1-fuse</jetty-version>
        <jettison-version>1.4.0</jettison-version>

<!--        <postgis-jdbc-version>1.1.6</postgis-jdbc-version>-->
<!--        <postgis-jdbc-version>1.3.3</postgis-jdbc-version>-->

        <persistence-version>1.0</persistence-version>
        <hibernate-version>5.5.0.Final</hibernate-version>
        <hibernate-generic-dao-version>1.2.0</hibernate-generic-dao-version>
        <asm-version>2.2.3</asm-version>
        <cglib-version>2.1_3</cglib-version>
        <guava-version>18.0</guava-version>
        <mockito-version>1.10.19</mockito-version>

        <javassist-version>3.8.0.GA</javassist-version>

        <geoapi-version>2.3-M1</geoapi-version>
... (lines 136-561 omitted)
            <dependency>
                <groupId>org.springframework</groupId>
                <artifactId>spring-tx</artifactId>
                <version>${spring-version}</version>
            </dependency>
            <dependency>
                <groupId>org.springframework</groupId>
                <artifactId>spring-context-support</artifactId>
                <version>${spring-version}</version>
            </dependency>
            <dependency>
                <groupId>org.springframework</groupId>
                <artifactId>spring-jdbc</artifactId>
                <version>${spring-version}</version>
<!--                <scope>provided</scope>-->
            </dependency>

            <dependency>
                <groupId>org.springframework</groupId>
                <artifactId>spring-orm</artifactId>
                <version>${spring-version}</version>
            </dependency>

            <dependency>
                <groupId>org.springframework</groupId>
... (lines 587-772 omitted)
		    <!-- =========================================================== -->
            <dependency>
                <groupId>org.hibernatespatial</groupId>
                <artifactId>hibernate-spatial-postgis</artifactId>
                <version>1.1.1</version>
            </dependency>

		    <!-- =========================================================== -->
		    <!--     POSTGRES- POSTGIS                                       -->
		    <!-- =========================================================== -->
            <dependency>
                <groupId>org.postgis</groupId>
                <artifactId>postgis-jdbc</artifactId>
                <version>1.3.3</version>
            </dependency>
            <dependency>
                <groupId>org.postgresql</groupId>
                <artifactId>postgresql</artifactId>
                <version>42.2.23</version>
            </dependency>
            <dependency>
                <groupId>com.vividsolutions</groupId>
                <artifactId>jts</artifactId>
                <version>1.10</version>
            </dependency>
... (lines 798-893 omitted)
            </dependency>
            <dependency>
                <groupId>org.geotools</groupId>
                <artifactId>gt-coveragetools</artifactId>
                <version>${gt-version}</version>
            </dependency>
            <dependency>
                <groupId>org.geotools</groupId>
                <artifactId>gt-shapefile</artifactId>
                <version>${gt-version}</version>
            </dependency>
            <dependency>
                <groupId>org.geotools.jdbc</groupId>
                <artifactId>gt-jdbc-postgis</artifactId>
                <version>${gt-version}</version>
            </dependency>
            <dependency>
                <groupId>org.geotools</groupId>
                <artifactId>gt-epsg-wkt</artifactId>
                <version>${gt-version}</version>
            </dependency>

        </dependencies>
    </dependencyManagement>

    <build>
```

### src/web/app/pom.xml  (build file (declares the updated dependency))
```
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>it.geosolutions.geostore</groupId>
        <artifactId>geostore-web</artifactId>
        <version>1.8-SNAPSHOT</version>
    </parent>

    <artifactId>geostore-webapp</artifactId>
    <packaging>war</packaging>

    <name>GeoStore - Webapp</name>

    <developers>
        <developer>
            <name>Emanuele Tajariol</name>
            <id>ETj</id>
            <organization>GeoSolutions</organization>
        </developer>
    </developers>

    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>

    <dependencies>
        <!-- ================================================================ -->
        <!-- GeoStore modules -->
        <!-- ================================================================ -->
        <dependency>
            <groupId>it.geosolutions.geostore</groupId>
            <artifactId>geostore-persistence</artifactId>
        </dependency>
        <!-- =============================================================== -->

        <dependency>
            <groupId>it.geosolutions.geostore</groupId>
            <artifactId>geostore-rest-impl</artifactId>
        </dependency>

        <!-- Avoids java.lang.ClassNotFoundException: com.sun.ws.rs.ext.RuntimeDelegateImpl -->
        <dependency>
            <groupId>org.apache.cxf</groupId>
            <artifactId>cxf-rt-frontend-jaxrs</artifactId>
            <!-- <scope>test</scope> -->
        </dependency>
        <dependency>
            <groupId>org.apache.cxf</groupId>
            <artifactId>cxf-rt-rs-extension-providers</artifactId>
        </dependency>
        <dependency>
            <groupId>org.apache.cxf</groupId>
            <artifactId>cxf-rt-rs-json-basic</artifactId>
        </dependency>
        <dependency>
            <groupId>org.codehaus.jettison</groupId>
            <artifactId>jettison</artifactId>
        </dependency>

        <!-- =========================================================== -->
        <!-- TEST -->
        <!-- <dependency> -->
        <!-- <groupId>javax.servlet</groupId> -->
        <!-- <artifactId>servlet-api</artifactId> -->
        <!-- <scope>provided</scope> -->
        <!-- </dependency> -->

        <dependency>
            <groupId>commons-httpclient</groupId>
            <artifactId>commons-httpclient</artifactId>
        </dependency>

        <dependency>
            <groupId>org.apache.cxf</groupId>
            <artifactId>cxf-rt-transports-http-jetty</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.cxf</groupId>
            <artifactId>cxf-rt-rs-client</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
        </dependency>

        <!-- ================================================================ -->
        <!-- GeoStore modules -->
        <!-- ================================================================ -->

        <!-- JUnit -->
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <scope>test</scope>
        </dependency>

        <!-- LDAP Deps -->
        <dependency>
            <groupId>org.apache.directory.server</groupId>
            <artifactId>apacheds-all</artifactId>
            <version>1.5.5</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.apache.directory.shared</groupId>
            <artifactId>shared-ldap</artifactId>
            <version>0.9.16</version>
            <scope>test</scope>
        </dependency>

        <!-- Jetty server -->
        <dependency>
            <groupId>org.mortbay.jetty</groupId>
            <artifactId>jetty</artifactId>
            <version>6.1.14</version>
            <scope>test</scope>
        </dependency>
        <!-- =========================================================== -->
        <!--     JAVAX SERVLET & JSP                                     -->
        <!-- =========================================================== -->
        <dependency>
            <groupId>javax.servlet</groupId>
            <artifactId>servlet-api</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>jstl</groupId>
            <artifactId>jstl</artifactId>
            <version>1.2</version>
            <scope>test</scope>
        </dependency>

    </dependencies>

    <!-- if you want to create a new profile for support another DB create a
    profile including JDBC dependency and right esclusion/inclusion rule for
    load the right override file -->
    <!-- Profile for supporting Postgres -->
    <profiles>
        <profile>
            <id>postgres</id>
            <build>
                <!-- Copy the postgres custom geostore-datasource-ovr.properties -->
                <plugins>
                    <plugin>
                        <artifactId>maven-antrun-plugin</artifactId>
                        <version>1.1</version>
                        <executions>
                            <execution>
                                <phase>process-classes</phase>
                                <configuration>
                                    <tasks>
                                        <copy file="src/main/resources/db-conf/postgres.properties" tofile="${project.build.outputDirectory}/geostore-datasource-ovr.properties" overwrite="true" verbose="true" />
                                    </tasks>
                                </configuration>
                                <goals>
                                    <goal>run</goal>
                                </goals>
                            </execution>
                        </executions>
                    </plugin>
                </plugins>
            </build>

            <dependencies>
                <!-- POSTGRESQL database driver -->
                <dependency>
                    <groupId>org.postgresql</groupId>
                    <artifactId>postgresql</artifactId>
                </dependency>
            </dependencies>
        </profile>

        <profile>
            <id>h2_disk</id>
            <build>
                <!-- Copy the postgres custom geostore-datasource-ovr.properties -->
                <plugins>
                    <plugin>
                        <artifactId>maven-antrun-plugin</artifactId>
                        <version>1.1</version>
                        <executions>
                            <execution>
                                <phase>process-classes</phase>
                                <configuration>
                                    <tasks>
                                        <copy file="src/main/resources/db-conf/h2_disk.properties" tofile="${project.build.outputDirectory}/geostore-datasource-ovr.properties" overwrite="true" verbose="true" />
                                    </tasks>
                                </configuration>
                                <goals>
                                    <goal>run</goal>
                                </goals>
                            </execution>
                        </executions>
                    </plugin>
                </plugins>
            </build>

        </profile>

        <profile>
            <id>oracle</id>
            <build>
                <!-- Copy the postgres custom geostore-datasource-ovr.properties -->
                <plugins>
                    <plugin>
                        <artifactId>maven-antrun-plugin</artifactId>
                        <version>1.1</version>
                        <executions>
                            <execution>
                                <phase>process-classes</phase>
                                <configuration>
                                    <tasks>
                                        <copy file="src/main/resources/db-conf/oracle.properties" tofile="${project.build.outputDirectory}/geostore-datasource-ovr.properties" overwrite="true" verbose="true" />
                                    </tasks>
                                </configuration>
                                <goals>
                                    <goal>run</goal>
                                </goals>
                            </execution>
                        </executions>
                    </plugin>
                </plugins>
            </build>

            <dependencies>
                <!-- ORACLE database driver -->
                <dependency>
                    <groupId>com.oracle</groupId>
                    <artifactId>ojdbc6</artifactId>
                    <version>11.2.0</version>
                </dependency>
            </dependencies>
        </profile>

        <profile>
            <id>extjs</id>
            <dependencies>
                <dependency>
                    <groupId>it.geosolutions.geostore</groupId>
                    <artifactId>geostore-rest-extjs</artifactId>
                </dependency>
            </dependencies>
        </profile>

        <profile>
            <id>auditing</id>
            <dependencies>
                <dependency>
                    <groupId>it.geosolutions.geostore</groupId>
                    <artifactId>geostore-rest-auditing</artifactId>
                </dependency>
            </dependencies>
        </profile>
    </profiles>

    <build>
        <finalName>geostore</finalName>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <encoding>utf8</encoding>
                    <source>1.8</source>
                    <target>1.8</target>
                </configuration>
            </plugin>

            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-war-plugin</artifactId>
                <version>2.6</version>
                <configuration>
                    <packagingExcludes>WEB-INF/lib/apacheds-all*.jar</packagingExcludes>
                </configuration>
            </plugin>

            <!-- Run the application using "mvn jetty:run" -->
            <plugin>
                <groupId>org.mortbay.jetty</groupId>
                <artifactId>maven-jetty-plugin</artifactId>
                <version>6.1.26</version>
                <configuration>
                    <!-- <webAppSourceDirectory>${basedir}/war</webAppSourceDirectory> -->
                    <webAppConfig>
                        <contextPath>/geostore</contextPath>
                    </webAppConfig>
                    <connectors>
                        <connector implementation="org.mortbay.jetty.nio.SelectChannelConnector">
                            <port>9191</port>
                            <maxIdleTime>60000</maxIdleTime>
                        </connector>
                    </connectors>
                    <reload>manual</reload>
                </configuration>
            </plugin>

        </plugins>

    </build>


</project>
```


Now write the explanation and the single ```diff block.
