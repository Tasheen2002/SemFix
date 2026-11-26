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
`com.thoughtworks.xstream:xstream` was updated from `1.4.17` to `1.4.19`. The project compiles, but tests now fail.

## Failure (from the build log)
Failing test classes: org.apache.log4j.chainsaw.LogPanelPreferenceModelTest
Exception types: com.thoughtworks.xstream.security.ForbiddenClassException
Error lines:
- com.thoughtworks.xstream.security.ForbiddenClassException: org.apache.log4j.chainsaw.LogPanelPreferenceModel
Project stack frames:
- org.apache.log4j.chainsaw.LogPanelPreferenceModelTest (LogPanelPreferenceModelTest.java:47)

## Project files (at the breaking commit)
### pom.xml  (build file (declares the updated dependency))
```
<!--
 Licensed to the Apache Software Foundation (ASF) under one or more
 contributor license agreements.  See the NOTICE file distributed with
 this work for additional information regarding copyright ownership.
 The ASF licenses this file to You under the Apache License, Version 2.0
 (the "License"); you may not use this file except in compliance with
 the License.  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

-->
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/maven-v4_0_0.xsd">
  <parent>
    <groupId>org.apache.logging</groupId>
    <artifactId>logging-parent</artifactId>
    <version>5</version>
    <relativePath/>
  </parent>
  <modelVersion>4.0.0</modelVersion>
  <groupId>log4j</groupId>
  <artifactId>apache-chainsaw</artifactId>
  <name>Apache Chainsaw</name>
  <version>2.2.0-SNAPSHOT</version>
  <description>Graphical Viewer for Logging events from a local or remote log4j event system.</description>
  <url>https://logging.apache.org/chainsaw</url>
  <inceptionYear>2002</inceptionYear>
  <packaging>jar</packaging>

  <issueManagement>
    <system>JIRA</system>
    <url>https://issues.apache.org/jira/browse/CHAINSAW</url>
  </issueManagement>

  <mailingLists>
    <mailingList>
      <name>log4j-user</name>
      <subscribe>log4j-user-subscribe@logging.apache.org</subscribe>
      <unsubscribe>log4j-user-unsubscribe@logging.apache.org</unsubscribe>
      <post>log4j-user@logging.apache.org</post>
      <archive>https://lists.apache.org/list.html?log4j-user@logging.apache.org</archive>
      <otherArchives>
        <otherArchive>http://mail-archives.apache.org/mod_mbox/logging-log4j-user/</otherArchive>
        <otherArchive>http://marc.info/?l=log4j-user</otherArchive>
        <otherArchive>http://dir.gmane.org/gmane.comp.jakarta.log4j.user</otherArchive>
      </otherArchives>
    </mailingList>
    <mailingList>
      <name>dev : development of the logging projects including chainsaw</name>
      <subscribe>dev-subscribe@logging.apache.org</subscribe>
      <unsubscribe>dev-unsubscribe@logging.apache.org</unsubscribe>
      <post>dev@logging.apache.org</post>
      <archive>https://lists.apache.org/list.html?dev@logging.apache.org</archive>
      <otherArchives>
        <otherArchive>http://mail-archives.apache.org/mod_mbox/logging-dev/</otherArchive>
      </otherArchives>
    </mailingList>
    <mailingList>
      <name>logging commits : all svn/git commits of the logging projects including chainsaw</name>
      <subscribe>commits-subscribe@logging.apache.org</subscribe>
      <unsubscribe>commits-unsubscribe@logging.apache.org</unsubscribe>
      <post>Read-Only List</post>
      <archive>http://mail-archives.apache.org/mod_mbox/logging-commits/</archive>
    </mailingList>
  </mailingLists>

  <developers>
    <developer>
      <id>mwomack</id>
      <name>Mark Womack</name>
      <email>mwomack@apache.org</email>
    </developer>
    <developer>
      <id>carnold</id>
      <name>Curt Arnold</name>
      <email>carnold@apache.org</email>
    </developer>
    <developer>
      <id>sdeboy</id>
      <name>Scott Deboy</name>
      <email>sdeboy@apache.org</email>
    </developer>
    <developer>
      <id>psmith</id>
      <name>Paul Smith</name>
      <email>psmith@apache.org</email>
    </developer>
    <developer>
      <id>mattsicker</id>
      <name>Matt Sicker</name>
      <email>mattsicker@apache.org</email>
    </developer>
  </developers>
  <contributors>
    <contributor>
      <name>Isuru Suriarachchi</name>
    </contributor>
  </contributors>

  <licenses>
    <license>
      <name>Apache License, Version 2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
      <distribution>repo</distribution>
    </license>
  </licenses>

  <scm>
    <connection>scm:git:https://git-wip-us.apache.org/repos/asf/logging-chainsaw.git</connection>
    <developerConnection>scm:git:https://git-wip-us.apache.org/repos/asf/logging-chainsaw.git</developerConnection>
    <url>https://git-wip-us.apache.org/repos/asf?p=logging-chainsaw.git</url>
  </scm>

  <properties>
    <chainsaw.mainclass>org.apache.log4j.chainsaw.LogUI</chainsaw.mainclass>
    <maven.compiler.source>11</maven.compiler.source>
    <maven.compiler.target>11</maven.compiler.target>
    <dependency.locations.enabled>false</dependency.locations.enabled>
    <ChainsawReleaseVersion>2.1.0</ChainsawReleaseVersion>
    <ChainsawReleaseManager>Robert Middleton</ChainsawReleaseManager>
    <ChainsawReleaseKey>B095DD52</ChainsawReleaseKey>
  </properties>

    <build>
        <plugins>
            <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.8.1</version>
            <configuration>
              <source>11</source>
              <target>11</target>
            </configuration>
            </plugin>
            
        </plugins>
    </build>
    
  <dependencies>
    <dependency>
      <groupId>org.apache.logging.log4j</groupId>
      <artifactId>log4j-api</artifactId>
      <version>2.17.1</version>
    </dependency>
    <dependency>
      <groupId>org.apache.logging.log4j</groupId>
      <artifactId>log4j-core</artifactId>
      <version>2.17.1</version>
    </dependency>
    <dependency>
      <groupId>javax.jmdns</groupId>
      <artifactId>jmdns</artifactId>
      <version>3.4.1</version>
    </dependency>
    <dependency>
      <groupId>com.thoughtworks.xstream</groupId>
      <artifactId>xstream</artifactId>
      <version>1.4.19</version>
    </dependency>
    <dependency>
      <groupId>commons-vfs</groupId>
      <artifactId>commons-vfs</artifactId>
      <version>1.0</version>
    </dependency>
    <dependency>
      <groupId>commons-logging</groupId>
      <artifactId>commons-logging</artifactId>
      <version>1.1.1</version>
    </dependency>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>3.8.1</version>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.apache.openejb</groupId>
      <artifactId>javaee-api</artifactId>
      <version>5.0-2</version>
      <type>jar</type>
      <scope>provided</scope>
    </dependency>
    <dependency>
      <groupId>com.jcraft</groupId>
      <artifactId>jsch</artifactId>
      <version>0.1.55</version>
    </dependency>
    <dependency>
      <groupId>hsqldb</groupId>
      <artifactId>hsqldb</artifactId>
      <version>1.8.0.7</version>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.apache.geronimo.specs</groupId>
      <artifactId>geronimo-jms_1.1_spec</artifactId>
      <version>1.0</version>
      <optional>true</optional>
      <scope>provided</scope>
    </dependency>
    <dependency>
      <groupId>org.projectlombok</groupId>
      <artifactId>lombok</artifactId>
      <version>1.18.22</version>
      <scope>provided</scope>
    </dependency>
    <dependency>
      <groupId>com.owlike</groupId>
      <artifactId>genson</artifactId>
      <version>1.6</version>
    </dependency>
  </dependencies>

  <reporting>
    <excludeDefaults>true</excludeDefaults>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jxr-plugin</artifactId>
        <version>2.5</version>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-release-plugin</artifactId>
        <configuration>
          <goals>site-deploy</goals>
          <goals>assembly:assembly</goals>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-changes-plugin</artifactId>
        <version>2.12.1</version>
        <reportSets>
          <reportSet>
            <reports>
              <report>jira-report</report>
              <report>changes-report</report>
            </reports>
          </reportSet>
        </reportSets>
      </plugin>
      <plugin>
        <artifactId>maven-pmd-plugin</artifactId>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-javadoc-plugin</artifactId>
        <version>3.3.2</version>
        <configuration>
          <bottom><![CDATA[<p align="center">Copyright &#169; {inceptionYear}-{currentYear} {organizationName}. All Rights Reserved.<br />
          Apache Logging, Apache Log4j, Log4j, Apache Chainsaw, Chainsaw, Apache, the Apache feather logo, the Apache Logging project logo,
          and the Apache Log4j logo are trademarks of The Apache Software Foundation.</p>]]></bottom>
          <encoding>UTF-8</encoding>
          <doclint>none</doclint>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-project-info-reports-plugin</artifactId>
        <version>2.9</version>
        <reportSets>
          <reportSet>
            <reports>
              <!--report>cim</report-->
              <report>scm</report>
              <report>project-team</report>
              <report>issue-tracking</report>
              <report>mailing-list</report>
              <report>dependencies</report>
            </reports>
          </reportSet>
        </reportSets>
      </plugin>
    </plugins>
  </reporting>

  <distributionManagement>
    <downloadUrl>https://logging.apache.org/log4j/chainsaw/download.html</downloadUrl>
    <site>
      <id>www.example.com</id>
      <url>scp://www.example.com/www/docs/project/</url>
    </site>
  </distributionManagement>

  <profiles>
    <profile>
      <id>mac</id>
      <activation>
        <os>
          <family>mac</family>
        </os>
      </activation>
      <build>
        <plugins>
          <plugin>
            <groupId>de.perdian.maven.plugins</groupId>
            <artifactId>macosappbundler-maven-plugin</artifactId>
            <version>1.10.2</version>
            <configuration>
              <plist>
                <CFBundleIconFile>src/main/resources/logo.icns</CFBundleIconFile>
                <CFBundleDisplayName>Chainsaw</CFBundleDisplayName>
                <CFBundleDevelopmentRegion>English</CFBundleDevelopmentRegion>
                <CFBundleURLTypes>
                  <string>msa</string>
                </CFBundleURLTypes>
                <JVMMainClassName>${chainsaw.mainclass}</JVMMainClassName>
                <JVMVersion>11+</JVMVersion>
                <JVMOptions>
                  <jvmOption>-Xms128m</jvmOption>
                  <jvmOption>-Xmx512m</jvmOption>
                </JVMOptions>
              </plist>
              <dmg>
                <generate>true</generate>
                <additionalResources>
                  <additionalResource>
                    <directory>src/bundle/macos/distribution</directory>
                  </additionalResource>
                </additionalResources>
              </dmg>
            </configuration>
            <executions>
              <execution>
                <phase>package</phase>
                <goals>
                  <goal>bundle</goal>
                </goals>
              </execution>
            </executions>
          </plugin>
        </plugins>
      </build>
    </profile>

    <profile>
      <id>development</id>
      <repositories>
        <repository>
          <id>apache.snapshots</id>
          <name>Apache Snapshot Repository</name>
          <url>https://repository.apache.org/snapshots</url>
          <releases>
            <enabled>false</enabled>
          </releases>
        </repository>
      </repositories>
    </profile>
    
    <profile>
        <id>packaging</id>
        <build>
        <plugins>
          <plugin>
            <groupId>org.apache.rat</groupId>
            <artifactId>apache-rat-plugin</artifactId>
          </plugin>
          <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-project-info-reports-plugin</artifactId>
          </plugin>
          <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-surefire-plugin</artifactId>
            <configuration>
              <workingDirectory>target</workingDirectory>
            </configuration>
          </plugin>
          
          <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-jar-plugin</artifactId>
            <version>3.2.2</version>
            <configuration>
              <archive>
                <manifest>
                  <mainClass>${chainsaw.mainclass}</mainClass>
                  <addClasspath>true</addClasspath>
                </manifest>
                <manifestSections>
                  <manifestSection>
                    <name>org.apache.log4j</name>
                    <manifestEntries>
                      <Implementation-Title>${project.name}</Implementation-Title>
                      <Implementation-Version>${project.version}</Implementation-Version>
                      <Implementation-Vendor>Apache Software Foundation</Implementation-Vendor>
                    </manifestEntries>
                  </manifestSection>
                </manifestSections>
              </archive>
            </configuration>
          </plugin>
          
          <plugin>
            <groupId>org.codehaus.mojo</groupId>
            <artifactId>appassembler-maven-plugin</artifactId>
            <executions>
              <execution>
                <phase>package</phase>
                <goals>
                  <goal>assemble</goal>
                </goals>
              </execution>
            </executions>
            <configuration>
              <showConsoleWindow>false</showConsoleWindow>
              <programs>
                <program>
                  <mainClass>${chainsaw.mainclass}</mainClass>
                  <name>chainsaw</name>
                </program>
              </programs>
            </configuration>
          </plugin>
          <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-assembly-plugin</artifactId>
            <executions>
              <execution>
                <id>make-assembly</id>
                <phase>package</phase>
                <goals>
                  <goal>single</goal>
                </goals>
                <configuration>
                  <descriptors>
                    <descriptor>src/assembly/bin.xml</descriptor>
                    <descriptor>src/assembly/standalone.xml</descriptor>
                  </descriptors>
                  <!-- we append the assembly ID here,but note that the bin assembly does not have an id specified
                      in its config, so it doesn't have a suffix -->
                  <appendAssemblyId>true</appendAssemblyId>
                </configuration>
              </execution>
            </executions>
          </plugin>
          <plugin>
            <groupId>org.codehaus.mojo</groupId>
            <artifactId>build-helper-maven-plugin</artifactId>
            <executions>
              <execution>
                <id>attach-artifacts</id>
                <phase>package</phase>
                <goals>
                  <goal>attach-artifact</goal>
                </goals>
                <configuration>
                  <artifacts>
                    <artifact>
                      <file>target/${project.artifactId}-${project.version}-standalone.zip</file>
                      <type>zip</type>
                      <classifier>standalone</classifier>
                    </artifact>
                  </artifacts>
                </configuration>
              </execution>
            </executions>
          </plugin>
          <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-source-plugin</artifactId>
            <executions>
              <execution>
                <goals>
                  <goal>jar</goal>
                </goals>
              </execution>
            </executions>
          </plugin>
          <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-site-plugin</artifactId>
            <version>3.7.1</version>
            <dependencies>
              <dependency>
                <groupId>org.asciidoctor</groupId>
                <artifactId>asciidoctor-maven-plugin</artifactId>
                <version>1.5.6</version>
              </dependency>
            </dependencies>
            <configuration>
              <!-- only build English site even on other language OS -->
              <locales>en</locales>
              <!-- Exclude the navigation file for Maven 1 sites
                   and the changes file used by the changes-plugin,
                   as they interfere with the site generation. -->
              <moduleExcludes>
                <xdoc>navigation.xml,changes.xml</xdoc>
              </moduleExcludes>
              <asciidoc>
                <attributes>
                  <!-- copy any site properties wanted in asciidoc files -->
                  <ChainsawReleaseVersion>${ChainsawReleaseVersion}</ChainsawReleaseVersion>
                  <ChainsawReleaseManager>${ChainsawReleaseManager}</ChainsawReleaseManager>
                  <ChainsawReleaseKey>${ChainsawReleaseKey}</ChainsawReleaseKey>
                </attributes>
              </asciidoc>
            </configuration>
          </plugin>
        </plugins>
        </build>
    </profile>
  </profiles>
</project>
```

