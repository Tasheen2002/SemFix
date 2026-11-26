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
`commons-io:commons-io` was updated from `2.7` to `2.11.0`. The project compiles, but tests now fail.

## Failure (from the build log)
Failing test classes: net.masterthought.cucumber.ReportBuilderTest
Exception types: java.lang.IllegalArgumentException
Error lines:
- java.lang.IllegalArgumentException: Parameter 'srcFile' is not a file: src/test/resources/js
SLF4J console output:
- SLF4J: Failed to load class "org.slf4j.impl.StaticLoggerBinder".
- SLF4J: Defaulting to no-operation (NOP) logger implementation
- SLF4J: See http://www.slf4j.org/codes.html#StaticLoggerBinder for further details.
Project stack frames:
- net.masterthought.cucumber.ReportBuilder (ReportBuilder.java:174)
- net.masterthought.cucumber.ReportBuilderTest (ReportBuilderTest.java:228)

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

### Past case 2: org.slf4j:slf4j-api 1.7.36 -> 2.0.3 (retest/recheck)
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
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>net.masterthought</groupId>
    <artifactId>cucumber-reporting</artifactId>
    <packaging>jar</packaging>
    <version>5.7.6-SNAPSHOT</version>
    <name>cucumber-reporting</name>
    <url>https://github.com/damianszczepanik/cucumber-reporting</url>

    <properties>
        <project.reporting.outputEncoding>UTF-8</project.reporting.outputEncoding>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <project.build.resourceEncoding>UTF-8</project.build.resourceEncoding>
        <maven.compile.encoding>UTF-8</maven.compile.encoding>

        <powermock.version>1.7.3</powermock.version>
        <jackson.version>2.13.2.20220328</jackson.version>
        <jmockit.version>1.34</jmockit.version> <!-- last version that supports reflections -->

        <test.integration.pattern>**/*IntegrationTest*.java</test.integration.pattern>
    </properties>

    <parent>
        <groupId>org.sonatype.oss</groupId>
        <artifactId>oss-parent</artifactId>
        <version>7</version>
    </parent>

    <distributionManagement>
        <snapshotRepository>
            <id>ossrh</id>
            <url>https://oss.sonatype.org/content/repositories/snapshots</url>
        </snapshotRepository>
        <repository>
            <id>ossrh</id>
            <url>https://oss.sonatype.org/service/local/staging/deploy/maven2/</url>
        </repository>
    </distributionManagement>

    <scm>
        <connection>scm:git:git@github.com:damianszczepanik/cucumber-reporting.git</connection>
        <developerConnection>scm:git:git@github.com:damianszczepanik/cucumber-reporting.git</developerConnection>
        <url>git@github.com:damianszczepanik/cucumber-reporting.git</url>
    </scm>
    <ciManagement>
        <system>travis</system>
        <url>https://travis-ci.com/github/damianszczepanik/cucumber-reporting</url>
    </ciManagement>

    <description>
        Provides pretty html reports for Cucumber. It works by generating html from the cucumber json file.
    </description>

    <licenses>
        <license>
            <name>LGPL 2.1</name>
            <url>http://www.gnu.org/licenses/lgpl-2.1.html</url>
        </license>
    </licenses>

    <developers>
        <developer>
            <id>damianszczepanik</id>
            <name>Damian Szczepanik</name>
            <email>damianszczepanik@github</email>
        </developer>
        <developer>
            <id>kingsleyh</id>
            <name>Kingsley Hendrickse</name>
            <email>kingsley.hendrickse@gmail.com</email>
        </developer>
    </developers>

    <profiles>
        <profile>
            <id>release-sign-artifacts</id>
            <activation>
                <property>
                    <!-- will be set by the release plugin upon performing
                         mvn release:clean release:prepare release:perform -->
                    <name>performRelease</name>
                    <value>true</value>
                </property>
            </activation>

            <properties>
                <gpg.keyname>0738FA8F</gpg.keyname>
                <release.username>Damian Szczepanik</release.username>
            </properties>

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

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
                <configuration>
                    <source>1.8</source>
                    <target>1.8</target>
                    <encoding>UTF-8</encoding>
                </configuration>
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
                <artifactId>maven-javadoc-plugin</artifactId>
                <version>3.2.0</version>
                <configuration>
                    <source>8</source>
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
                <groupId>org.jacoco</groupId>
                <artifactId>jacoco-maven-plugin</artifactId>
                <version>0.8.6</version>
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
                <artifactId>maven-surefire-plugin</artifactId>
                <version>2.18.1</version>
                <configuration>
                    <systemPropertyVariables>
                        <!-- JaCoCo runtime must know where to dump coverage: -->
                        <jacoco-agent.destfile>target/jacoco.exec</jacoco-agent.destfile>
                    </systemPropertyVariables>
                    <excludes>
                        <!-- Integration tests should not be counted by code coverage -->
                        <exclude>${test.integration.pattern}</exclude>
                    </excludes>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-failsafe-plugin</artifactId>
                <version>2.22.2</version>
                <configuration>
                    <includes>
                        <!-- Run only integration tests -->
                        <include>${test.integration.pattern}</include>
                    </includes>
                </configuration>
                <executions>
                    <execution>
                        <goals>
                            <goal>integration-test</goal>
                            <goal>verify</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>

    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>com.fasterxml.jackson</groupId>
                <artifactId>jackson-bom</artifactId>
                <version>${jackson.version}</version>
                <type>pom</type>
                <scope>import</scope>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <dependencies>
        <dependency>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
        </dependency>
        <dependency>
            <groupId>com.fasterxml.jackson.datatype</groupId>
            <artifactId>jackson-datatype-jsr310</artifactId>
        </dependency>
        <dependency>
            <groupId>org.apache.velocity</groupId>
            <artifactId>velocity-engine-core</artifactId>
            <version>2.3</version>
        </dependency>
        <dependency>
            <groupId>joda-time</groupId>
            <artifactId>joda-time</artifactId>
            <version>2.12.2</version>
        </dependency>
        <dependency>
            <groupId>org.apache.commons</groupId>
            <artifactId>commons-lang3</artifactId>
            <version>3.12.0</version>
        </dependency>
        <dependency>
            <groupId>commons-io</groupId>
            <artifactId>commons-io</artifactId>
            <version>2.11.0</version>
        </dependency>
        <dependency>
            <groupId>org.codehaus.plexus</groupId>
            <artifactId>plexus-utils</artifactId>
            <version>3.5.0</version>
        </dependency>
        <dependency>
            <groupId>org.jsoup</groupId>
            <artifactId>jsoup</artifactId>
            <version>1.15.4</version>
        </dependency>
        <dependency>
            <groupId>com.googlecode.owasp-java-html-sanitizer</groupId>
            <artifactId>owasp-java-html-sanitizer</artifactId>
            <version>20220608.1</version>
        </dependency>

        <!-- for testing -->
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.2</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.jmockit</groupId>
            <artifactId>jmockit</artifactId>
            <version>${jmockit.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.powermock</groupId>
            <artifactId>powermock-api-mockito</artifactId>
            <version>${powermock.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.powermock</groupId>
            <artifactId>powermock-module-junit4</artifactId>
            <version>${powermock.version}</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>org.assertj</groupId>
            <artifactId>assertj-core</artifactId>
            <version>3.24.2</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>commons-configuration</groupId>
            <artifactId>commons-configuration</artifactId>
            <version>1.10</version>
        </dependency>
    </dependencies>
</project>
```

### src/test/java/net/masterthought/cucumber/ReportBuilderTest.java  (failing test)
```
... (lines 0-0 omitted)
package net.masterthought.cucumber;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.assertj.core.api.Assertions.fail;

import java.io.File;
import java.io.FileFilter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import mockit.Deencapsulation;
import net.masterthought.cucumber.generators.OverviewReport;
import net.masterthought.cucumber.json.Feature;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.filefilter.WildcardFileFilter;
import org.junit.Before;
import org.junit.Test;

/**
 * @author Damian Szczepanik (damianszczepanik@github)
 */
