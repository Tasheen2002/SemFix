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
`org.codehaus.plexus:plexus-io` was updated from `3.2.0` to `3.3.0`. The project compiles, but tests now fail.

## Failure (from the build log)
Failing test classes: org.codehaus.plexus.archiver.snappy.SnappyArchiverTest, org.codehaus.plexus.archiver.bzip2.BZip2ArchiverTest, org.codehaus.plexus.archiver.xz.XzArchiverTest, org.codehaus.plexus.archiver.tar.TarFileTest, org.codehaus.plexus.archiver.tar.TarArchiverTest, org.codehaus.plexus.archiver.zip.ZipArchiverTest, org.codehaus.plexus.archiver.gzip.GZipArchiverTest, org.codehaus.plexus.archiver.SymlinkTest
Exception types: org.codehaus.plexus.archiver.ArchiverException
Error lines:
- org.codehaus.plexus.archiver.ArchiverException: Not a directory: test/resources/symlinks/src/symLinkToDirOnTheOutside
- org.codehaus.plexus.archiver.ArchiverException: Not a directory: bzz/symLinkToDirOnTheOutside
- org.codehaus.plexus.archiver.ArchiverException: Not a directory: plexus/src/symLinkToDirOnTheOutside
- org.codehaus.plexus.archiver.ArchiverException: Not a directory: plexus/symlinks/src/symLinkToDirOnTheOutside
- org.codehaus.plexus.archiver.ArchiverException: Not a directory: symLinkToDirOnTheOutside
Project stack frames:
- org.codehaus.plexus.archiver.snappy.SnappyArchiverTest (SnappyArchiverTest.java:53)
- org.codehaus.plexus.archiver.bzip2.BZip2ArchiverTest (BZip2ArchiverTest.java:53)
- org.codehaus.plexus.archiver.xz.XzArchiverTest (XzArchiverTest.java:49)
- org.codehaus.plexus.archiver.tar.TarFileTest (TarFileTest.java:100)
- org.codehaus.plexus.archiver.tar.TarFileTest (TarFileTest.java:39)
- org.codehaus.plexus.archiver.tar.TarFileTest (TarFileTest.java:77)
- org.codehaus.plexus.archiver.tar.TarFileTest (TarFileTest.java:58)
- org.codehaus.plexus.archiver.tar.TarArchiverTest (TarArchiverTest.java:515)
- org.codehaus.plexus.archiver.tar.TarArchiverTest (TarArchiverTest.java:557)
- org.codehaus.plexus.archiver.tar.TarArchiverTest (TarArchiverTest.java:508)
- org.codehaus.plexus.archiver.tar.TarArchiverTest (TarArchiverTest.java:540)
- org.codehaus.plexus.archiver.tar.TarArchiverTest (TarArchiverTest.java:548)

## Project files (at the breaking commit)
### pom.xml  (build file (declares the updated dependency))
```
<?xml version="1.0" encoding="UTF-8"?>

<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <parent>
    <groupId>org.codehaus.plexus</groupId>
    <artifactId>plexus</artifactId>
    <version>8</version>
  </parent>

  <artifactId>plexus-archiver</artifactId>
  <version>4.3.0-SNAPSHOT</version>
  <name>Plexus Archiver Component</name>

  <scm>
    <connection>scm:git:git@github.com:codehaus-plexus/plexus-archiver.git</connection>
    <developerConnection>scm:git:git@github.com:codehaus-plexus/plexus-archiver.git</developerConnection>
    <url>http://github.com/codehaus-plexus/plexus-archiver/tree/${project.scm.tag}/</url>
    <tag>plexus-archiver-4.2.3</tag>
  </scm>
  <issueManagement>
    <system>jira</system>
    <url>https://github.com/codehaus-plexus/plexus-archiver/issues</url>
  </issueManagement>
  <distributionManagement>
    <site>
      <id>github:gh-pages</id>
      <url>${project.scm.developerConnection}</url>
    </site>
  </distributionManagement>

  <properties>
    <javaVersion>8</javaVersion>
    <project.build.outputTimestamp>2022-01-02T11:13:08Z</project.build.outputTimestamp>
  </properties>

  <contributors>
    <contributor>
      <name>Dan Tran</name>
    </contributor>
    <contributor>
      <name>Richard van der Hoff</name>
    </contributor>
    <contributor>
      <name>Tomasz 'Trog' Welman</name>
      <email>trog@swmud.pl</email>
    </contributor>
  </contributors>

  <dependencies>
    <!-- Plexus dependencies -->
    <dependency>
      <groupId>org.codehaus.plexus</groupId>
      <artifactId>plexus-container-default</artifactId>
      <version>2.1.1</version>
      <scope>provided</scope>
    </dependency>
    <dependency>
      <groupId>org.codehaus.plexus</groupId>
      <artifactId>plexus-utils</artifactId>
      <version>3.4.1</version>
    </dependency>
    <dependency>
      <groupId>org.codehaus.plexus</groupId>
      <artifactId>plexus-io</artifactId>
      <version>3.3.0</version>
    </dependency>
    <!-- Apache Commons dependencies -->
    <dependency>
      <groupId>commons-io</groupId>
      <artifactId>commons-io</artifactId>
      <version>2.11.0</version>
    </dependency>
    <dependency>
      <groupId>org.apache.commons</groupId>
      <artifactId>commons-compress</artifactId>
      <version>1.21</version>
    </dependency>
    <!-- Other dependencies -->
    <dependency>
      <groupId>org.iq80.snappy</groupId>
      <artifactId>snappy</artifactId>
      <version>0.4</version>
    </dependency>
    <dependency>
      <groupId>org.tukaani</groupId>
      <artifactId>xz</artifactId>
      <version>1.9</version>
      <scope>runtime</scope>
    </dependency>
    <dependency>
      <groupId>com.google.code.findbugs</groupId>
      <artifactId>jsr305</artifactId>
      <version>3.0.2</version>
      <scope>provided</scope>
    </dependency>
    <!-- Test dependencies -->
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <version>4.13.2</version>
      <scope>test</scope>
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-release-plugin</artifactId>
        <configuration>
          <!-- olamy: exclude files with strange names as failed here on osx -->
          <checkModificationExcludes>
            <checkModificationExclude>**/src/test/resources/utf8/**</checkModificationExclude>
          </checkModificationExcludes>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-resources-plugin</artifactId>
        <!--
        maven totally change his way to copy symlink
        this mean the symlink is copied as a symlink and not anymore as a new file
        https://issues.apache.org/jira/browse/MRESOURCES-237
        -->
        <version>2.7</version>
      </plugin>
      <plugin>
        <groupId>org.codehaus.plexus</groupId>
        <artifactId>plexus-component-metadata</artifactId>
        <executions>
          <execution>
            <goals>
              <goal>generate-metadata</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-scm-publish-plugin</artifactId>
        <configuration>
          <content>${project.reporting.outputDirectory}</content><!-- mono-module doesn't require site:stage -->
        </configuration>
        <executions>
          <execution>
            <id>scm-publish</id>
            <phase>site-deploy</phase><!-- deploy site with maven-scm-publish-plugin -->
            <goals>
              <goal>publish-scm</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>

</project>
```