### src/test/java/org/apache/log4j/chainsaw/LogPanelPreferenceModelTest.java  (failing test)
```
/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.log4j.chainsaw;

import com.thoughtworks.xstream.XStream;
import com.thoughtworks.xstream.io.xml.DomDriver;

import junit.framework.TestCase;

public class LogPanelPreferenceModelTest extends TestCase {

    public void testLogPanelPreferenceModelSerialization() {
        LogPanelPreferenceModel model = new LogPanelPreferenceModel();
        
        
        /**
         * First modify the model from it's default state so we know we're actually storing
         * something 'different' for deserialization tests
         */
        
        model.setLevelIcons(!model.isLevelIcons());
        model.setWrapMessage(!model.isWrapMessage());
        model.setDateFormatPattern("yyyyDDmm");
        model.setLoggerPrecision("FATAL");
        model.setLogTreePanelVisible(!model.isLogTreePanelVisible());
        model.setScrollToBottom(model.isScrollToBottom());
        model.setToolTips(!model.isToolTips());
        
        XStream stream = new XStream(new DomDriver());
        String xml = stream.toXML(model);
//        System.out.println(xml);
        
        LogPanelPreferenceModel restored = (LogPanelPreferenceModel) stream.fromXML(xml);
        
        assertEquals(model.isLevelIcons(), restored.isLevelIcons());
        assertEquals(model.getDateFormatPattern(), restored.getDateFormatPattern());
        assertEquals(model.getLoggerPrecision(), restored.getLoggerPrecision());
        assertEquals(model.isLogTreePanelVisible(), restored.isLogTreePanelVisible());
        assertEquals(model.isScrollToBottom(), restored.isScrollToBottom());
        assertEquals(model.isToolTips(), restored.isToolTips());
        
        
        
    }
}
```