public class ReportBuilderTest extends ReportGenerator {

    private File reportDirectory;
    private File trendsFileTmp;

    @Before
    public void setUp() throws IOException {
        reportDirectory = new File("target", String.valueOf(System.currentTimeMillis()));
        // random temp directory
        reportDirectory.mkdirs();
        // root report directory
        new File(reportDirectory, ReportBuilder.BASE_DIRECTORY + configuration.getDirectorySuffixWithSeparator()).mkdir();
... (lines 41-187 omitted)
        Configuration configuration = new Configuration(reportDirectory, "myProject");
        ReportBuilder builder = new ReportBuilder(Collections.<String>emptyList(), configuration);
        File dir = new File(reportDirectory, ReportBuilder.BASE_DIRECTORY + configuration.getDirectorySuffixWithSeparator());

        // then
        try {
            Deencapsulation.invoke(builder, "copyResources", dir.getAbsolutePath(), new String[]{"someFile"});
            fail("Copying should fail!");
            // exception depends of operating system
        } catch (ValidationException | NullPointerException e) {
            // passed
        }
    }

    @Test
    public void copyCustomResources_OnInvalidPath_DoesNotThrowsException() {

        // given
        Configuration configuration = new Configuration(reportDirectory, "myProject");
        ReportBuilder builder = new ReportBuilder(Collections.emptyList(), configuration);
        File srcFile = new File("non-existent.file");
        File dstFile = Deencapsulation.invoke(builder, "createTempFile", "js", srcFile.getName());

        // when
        Deencapsulation.invoke(builder, "copyCustomResources", "js", srcFile);

        // then
        assertThat(dstFile).doesNotExist();
    }