### src/test/java/org/codehaus/plexus/archiver/snappy/SnappyArchiverTest.java  (failing test)
```
/*
 * The MIT License
 *
 * Copyright (c) 2004, The Codehaus
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is furnished to do
 * so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */
package org.codehaus.plexus.archiver.snappy;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.Arrays;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import org.codehaus.plexus.archiver.Archiver;
import org.codehaus.plexus.archiver.BasePlexusArchiverTest;
import org.codehaus.plexus.archiver.exceptions.EmptyArchiveException;
import org.codehaus.plexus.archiver.zip.ZipArchiver;
import org.codehaus.plexus.util.FileUtils;
import org.codehaus.plexus.util.IOUtil;

/**
 * Tests for the snappy archiver
 */
public class SnappyArchiverTest
    extends BasePlexusArchiverTest
{

    public void testCreateArchive()
        throws Exception
    {
        ZipArchiver zipArchiver = (ZipArchiver) lookup( Archiver.ROLE, "zip" );
        zipArchiver.addDirectory( getTestFile( "src" ) );
        zipArchiver.setDestFile( getTestFile( "target/output/archiveForSnappy.zip" ) );
        zipArchiver.createArchive();
        SnappyArchiver archiver = (SnappyArchiver) lookup( Archiver.ROLE, "snappy" );
        String[] inputFiles = new String[ 1 ];
        inputFiles[0] = "archiveForSnappy.zip";
        archiver.addDirectory( getTestFile( "target/output" ), inputFiles, null );
        archiver.setDestFile( getTestFile( "target/output/archive.snappy" ) );
        archiver.createArchive();
    }

    public void testCreateEmptyArchive()
        throws Exception
    {
        SnappyArchiver archiver = (SnappyArchiver) lookup( Archiver.ROLE, "snappy" );
        archiver.setDestFile( getTestFile( "target/output/empty.snappy" ) );
        try
        {
            archiver.createArchive();

            fail( "Creating empty archive should throw EmptyArchiveException" );
        }
        catch ( EmptyArchiveException ignore )
        {
        }
    }

    public void testCreateResourceCollection()
        throws Exception
    {
        final File pomFile = new File( "pom.xml" );
        final File snappyFile = new File( "target/output/pom.xml.snappy" );
        SnappyArchiver SnappyArchiver = (SnappyArchiver) lookup( Archiver.ROLE, "snappy" );
        SnappyArchiver.setDestFile( snappyFile );
        SnappyArchiver.addFile( pomFile, "pom.xml" );
        FileUtils.removePath( snappyFile.getPath() );
        SnappyArchiver.createArchive();

        System.out.println( "Created: " + snappyFile.getAbsolutePath() );

        final File zipFile = new File( "target/output/pom.zip" );
        ZipArchiver zipArchiver = (ZipArchiver) lookup( Archiver.ROLE, "zip" );
        zipArchiver.setDestFile( zipFile );
        zipArchiver.addArchivedFileSet( snappyFile, "prfx/" );
        FileUtils.removePath( zipFile.getPath() );
        zipArchiver.createArchive();

        final ZipFile juZipFile = new ZipFile( zipFile );
        final ZipEntry zipEntry = juZipFile.getEntry( "prfx/target/output/pom.xml" );
        final InputStream archivePom = juZipFile.getInputStream( zipEntry );
        final InputStream pom = Files.newInputStream( pomFile.toPath() );

        assertTrue( Arrays.equals( IOUtil.toByteArray( pom ), IOUtil.toByteArray( archivePom ) ) );
        archivePom.close();
        pom.close();
        juZipFile.close();
    }

    /**
     * Tests the Snappy archiver is forced set to true, and after that
     * tests the behavior when the forced is set to false.
     *
     * @throws Exception
     */
    public void testsnappyIsForcedBehaviour() throws Exception
    {
        SnappyArchiver SnappyArchiver = (SnappyArchiver) createArchiver( "snappy" );

        assertTrue( SnappyArchiver.isSupportingForced() );
        SnappyArchiver.createArchive();

        final long creationTime = SnappyArchiver.getDestFile().lastModified();

        waitUntilNewTimestamp( SnappyArchiver.getDestFile(), creationTime );

        SnappyArchiver = (SnappyArchiver) createArchiver( "snappy" );

        SnappyArchiver.setForced( true );
        SnappyArchiver.createArchive();

        final long firstRunTime = SnappyArchiver.getDestFile().lastModified();

        assertFalse( creationTime == firstRunTime );

        SnappyArchiver = (SnappyArchiver) createArchiver( "snappy" );

        SnappyArchiver.setForced( false );
        SnappyArchiver.createArchive();

        final long secondRunTime = SnappyArchiver.getDestFile().lastModified();

        assertEquals( firstRunTime, secondRunTime );
    }

}
```

### src/test/java/org/codehaus/plexus/archiver/bzip2/BZip2ArchiverTest.java  (failing test)
```
/*
 * The MIT License
 *
 * Copyright (c) 2004, The Codehaus
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is furnished to do
 * so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */
package org.codehaus.plexus.archiver.bzip2;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.Arrays;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import org.codehaus.plexus.archiver.Archiver;
import org.codehaus.plexus.archiver.BasePlexusArchiverTest;
import org.codehaus.plexus.archiver.exceptions.EmptyArchiveException;
import org.codehaus.plexus.archiver.zip.ZipArchiver;
import org.codehaus.plexus.util.FileUtils;
import org.codehaus.plexus.util.IOUtil;

/**
 * @author Emmanuel Venisse
 */
public class BZip2ArchiverTest
    extends BasePlexusArchiverTest
{

    public void testCreateArchive()
        throws Exception
    {
        ZipArchiver zipArchiver = (ZipArchiver) lookup( Archiver.ROLE, "zip" );
        zipArchiver.addDirectory( getTestFile( "src" ) );
        zipArchiver.setDestFile( getTestFile( "target/output/archiveForbz2.zip" ) );
        zipArchiver.createArchive();
        BZip2Archiver archiver = (BZip2Archiver) lookup( Archiver.ROLE, "bzip2" );
        String[] inputFiles = new String[ 1 ];
        inputFiles[0] = "archiveForbz2.zip";
        archiver.addDirectory( getTestFile( "target/output" ), inputFiles, null );
        archiver.setDestFile( getTestFile( "target/output/archive.bz2" ) );
        archiver.createArchive();
    }

    public void testCreateEmptyArchive()
        throws Exception
    {
        BZip2Archiver archiver = (BZip2Archiver) lookup( Archiver.ROLE, "bzip2" );
        archiver.setDestFile( getTestFile( "target/output/empty.bz2" ) );
        try
        {
            archiver.createArchive();

            fail( "Creating empty archive should throw EmptyArchiveException" );
        }
        catch ( EmptyArchiveException ignore )
        {
        }
    }

    public void testCreateResourceCollection()
        throws Exception
    {
        final File pomFile = new File( "pom.xml" );
        final File bz2File = new File( "target/output/pom.xml.bz2" );
        BZip2Archiver bzip2Archiver = (BZip2Archiver) lookup( Archiver.ROLE, "bzip2" );
        bzip2Archiver.setDestFile( bz2File );
        bzip2Archiver.addFile( pomFile, "pom.xml" );
        FileUtils.removePath( bz2File.getPath() );
        bzip2Archiver.createArchive();

        System.out.println( "Created: " + bz2File.getAbsolutePath() );

        final File zipFile = new File( "target/output/pom.zip" );
        ZipArchiver zipArchiver = (ZipArchiver) lookup( Archiver.ROLE, "zip" );
        zipArchiver.setDestFile( zipFile );
        zipArchiver.addArchivedFileSet( bz2File, "prfx/" );
        FileUtils.removePath( zipFile.getPath() );
        zipArchiver.createArchive();

        final ZipFile juZipFile = new ZipFile( zipFile );
        final ZipEntry zipEntry = juZipFile.getEntry( "prfx/target/output/pom.xml" );
        final InputStream archivePom = juZipFile.getInputStream( zipEntry );
        final InputStream pom = Files.newInputStream( pomFile.toPath() );

        assertTrue( Arrays.equals( IOUtil.toByteArray( pom ), IOUtil.toByteArray( archivePom ) ) );
        archivePom.close();
        pom.close();
        juZipFile.close();
    }

    /**
     * Tests the .bzip2 archiver is forced set to true, and after that
     * tests the behavior when the forced is set to false.
     *
     * @throws Exception
     */
    public void testBz2IsForcedBehaviour() throws Exception
    {
        BZip2Archiver bZip2Archiver = (BZip2Archiver) createArchiver( "bzip2" );

        assertTrue( bZip2Archiver.isSupportingForced() );
        bZip2Archiver.createArchive();

        final long creationTime = bZip2Archiver.getDestFile().lastModified();

        waitUntilNewTimestamp( bZip2Archiver.getDestFile(), creationTime );

        bZip2Archiver = (BZip2Archiver) createArchiver( "bzip2" );

        bZip2Archiver.setForced( true );
        bZip2Archiver.createArchive();

        final long firstRunTime = bZip2Archiver.getDestFile().lastModified();

        assertFalse( creationTime == firstRunTime );

        bZip2Archiver = (BZip2Archiver) createArchiver( "bzip2" );

        bZip2Archiver.setForced( false );
        bZip2Archiver.createArchive();

        final long secondRunTime = bZip2Archiver.getDestFile().lastModified();

        assertEquals( firstRunTime, secondRunTime );
    }

}
```