### src/main/resources/org/apache/log4j/chainsaw/favourites/package.html  (resource file named in the failing test)
```
<!--
 Licensed to the Apache Software Foundation (ASF) under one or more
 contributor license agreements.  See the NOTICE file distributed with
 this work for additional information regarding copyright ownership.
 The ASF licenses this file to You under the Apache License, Version 2.0
 (the "License"); you may not use this file except in compliance with
 the License.  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

-->
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
<html> <head>
<title></title>
</head>

<body>

<p>The Favourites package.

<hr>
<h2>Prototype Rules</h2>
The following rules are checked against a potential prototype instance to ensure it can
be used and saved for later use:

<ul>
	<LI > Have a public no-arg constructor available
	<li> TODO - more rules
</ul>
</body> </html>
```

### src/main/resources/org/apache/log4j/chainsaw/package.html  (resource file named in the failing test)
```
<!--
 Licensed to the Apache Software Foundation (ASF) under one or more
 contributor license agreements.  See the NOTICE file distributed with
 this work for additional information regarding copyright ownership.
 The ASF licenses this file to You under the Apache License, Version 2.0
 (the "License"); you may not use this file except in compliance with
 the License.  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

-->
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">

<HTML>
  <HEAD>
    <TITLE>Chainsaw Tool</TITLE>
  </head>
    
  <BODY>

    <P>Chainsaw is a GUI log viewer and filter for the log4j
package. By default it listens for <a
href="../spi/LoggingEvent.html">LoggingEvent</A> objects sent using
the <A href="../net/SocketAppender.html">SocketAppender</A> and
displays them in a table. The events can be filtered based on:</P>

    <UL>
      <LI>Level </li>

      <LI>Thread name</li>

      <LI>Logger</li>
      <LI>Message</li>

      <LI>NDC</LI>
    </UL>

    <P>All the details for each event can be displayed by selecting
      the event in the table.</P> 

    <P>Chainsaw also supports loading a events logged to a file using
      the <A href="../xml/XMLLayout.html">XMLLayout</A> format. This
      is great for analysing log files, and means you do not need to
      keep Chainsaw running continously. It is easy to add support
      for loading events from other sources like JDBC.</P> 

    <P>A picture is worth a thousand words: </P>

    <P align=center><A
      href="doc-files/Chainsawv2.gif"><IMG
      height="50%" alt="Screen shot of chainsaw"
      src="doc-files/Chainsawv2.gif"
      width="50%"></A>.</P> 

    <P>Finally, why is it called chainsaw?
      Because it cuts your log (file) down to size. :-)
    </P>


    <H2>Requirements</H2> 

    <P>Chainsaw is based on the Swing API and requires JDK 1.4 or later.</P>


    <H2>Running chainsaw</H2>

    <H3>Setup</H3>
    <P>You need to include the <code>log4j.jar</code> and <code>xstream.jar</code> in the classpath.

    <H3>Usage</H3>

    <P>The command line usage is:</P>

    <PRE>  java -D&lt;property&gt;=&lt;value&gt; org.apache.log4j.chainsaw.LogUI </PRE>

    <H2>Configuring Log4J</H2>

    <P>You will need to configure log4j to send logging events to
      Chainsaw.  There is an example Log4j xml configuration file included with Chainsaw, you can view it inside
      the Chainsaw GUI by clicking on the button in the welcome screen.</P>




  </body>
</html>
```

### src/main/resources/org/apache/log4j/chainsaw/prefs/default.properties  (resource file named in the failing test)
```
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ====================================
# The Default Settings for Chainsaw
# ====================================

# These next settings define the location and dimensions of the main
# window when it is first realized on startup
main.window.x=0
main.window.y=0
# default width and height to -1 will display the app at full screen resolution
main.window.width=-1
main.window.height=-1

table.columns.order=ID,TIMESTAMP,MARKER,LEVEL,LOGGER,MESSAGE,THROWABLE,THREAD,NDC,CLASS,METHOD,FILE,LINE,MILLISDELTA
table.columns.widths=50,80,95,50,100,500,100,100,100,100,100,100,100,100

SavedConfigs.Size=0
DateFormat.1=HH:mm:ss
DateFormat.2=HH:mm
identifierExpression=PROP.hostname - PROP.application


# These are the default LogPanel settings
dateFormatPattern=HH:mm:ss
levelIcons=false
loggerPrecision=
toolTips=false
scrollToBottom=true
logTreePanelVisible=true
detailPaneVisible=true
highlightSearchMatchText=true
wrapMessage=true
searchResultsVisible=true
```


Now write the explanation and the single ```diff block.