    @Test
    public void copyCustomResources_OnDirAsFile_ThrowsIOException() {

        // given
        Configuration configuration = new Configuration(reportDirectory, "myProject");
        ReportBuilder builder = new ReportBuilder(Collections.<String>emptyList(), configuration);
        File dir = new File("src/test/resources/js");

        // then
        try {
            Deencapsulation.invoke(builder, "copyCustomResources", "js", dir);
            fail("Copying should fail!");
            // exception depends of operating system
        } catch (ValidationException e) {
            // passed
        }
    }

    @Test
    public void copyCustomResources_CheckCopiedFiles() {

        // given
        Configuration configuration = new Configuration(reportDirectory, "myProject");
        configuration.addCustomJsFiles(Collections.singletonList("src/test/resources/js/test.js"));
        configuration.addCustomCssFiles(Collections.singletonList("src/test/resources/css/test.css"));
        ReportBuilder builder = new ReportBuilder(Collections.<String>emptyList(), configuration);

        // when
        Deencapsulation.invoke(builder, "copyCustomJsAndCssResources");

        // then
        assertPageExists(reportDirectory, configuration.getDirectorySuffixWithSeparator(), "/js/test.js");
        assertPageExists(reportDirectory, configuration.getDirectorySuffixWithSeparator(), "/css/test.css");
    }

    @Test
    public void collectPages_CollectsPages() {

        // given
        setUpWithJson(SAMPLE_JSON);

        ReportBuilder builder = new ReportBuilder(jsonReports, configuration);
        Deencapsulation.setField(builder, "reportResult", new ReportResult(features, configuration));

        // when
        Deencapsulation.invoke(builder, "generatePages", new Trends());

        // then
        assertThat(countHtmlFiles(configuration)).hasSize(9);
    }
```

### src/test/resources/json/empty.json  (resource file named in the failing test)
```
[
]
```

### src/main/java/net/masterthought/cucumber/ReportBuilder.java  (class in the failing stack trace)
```
package net.masterthought.cucumber;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.io.Reader;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;

import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import com.fasterxml.jackson.databind.SerializationFeature;
import net.masterthought.cucumber.generators.ErrorPage;
import net.masterthought.cucumber.generators.FailuresOverviewPage;
import net.masterthought.cucumber.generators.FeatureReportPage;
import net.masterthought.cucumber.generators.FeaturesOverviewPage;
import net.masterthought.cucumber.generators.StepsOverviewPage;
import net.masterthought.cucumber.generators.TagReportPage;
import net.masterthought.cucumber.generators.TagsOverviewPage;
import net.masterthought.cucumber.generators.TrendsOverviewPage;
import net.masterthought.cucumber.json.Feature;
import net.masterthought.cucumber.json.support.TagObject;
import org.apache.commons.io.FileUtils;

public class ReportBuilder {