### src/test/java/org/codehaus/plexus/archiver/xz/XzArchiverTest.java  (failing test)
```
/*
 * Copyright 2016 Codehaus.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.codehaus.plexus.archiver.xz;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.Arrays;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import org.codehaus.plexus.archiver.Archiver;
import org.codehaus.plexus.archiver.BasePlexusArchiverTest;
import org.codehaus.plexus.archiver.exceptions.EmptyArchiveException;
import org.codehaus.plexus.archiver.zip.ZipArchiver;
import org.codehaus.plexus.util.FileUtils;
import org.codehaus.plexus.util.IOUtil;
import static junit.framework.TestCase.assertEquals;
import static junit.framework.TestCase.assertFalse;
import static junit.framework.TestCase.assertTrue;
import static org.codehaus.plexus.PlexusTestCase.getTestFile;

/**
 * @author philip.lourandos
 * @since 3.3
 */
public class XzArchiverTest extends BasePlexusArchiverTest
{

    public void testCreateArchive()
        throws Exception
    {
        ZipArchiver zipArchiver = (ZipArchiver) lookup( Archiver.ROLE, "zip" );
        zipArchiver.addDirectory( getTestFile( "src" ) );
        zipArchiver.setDestFile( getTestFile( "target/output/archiveForxz.zip" ) );
        zipArchiver.createArchive();

        XZArchiver archiver = (XZArchiver) lookup( Archiver.ROLE, "xz" );
        String[] inputFiles = new String[ 1 ];
        inputFiles[0] = "archiveForxz.zip";

        File targetOutputFile = getTestFile( "target/output/archive.xz" );
        if ( targetOutputFile.exists() )
        {
            FileUtils.fileDelete( targetOutputFile.getPath() );
        }
        assertFalse( targetOutputFile.exists() );

        archiver.addDirectory( getTestFile( "target/output" ), inputFiles, null );
        archiver.setDestFile( targetOutputFile );
        archiver.createArchive();

        assertTrue( targetOutputFile.exists() );
    }

    public void testCreateEmptyArchive()
        throws Exception
    {
        XZArchiver archiver = (XZArchiver) lookup( Archiver.ROLE, "xz" );
        archiver.setDestFile( getTestFile( "target/output/empty.xz" ) );
        try
        {
            archiver.createArchive();

            fail( "Creating empty archive should throw EmptyArchiveException" );
        }
        catch ( EmptyArchiveException ignore )
        {
        }
    }

    public void testCreateResourceCollection() throws Exception
    {
        final File pomFile = new File( "pom.xml" );
        final File xzFile = new File( "target/output/pom.xml.xz" );
        XZArchiver xzArchiver = (XZArchiver) lookup( Archiver.ROLE, "xz" );
        xzArchiver.setDestFile( xzFile );
        xzArchiver.addFile( pomFile, "pom.xml" );
        FileUtils.removePath( xzFile.getPath() );
        xzArchiver.createArchive();

        System.out.println( "Created: " + xzFile.getAbsolutePath() );

        final File zipFile = new File( "target/output/pomxz.zip" );
        ZipArchiver zipArchiver = (ZipArchiver) lookup( Archiver.ROLE, "zip" );
        zipArchiver.setDestFile( zipFile );
        zipArchiver.addArchivedFileSet( xzFile, "prfx/" );
        FileUtils.removePath( zipFile.getPath() );
        zipArchiver.createArchive();

        final ZipFile juZipFile = new ZipFile( zipFile );
        final ZipEntry zipEntry = juZipFile.getEntry( "prfx/target/output/pom.xml" );
        final InputStream archivePom = juZipFile.getInputStream( zipEntry );
        final InputStream pom = Files.newInputStream( pomFile.toPath() );

        assertTrue( Arrays.equals( IOUtil.toByteArray( pom ), IOUtil.toByteArray( archivePom ) ) );
        archivePom.close();
        pom.close();
        juZipFile.close();
    }

    /**
     * Tests the .xz archiver is forced set to true, and after that
     * tests the behavior when the forced is set to false.
     *
     * @throws Exception
     */
    public void testXzIsForcedBehaviour() throws Exception
    {
        XZArchiver xzArchiver = (XZArchiver) createArchiver( "xz" );

        assertTrue( xzArchiver.isSupportingForced() );
        xzArchiver.createArchive();

        final long creationTime = xzArchiver.getDestFile().lastModified();

        waitUntilNewTimestamp( xzArchiver.getDestFile(), creationTime );

        xzArchiver = (XZArchiver) createArchiver( "xz" );

        xzArchiver.setForced( true );
        xzArchiver.createArchive();

        final long firstRunTime = xzArchiver.getDestFile().lastModified();

        assertFalse( creationTime == firstRunTime );

        xzArchiver = (XZArchiver) createArchiver( "xz" );

        xzArchiver.setForced( false );
        xzArchiver.createArchive();

        final long secondRunTime = xzArchiver.getDestFile().lastModified();

        assertEquals( firstRunTime, secondRunTime );
    }

}
```

