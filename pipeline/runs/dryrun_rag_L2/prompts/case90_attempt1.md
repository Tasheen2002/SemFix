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
Failing test classes: de.retest.recheck.ui.diff.AttributeDifferenceTest, de.retest.recheck.ignore.JSFilterImplTest, de.retest.recheck.review.workers.MigrateIgnoreFileTest, de.retest.recheck.review.workers.LoadAndSaveFilterWorkerTest, DefaultRecheckIgnoreTest, DefaultRecheckIgnoreJsTest
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

### Past case 2: org.slf4j:slf4j-api 1.7.36 -> 2.0.5 (alphagov/pay-adminusers)
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

### Past case 3: org.slf4j:slf4j-api 1.7.36 -> 2.0.5 (s4u/sign-maven-plugin)
Symptom: java.lang.ClassCastException
  java.lang.ClassCastException: class org.slf4j.helpers.NOPLogger cannot be cast to class org.simplify4u.slf4jmock.internal.ProxyMock (org.slf4j.helpers.NOPLogger and org.simplify4u.slf4jmock.internal.ProxyMock are in unnamed module of loader
Behavior change: LoggerFactory returns NOPLogger
Fix (RESEARCHER_WRITTEN, written by the researchers (validated, but not the project's own fix); validated: all tests pass): Replace org.simplify4u:slf4j-mock 2.2.0/2.3.0 (SLF4J-1 binding) with org.simplify4u:slf4j2-mock 2.3.0 (same author and packages, SLF4J-2 provider).
```diff
diff --git a/pom.xml b/pom.xml
--- a/pom.xml
+++ b/pom.xml
@@ -181,7 +181,7 @@
             </dependency>
             <dependency>
                 <groupId>org.simplify4u</groupId>
-                <artifactId>slf4j-mock</artifactId>
+                <artifactId>slf4j2-mock</artifactId>
                 <version>2.3.0</version>
             </dependency>
 
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
<?xml version="1.0"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
	<modelVersion>4.0.0</modelVersion>

	<groupId>de.retest</groupId>
	<artifactId>recheck</artifactId>
	<version>1.14.0-SNAPSHOT</version>

	<name>recheck</name>
	<description>Replace traditional assertions with a single check.</description>
	<url>https://retest.de/recheck/</url>

	<organization>
		<name>retest @ UBS Hainer GmbH</name>
		<url>https://retest.de/</url>
	</organization>

	<developers>
		<developer>
			<id>team</id>
			<name>The retest developers</name>
			<email>info@retest.de</email>
			<url>https://github.com/orgs/retest/people</url>
		</developer>
	</developers>

	<contributors>
		<contributor>
			<name>The contributors</name>
			<url>https://github.com/retest/${project.artifactId}/graphs/contributors</url>
		</contributor>
	</contributors>

	<licenses>
		<license>
			<name>GNU Affero General Public License (AGPL), Version 3</name>
			<url>https://gnu.org/licenses/agpl-3.0.html</url>
		</license>
	</licenses>

	<properties>
		<java.version>1.8</java.version>
		<git.repo.host>github.com</git.repo.host>
		<git.repo.path>retest/${project.artifactId}</git.repo.path>
		<project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
		<project.resources.sourceEncoding>UTF-8</project.resources.sourceEncoding>
		<project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
		<maven.surefire.and.failsafe.version>3.0.0-M6</maven.surefire.and.failsafe.version>
		<logback.version>1.2.11</logback.version>
		<eclipse.persistence.version>2.5.2</eclipse.persistence.version>
	</properties>

	<distributionManagement>
		<snapshotRepository>
			<id>ossrh</id>
			<url>https://oss.sonatype.org/content/repositories/snapshots/</url>
		</snapshotRepository>
		<repository>
			<id>ossrh</id>
			<url>https://oss.sonatype.org/service/local/staging/deploy/maven2/</url>
		</repository>
	</distributionManagement>

	<repositories>
		<repository>
			<id>central</id>
			<url>https://repo.maven.apache.org/maven2/</url>
		</repository>
		<repository>
			<id>jitpack.io</id>
			<url>https://jitpack.io/</url>
		</repository>
	</repositories>

	<dependencies>
		<dependency>
			<groupId>org.slf4j</groupId>
			<artifactId>slf4j-api</artifactId>
			<version>2.0.5</version>
		</dependency>

		<dependency>
			<groupId>org.apache.commons</groupId>
			<artifactId>commons-lang3</artifactId>
			<version>3.12.0</version>
		</dependency>

		<dependency>
			<groupId>org.projectlombok</groupId>
			<artifactId>lombok</artifactId>
			<version>1.18.24</version>
		</dependency>

		<dependency>
			<groupId>com.google.guava</groupId>
			<artifactId>guava</artifactId>
			<version>31.1-jre</version>
		</dependency>

		<dependency>
			<groupId>com.esotericsoftware.kryo</groupId>
			<artifactId>kryo5</artifactId>
			<version>5.3.0</version>
		</dependency>

		<dependency>
			<groupId>org.lz4</groupId>
			<artifactId>lz4-java</artifactId>
			<version>1.8.0</version>
		</dependency>

		<dependency>
			<groupId>commons-io</groupId>
			<artifactId>commons-io</artifactId>
			<version>2.11.0</version>
		</dependency>

		<dependency>
			<groupId>javax.xml.bind</groupId>
			<artifactId>jaxb-api</artifactId>
			<version>2.3.1</version>
		</dependency>

		<dependency>
			<groupId>com.konghq</groupId>
			<artifactId>unirest-java</artifactId>
			<version>3.13.10</version>
		</dependency>

		<dependency>
			<groupId>com.auth0</groupId>
			<artifactId>jwks-rsa</artifactId>
			<version>0.21.1</version>
		</dependency>

		<dependency>
			<groupId>com.auth0</groupId>
			<artifactId>java-jwt</artifactId>
			<version>3.19.2</version>
		</dependency>

		<dependency>
			<groupId>org.aeonbits.owner</groupId>
			<artifactId>owner-java8</artifactId>
			<version>1.0.12</version>
		</dependency>

		<dependency>
			<groupId>org.eclipse.persistence</groupId>
			<artifactId>org.eclipse.persistence.moxy</artifactId>
			<version>3.0.2</version>
		</dependency>

		<!-- required by eclipse moxy -->
		<dependency>
			<groupId>com.sun.activation</groupId>
			<artifactId>jakarta.activation</artifactId>
			<version>2.0.1</version>
		</dependency>
		<dependency>
			<groupId>com.sun.mail</groupId>
			<artifactId>jakarta.mail</artifactId>
			<version>2.0.1</version>
		</dependency>

		<dependency>
			<groupId>org.apache.commons</groupId>
			<artifactId>commons-text</artifactId>
			<version>1.9</version>
		</dependency>

		<dependency>
			<groupId>org.mozilla</groupId>
			<artifactId>rhino</artifactId>
			<version>1.7.14</version>
		</dependency>

		<dependency>
			<groupId>cat.inspiracio</groupId>
			<artifactId>rhino-js-engine</artifactId>
			<version>1.7.10</version>
		</dependency>

		<!-- test dependencies -->

		<dependency>
			<groupId>org.junit.jupiter</groupId>
			<artifactId>junit-jupiter</artifactId>
			<version>5.8.2</version>
			<scope>test</scope>
		</dependency>

		<dependency>
			<groupId>ch.qos.logback</groupId>
			<artifactId>logback-core</artifactId>
			<version>${logback.version}</version>
			<scope>test</scope>
		</dependency>

		<dependency>
			<groupId>ch.qos.logback</groupId>
			<artifactId>logback-classic</artifactId>
			<version>${logback.version}</version>
			<scope>test</scope>
		</dependency>

		<dependency>
			<groupId>org.mockito</groupId>
			<artifactId>mockito-core</artifactId>
			<version>4.6.0</version>
			<scope>test</scope>
		</dependency>

		<dependency>
			<groupId>org.powermock</groupId>
			<artifactId>powermock-api-mockito2</artifactId>
			<version>2.0.9</version>
			<scope>test</scope>
		</dependency>

		<dependency>
			<groupId>org.powermock</groupId>
			<artifactId>powermock-module-junit4</artifactId>
			<version>2.0.9</version>
			<scope>test</scope>
		</dependency>

		<dependency>
			<groupId>org.powermock</groupId>
			<artifactId>powermock-module-junit4-rule-agent</artifactId>
			<version>2.0.9</version>
			<scope>test</scope>
		</dependency>

		<dependency>
			<groupId>org.assertj</groupId>
			<artifactId>assertj-core</artifactId>
			<version>3.23.1</version>
			<scope>test</scope>
		</dependency>

		<dependency>
			<groupId>com.approvaltests</groupId>
			<artifactId>approvaltests</artifactId>
			<version>15.5.0</version>
			<scope>test</scope>
		</dependency>

		<dependency>
			<groupId>com.github.stefanbirkner</groupId>
			<artifactId>system-rules</artifactId>
			<version>1.19.0</version>
			<scope>test</scope>
		</dependency>

		<dependency>
			<groupId>org.junit-pioneer</groupId>
			<artifactId>junit-pioneer</artifactId>
			<version>1.7.1</version>
			<scope>test</scope>
			<exclusions>
				<exclusion>
					<groupId>org.junit.platform</groupId>
					<artifactId>junit-platform-commons</artifactId>
				</exclusion>
			</exclusions>
		</dependency>

		<dependency>
			<groupId>io.github.netmikey.logunit</groupId>
			<artifactId>logunit-core</artifactId>
			<version>1.1.3</version>
			<scope>test</scope>
		</dependency>

		<dependency>
			<groupId>io.github.netmikey.logunit</groupId>
			<artifactId>logunit-logback</artifactId>
			<version>1.1.3</version>
			<scope>test</scope>
		</dependency>

	</dependencies>

	<build>
		<plugins>
			<plugin>
				<artifactId>maven-compiler-plugin</artifactId>
				<version>3.10.1</version>
				<configuration>
					<source>${java.version}</source>
					<target>${java.version}</target>
					<compilerArgument>-Xlint:all</compilerArgument>
				</configuration>
			</plugin>

			<plugin>
				<groupId>org.apache.maven.plugins</groupId>
				<artifactId>maven-surefire-plugin</artifactId>
				<version>${maven.surefire.and.failsafe.version}</version>
				<configuration>
					<includes>
						<!-- overwrite default, prevent run of files matching `Test*.class` -->
						<include>%regex[.*Test.class]</include>
					</includes>
					<properties>
						<configurationParameters>
							junit.jupiter.execution.parallel.enabled=true
						</configurationParameters>
					</properties>
				</configuration>
			</plugin>

			<plugin>
				<groupId>org.apache.maven.plugins</groupId>
				<artifactId>maven-failsafe-plugin</artifactId>
				<version>${maven.surefire.and.failsafe.version}</version>
				<configuration>
					<!-- combine Surefire and Failsafe reports for SonarCloud -->
					<!-- see https://stackoverflow.com/a/15567782 -->
					<reportsDirectory>${project.build.directory}/surefire-reports/</reportsDirectory>
				</configuration>
				<executions>
					<execution>
						<id>run-integration-tests</id>
						<goals>
							<goal>integration-test</goal>
							<goal>verify</goal>
						</goals>
					</execution>
				</executions>
			</plugin>

			<plugin>
				<groupId>org.apache.maven.plugins</groupId>
				<artifactId>maven-jar-plugin</artifactId>
				<version>3.2.2</version>
				<configuration>
					<archive>
						<manifest>
							<addDefaultImplementationEntries>true</addDefaultImplementationEntries>
							<addDefaultSpecificationEntries>true</addDefaultSpecificationEntries>
						</manifest>
						<manifestEntries>
							<Automatic-Module-Name>de.retest.recheck</Automatic-Module-Name>
						</manifestEntries>
					</archive>
				</configuration>
			</plugin>

			<plugin>
				<groupId>com.amashchenko.maven.plugin</groupId>
				<artifactId>gitflow-maven-plugin</artifactId>
				<version>1.18.0</version>
				<configuration>
					<gitFlowConfig>
						<productionBranch>main</productionBranch>
						<releaseBranchPrefix>release/v</releaseBranchPrefix>
						<hotfixBranchPrefix>hotfix/v</hotfixBranchPrefix>
						<versionTagPrefix>v</versionTagPrefix>
					</gitFlowConfig>
					<commitDevelopmentVersionAtStart>true</commitDevelopmentVersionAtStart>
					<skipTestProject>true</skipTestProject>
					<useSnapshotInHotfix>true</useSnapshotInHotfix>
					<useSnapshotInRelease>true</useSnapshotInRelease>
					<versionDigitToIncrement>1</versionDigitToIncrement>
					<commitMessagePrefix xml:space="preserve">ci: </commitMessagePrefix>
					<pushRemote>true</pushRemote>
				</configuration>
			</plugin>

			<plugin>
				<groupId>org.apache.maven.plugins</groupId>
				<artifactId>maven-source-plugin</artifactId>
				<version>3.2.1</version>
				<executions>
					<execution>
						<id>bundle-sources</id>
						<goals>
							<goal>jar</goal>
						</goals>
					</execution>
				</executions>
			</plugin>

			<plugin>
				<groupId>org.apache.maven.plugins</groupId>
				<artifactId>maven-javadoc-plugin</artifactId>
				<version>3.4.0</version>
				<executions>
					<execution>
						<id>bundle-javadoc</id>
						<goals>
							<goal>jar</goal>
						</goals>
					</execution>
				</executions>
				<configuration>
					<!-- downgrade to fix Maven build with Java 13 -->
					<!-- see https://bugs.openjdk.java.net/browse/JDK-8212233 -->
					<source>8</source>
					<!-- see https://stackoverflow.com/q/38707030 -->
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
				<artifactId>maven-enforcer-plugin</artifactId>
				<version>3.0.0</version>
				<executions>
					<execution>
						<id>enforce-maven</id>
						<goals>
							<goal>enforce</goal>
						</goals>
						<configuration>
							<rules>
								<requireMavenVersion>
									<version>3.4</version>
								</requireMavenVersion>
							</rules>
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
					<nexusUrl>https://oss.sonatype.org/</nexusUrl>
					<serverId>ossrh</serverId>
					<stagingProfileId>506dfd640832af</stagingProfileId>
				</configuration>
			</plugin>
		</plugins>
	</build>

	<profiles>
		<profile>
			<id>sign</id>
			<build>
				<plugins>
					<plugin>
						<groupId>org.apache.maven.plugins</groupId>
						<artifactId>maven-gpg-plugin</artifactId>
						<version>3.0.1</version>
						<configuration>
							<skip>${gpg.skip}</skip>
							<passphrase>${env.GPG_PASSPHRASE}</passphrase>
							<gpgArguments>
								<!-- This is necessary for gpg to not try to use the pinentry programs -->
								<arg>--pinentry-mode</arg>
								<arg>loopback</arg>
							</gpgArguments>
						</configuration>
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
			<id>coverage</id>
			<build>
				<plugins>
					<plugin>
						<groupId>org.jacoco</groupId>
						<artifactId>jacoco-maven-plugin</artifactId>
						<version>0.8.8</version>
						<executions>
							<execution>
								<id>prepare-agent</id>
								<goals>
									<goal>prepare-agent</goal>
								</goals>
							</execution>
							<execution>
								<id>report</id>
								<goals>
									<goal>report</goal>
								</goals>
							</execution>
						</executions>
					</plugin>
				</plugins>
			</build>
		</profile>
	</profiles>

	<scm>
		<connection>scm:git:https://${git.repo.host}/${git.repo.path}.git</connection>
		<developerConnection>scm:git:ssh://git@${git.repo.host}/${git.repo.path}.git</developerConnection>
		<url>https://${git.repo.host}/${git.repo.path}/</url>
		<tag>HEAD</tag>
	</scm>
</project>
```

### src/test/java/de/retest/recheck/ui/diff/AttributeDifferenceTest.java  (failing test)
```
package de.retest.recheck.ui.diff;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.stream.Stream;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import io.github.netmikey.logunit.api.LogCapturer;

class AttributeDifferenceTest {

	@RegisterExtension
	LogCapturer logs = LogCapturer.create().captureForType( AttributeDifference.class );

	@Test
	void apply_changes_to_null_attribute_yields_NullPointerException() throws Exception {
		final AttributeDifference cut = new AttributeDifference();
		assertThatThrownBy( () -> cut.applyChangeTo( null ) ) //
				.isInstanceOf( NullPointerException.class ) //
				.hasMessage( "Cannot apply change to an attribute that is null." );
	}

	@Test
	void identifier_should_respect_key() {
		final AttributeDifference bottom =
				new AttributeDifference( "border-bottom-color", "rgba(0, 0, 0, 0.26)", "rgba(0, 0, 0, 0.32)" );
		final AttributeDifference top =
				new AttributeDifference( "border-top-color", "rgba(0, 0, 0, 0.26)", "rgba(0, 0, 0, 0.32)" );

		assertThat( bottom.identifier() ).isNotEqualTo( top.identifier() );
	}

	@Test
	void compare_to_same_object_is_zero() throws Exception {
		final AttributeDifference cut = new AttributeDifference();
		assertThat( cut.compareTo( cut ) ).isEqualTo( 0 );
	}

	@ParameterizedTest
	@MethodSource( "warnArgs" )
	void should_warn_if_attributes_dont_match( final String expected, final String fromAttribute ) throws Exception {
		final String key = "key";
		final AttributeDifference cut = new AttributeDifference( key, expected, null );

		cut.warnIfAttributesDontMatch( fromAttribute );

		final String log = "Mismatch for attribute '" + key + "': value from Golden Master '" + fromAttribute + "', "
				+ "value from test report '" + expected + "'. This could be due to a change in between.";

		logs.assertContains( log );
	}

	static Stream<Arguments> warnArgs() {
		return Stream.of( //
				Arguments.of( "something", null ), //
				Arguments.of( "something", "" ), //
				Arguments.of( null, "somethingElse" ), //
				Arguments.of( "", "somethingElse" ), //
				Arguments.of( "something", "somethingElse" ) );
	}

	@ParameterizedTest
	@MethodSource( "dontWarnArgs" )
	void should_not_warn_if_attributes_are_null_or_empty_or_match( final String expected, final String fromAttribute )
			throws Exception {
		final String key = "key";
		final AttributeDifference cut = new AttributeDifference( key, expected, null );

		cut.warnIfAttributesDontMatch( fromAttribute );

		assertThat( logs.getEvents() ).isEmpty();
	}

	static Stream<Arguments> dontWarnArgs() {
		return Stream.of( //
				Arguments.of( null, null ), //
				Arguments.of( "", null ), //
				Arguments.of( null, "" ), //
				Arguments.of( "", "" ), //
				Arguments.of( "unchanged", "unchanged" ) );
	}
}
```

### src/test/java/de/retest/recheck/ignore/JSFilterImplTest.java  (failing test)
```
package de.retest.recheck.ignore;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;

import java.awt.Rectangle;
import java.io.Reader;
import java.io.StringReader;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;

import de.retest.recheck.ignore.Filter.ChangeType;
import de.retest.recheck.ui.descriptors.Element;
import de.retest.recheck.ui.diff.AttributeDifference;
import io.github.netmikey.logunit.api.LogCapturer;

class JSFilterImplTest {

	@RegisterExtension
	LogCapturer warningAndErrorLogs = LogCapturer.create() //
			.captureForType( JSFilterImpl.class );

	Path ctorArg = Paths.get( "nonExistentFilterFile" );

	@Test
	void no_matches_function_should_not_cause_exception() {
		final JSFilterImpl cut = new JSFilterImpl( ctorArg ) {
			@Override
			Reader readScriptFile( final Path path ) {
				return new StringReader( "" );
			}
		};
		cut.matches( mock( Element.class ) );
	}

	@Test
	void invalid_matches_function_should_not_cause_exception() {
		final JSFilterImpl cut = new JSFilterImpl( ctorArg ) {
			@Override
			Reader readScriptFile( final Path path ) {
				return new StringReader( "asdasd.asd.asd();" );
			}
		};
		cut.matches( mock( Element.class ) );
	}

	@Test
	void nonexistent_file_should_not_cause_exception() {
		final JSFilterImpl cut = new JSFilterImpl( ctorArg ) {};
		cut.matches( mock( Element.class ) );
	}

	@Test
	void matches_should_be_called() {
		final JSFilterImpl cut = new JSFilterImpl( ctorArg ) {
			@Override
			Reader readScriptFile( final Path path ) {
				return new StringReader( "function matches(element) { return true; }" );
			}
		};
		assertThat( cut.matches( mock( Element.class ) ) ).isTrue();
	}

	@Test
	void matches_with_changetype_should_be_called() {
		final JSFilterImpl cut = new JSFilterImpl( ctorArg ) {
			@Override
			Reader readScriptFile( final Path path ) {
				return new StringReader( "function matches(element, changetype) { return changetype == 'inserted'; }" );
			}
		};
		assertThat( cut.matches( mock( Element.class ), ChangeType.INSERTED ) ).isTrue();
		assertThat( cut.matches( mock( Element.class ), ChangeType.DELETED ) ).isFalse();
		assertThat( cut.matches( mock( Element.class ), ChangeType.CHANGED ) ).isFalse();
	}

	@Test
	void matches_should_be_called_with_element_param() {
		final JSFilterImpl cut = new JSFilterImpl( ctorArg ) {
			@Override
			Reader readScriptFile( final Path path ) {
				return new StringReader( //
						"function matches(element) { " //
								+ "if (element != null) {" //
								+ "  return true;" //
								+ "} " //
								+ "  return false;" //
								+ "}" );
			}
		};
		assertThat( cut.matches( mock( Element.class ) ) ).isTrue();
	}

	@Test
	void matches_example_implementation() {
		final JSFilterImpl cut = new JSFilterImpl( ctorArg ) {
			@Override
			Reader readScriptFile( final Path path ) {
				return new StringReader( //
						"function matches(element, diff) { \n" //
								+ "  if (diff.key == 'outline') {\n" //
								+ "    return (Math.abs(diff.expected.x - diff.actual.x) <= 5) && \n" //
								+ "			  (Math.abs(diff.expected.y - diff.actual.y) <= 5) && \n" //
								+ "			  (Math.abs(diff.expected.width - diff.actual.width) <= 5) && \n" //
								+ "			  (Math.abs(diff.expected.height - diff.actual.height) <= 5);\n" //
								+ "  } \n" //
								+ "  return false;\n" //
								+ "}\n" );
			}
		};
		final Element element = mock( Element.class );
		assertThat( cut.matches( element, new AttributeDifference( "outline", new Rectangle( 580, 610, 200, 20 ),
				new Rectangle( 578, 605, 200, 20 ) ) ) ).isTrue();
		assertThat( cut.matches( element, new AttributeDifference( "outline", new Rectangle( 580, 610, 200, 20 ),
				new Rectangle( 500, 605, 200, 20 ) ) ) ).isFalse();
	}

	@Test
	void matches_return_null_should_be_false() {
		final JSFilterImpl cut = new JSFilterImpl( ctorArg ) {
			@Override
			Reader readScriptFile( final Path path ) {
				return new StringReader( //
						"function matches(element, diff) { " //
								+ "  return;" //
								+ "}" );
			}
		};
		final Element element = mock( Element.class );
		assertThat( cut.matches( element, new AttributeDifference( "outline", "580", "578" ) ) ).isFalse();
	}

	@Test
	void matches_return_non_boolean_should_not_throw_exc() {
		final JSFilterImpl cut = new JSFilterImpl( ctorArg ) {
			@Override
			Reader readScriptFile( final Path path ) {
				return new StringReader( //
						"function matches(element, diff) { " //
								+ "  return \"this is not a bool\";" //
								+ "}" );
			}
		};
		final Element element = mock( Element.class );
		assertThat( cut.matches( element, new AttributeDifference( "outline", "580", "578" ) ) ).isFalse();
	}

	@Test
	void matches_filter_URL_example_implementation() {
		final JSFilterImpl cut = new JSFilterImpl( ctorArg ) {
			@Override
			Reader readScriptFile( final Path path ) {
				return new StringReader( //
						"function matches(element, diff) {" //
								+ "  var re = /http[s]?:\\/\\/[\\w.:\\d\\-]*/;" //
								+ "  var expected = new String(diff.expected);" //
								+ "  var actual = new String(diff.actual);" //
								+ "  cleanExpected = expected.replace(re, '');" //
								+ "  cleanActual = actual.replace(re, '');" //
								+ "  return cleanExpected === cleanActual;" //
								+ "}" );
			}
		};
		final Element element = mock( Element.class );
		assertThat( cut.matches( element, new AttributeDifference( "background-image",
				"url(\"https://www2.test.k8s.bigcct.be/.imaging/default/dam/clients/BT_logo.svg.png/jcr:content.png\")",
				"url(\"http://icullen-website-public-spring4-8:8080/.imaging/default/dam/clients/BT_logo.svg.png/jcr:content.png\")" ) ) )
						.isTrue();
		assertThat( cut.matches( element, new AttributeDifference( "background-image",
				"url(\"https://www2.test.k8s.bigcct.be/.imaging/default/dam/clients/BT_logo.svg.png/jcr:content.png\")",
				"url(\"http://icullen-website-public-spring4-8:8080/some-other-URL.png\")" ) ) ).isFalse();
	}

	@Test
	void calling_erroneous_method_twice_with_different_args_should_actually_call_method() {
		final JSFilterImpl cut = new JSFilterImpl( ctorArg ) {
			@Override
			Reader readScriptFile( final Path path ) {
				return new StringReader( //
						"function matches(element) { " //
								+ "if (element != null) {" //
								+ "  return true;" //
								+ "}" //
								+ "throw 42;" //
								+ "}" );
			}
		};
		cut.matches( null );
		assertThat( cut.matches( mock( Element.class ) ) ).isTrue();
	}

	@Test
	void no_method_warning_should_only_be_printed_once_for_element() {
		final JSFilterImpl cut = new JSFilterImpl( ctorArg ) {
			@Override
			Reader readScriptFile( final Path path ) {
				return new StringReader( "" );
			}
		};
		cut.matches( mock( Element.class ) );
		cut.matches( mock( Element.class ) );
		assertThat( warningAndErrorLogs.size() ).isEqualTo( 1 );
	}

	@Test
	void no_method_warning_should_only_be_printed_once_for_element_and_diff() {
		final JSFilterImpl cut = new JSFilterImpl( ctorArg ) {
			@Override
			Reader readScriptFile( final Path path ) {
				return new StringReader( "" );
			}
		};
		cut.matches( mock( Element.class ), mock( AttributeDifference.class ) );
		cut.matches( mock( Element.class ), mock( AttributeDifference.class ) );
		assertThat( warningAndErrorLogs.size() ).isEqualTo( 1 );
	}
}
```

### src/test/java/de/retest/recheck/review/workers/MigrateIgnoreFileTest.java  (failing test)
```
package de.retest.recheck.review.workers;

import static de.retest.recheck.RecheckProperties.RETEST_FOLDER_NAME;
import static de.retest.recheck.configuration.ProjectConfiguration.RECHECK_IGNORE;
import static de.retest.recheck.configuration.ProjectConfiguration.RECHECK_IGNORE_JSRULES;
import static de.retest.recheck.configuration.ProjectConfiguration.RETEST_PROJECT_ROOT;
import static org.assertj.core.api.Assertions.assertThat;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.junit.jupiter.api.io.TempDir;
import org.junitpioneer.jupiter.ClearSystemProperty;

import de.retest.recheck.review.GlobalIgnoreApplier;
import de.retest.recheck.review.counter.NopCounter;
import de.retest.recheck.review.ignore.AttributeFilter.AttributeFilterLoader;
import de.retest.recheck.review.ignore.FilterPreserveLineLoader;
import de.retest.recheck.review.ignore.io.ErrorHandlingLoader;
import io.github.netmikey.logunit.api.LogCapturer;

class MigrateIgnoreFileTest {

	@RegisterExtension
	LogCapturer warningAndErrorLogs = LogCapturer.create() //
			.captureForType( AttributeFilterLoader.class ) //
			.captureForType( FilterPreserveLineLoader.class ) //
			.captureForType( ErrorHandlingLoader.class );

	Path configFolder;
	Path migratedIgnoreFile;
	Path tempIgnoreFile;

	@BeforeEach
	void setUp( @TempDir final Path temp ) throws Exception {
		configFolder = temp.resolve( RETEST_FOLDER_NAME );
		Files.createDirectory( configFolder );

		final Path jsIgnoreFile = configFolder.resolve( RECHECK_IGNORE_JSRULES );
		Files.createFile( jsIgnoreFile );

		final Path origIgnoreFile =
				Paths.get( "src/test/resources/de/retest/recheck/review/workers/legacy-recheck.ignore" );
		migratedIgnoreFile = Paths.get( "src/test/resources/de/retest/recheck/review/workers/" + RECHECK_IGNORE );
		tempIgnoreFile = configFolder.resolve( RECHECK_IGNORE );
		Files.copy( origIgnoreFile, tempIgnoreFile );

	}

	@Test
	@ClearSystemProperty( key = RETEST_PROJECT_ROOT )
	void loaded_ignore_file_should_be_migrated() throws Exception {
		System.setProperty( RETEST_PROJECT_ROOT, configFolder.toString() );
		final LoadFilterWorker load = new LoadFilterWorker( NopCounter.getInstance() );
		final GlobalIgnoreApplier gia = load.load();
		final SaveFilterWorker save = new SaveFilterWorker( gia );

		save.save();

		assertThat( tempIgnoreFile ).hasSameContentAs( migratedIgnoreFile );

		assertThat( warningAndErrorLogs.size() ).isEqualTo( 3 );
		warningAndErrorLogs.assertContains(
				"'attribute=possible-*regex' contains '*'. For regular expressions, please use 'attribute-regex=possible-*regex'." );
		warningAndErrorLogs.assertContains( "Please remove leading whitespace from the following line:\n" //
				+ " attribute:foo" );
		warningAndErrorLogs.assertContains(
				"For ignoring an attribute globally, please use 'attribute=' (to ensure weired line breaks do not break your ignore file)." );
	}

}
```

### src/test/java/de/retest/recheck/review/workers/LoadAndSaveFilterWorkerTest.java  (failing test)
```
package de.retest.recheck.review.workers;

import static de.retest.recheck.RecheckProperties.RETEST_FOLDER_NAME;
import static de.retest.recheck.configuration.ProjectConfiguration.RECHECK_IGNORE;
import static de.retest.recheck.configuration.ProjectConfiguration.RECHECK_IGNORE_JSRULES;
import static de.retest.recheck.configuration.ProjectConfiguration.RETEST_PROJECT_ROOT;
import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.stream.Stream;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.junit.jupiter.api.io.TempDir;
import org.junitpioneer.jupiter.ClearSystemProperty;

import de.retest.recheck.ignore.PersistentFilter;
import de.retest.recheck.review.GlobalIgnoreApplier;
import de.retest.recheck.review.counter.NopCounter;
import de.retest.recheck.review.ignore.AttributeFilter.AttributeFilterLoader;
import de.retest.recheck.review.ignore.FilterPreserveLineLoader;
import de.retest.recheck.review.ignore.io.ErrorHandlingLoader;
import io.github.netmikey.logunit.api.LogCapturer;

class LoadAndSaveFilterWorkerTest {

	@RegisterExtension
	LogCapturer warningAndErrorLogs = LogCapturer.create() //
			.captureForType( AttributeFilterLoader.class ) //
			.captureForType( FilterPreserveLineLoader.class ) //
			.captureForType( ErrorHandlingLoader.class );

	Path configFolder;
	Path origIgnoreFile;
	Path tempIgnoreFile;

	@BeforeEach
	void setUp( @TempDir final Path temp ) throws Exception {
		configFolder = temp.resolve( RETEST_FOLDER_NAME );
		Files.createDirectory( configFolder );

		final Path jsIgnoreFile = configFolder.resolve( RECHECK_IGNORE_JSRULES );
		Files.createFile( jsIgnoreFile );

		origIgnoreFile = Paths.get( "src/test/resources/de/retest/recheck/review/workers/" + RECHECK_IGNORE );
		tempIgnoreFile = configFolder.resolve( RECHECK_IGNORE );
		Files.copy( origIgnoreFile, tempIgnoreFile );

	}

	@Test
	@ClearSystemProperty( key = RETEST_PROJECT_ROOT )
	void loaded_ignore_file_should_be_saved_without_changes() throws Exception {
		System.setProperty( RETEST_PROJECT_ROOT, configFolder.toString() );
		final LoadFilterWorker load = new LoadFilterWorker( NopCounter.getInstance() ) {
			@Override
			protected Stream<PersistentFilter> getUserIgnoreFileFilters( final Path userIgnoreFile )
					throws IOException {
				return Stream.empty();
			}
		};
		final GlobalIgnoreApplier gia = load.load();
		final SaveFilterWorker save = new SaveFilterWorker( gia );

		save.save();

		assertThat( tempIgnoreFile ).hasSameContentAs( origIgnoreFile );

		assertThat( warningAndErrorLogs.size() ).isEqualTo( 3 );
		warningAndErrorLogs.assertContains(
				"'attribute=possible-*regex' contains '*'. For regular expressions, please use 'attribute-regex=possible-*regex'." );
		warningAndErrorLogs.assertContains( "Please remove leading whitespace from the following line:\n" //
				+ " attribute:foo" );
		warningAndErrorLogs.assertContains(
				"For ignoring an attribute globally, please use 'attribute=' (to ensure weired line breaks do not break your ignore file)." );
	}

}
```

### src/test/java/DefaultRecheckIgnoreTest.java  (failing test)
```
import static de.retest.recheck.ignore.FilterLoader.load;
import static java.nio.file.Paths.get;
import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;

import de.retest.recheck.review.ignore.io.ErrorHandlingLoader;
import io.github.netmikey.logunit.api.LogCapturer;

class DefaultRecheckIgnoreTest {

	@RegisterExtension
	LogCapturer warningAndErrorLogs = LogCapturer.create() //
			.captureForType( ErrorHandlingLoader.class );

	@Test
	void default_recheck_ignore_should_load_without_exception() throws Exception {
		load( get( getClass().getResource( "default-recheck.ignore" ).toURI() ) ).load();

		// Assert that no error was logged...
		assertThat( warningAndErrorLogs.size() ).isEqualTo( 0 );
	}

}
```

### src/test/java/DefaultRecheckIgnoreJsTest.java  (failing test)
```
import static org.assertj.core.api.Assertions.assertThat;

import java.nio.file.Paths;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.RegisterExtension;
import org.slf4j.event.Level;

import de.retest.recheck.ignore.JSFilterImpl;
import io.github.netmikey.logunit.api.LogCapturer;

public class DefaultRecheckIgnoreJsTest {

	@RegisterExtension
	LogCapturer warningAndErrorLogs = LogCapturer.create() //
			.forLevel( Level.WARN ) //
			.captureForType( JSFilterImpl.class );

	@Test
	void default_recheck_ignore_should_load_without_exception() throws Exception {
		new JSFilterImpl( Paths.get( getClass().getResource( "default-recheck.ignore.js" ).toURI() ) );

		// Assert that no error was logged...
		assertThat( warningAndErrorLogs.size() ).isEqualTo( 0 );
	}

}
```

### src/test/resources/persistence/simple_folder_persisted/retest.xml  (resource file named in the failing test)
```
<?xml version="1.0" encoding="UTF-8"?>
<reTestXmlDataContainer reTestVersion="unspecified development version" dataType="de.retest.recheck.persistence.xml.TestPersistable" dataTypeVersion="9001">
    <data xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="testPersistable"/>
</reTestXmlDataContainer>
```

### src/test/resources/retest/recheck/de.retest.recheck.RecheckImplIT legacy spaces/with legacy spaces.check.recheck/retest.xml  (resource file named in the failing test)
```
<?xml version="1.0" encoding="UTF-8"?>
<reTestXmlDataContainer xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" reTestVersion="${pom.parent.version}" dataType="de.retest.recheck.ui.descriptors.SutState" dataTypeVersion="4">
	<data xsi:type="sutState">
		<descriptors retestId="foo-id" screenId="0" screen="screen" title="title">
			<identifyingAttributes>
				<attributes>
					<attribute key="name" xsi:type="textAttribute">test</attribute>
					<attribute key="path" xsi:type="pathAttribute">foo[1]/bar[1]</attribute>
					<attribute key="suffix" xsi:type="suffixAttribute">1</attribute>
					<attribute key="text" xsi:type="textAttribute">test</attribute>
					<attribute key="type" xsi:type="stringAttribute">test</attribute>
				</attributes>
			</identifyingAttributes>
			<attributes>
				<attributes>
					<entry>
						<key>foo-1</key>
						<value xsi:type="xsd:string">bar-1</value>
					</entry>
					<entry>
						<key>foo-2</key>
						<value xsi:type="xsd:string">bar-2</value>
					</entry>
					<entry>
						<key>foo-3</key>
						<value xsi:type="xsd:string">bar-3</value>
					</entry>
				</attributes>
			</attributes>
			<containedElements retestId="same-id">
				<identifyingAttributes>
					<attributes>
						<attribute key="name" xsi:type="textAttribute">same</attribute>
						<attribute key="path" xsi:type="pathAttribute">foo[1]/bar[1]/same[1]</attribute>
						<attribute key="suffix" xsi:type="suffixAttribute">1</attribute>
						<attribute key="text" xsi:type="textAttribute">same</attribute>
						<attribute key="type" xsi:type="stringAttribute">same</attribute>
					</attributes>
				</identifyingAttributes>
				<attributes>
					<attributes>
						<entry>
							<key>bar-1</key>
							<value xsi:type="xsd:string">bar-1</value>
						</entry>
						<entry>
							<key>bar-2</key>
							<value xsi:type="xsd:string">bar-2</value>
						</entry>
						<entry>
							<key>bar-3</key>
							<value xsi:type="xsd:string">bar-3</value>
						</entry>
					</attributes>
				</attributes>
			</containedElements>
			<containedElements retestId="delete-id">
				<identifyingAttributes>
					<attributes>
						<attribute key="name" xsi:type="textAttribute">delete</attribute>
						<attribute key="path" xsi:type="pathAttribute">foo[1]/bar[1]/remove[1]/delete[1]</attribute>
						<attribute key="suffix" xsi:type="suffixAttribute">1</attribute>
						<attribute key="text" xsi:type="textAttribute">delete</attribute>
						<attribute key="type" xsi:type="stringAttribute">delete</attribute>
					</attributes>
				</identifyingAttributes>
				<attributes>
					<attributes>
						<entry>
							<key>bar-1</key>
							<value xsi:type="xsd:string">bar-1</value>
						</entry>
						<entry>
							<key>bar-2</key>
							<value xsi:type="xsd:string">bar-2</value>
						</entry>
						<entry>
							<key>bar-3</key>
							<value xsi:type="xsd:string">bar-3</value>
						</entry>
					</attributes>
				</attributes>
			</containedElements>
		</descriptors>
	</data>
</reTestXmlDataContainer>
```

### src/test/resources/retest/recheck/de.retest.recheck.RecheckImplIT spaces/with spaces.check.recheck/retest.xml  (resource file named in the failing test)
```
<?xml version="1.0" encoding="UTF-8"?>
<reTestXmlDataContainer xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" reTestVersion="${pom.parent.version}" dataType="de.retest.recheck.ui.descriptors.SutState" dataTypeVersion="4">
	<data xsi:type="sutState">
		<descriptors retestId="foo-id" screenId="0" screen="screen" title="title">
			<identifyingAttributes>
				<attributes>
					<attribute key="name" xsi:type="textAttribute">test</attribute>
					<attribute key="path" xsi:type="pathAttribute">foo[1]/bar[1]</attribute>
					<attribute key="suffix" xsi:type="suffixAttribute">1</attribute>
					<attribute key="text" xsi:type="textAttribute">test</attribute>
					<attribute key="type" xsi:type="stringAttribute">test</attribute>
				</attributes>
			</identifyingAttributes>
			<attributes>
				<attributes>
					<entry>
						<key>foo-1</key>
						<value xsi:type="xsd:string">bar-1</value>
					</entry>
					<entry>
						<key>foo-2</key>
						<value xsi:type="xsd:string">bar-2</value>
					</entry>
					<entry>
						<key>foo-3</key>
						<value xsi:type="xsd:string">bar-3</value>
					</entry>
				</attributes>
			</attributes>
			<containedElements retestId="same-id">
				<identifyingAttributes>
					<attributes>
						<attribute key="name" xsi:type="textAttribute">same</attribute>
						<attribute key="path" xsi:type="pathAttribute">foo[1]/bar[1]/same[1]</attribute>
						<attribute key="suffix" xsi:type="suffixAttribute">1</attribute>
						<attribute key="text" xsi:type="textAttribute">same</attribute>
						<attribute key="type" xsi:type="stringAttribute">same</attribute>
					</attributes>
				</identifyingAttributes>
				<attributes>
					<attributes>
						<entry>
							<key>bar-1</key>
							<value xsi:type="xsd:string">bar-1</value>
						</entry>
						<entry>
							<key>bar-2</key>
							<value xsi:type="xsd:string">bar-2</value>
						</entry>
						<entry>
							<key>bar-3</key>
							<value xsi:type="xsd:string">bar-3</value>
						</entry>
					</attributes>
				</attributes>
			</containedElements>
			<containedElements retestId="delete-id">
				<identifyingAttributes>
					<attributes>
						<attribute key="name" xsi:type="textAttribute">delete</attribute>
						<attribute key="path" xsi:type="pathAttribute">foo[1]/bar[1]/remove[1]/delete[1]</attribute>
						<attribute key="suffix" xsi:type="suffixAttribute">1</attribute>
						<attribute key="text" xsi:type="textAttribute">delete</attribute>
						<attribute key="type" xsi:type="stringAttribute">delete</attribute>
					</attributes>
				</identifyingAttributes>
				<attributes>
					<attributes>
						<entry>
							<key>bar-1</key>
							<value xsi:type="xsd:string">bar-1</value>
						</entry>
						<entry>
							<key>bar-2</key>
							<value xsi:type="xsd:string">bar-2</value>
						</entry>
						<entry>
							<key>bar-3</key>
							<value xsi:type="xsd:string">bar-3</value>
						</entry>
					</attributes>
				</attributes>
			</containedElements>
		</descriptors>
	</data>
</reTestXmlDataContainer>
```

### src/test/resources/retest/recheck/de.retest.recheck.RecheckImplIT/filter-deleted.check.recheck/retest.xml  (resource file named in the failing test)
```
<?xml version="1.0" encoding="UTF-8"?>
<reTestXmlDataContainer xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" reTestVersion="${pom.parent.version}" dataType="de.retest.recheck.ui.descriptors.SutState" dataTypeVersion="4">
	<data xsi:type="sutState">
		<descriptors retestId="foo-id" screenId="0" screen="screen" title="title">
			<identifyingAttributes>
				<attributes>
					<attribute key="name" xsi:type="textAttribute">test</attribute>
					<attribute key="path" xsi:type="pathAttribute">foo[1]/bar[1]</attribute>
					<attribute key="suffix" xsi:type="suffixAttribute">1</attribute>
					<attribute key="text" xsi:type="textAttribute">test</attribute>
					<attribute key="type" xsi:type="stringAttribute">test</attribute>
				</attributes>
			</identifyingAttributes>
			<attributes>
				<attributes>
					<entry>
						<key>foo-1</key>
						<value xsi:type="xsd:string">bar-1</value>
					</entry>
					<entry>
						<key>foo-2</key>
						<value xsi:type="xsd:string">bar-2</value>
					</entry>
					<entry>
						<key>foo-3</key>
						<value xsi:type="xsd:string">bar-3</value>
					</entry>
				</attributes>
			</attributes>
			<containedElements retestId="same-id">
				<identifyingAttributes>
					<attributes>
						<attribute key="name" xsi:type="textAttribute">same</attribute>
						<attribute key="path" xsi:type="pathAttribute">foo[1]/bar[1]/same[1]</attribute>
						<attribute key="suffix" xsi:type="suffixAttribute">1</attribute>
						<attribute key="text" xsi:type="textAttribute">same</attribute>
						<attribute key="type" xsi:type="stringAttribute">same</attribute>
					</attributes>
				</identifyingAttributes>
				<attributes>
					<attributes>
						<entry>
							<key>bar-1</key>
							<value xsi:type="xsd:string">bar-1</value>
						</entry>
						<entry>
							<key>bar-2</key>
							<value xsi:type="xsd:string">bar-2</value>
						</entry>
						<entry>
							<key>bar-3</key>
							<value xsi:type="xsd:string">bar-3</value>
						</entry>
					</attributes>
				</attributes>
			</containedElements>
			<containedElements retestId="delete-id">
				<identifyingAttributes>
					<attributes>
						<attribute key="name" xsi:type="textAttribute">delete</attribute>
						<attribute key="path" xsi:type="pathAttribute">foo[1]/bar[1]/remove[1]/delete[1]</attribute>
						<attribute key="suffix" xsi:type="suffixAttribute">1</attribute>
						<attribute key="text" xsi:type="textAttribute">delete</attribute>
						<attribute key="type" xsi:type="stringAttribute">delete</attribute>
					</attributes>
				</identifyingAttributes>
				<attributes>
					<attributes>
						<entry>
							<key>bar-1</key>
							<value xsi:type="xsd:string">bar-1</value>
						</entry>
						<entry>
							<key>bar-2</key>
							<value xsi:type="xsd:string">bar-2</value>
						</entry>
						<entry>
							<key>bar-3</key>
							<value xsi:type="xsd:string">bar-3</value>
						</entry>
					</attributes>
				</attributes>
			</containedElements>
		</descriptors>
	</data>
</reTestXmlDataContainer>
```

### src/test/resources/retest/recheck/de.retest.recheck.RecheckImplIT/filter.check.recheck/retest.xml  (resource file named in the failing test)
```
<?xml version="1.0" encoding="UTF-8"?>
<reTestXmlDataContainer xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" reTestVersion="${pom.parent.version}" dataType="de.retest.recheck.ui.descriptors.SutState" dataTypeVersion="4">
	<data xsi:type="sutState">
		<descriptors retestId="foo-id" screenId="0" screen="screen" title="title">
			<identifyingAttributes>
				<attributes>
					<attribute key="name" xsi:type="textAttribute">test</attribute>
					<attribute key="path" xsi:type="pathAttribute">foo[1]/bar[1]</attribute>
					<attribute key="suffix" xsi:type="suffixAttribute">1</attribute>
					<attribute key="text" xsi:type="textAttribute">test</attribute>
					<attribute key="type" xsi:type="stringAttribute">test</attribute>
				</attributes>
			</identifyingAttributes>
			<attributes>
				<attributes>
					<entry>
						<key>foo-1</key>
						<value xsi:type="xsd:string">bar-1</value>
					</entry>
					<entry>
						<key>foo-2</key>
						<value xsi:type="xsd:string">bar-2</value>
					</entry>
					<entry>
						<key>foo-3</key>
						<value xsi:type="xsd:string">bar-3</value>
					</entry>
				</attributes>
			</attributes>
			<containedElements retestId="same-id">
				<identifyingAttributes>
					<attributes>
						<attribute key="name" xsi:type="textAttribute">same</attribute>
						<attribute key="path" xsi:type="pathAttribute">foo[1]/bar[1]/same[1]</attribute>
						<attribute key="suffix" xsi:type="suffixAttribute">1</attribute>
						<attribute key="text" xsi:type="textAttribute">same</attribute>
						<attribute key="type" xsi:type="stringAttribute">same</attribute>
					</attributes>
				</identifyingAttributes>
				<attributes>
					<attributes>
						<entry>
							<key>bar-1</key>
							<value xsi:type="xsd:string">bar-1</value>
						</entry>
						<entry>
							<key>bar-2</key>
							<value xsi:type="xsd:string">bar-2</value>
						</entry>
						<entry>
							<key>bar-3</key>
							<value xsi:type="xsd:string">bar-3</value>
						</entry>
					</attributes>
				</attributes>
			</containedElements>
			<containedElements retestId="delete-id">
				<identifyingAttributes>
					<attributes>
						<attribute key="name" xsi:type="textAttribute">delete</attribute>
						<attribute key="path" xsi:type="pathAttribute">foo[1]/bar[1]/remove[1]/delete[1]</attribute>
						<attribute key="suffix" xsi:type="suffixAttribute">1</attribute>
						<attribute key="text" xsi:type="textAttribute">delete</attribute>
						<attribute key="type" xsi:type="stringAttribute">delete</attribute>
					</attributes>
				</identifyingAttributes>
				<attributes>
					<attributes>
						<entry>
							<key>bar-1</key>
							<value xsi:type="xsd:string">bar-1</value>
						</entry>
						<entry>
							<key>bar-2</key>
							<value xsi:type="xsd:string">bar-2</value>
						</entry>
						<entry>
							<key>bar-3</key>
							<value xsi:type="xsd:string">bar-3</value>
						</entry>
					</attributes>
				</attributes>
			</containedElements>
		</descriptors>
	</data>
</reTestXmlDataContainer>
```

### src/test/resources/retest/recheck/de.retest.recheck.RecheckImplIT/no-filter.check.recheck/retest.xml  (resource file named in the failing test)
```
<?xml version="1.0" encoding="UTF-8"?>
<reTestXmlDataContainer xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" reTestVersion="${pom.parent.version}" dataType="de.retest.recheck.ui.descriptors.SutState" dataTypeVersion="4">
	<data xsi:type="sutState">
		<descriptors retestId="foo-id" screenId="0" screen="screen" title="title">
			<identifyingAttributes>
				<attributes>
					<attribute key="name" xsi:type="textAttribute">test</attribute>
					<attribute key="path" xsi:type="pathAttribute">foo[1]/bar[1]</attribute>
					<attribute key="suffix" xsi:type="suffixAttribute">1</attribute>
					<attribute key="text" xsi:type="textAttribute">test</attribute>
					<attribute key="type" xsi:type="stringAttribute">test</attribute>
				</attributes>
			</identifyingAttributes>
			<attributes>
				<attributes>
					<entry>
						<key>foo-1</key>
						<value xsi:type="xsd:string">bar-1</value>
					</entry>
					<entry>
						<key>foo-2</key>
						<value xsi:type="xsd:string">bar-2</value>
					</entry>
					<entry>
						<key>foo-3</key>
						<value xsi:type="xsd:string">bar-3</value>
					</entry>
				</attributes>
			</attributes>
			<containedElements retestId="same-id">
				<identifyingAttributes>
					<attributes>
						<attribute key="name" xsi:type="textAttribute">same</attribute>
						<attribute key="path" xsi:type="pathAttribute">foo[1]/bar[1]/same[1]</attribute>
						<attribute key="suffix" xsi:type="suffixAttribute">1</attribute>
						<attribute key="text" xsi:type="textAttribute">same</attribute>
						<attribute key="type" xsi:type="stringAttribute">same</attribute>
					</attributes>
				</identifyingAttributes>
				<attributes>
					<attributes>
						<entry>
							<key>bar-1</key>
							<value xsi:type="xsd:string">bar-1</value>
						</entry>
						<entry>
							<key>bar-2</key>
							<value xsi:type="xsd:string">bar-2</value>
						</entry>
						<entry>
							<key>bar-3</key>
							<value xsi:type="xsd:string">bar-3</value>
						</entry>
					</attributes>
				</attributes>
			</containedElements>
			<containedElements retestId="delete-id">
				<identifyingAttributes>
					<attributes>
						<attribute key="name" xsi:type="textAttribute">delete</attribute>
						<attribute key="path" xsi:type="pathAttribute">foo[1]/bar[1]/remove[1]/delete[1]</attribute>
						<attribute key="suffix" xsi:type="suffixAttribute">1</attribute>
						<attribute key="text" xsi:type="textAttribute">delete</attribute>
						<attribute key="type" xsi:type="stringAttribute">delete</attribute>
					</attributes>
				</identifyingAttributes>
				<attributes>
					<attributes>
						<entry>
							<key>bar-1</key>
							<value xsi:type="xsd:string">bar-1</value>
						</entry>
						<entry>
							<key>bar-2</key>
							<value xsi:type="xsd:string">bar-2</value>
						</entry>
						<entry>
							<key>bar-3</key>
							<value xsi:type="xsd:string">bar-3</value>
						</entry>
					</attributes>
				</attributes>
			</containedElements>
		</descriptors>
	</data>
</reTestXmlDataContainer>
```


Now write the explanation and the single ```diff block.