    private static final Logger LOG = Logger.getLogger(ReportBuilder.class.getName());

    /**
     * Page that should be displayed when the reports is generated. Shared between {@link FeaturesOverviewPage} and
     * {@link ErrorPage}.
     */
    public static final String HOME_PAGE = "overview-features.html";

    /**
     * Subdirectory where the report will be created.
     */
    public static final String BASE_DIRECTORY = "cucumber-html-reports";
    /**
     * Separator between main directory name and specified suffix
     */
    public static final String SUFFIX_SEPARATOR = "_";


    private static final ObjectMapper mapper = new ObjectMapper();

    private ReportResult reportResult;
    private final ReportParser reportParser;

    private Configuration configuration;
    private List<String> jsonFiles;

    /**
     * Flag used to detect if the file with updated trends is saved.
     * If the report crashes and the trends was not saved then it tries to save trends again with empty data
     * to mark that the build crashed.
     */
    private boolean wasTrendsFileSaved = false;

    public ReportBuilder(List<String> jsonFiles, Configuration configuration) {
        this.jsonFiles = jsonFiles;
        this.configuration = configuration;
        reportParser = new ReportParser(configuration);
    }

    /**
     * Parses provided files and generates the report. When generating process fails
     * report with information about error is provided.
     *
     * @return stats for the generated report
     */
    public Reportable generateReports() {
        Trends trends = null;

        try {
            // first copy static resources so ErrorPage is displayed properly
            copyStaticResources();

            // copy custom js and css resources if specific in configuration
            copyCustomJsAndCssResources();

            // create directory for embeddings before files are generated
            createEmbeddingsDirectory();

            // add metadata info sourced from files
            reportParser.parseClassificationsFiles(configuration.getClassificationFiles());

            // parse json files for results
            List<Feature> features = reportParser.parseJsonFiles(jsonFiles);
            reportResult = new ReportResult(features, configuration);
            Reportable reportable = reportResult.getFeatureReport();

            if (configuration.isTrendsAvailable()) {
                // prepare data required by generators, collect generators and generate pages
                trends = updateAndSaveTrends(reportable);
            }

            // Collect and generate pages in a single pass
            generatePages(trends);

            return reportable;

            // whatever happens we want to provide at least error page instead of incomplete report or exception
        } catch (Exception e) {
            generateErrorPage(e);
            // update trends so there is information in history that the build failed

            // if trends was not created then something went wrong
            // and information about build failure should be saved
            if (!wasTrendsFileSaved && configuration.isTrendsAvailable()) {
                Reportable reportable = new EmptyReportable();
                updateAndSaveTrends(reportable);
            }

            // something went wrong, don't pass result that might be incomplete
            return null;
        }
    }

    private void copyCustomJsAndCssResources() {
        for (String jsFile : configuration.getCustomJsFiles()) {
            File file = new File(jsFile);
            copyCustomResources("js", file);
        }

        for (String cssFile : configuration.getCustomCssFiles()) {
            File file = new File(cssFile);
            copyCustomResources("css", file);
        }
    }

    private void copyStaticResources() {
        copyResources("css", "cucumber.css", "bootstrap.min.css", "font-awesome.min.css");
        copyResources("js", "jquery.min.js", "jquery.tablesorter.min.js", "bootstrap.min.js", "Chart.min.js",
                "moment.min.js");
        copyResources("fonts", "FontAwesome.otf", "fontawesome-webfont.svg", "fontawesome-webfont.woff",
                "fontawesome-webfont.eot", "fontawesome-webfont.ttf", "fontawesome-webfont.woff2",
                "glyphicons-halflings-regular.eot", "glyphicons-halflings-regular.eot",
                "glyphicons-halflings-regular.woff2", "glyphicons-halflings-regular.woff",
                "glyphicons-halflings-regular.ttf", "glyphicons-halflings-regular.svg");
        copyResources("images", "favicon.png");
    }

    private void createEmbeddingsDirectory() {
        configuration.getEmbeddingDirectory().mkdirs();
    }