### src/test/java/org/codehaus/plexus/archiver/tar/TarFileTest.java  (failing test)
```
package org.codehaus.plexus.archiver.tar;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.Arrays;
import java.util.Enumeration;
import org.apache.commons.compress.archivers.tar.TarArchiveEntry;
import org.codehaus.plexus.PlexusTestCase;
import org.codehaus.plexus.archiver.Archiver;
import org.codehaus.plexus.archiver.bzip2.BZip2Compressor;
import org.codehaus.plexus.archiver.gzip.GZipCompressor;
import org.codehaus.plexus.archiver.util.Compressor;
import org.codehaus.plexus.util.FileUtils;
import org.codehaus.plexus.util.IOUtil;
import static org.codehaus.plexus.components.io.resources.ResourceFactory.createResource;

/**
 * Test case for {@link TarFile}.
 */
public class TarFileTest
    extends PlexusTestCase
{

    private interface TarFileCreator
    {

        TarFile newTarFile( File file ) throws IOException;

    }

    /**
     * Test for the uncompressed tar file, {@link TarFile}.
     */
    public void testTarFile() throws Exception
    {
        testTarFile( null, null, new TarFileCreator()
        {

            @Override
            public TarFile newTarFile( File file )
                throws IOException
            {
                return new TarFile( file );
            }

        } );
    }

    /**
     * Test for the gzip compressed tar file, {@link GZipTarFile}.
     */
    public void testGZipTarFile() throws Exception
    {
        final GZipCompressor compressor = new GZipCompressor();
        testTarFile( compressor, ".gz", new TarFileCreator()
        {

            @Override
            public TarFile newTarFile( File file )
                throws IOException
            {
                return new GZipTarFile( file );
            }

        } );
    }

    /**
     * Test for the bzip2 compressed tar file, {@link BZip2TarFile}.
     */
    public void testBZip2TarFile() throws Exception
    {
        final BZip2Compressor compressor = new BZip2Compressor();
        testTarFile( compressor, ".bz2", new TarFileCreator()
        {

            @Override
            public TarFile newTarFile( File file )
                throws IOException
            {
                return new BZip2TarFile( file );
            }

        } );
    }

    private void testTarFile( Compressor compressor, String extension,
                              TarFileCreator tarFileCreator )
        throws Exception
    {
        File file = new File( "target/output/TarFileTest.tar" );
        final TarArchiver archiver = (TarArchiver) lookup( Archiver.ROLE, "tar" );
        archiver.setLongfile( TarLongFileMode.posix );
        archiver.setDestFile( file );
        archiver.addDirectory( new File( "src" ) );
        FileUtils.removePath( file.getPath() );
        archiver.createArchive();
        if ( compressor != null )
        {
            final File compressedFile = new File( file.getPath() + extension );
            compressor.setSource( createResource( file, file.getName() ) );
            compressor.setDestFile( compressedFile );
            compressor.compress();
            compressor.close();
            file = compressedFile;
        }
        final TarFile tarFile = tarFileCreator.newTarFile( file );

        for ( Enumeration en = tarFile.getEntries(); en.hasMoreElements(); )
        {
            final TarArchiveEntry te = (TarArchiveEntry) en.nextElement();
            if ( te.isDirectory() || te.isSymbolicLink() )
            {
                continue;
            }
            final File teFile = new File( "src", te.getName() );
            final InputStream teStream = tarFile.getInputStream( te );
            final InputStream fileStream = Files.newInputStream( teFile.toPath() );
            assertTrue( Arrays.equals( IOUtil.toByteArray( teStream ), IOUtil.toByteArray( fileStream ) ) );
            teStream.close();
            fileStream.close();
        }

        tarFile.close();
    }

}
```

### src/test/java/org/codehaus/plexus/archiver/tar/TarArchiverTest.java  (failing test)
```
... (lines 0-0 omitted)
/*
 * The MIT License
 *
 * Copyright (c) 2004, The Codehaus
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is furnished to do
 * so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */
package org.codehaus.plexus.archiver.tar;

import static org.codehaus.plexus.archiver.util.Streams.bufferedInputStream;
import static org.codehaus.plexus.components.io.resources.ResourceFactory.createResource;

import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.Enumeration;
import java.util.LinkedHashMap;
import java.util.Map;

import org.apache.commons.compress.archivers.tar.TarArchiveEntry;
... (lines 41-461 omitted)
            return compressedFile;
        }

        @Override
        TarFile newTarFile( File tarFile )
        {
            return new GZipTarFile( tarFile );
        }

    }

    private class BZip2TarHandler
        extends TarHandler
    {

        @Override
        File createTarFile()
            throws Exception
        {
            File file = super.createTarFile();
            File compressedFile = new File( file.getPath() + ".bz2" );
            Compressor compressor = new BZip2Compressor();
            compressor.setSource( createResource( file ) );
            compressor.setDestFile( compressedFile );
            compressor.compress();
            compressor.close();
            return compressedFile;
        }

        @Override
        TarFile newTarFile( File tarFile )
        {
            return new BZip2TarFile( tarFile );
        }

    }

    public void testUncompressedResourceCollection()
        throws Exception
    {
        testCreateResourceCollection( new TarHandler() );
    }

    public void testGzipCompressedResourceCollection()
        throws Exception
    {
        testCreateResourceCollection( new GZipTarHandler() );
    }

    public void testGzipFIleHandleLeak()
        throws Exception
    {
        GZipTarHandler tarHandler = new GZipTarHandler();
        final File tarFile = tarHandler.createTarFile();
        final File tarFile2 = tarHandler.createTarfile2( tarFile );
        final TarFile cmp1 = tarHandler.newTarFile( tarFile );
        final TarFile cmp2 = new TarFile( tarFile2 );
        ArchiveFileComparator.forEachTarArchiveEntry( cmp1, new ArchiveFileComparator.TarArchiveEntryConsumer()
        {

            @Override
            public void accept( TarArchiveEntry ze1 )
                throws IOException
            {
                final String name1 = ze1.getName();
                Assert.assertNotNull( name1 );

            }

        } );
        cmp1.close();
        cmp2.close();

    }

    public void testBzip2CompressedResourceCollection()
        throws Exception
    {
        testCreateResourceCollection( new BZip2TarHandler() );
    }

    public void testTarFileNotClosingInputStream()
        throws Exception
    {
        // Supposedly not closing the stream according to yjp.
        TarHandler tarHandler = new BZip2TarHandler();
        final File fileName = tarHandler.createTarFile();
        final TarFile tarFile = tarHandler.newTarFile( fileName );
        tarFile.getEntries();
        tarFile.close();
    }

    private void testCreateResourceCollection( TarHandler tarHandler )
        throws Exception
    {
        final File tarFile = tarHandler.createTarFile();
        final File tarFile2 = tarHandler.createTarfile2( tarFile );
        final TarFile cmp1 = tarHandler.newTarFile( tarFile );
        final TarFile cmp2 = new TarFile( tarFile2 );
        ArchiveFileComparator.assertEquals( cmp1, cmp2, "prfx/" );
        cmp1.close();
        cmp2.close();
    }

    public void testSymlinkArchivedFileSet()
        throws Exception
    {
        final File tarFile = getTestFile( "src/test/resources/symlinks/symlinks.tar" );
        final File tarFile2 = getTestFile( "target/output/pasymlinks-archivedFileset.tar" );
        final TarArchiver tarArchiver = getPosixTarArchiver();
        tarArchiver.setDestFile( tarFile2 );
        DefaultArchivedFileSet archivedFileSet = DefaultArchivedFileSet.archivedFileSet( tarFile );
        archivedFileSet.setUsingDefaultExcludes( false );
        tarArchiver.addArchivedFileSet( archivedFileSet );
        tarArchiver.createArchive();

        final TarFile cmp1 = new TarFile( tarFile );
        final TarFile cmp2 = new TarFile( tarFile2 );
        ArchiveFileComparator.assertEquals( cmp1, cmp2, "" );
    }

}
```

### src/test/java/org/codehaus/plexus/archiver/zip/ZipArchiverTest.java  (failing test)
```
... (lines 0-0 omitted)
/*
 * The MIT License
 *
 * Copyright (c) 2004, The Codehaus
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is furnished to do
 * so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */
package org.codehaus.plexus.archiver.zip;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.io.Writer;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.attribute.FileTime;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.Date;
import java.util.Enumeration;
... (lines 41-89 omitted)
    {
        File zipFile = getTestFile( "target/output/zip-with-implicit-dirmode.zip" );

        ZipArchiver archiver = getZipArchiver( zipFile );

        archiver.setDefaultDirectoryMode( 0777 );
        archiver.setDirectoryMode( 0641 );
        archiver.setFileMode( 0222 );
        archiver.addFile( new File( "pom.xml" ), "fizz/buzz/pom.xml" );
        archiver.setDefaultDirectoryMode( 0530 );
        archiver.setDirectoryMode( -1 ); // Not forced mode
        archiver.setFileMode( 0111 );
        archiver.addFile( new File( "pom.xml" ), "fazz/bazz/pam.xml" );
        archiver.createArchive();

        assertTrue( zipFile.exists() );
        ZipFile zf = new ZipFile( zipFile );
        ZipArchiveEntry fizz = zf.getEntry( "fizz/" );
        assertEquals( 040641, fizz.getUnixMode() );
        ZipArchiveEntry pom = zf.getEntry( "fizz/buzz/pom.xml" );
        assertEquals( 0100222, pom.getUnixMode() );

        ZipArchiveEntry fazz = zf.getEntry( "fazz/" );
        assertEquals( 040530, fazz.getUnixMode() );
        ZipArchiveEntry pam = zf.getEntry( "fazz/bazz/pam.xml" );
        assertEquals( 0100111, pam.getUnixMode() );
    }

    public void testOveriddenPermissions()
        throws IOException
    {
        if ( !Os.isFamily( Os.FAMILY_WINDOWS ) )
        {
            File zipFile = getTestFile( "target/output/zip-with-overriden-modes.zip" );

            ZipArchiver archiver = getZipArchiver( zipFile );
            archiver.setDefaultDirectoryMode( 0777 );
            archiver.setDirectoryMode( 0641 );
            archiver.setFileMode( 0777 );
            archiver.addDirectory( new File( "src/test/resources/symlinks/src" ) );
            archiver.createArchive();

            assertTrue( zipFile.exists() );
            ZipFile zf = new ZipFile( zipFile );
            ZipArchiveEntry fizz = zf.getEntry( "symDir" );
            assertTrue( fizz.isUnixSymlink() );
            ZipArchiveEntry symR = zf.getEntry( "symR" );
            assertTrue( symR.isUnixSymlink() );
        }
    }

    public void testCreateArchiveWithDetectedModes()
        throws Exception
    {

        String[] executablePaths =
        {
            "path/to/executable", "path/to/executable.bat"
        };

        String[] confPaths =
        {
            "path/to/etc/file", "path/to/etc/file2"
        };

        String[] logPaths =
        {
            "path/to/logs/log.txt"
        };

        int exeMode = 0777;
        int confMode = 0600;
        int logMode = 0640;

        if ( Os.isFamily( Os.FAMILY_WINDOWS ) )
        {
            StackTraceElement e = new Throwable().getStackTrace()[0];
            System.out.println(
                "Cannot execute test: " + e.getMethodName() + " on " + System.getProperty( "os.name" ) );
            return;
        }
... (lines 171-323 omitted)
    }

    private ZipArchiver getZipArchiver( File destFile )
    {
        final ZipArchiver zipArchiver = getZipArchiver();
        zipArchiver.setDestFile( destFile );
        return zipArchiver;
    }

    private ZipUnArchiver getZipUnArchiver( File testJar )
        throws Exception
    {
        ZipUnArchiver zu = (ZipUnArchiver) lookup( UnArchiver.ROLE, "zip" );
        zu.setSourceFile( testJar );
        return zu;
    }

    private void writeFile( File dir, String fname, int mode )
        throws IOException, ArchiverException
    {
        File file = new File( dir, fname );

        if ( file.getParentFile() != null )
        {
            file.getParentFile().mkdirs();
        }

        try ( Writer writer = Files.newBufferedWriter( file.toPath(), StandardCharsets.UTF_8 ) )
        {
            writer.write( "This is a test file." );
        }

        ArchiveEntryUtils.chmod( file, mode );
    }

    public void testCreateArchive()
        throws Exception
    {
        ZipArchiver archiver = newArchiver( "archive1.zip" );

        createArchive( archiver );
    }

    public void testRecompressAddedZips() throws Exception
    {
        // check that by default the zip archives are re-compressed

        final File zipFileRecompress = getTestFile( "target/output/recompress-added-zips.zip" );
        final ZipArchiver zipArchiverRecompress = getZipArchiver( zipFileRecompress );
        zipArchiverRecompress.addDirectory( getTestFile( "src/test/jars" ) );
        FileUtils.removePath( zipFileRecompress.getPath() );
        zipArchiverRecompress.createArchive();

        final ZipFile zfRecompress = new ZipFile( zipFileRecompress );
        assertEquals( ZipEntry.DEFLATED, zfRecompress.getEntry( "test.zip" ).getMethod() );
        assertEquals( ZipEntry.DEFLATED, zfRecompress.getEntry( "test.jar" ).getMethod() );
        assertEquals( ZipEntry.DEFLATED, zfRecompress.getEntry( "test.rar" ).getMethod() );
        assertEquals( ZipEntry.DEFLATED, zfRecompress.getEntry( "test.tar.gz" ).getMethod() );
        zfRecompress.close();

        // make sure the zip files are not re-compressed when recompressAddedZips is set to false

        final File zipFileDontRecompress = getTestFile( "target/output/dont-recompress-added-zips.zip" );
        ZipArchiver zipArchiver = getZipArchiver( zipFileDontRecompress );
        zipArchiver.addDirectory( getTestFile( "src/test/jars" ) );
        zipArchiver.setRecompressAddedZips( false );
        FileUtils.removePath( zipFileDontRecompress.getPath() );
        zipArchiver.createArchive();

        final ZipFile zfDontRecompress = new ZipFile( zipFileDontRecompress );
        final ZipArchiveEntry zipEntry = zfDontRecompress.getEntry( "test.zip" );
        final ZipArchiveEntry jarEntry = zfDontRecompress.getEntry( "test.jar" );
        final ZipArchiveEntry rarEntry = zfDontRecompress.getEntry( "test.rar" );
        final ZipArchiveEntry tarEntry = zfDontRecompress.getEntry( "test.tar.gz" );
        // check if only zip files are not compressed...
        assertEquals( ZipEntry.STORED, zipEntry.getMethod() );
        assertEquals( ZipEntry.STORED, jarEntry.getMethod() );
        assertEquals( ZipEntry.STORED, rarEntry.getMethod() );
        assertEquals( ZipEntry.DEFLATED, tarEntry.getMethod() );
        // ...and no file is corrupted in the process
        assertTrue( IOUtil.contentEquals( Files.newInputStream( getTestFile( "src/test/jars/test.zip" ).toPath() ),
... (lines 405-444 omitted)
        File a3byteFile = new File( destFile,
                                    "prefixUsers/kristian/lsrc/plexus/plexus-archiver/src/main/java/org/codehaus/plexus/archiver/zip/ZipArchiver.java" );
        assertTrue( a3byteFile.exists() );
        assertTrue( a3byteFile.length() == 3 );
    }

    public void testCreateArchiveWithStreamTransformer()
        throws IOException
    {
        InputStreamTransformer is = new InputStreamTransformer()
        {

            @Nonnull
            @Override
            public InputStream transform( @Nonnull PlexusIoResource resource, @Nonnull InputStream inputStream )
                throws IOException
            {
                return new BoundedInputStream( inputStream, 3 );
            }

        };

        final ZipArchiver zipArchiver = getZipArchiver( getTestFile( "target/output/all3bytes.zip" ) );
        File zipFIle = new File( "src/test/resources/test.zip" );
        DefaultArchivedFileSet afs = new DefaultArchivedFileSet( zipFIle );
        afs.setStreamTransformer( is );
        afs.setPrefix( "azip/" );
        zipArchiver.addArchivedFileSet( afs );

        DefaultFileSet dfs = new DefaultFileSet( new File( "src/test/resources/mjar179" ) );
        dfs.setStreamTransformer( is );
        dfs.setPrefix( "mj179/" );
        zipArchiver.addFileSet( dfs );

        PlexusIoFileResourceCollection files = new PlexusIoFileResourceCollection();
        files.setBaseDir( new File( "src/test/resources" ) );
        files.setStreamTransformer( is );
        files.setPrefix( "plexus/" );
        zipArchiver.addResources( files );

        zipArchiver.createArchive();

    }

    private ZipArchiver newArchiver( String name )
        throws Exception
    {
        ZipArchiver archiver = getZipArchiver( getTestFile( "target/output/" + name ) );

        archiver.setFileMode( 0640 );
        archiver.addFile( getTestFile( "src/test/resources/manifests/manifest1.mf" ), "one.txt" );
        archiver.addFile( getTestFile( "src/test/resources/manifests/manifest2.mf" ), "two.txt", 0664 );

        // reset default file mode for files included from now on
        archiver.setFileMode( 0400 );
        archiver.setDirectoryMode( 0777 );
        archiver.addDirectory( getTestFile( "src/test/resources/world-writable/" ), "worldwritable/" );

        archiver.setDirectoryMode( 0070 );
        archiver.addDirectory( getTestFile( "src/test/resources/group-writable/" ), "groupwritable/" );

        archiver.setDirectoryMode( 0500 );
        archiver.setFileMode( 0400 );
        archiver.addDirectory( getTestFile( "src" ) );

        return archiver;
    }

    private void fileModeAssert( int expected, int actual )
    {
        assertEquals( Integer.toString( expected, 8 ), Integer.toString( actual, 8 ) );
    }

    private void createArchive( ZipArchiver archiver )
        throws ArchiverException, IOException
    {
        archiver.createArchive();

        ZipFile zf = new ZipFile( archiver.getDestFile() );

        Enumeration e = zf.getEntries();

        while ( e.hasMoreElements() )
        {
            ZipArchiveEntry ze = (ZipArchiveEntry) e.nextElement();
            if ( ze.isDirectory() )
            {
                if ( ze.getName().startsWith( "worldwritable" ) )
                {
                    fileModeAssert( 0777, UnixStat.PERM_MASK & ze.getUnixMode() );
                }
                else if ( ze.getName().startsWith( "groupwritable" ) )
                {
                    fileModeAssert( 0070, UnixStat.PERM_MASK & ze.getUnixMode() );
                }
                else
                {
                    fileModeAssert( 0500, UnixStat.PERM_MASK & ze.getUnixMode() );
                }
            }
            else
            {
                if ( ze.getName().equals( "one.txt" ) )
                {
                    fileModeAssert( 0640, UnixStat.PERM_MASK & ze.getUnixMode() );
                }
                else if ( ze.getName().equals( "two.txt" ) )
                {
                    fileModeAssert( 0664, UnixStat.PERM_MASK & ze.getUnixMode() );
                }
                else if ( ze.isUnixSymlink() )
                {
                    //         assertEquals( ze.getName(), 0500, UnixStat.PERM_MASK & ze.getUnixMode() );
                }
                else
                {
                    fileModeAssert( 0400, UnixStat.PERM_MASK & ze.getUnixMode() );
                }
            }

        }
    }

    public void testSymlinkZip()
        throws Exception
    {
        if ( !Os.isFamily( Os.FAMILY_WINDOWS ) )
        {
            final File zipFile = getTestFile( "target/output/pasymlinks.zip" );
            final ZipArchiver zipArchiver = getZipArchiver( zipFile );
            PlexusIoFileResourceCollection files = new PlexusIoFileResourceCollection();
            files.setFollowingSymLinks( false );
            files.setBaseDir( new File( "src/test/resources/symlinks" ) );
            files.setPrefix( "plexus/" );
            zipArchiver.addResources( files );
            zipArchiver.createArchive();
            final File output = getTestFile( "target/output/unzipped" );
            output.mkdirs();
            final ZipUnArchiver zipUnArchiver = getZipUnArchiver( zipFile );
            zipUnArchiver.setDestFile( output );
            zipUnArchiver.extract();
            File symDir = new File( "target/output/unzipped/plexus/src/symDir" );
            PlexusIoResourceAttributes fa = FileAttributes.uncached( symDir );
            assertTrue( fa.isSymbolicLink() );
        }
    }

    @SuppressWarnings( "ResultOfMethodCallIgnored" )
    public void testSymlinkFileSet()
        throws Exception
    {
        if ( !Os.isFamily( Os.FAMILY_WINDOWS ) )
        {
            final File zipFile = getTestFile( "target/output/pasymlinks-fileset.zip" );
            final ZipArchiver zipArchiver = getZipArchiver( zipFile );
            final DefaultFileSet fs = new DefaultFileSet();
            fs.setPrefix( "bzz/" );
            fs.setDirectory( new File( "src/test/resources/symlinks/src" ) );
            zipArchiver.addFileSet( fs );
            zipArchiver.createArchive();
            final File output = getTestFile( "target/output/unzipped/symlFs" );
            output.mkdirs();
            final ZipUnArchiver zipUnArchiver = getZipUnArchiver( zipFile );
            zipUnArchiver.setDestFile( output );
            zipUnArchiver.extract();
            File symDir = new File( output, "bzz/symDir" );
            PlexusIoResourceAttributes fa = FileAttributes.uncached( symDir );
            assertTrue( fa.isSymbolicLink() );
        }
    }

    public void testSymlinkArchivedFileSet()
        throws Exception
    {
        final File zipFile = getTestFile( "src/test/resources/symlinks/symlinks.zip" );
        final File zipFile2 = getTestFile( "target/output/pasymlinks-archivedFileset.zip" );
        final ZipArchiver zipArchiver = getZipArchiver( zipFile2 );
        zipArchiver.addArchivedFileSet( zipFile );
        zipArchiver.createArchive();

        final ZipFile cmp1 = new ZipFile( zipFile );
        final ZipFile cmp2 = new ZipFile( zipFile2 );
        ArchiveFileComparator.assertEquals( cmp1, cmp2, "" );
    }

    /*
     * Zip archives store file modification times with a granularity of two seconds.
     * Verify that ZipArchiver rounds up the last modified time.
     */
    public void testLastModifiedTimeRounding()
        throws Exception
    {
        File oddSecondsTimestampFile = File.createTempFile( "odd-seconds-timestamp", null );
        oddSecondsTimestampFile.deleteOnExit();
        // The milliseconds part is set to zero as not all filesystem support timestamp more granular than second.
        Files.setLastModifiedTime( oddSecondsTimestampFile.toPath(), FileTime.fromMillis( 1534189011_000L ) );
        File evenSecondsTimestampFile = File.createTempFile( "even-seconds-timestamp", null );
        evenSecondsTimestampFile.deleteOnExit();
        Files.setLastModifiedTime( evenSecondsTimestampFile.toPath(), FileTime.fromMillis( 1534189012_000L ) );

        File destFile = getTestFile( "target/output/last-modified-time.zip" );
        ZipArchiver archiver = getZipArchiver( destFile );
        archiver.addFile( oddSecondsTimestampFile, "odd-seconds" );
        archiver.addFile( evenSecondsTimestampFile, "even-seconds" );
        archiver.createArchive();

        // verify that the last modified time of the entry is equal or newer than the original file
        ZipFile resultingZipFile = new ZipFile( destFile );
        assertEquals( 1534189012_000L, resultingZipFile.getEntry( "odd-seconds" ).getTime() );
        assertEquals( 1534189012_000L, resultingZipFile.getEntry( "even-seconds" ).getTime() );
    }

    /*
     */
    public void testForced()
        throws Exception
    {
        ZipArchiver archiver = newArchiver( "archive2.zip" );

        assertTrue( archiver.isForced() );
        File f = archiver.getDestFile();
        if ( f.exists() )
        {
            FileUtils.fileDelete( f.getPath() );
        }
        assertFalse( f.exists() );
        createArchive( archiver );
        long l1 = f.lastModified();
        assertTrue( f.exists() );

        archiver = newArchiver( "archive2.zip" );
        waitUntilNewTimestamp( archiver.getDestFile(), l1 );
        createArchive( archiver );
        long l2 = f.lastModified();
        assertTrue( f.exists() );
        assertTrue( l2 > l1 );

        archiver = newArchiver( "archive2.zip" );
        assertTrue( archiver.isSupportingForced() );
        archiver.setForced( false );
        assertFalse( archiver.isForced() );

        createArchive( archiver );
        long l3 = f.lastModified();
        assertTrue( f.exists() );
        assertEquals( l2, l3 );
    }

    // Used to investigate extrafields
    public void testLookAtExtraZipFields_from_macos()
        throws IOException
    {
        InputStream fis = Streams.fileInputStream( new File( "src/test/resources/zip-timestamp/macOsZipFile.zip" ) );
        ZipInputStream zis = new ZipInputStream( fis );
        final java.util.zip.ZipEntry evenEntry = zis.getNextEntry();
        final ZipExtraField[] parse = ExtraFieldUtils.parse( evenEntry.getExtra() );
        System.out.println( Arrays.asList( parse ) );
        final java.util.zip.ZipEntry oddEntry = zis.getNextEntry();

        System.out.println( Arrays.asList( ExtraFieldUtils.parse( oddEntry.getExtra() ) ) );

        System.out.println( "oddEntry.getTime() = " + new Date( oddEntry.getTime() ).toString() );
        System.out.println( "oddEntry.getName() = " + oddEntry.getName() );
        System.out.println( "new String(oddEntry.getExtra()) = " + new String( oddEntry.getExtra() ) );
        System.out.println( "evenEntry.getName() = " + evenEntry.getName() );
        System.out.println( "evenEntry.getTime() = " + new Date( evenEntry.getTime() ).toString() );
        System.out.println( "new String(evenEntry.getExtra()) = " + new String( evenEntry.getExtra() ) );
... (lines 712-729 omitted)
        zos.close();

        ByteArrayInputStream bais = new ByteArrayInputStream( baos.toByteArray() );
        ZipInputStream zipInputStream = new ZipInputStream( bais );
        final java.util.zip.ZipEntry oddEntry = zipInputStream.getNextEntry();
        System.out.println( "oddEntry.getTime() = " + new Date( oddEntry.getTime() ).toString() );
        System.out.println( "oddEntry.getName() = " + oddEntry.getName() );
        final java.util.zip.ZipEntry evenEntry = zipInputStream.getNextEntry();
        System.out.println( "evenEntry.getName() = " + evenEntry.getName() );
        System.out.println( "evenEntry.getTime() = " + new Date( evenEntry.getTime() ).toString() );
    }

    public void notestJustThatOne()
        throws Exception
    {
        final File srcDir = new File( "src" );
        String[] inc =
        {
            "test/java/org/codehaus/plexus/archiver/zip/ZipShortTest.java"
        };
        final File zipFile = new File( "target/output/zz1.zip" );

        final File zipFile2 = new File( "target/output/zz2.zip" );
        ZipArchiver zipArchiver2 = getZipArchiver( zipFile2 );

        // Bugbug: This does not work on 1.8....?
        zipArchiver2.addArchivedFileSet( zipFile );
        FileUtils.removePath( zipFile2.getPath() );
        zipArchiver2.createArchive();
    }

    public void testCreateResourceCollection()
        throws Exception
    {
        final File srcDir = new File( "src" );
        final File zipFile = new File( "target/output/src.zip" );
        ZipArchiver zipArchiver = getZipArchiver( zipFile );
        zipArchiver.addDirectory( srcDir, null, FileUtils.getDefaultExcludes() );
        zipArchiver.setEncoding( "UTF-8" );
        FileUtils.removePath( zipFile.getPath() );
        zipArchiver.createArchive();

        final File zipFile2 = new File( "target/output/src2.zip" );
        ZipArchiver zipArchiver2 = getZipArchiver( zipFile2 );
        zipArchiver2.addArchivedFileSet( zipFile, "prfx/" );
        zipArchiver2.setEncoding( "UTF-8" );
        FileUtils.removePath( zipFile2.getPath() );
        zipArchiver2.createArchive();

        final ZipFile cmp1 = new ZipFile( zipFile );
        final ZipFile cmp2 = new ZipFile( zipFile2 );
        ArchiveFileComparator.assertEquals( cmp1, cmp2, "prfx/" );
        cmp1.close();
        cmp2.close();
    }

    public void testZipNonConcurrentResourceCollection()
        throws Exception
    {
        final File tarFile = getTestFile( "target/output/zip-non-concurrent.tar" );
        TarArchiver tarArchiver = (TarArchiver) lookup( Archiver.ROLE, "tar" );
        tarArchiver.setDestFile( tarFile );
        // We're testing concurrency issue so we need large amount of files
        for ( int i = 0; i < 100; i++ )
        {
            tarArchiver.addFile( getTestFile( "src/test/resources/manifests/manifest1.mf" ),
                                 "manifest1.mf" + i );
            // Directories are added separately so let's test them too
            tarArchiver.addFile( getTestFile( "src/test/resources/manifests/manifest2.mf" ),
                                 "subdir" + i + "/manifest2.mf" );
        }
        tarArchiver.createArchive();

        final File zipFile = new File( "target/output/zip-non-concurrent.zip" );
        ZipArchiver zipArchive = getZipArchiver( zipFile );
        zipArchive.addArchivedFileSet( tarFile, "prfx/" );
        zipArchive.setEncoding( "UTF-8" );
        zipArchive.createArchive();

        final TarFile cmp1 = new TarFile( tarFile );
        final ZipFile cmp2 = new ZipFile( zipFile );
```