    private void copyResources(String resourceLocation, String... resources) {
        for (String resource : resources) {
            File tempFile = createTempFile(resourceLocation, resource);
            // don't change this implementation unless you verified it works on Jenkins
            try {
                FileUtils.copyInputStreamToFile(
                        this.getClass().getResourceAsStream("/" + resourceLocation + "/" + resource), tempFile);
            } catch (IOException e) {
                // based on FileUtils implementation, should never happen even is declared
                throw new ValidationException(e);
            }
        }
    }

    private void copyCustomResources(String resourceLocation, File srcFile) {
        File tempFile = createTempFile(resourceLocation, srcFile.getName());

        try {
            FileUtils.copyFile(srcFile, tempFile);
        } catch (FileNotFoundException e) {
            LOG.log(Level.WARNING, "File not found: {0}", srcFile.getAbsolutePath());
            LOG.log(Level.FINE, "", e);
        } catch (IOException e) {
            throw new ValidationException(e);
        }
    }

    private File createTempFile(String resourceLocation, String resource) {
        return new File(configuration.getReportDirectory().getAbsoluteFile(),
                BASE_DIRECTORY + configuration.getDirectorySuffixWithSeparator() + File.separatorChar + resourceLocation + File.separatorChar + resource);
    }

    private void generatePages(Trends trends) {
        new FeaturesOverviewPage(reportResult, configuration).generatePage();

        for (Feature feature : reportResult.getAllFeatures()) {
            new FeatureReportPage(reportResult, configuration, feature).generatePage();
        }

        new TagsOverviewPage(reportResult, configuration).generatePage();

        for (TagObject tagObject : reportResult.getAllTags()) {
            new TagReportPage(reportResult, configuration, tagObject).generatePage();
        }

        new StepsOverviewPage(reportResult, configuration).generatePage();
        new FailuresOverviewPage(reportResult, configuration).generatePage();

        if (configuration.isTrendsAvailable()) {
            new TrendsOverviewPage(reportResult, configuration, trends).generatePage();
        }
    }


    private Trends updateAndSaveTrends(Reportable reportable) {
        Trends trends = loadOrCreateTrends();
        appendToTrends(trends, reportable);

        // display only last n items - don't skip items if limit is not defined
        if (configuration.getTrendsLimit() > 0) {
            trends.limitItems(configuration.getTrendsLimit());
        }

        // save updated trends so it contains history only for the last builds
        saveTrends(trends, configuration.getTrendsStatsFile());

        return trends;
    }

    private Trends loadOrCreateTrends() {
        File trendsFile = configuration.getTrendsStatsFile();
        if (trendsFile != null && trendsFile.exists()) {
            return loadTrends(trendsFile);
        } else {
            return new Trends();
        }
    }

    private static Trends loadTrends(File file) {
        try (Reader reader = new InputStreamReader(new FileInputStream(file), StandardCharsets.UTF_8)) {
            return mapper.readValue(reader, Trends.class);
        } catch (JsonMappingException e) {
            throw new ValidationException(String.format("File '%s' could not be parsed as file with trends!", file), e);
        } catch (IOException e) {
            // IO problem - stop generating and re-throw the problem
            throw new ValidationException(e);
        }
    }

    private void appendToTrends(Trends trends, Reportable result) {
        trends.addBuild(configuration.getBuildNumber(), result);
    }

    private void saveTrends(Trends trends, File file) {
        ObjectWriter objectWriter = mapper.writer().with(SerializationFeature.INDENT_OUTPUT);
        try (Writer writer = new OutputStreamWriter(new FileOutputStream(file), StandardCharsets.UTF_8)) {
            objectWriter.writeValue(writer, trends);
            wasTrendsFileSaved = true;
        } catch (IOException e) {
            wasTrendsFileSaved = false;
            throw new ValidationException("Could not save updated trends in file: " + file.getAbsolutePath(), e);
        }
    }

    private void generateErrorPage(Exception exception) {
        LOG.log(Level.WARNING, "Unexpected error", exception);
        ErrorPage errorPage = new ErrorPage(reportResult, configuration, exception, jsonFiles);
        errorPage.generatePage();
    }
}
```


Now write the explanation and the single ```diff block.