### src/test/java/org/codehaus/plexus/archiver/gzip/GZipArchiverTest.java  (failing test)
```
/*
 * The MIT License
 *
 * Copyright (c) 2004, The Codehaus
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of
 * this software and associated documentation files (the "Software"), to deal in
 * the Software without restriction, including without limitation the rights to
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is furnished to do
 * so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */
package org.codehaus.plexus.archiver.gzip;

import java.io.File;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.Arrays;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

import org.codehaus.plexus.archiver.Archiver;
import org.codehaus.plexus.archiver.BasePlexusArchiverTest;
import org.codehaus.plexus.archiver.exceptions.EmptyArchiveException;
import org.codehaus.plexus.archiver.zip.ZipArchiver;
import org.codehaus.plexus.util.FileUtils;
import org.codehaus.plexus.util.IOUtil;

/**
 * @author Emmanuel Venisse
 */
public class GZipArchiverTest
    extends BasePlexusArchiverTest
{

    public void testCreateArchive()
        throws Exception
    {
        ZipArchiver zipArchiver = (ZipArchiver) lookup( Archiver.ROLE, "zip" );
        zipArchiver.addDirectory( getTestFile( "src" ) );
        zipArchiver.setDestFile( getTestFile( "target/output/archiveForGzip.zip" ) );
        zipArchiver.createArchive();
        GZipArchiver archiver = (GZipArchiver) lookup( Archiver.ROLE, "gzip" );
        String[] inputFiles = new String[ 1 ];
        inputFiles[0] = "archiveForGzip.zip";
        archiver.addDirectory( getTestFile( "target/output" ), inputFiles, null );
        archiver.setDestFile( getTestFile( "target/output/archive.gzip" ) );
        archiver.createArchive();
    }


    public void testCreateEmptyArchive()
        throws Exception
    {
        GZipArchiver archiver = (GZipArchiver) lookup( Archiver.ROLE, "gzip" );
        archiver.setDestFile( getTestFile( "target/output/empty.gz" ) );
        try
        {
            archiver.createArchive();

            fail( "Creating empty archive should throw EmptyArchiveException" );
        }
        catch ( EmptyArchiveException ignore )
        {
        }
    }

    public void testCreateResourceCollection()
        throws Exception
    {
        final File pomFile = new File( "pom.xml" );
        final File gzFile = new File( "target/output/pom.xml.gz" );
        GZipArchiver gzipArchiver = (GZipArchiver) lookup( Archiver.ROLE, "gzip" );
        gzipArchiver.setDestFile( gzFile );
        gzipArchiver.addFile( pomFile, "pom.xml" );
        FileUtils.removePath( gzFile.getPath() );
        gzipArchiver.createArchive();

        final File zipFile = new File( "target/output/pom.zip" );
        ZipArchiver zipArchiver = (ZipArchiver) lookup( Archiver.ROLE, "zip" );
        zipArchiver.setDestFile( zipFile );
        zipArchiver.addArchivedFileSet( gzFile, "prfx/" );
        FileUtils.removePath( zipFile.getPath() );
        zipArchiver.createArchive();

        final ZipFile juZipFile = new ZipFile( zipFile );
        final ZipEntry zipEntry = juZipFile.getEntry( "prfx/target/output/pom.xml" );
        final InputStream archivePom = juZipFile.getInputStream( zipEntry );
        final InputStream pom = Files.newInputStream( pomFile.toPath() );
        assertTrue( Arrays.equals( IOUtil.toByteArray( pom ), IOUtil.toByteArray( archivePom ) ) );
        archivePom.close();
        pom.close();
        juZipFile.close();
    }

    /**
     * Tests the .gzip archiver is forced set to true, and after that
     * tests the behavior when the forced is set to false.
     *
     * @throws Exception
     */
    public void testTarGzIsForcedBehaviour() throws Exception
    {
        GZipArchiver gZipArchiver = (GZipArchiver) createArchiver( "gzip" );

        assertTrue( gZipArchiver.isSupportingForced() );
        gZipArchiver.createArchive();

        final long creationTime = gZipArchiver.getDestFile().lastModified();

        waitUntilNewTimestamp( gZipArchiver.getDestFile(), creationTime );

        gZipArchiver = (GZipArchiver) createArchiver( "gzip" );

        gZipArchiver.setForced( true );
        gZipArchiver.createArchive();

        final long firstRunTime = gZipArchiver.getDestFile().lastModified();

        assertFalse( creationTime == firstRunTime );

        gZipArchiver = (GZipArchiver) createArchiver( "gzip" );

        gZipArchiver.setForced( false );
        gZipArchiver.createArchive();

        final long secondRunTime = gZipArchiver.getDestFile().lastModified();

        assertEquals( firstRunTime, secondRunTime );
    }

}
```

### src/test/java/org/codehaus/plexus/archiver/SymlinkTest.java  (failing test)
```
package org.codehaus.plexus.archiver;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import org.codehaus.plexus.PlexusTestCase;
import org.codehaus.plexus.archiver.dir.DirectoryArchiver;
import org.codehaus.plexus.archiver.tar.TarArchiver;
import org.codehaus.plexus.archiver.tar.TarLongFileMode;
import org.codehaus.plexus.archiver.tar.TarUnArchiver;
import org.codehaus.plexus.archiver.zip.ZipArchiver;
import org.codehaus.plexus.archiver.zip.ZipUnArchiver;
import org.codehaus.plexus.util.Os;

/**
 * @author Kristian Rosenvold
 */
public class SymlinkTest
    extends PlexusTestCase
{

    public void testSymlinkDir()
        throws IOException
    {
        if ( !Os.isFamily( Os.FAMILY_WINDOWS ) )
        {
            File dummyContent = getTestFile( "src/test/resources/symlinks/src/symDir" );
            assertTrue( dummyContent.isDirectory() );
            assertTrue( Files.isSymbolicLink( dummyContent.toPath() ) );
        }
    }

    public void testSymlinkDirWithSlash()
        throws IOException
    {
       
... (truncated: context budget reached)
```

### src/main/resources/META-INF/plexus/components.xml  (resource file named in the failing test)
```

... (truncated: context budget reached)
```

### src/test/resources/folders/b/FileInB.txt  (resource file named in the failing test)
```

... (truncated: context budget reached)
```

### src/test/resources/jar-security/dummy.txt  (resource file named in the failing test)
```

... (truncated: context budget reached)
```

### src/test/resources/zip-timestamp/file-with-even-time.txt  (resource file named in the failing test)
```

... (truncated: context budget reached)
```

### src/test/resources/zip-timestamp/file-with-odd-time.txt  (resource file named in the failing test)
```

... (truncated: context budget reached)
```

### src/test/resources/zip-timestamp/foo/file-with-even-time.txt  (resource file named in the failing test)
```

... (truncated: context budget reached)
```


Now write the explanation and the single ```diff block.
