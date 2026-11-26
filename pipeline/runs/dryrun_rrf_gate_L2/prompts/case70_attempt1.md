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
`org.json:json` was updated from `20090211` to `20230227`. The project compiles, but tests now fail.

## Failure (from the build log)
Failing test classes: org.geoserver.shell.ScriptCommandsTest
Exception types: org.json.JSONException
Error lines:
- org.json.JSONException: JSONObject["id"] is not a string (class java.lang.Integer : 0).
- org.json.JSONException: JSONObject["id"] is not a string (class java.lang.Integer : 1).
Project stack frames:
- org.geoserver.shell.ScriptCommands (ScriptCommands.java:298)
- org.geoserver.shell.ScriptCommandsTest (ScriptCommandsTest.java:422)
- org.geoserver.shell.ScriptCommands (ScriptCommands.java:314)
- org.geoserver.shell.ScriptCommandsTest (ScriptCommandsTest.java:437)

## Project files (at the breaking commit)
### pom.xml  (build file (declares the updated dependency))
```
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>org.geoserver</groupId>
    <artifactId>geoserver-shell</artifactId>
    <version>0.4-SNAPSHOT</version>
    <packaging>jar</packaging>
    <name>geoserver-shell</name>
    <url>http://maven.apache.org</url>
    <properties>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.shell</groupId>
            <artifactId>spring-shell</artifactId>
            <version>1.2.0.RELEASE</version>
        </dependency>
        <dependency>
            <groupId>it.geosolutions</groupId>
            <artifactId>geoserver-manager</artifactId>
            <version>1.7.0</version>
        </dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-api</artifactId>
            <version>1.6.6</version>
        </dependency>
        <dependency>
            <groupId>org.slf4j</groupId>
            <artifactId>slf4j-nop</artifactId>
            <version>1.6.6</version>
        </dependency>
        <dependency>
            <groupId>org.json</groupId>
            <artifactId>json</artifactId>
            <version>20230227</version>
        </dependency>
        <dependency>
            <groupId>org.geotools</groupId>
            <artifactId>gt-main</artifactId>
            <version>24.0</version>
        </dependency>
        <dependency>
            <groupId>org.geotools</groupId>
            <artifactId>gt-epsg-hsql</artifactId>
            <version>24.0</version>
        </dependency>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.1</version>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.xebialabs.restito</groupId>
            <artifactId>restito</artifactId>
            <version>0.8.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
    <repositories>
        <repository>
            <id>osgeo-releases</id>
            <name>OSGeo Nexus Release Repository</name>
            <url>https://repo.osgeo.org/repository/release/</url>
            <snapshots>
                <enabled>false</enabled>
            </snapshots>
            <releases>
                <enabled>true</enabled>
            </releases>
        </repository>
        <repository>
            <id>osgeo-snapshots</id>
            <name>OSGeo Nexus Snapshot Repository</name>
            <url>https://repo.osgeo.org/repository/snapshot/</url>
            <snapshots>
                <enabled>true</enabled>
            </snapshots>
            <releases>
                <enabled>false</enabled>
            </releases>
        </repository>
        <repository>
            <id>geosolutions</id>
            <url>https://maven.geo-solutions.it/</url>
        </repository>
    </repositories>
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.0</version>
                <configuration>
                    <source>1.8</source>
                    <target>1.8</target>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.codehaus.mojo</groupId>
                <artifactId>cobertura-maven-plugin</artifactId>
                <version>2.7</version>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-jar-plugin</artifactId>
                <version>3.2.0</version>
                <configuration>
                    <archive>
                        <manifest>
                            <addClasspath>true</addClasspath>
                            <mainClass>org.springframework.shell.Bootstrap</mainClass>
                        </manifest>
                    </archive>
                </configuration>
            </plugin>
            <plugin>
                <artifactId>maven-assembly-plugin</artifactId>
                <version>3.3.0</version>
                <configuration>
                    <descriptors>
                        <descriptor>src/main/assembly/dir.xml</descriptor>
                        <descriptor>src/main/assembly/zip.xml</descriptor>
                    </descriptors>
                </configuration>
                <executions>
                    <execution>
                        <id>make-assembly</id>
                        <phase>package</phase>
                        <goals>
                            <goal>single</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-shade-plugin</artifactId>
                <version>3.2.4</version>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals>
                            <goal>shade</goal>
                        </goals>
                        <configuration>
                            <finalName>gs-shell-${project.version}</finalName>
                            <transformers>
                                <transformer
                                        implementation="org.apache.maven.plugins.shade.resource.AppendingTransformer">
                                    <resource>META-INF/spring.handlers</resource>
                                </transformer>
                                <transformer
                                        implementation="org.apache.maven.plugins.shade.resource.AppendingTransformer">
                                    <resource>META-INF/spring.schemas</resource>
                                </transformer>
                                <transformer
                                        implementation="org.apache.maven.plugins.shade.resource.ManifestResourceTransformer">
                                    <mainClass>org.springframework.shell.Bootstrap</mainClass>
                                </transformer>
                                <transformer
                                        implementation="org.apache.maven.plugins.shade.resource.ServicesResourceTransformer"/>
                                <transformer
                                        implementation="org.apache.maven.plugins.shade.resource.XmlAppendingTransformer">
                                    <resource>META-INF/spring/spring-shell-plugin.xml</resource>
                                </transformer>
                            </transformers>
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
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

### src/test/java/org/geoserver/shell/ScriptCommandsTest.java  (failing test)
```
... (lines 0-0 omitted)
package org.geoserver.shell;

import org.apache.commons.io.FileUtils;
import org.glassfish.grizzly.http.Method;
import org.glassfish.grizzly.http.util.HttpStatus;
import org.junit.Test;
import org.springframework.shell.support.util.OsUtils;

import java.io.File;
import java.io.FileWriter;

import static com.xebialabs.restito.builder.stub.StubHttp.whenHttp;
import static com.xebialabs.restito.builder.verify.VerifyHttp.verifyHttp;
import static com.xebialabs.restito.semantics.Action.status;
import static com.xebialabs.restito.semantics.Action.stringContent;
import static com.xebialabs.restito.semantics.Condition.*;
import static junit.framework.Assert.assertEquals;
import static junit.framework.Assert.assertTrue;

public class ScriptCommandsTest extends BaseTest {

    // WPS

    @Test
    public void listWps() throws Exception {
        whenHttp(server).match(get("/geoserver/rest/scripts/wps.json")).then(stringContent(getResourceString("scripts.json")), status(HttpStatus.OK_200));

        Geoserver geoserver = new Geoserver("http://00.0.0.0:8888/geoserver", "admin", "geoserver");
        ScriptCommands commands = new ScriptCommands();
        commands.setGeoserver(geoserver);
        String actual = commands.listWps();
        String expected = "buffer.groovy" + OsUtils.LINE_SEPARATOR + "merge.groovy" + OsUtils.LINE_SEPARATOR;
        assertEquals(expected, actual);

        verifyHttp(server).once(method(Method.GET), uri("/geoserver/rest/scripts/wps.json"));
    }

    @Test
    public void getWps() throws Exception {
        whenHttp(server).match(get("/geoserver/rest/scripts/wps/buffer.groovy")).then(stringContent(getResourceString("script.groovy")), status(HttpStatus.OK_200));
... (lines 41-381 omitted)

        Geoserver geoserver = new Geoserver("http://00.0.0.0:8888/geoserver", "admin", "geoserver");
        ScriptCommands commands = new ScriptCommands();
        commands.setGeoserver(geoserver);

        File file = File.createTempFile("buffer", "groovy");
        FileWriter writer = new FileWriter(file);
        writer.write(getResourceString("script.groovy"));
        writer.close();

        boolean result = commands.modifyApp("buffer", "groovy", file);
        assertTrue(result);

        verifyHttp(server).once(method(Method.PUT), uri("/geoserver/rest/scripts/apps/buffer/main.groovy"));
    }

    @Test
    public void deleteApp() throws Exception {
        whenHttp(server).match(delete("/geoserver/rest/scripts/apps/buffer/main.groovy")).then(stringContent("true"), status(HttpStatus.OK_200));

        Geoserver geoserver = new Geoserver("http://00.0.0.0:8888/geoserver", "admin", "geoserver");
        ScriptCommands commands = new ScriptCommands();
        commands.setGeoserver(geoserver);

        boolean result = commands.deleteApp("buffer","groovy");
        assertTrue(result);

        verifyHttp(server).once(method(Method.DELETE), uri("/geoserver/rest/scripts/apps/buffer/main.groovy"));
    }

    // Session

    @Test
    public void listSession() throws Exception {
        whenHttp(server).match(get("/geoserver/rest/sessions")).then(stringContent(getResourceString("sessions.json")), status(HttpStatus.OK_200));

        Geoserver geoserver = new Geoserver("http://00.0.0.0:8888/geoserver", "admin", "geoserver");
        ScriptCommands commands = new ScriptCommands();
        commands.setGeoserver(geoserver);

        String actual = commands.listSession(null);
        String expected = "0 groovy" + OsUtils.LINE_SEPARATOR + "1 python" + OsUtils.LINE_SEPARATOR;
        assertEquals(expected, actual);

        verifyHttp(server).once(method(Method.GET), uri("/geoserver/rest/sessions"));
    }

    @Test
    public void getSession() throws Exception {
        whenHttp(server).match(get("/geoserver/rest/sessions/groovy/1")).then(stringContent(getResourceString("session.json")), status(HttpStatus.OK_200));

        Geoserver geoserver = new Geoserver("http://00.0.0.0:8888/geoserver", "admin", "geoserver");
        ScriptCommands commands = new ScriptCommands();
        commands.setGeoserver(geoserver);

        String actual = commands.getSession("groovy","1");
        String expected = "1 groovy" + OsUtils.LINE_SEPARATOR;
        assertEquals(expected, actual);

        verifyHttp(server).once(method(Method.GET), uri("/geoserver/rest/sessions/groovy/1"));
    }

    @Test
    public void createSession() throws Exception {
        whenHttp(server).match(post("/geoserver/rest/sessions/groovy")).then(stringContent("1"), status(HttpStatus.OK_200));

        Geoserver geoserver = new Geoserver("http://00.0.0.0:8888/geoserver", "admin", "geoserver");
        ScriptCommands commands = new ScriptCommands();
        commands.setGeoserver(geoserver);

        String actual = commands.createSession("groovy");
        String expected = "1";
        assertEquals(expected, actual);

        verifyHttp(server).once(method(Method.POST), uri("/geoserver/rest/sessions/groovy"));
    }

    @Test
    public void runSession() throws Exception {
        whenHttp(server).match(put("/geoserver/rest/sessions/groovy/1")).then(stringContent("Hello World!"), status(HttpStatus.OK_200));

        Geoserver geoserver = new Geoserver("http://00.0.0.0:8888/geoserver", "admin", "geoserver");
        ScriptCommands commands = new ScriptCommands();
        commands.setGeoserver(geoserver);

        String actual = commands.runSession("groovy","1","println 'Hello World!'");
        String expected = "Hello World!";
        assertEquals(expected, actual);

        verifyHttp(server).once(method(Method.PUT), uri("/geoserver/rest/sessions/groovy/1"));
    }

}
```

### src/test/resources/scripts.json  (resource file named in the failing test)
```
{
    scripts: {
        script: [
            {name: "buffer.groovy"},
            {name: "merge.groovy"}
        ]
    }
}
```

### src/test/resources/session.json  (resource file named in the failing test)
```
{
    id: 1,
    engine: "groovy"
}
```

### src/test/resources/sessions.json  (resource file named in the failing test)
```
{
    sessions: [
        {id: 0, engine: "groovy"},
        {id: 1, engine: "python"}
    ]
}
```

### src/main/java/org/geoserver/shell/ScriptCommands.java  (class in the failing stack trace)
```
package org.geoserver.shell;

import it.geosolutions.geoserver.rest.HTTPUtils;
import org.apache.commons.io.FileUtils;
import org.json.JSONArray;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.shell.core.CommandMarker;
import org.springframework.shell.core.annotation.CliAvailabilityIndicator;
import org.springframework.shell.core.annotation.CliCommand;
import org.springframework.shell.core.annotation.CliOption;
import org.springframework.shell.support.util.OsUtils;
import org.springframework.stereotype.Component;

import java.io.File;

@Component("GeoServerScriptCommands")
public class ScriptCommands implements CommandMarker {

    @Autowired
    private Geoserver geoserver;

    public void setGeoserver(Geoserver gs) {
        this.geoserver = gs;
    }

    @CliAvailabilityIndicator({
            "scripting wps list", "scripting wps get", "scripting wps create", "scripting wps modify", "scripting wps delete",
            "scripting function list", "scripting function get", "scripting function create", "scripting function modify", "scripting function delete",
            "scripting wfs tx list", "scripting wfs tx get", "scripting wfs tx create", "scripting wfs tx modify", "scripting wfs tx delete",
            "scripting app list", "scripting app get", "scripting app create", "scripting app modify", "scripting app delete",
            "scripting session list", "scripting session get", "scripting session create", "scripting session run"
    })
    public boolean isCommandAvailable() {
        return geoserver.isSet();
    }

    // WPS

    @CliCommand(value = "scripting wps list", help = "List WPS scripts.")
    public String listWps() throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/wps.json";
        String result = HTTPUtils.get(url, geoserver.getUser(), geoserver.getPassword());
        JSONObject scriptsObject = new JSONObject(result).getJSONObject("scripts");
        JSONArray jsonArray = scriptsObject.getJSONArray("script");
        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < jsonArray.length(); i++) {
            String script = jsonArray.getJSONObject(i).getString("name");
            builder.append(script).append(OsUtils.LINE_SEPARATOR);
        }
        return builder.toString();
    }

    @CliCommand(value = "scripting wps get", help = "Get a WPS script.")
    public String getWps(
            @CliOption(key = "name", mandatory = true, help = "The script name") String name,
            @CliOption(key = "file", mandatory = false, help = "The output File") File file
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/wps/" + URLUtil.encode(name);
        String result = HTTPUtils.get(url, geoserver.getUser(), geoserver.getPassword());
        if (file != null) {
            FileUtils.write(file, result);
            return file.getAbsolutePath();
        } else {
            return result;
        }
    }

    @CliCommand(value = "scripting wps create", help = "Create a WPS script.")
    public boolean createWps(
            @CliOption(key = "name", mandatory = true, help = "The script name") String name,
            @CliOption(key = "file", mandatory = true, help = "The script File") File file
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/wps/" + URLUtil.encode(name);
        String result = HTTPUtils.put(url, file, "text/plain", geoserver.getUser(), geoserver.getPassword());
        return result != null;
    }

    @CliCommand(value = "scripting wps modify", help = "Modify a WPS script.")
    public boolean modifyWps(
            @CliOption(key = "name", mandatory = true, help = "The script name") String name,
            @CliOption(key = "file", mandatory = true, help = "The script File") File file
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/wps/" + URLUtil.encode(name);
        String result = HTTPUtils.put(url, file, "plain/text", geoserver.getUser(), geoserver.getPassword());
        return result != null;
    }

    @CliCommand(value = "scripting wps delete", help = "Delete a WPS script.")
    public boolean deleteWps(
            @CliOption(key = "name", mandatory = true, help = "The script name") String name
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/wps/" + URLUtil.encode(name);
        boolean result = HTTPUtils.delete(url, geoserver.getUser(), geoserver.getPassword());
        return result;
    }

    // Function

    @CliCommand(value = "scripting function list", help = "List filter function scripts.")
    public String listFunctions() throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/function.json";
        String result = HTTPUtils.get(url, geoserver.getUser(), geoserver.getPassword());
        JSONObject scriptsObject = new JSONObject(result).getJSONObject("scripts");
        JSONArray jsonArray = scriptsObject.getJSONArray("script");
        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < jsonArray.length(); i++) {
            String script = jsonArray.getJSONObject(i).getString("name");
            builder.append(script).append(OsUtils.LINE_SEPARATOR);
        }
        return builder.toString();
    }

    @CliCommand(value = "scripting function get", help = "Get a filter function script.")
    public String getFunction(
            @CliOption(key = "name", mandatory = true, help = "The script name") String name,
            @CliOption(key = "file", mandatory = false, help = "The output File") File file
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/function/" + URLUtil.encode(name);
        String result = HTTPUtils.get(url, geoserver.getUser(), geoserver.getPassword());
        if (file != null) {
            FileUtils.write(file, result);
            return file.getAbsolutePath();
        } else {
            return result;
        }
    }

    @CliCommand(value = "scripting function create", help = "Create a filter function script.")
    public boolean createFunction(
            @CliOption(key = "name", mandatory = true, help = "The script name") String name,
            @CliOption(key = "file", mandatory = true, help = "The script File") File file
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/function/" + URLUtil.encode(name);
        String result = HTTPUtils.put(url, file, "plain/text", geoserver.getUser(), geoserver.getPassword());
        return result != null;
    }

    @CliCommand(value = "scripting function modify", help = "Modify a filter function script.")
    public boolean modifyFunction(
            @CliOption(key = "name", mandatory = true, help = "The script name") String name,
            @CliOption(key = "file", mandatory = true, help = "The script File") File file
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/function/" + URLUtil.encode(name);
        String result = HTTPUtils.put(url, file, "plain/text", geoserver.getUser(), geoserver.getPassword());
        return result != null;
    }

    @CliCommand(value = "scripting function delete", help = "Delete a filter function script.")
    public boolean deleteFunction(
            @CliOption(key = "name", mandatory = true, help = "The script name") String name
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/function/" + URLUtil.encode(name);
        boolean result = HTTPUtils.delete(url, geoserver.getUser(), geoserver.getPassword());
        return result;
    }

    // WFS TX

    @CliCommand(value = "scripting wfs tx list", help = "List wfs transaction scripts.")
    public String listWfsTx() throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/wfs/tx.json";
        String result = HTTPUtils.get(url, geoserver.getUser(), geoserver.getPassword());
        JSONObject scriptsObject = new JSONObject(result).getJSONObject("scripts");
        JSONArray jsonArray = scriptsObject.getJSONArray("script");
        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < jsonArray.length(); i++) {
            String script = jsonArray.getJSONObject(i).getString("name");
            builder.append(script).append(OsUtils.LINE_SEPARATOR);
        }
        return builder.toString();
    }

    @CliCommand(value = "scripting wfs tx get", help = "Get a wfs transaction script.")
    public String getWfsTx(
            @CliOption(key = "name", mandatory = true, help = "The script name") String name,
            @CliOption(key = "file", mandatory = true, help = "The script File") File file
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/wfs/tx/" + URLUtil.encode(name);
        String result = HTTPUtils.get(url, geoserver.getUser(), geoserver.getPassword());
        if (file != null) {
            FileUtils.write(file, result);
            return file.getAbsolutePath();
        } else {
            return result;
        }
    }

    @CliCommand(value = "scripting wfs tx create", help = "Create a wfs transaction script.")
    public boolean createWfsTx(
            @CliOption(key = "name", mandatory = true, help = "The script name") String name,
            @CliOption(key = "file", mandatory = true, help = "The script File") File file
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/wfs/tx/" + URLUtil.encode(name);
        String result = HTTPUtils.put(url, file, "plain/text", geoserver.getUser(), geoserver.getPassword());
        return result != null;
    }

    @CliCommand(value = "scripting wfs tx modify", help = "Modify a wfs transaction script.")
    public boolean modifyWfsTx(
            @CliOption(key = "name", mandatory = true, help = "The script name") String name,
            @CliOption(key = "file", mandatory = true, help = "The script File") File file
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/wfs/tx/" + URLUtil.encode(name);
        String result = HTTPUtils.put(url, file, "plain/text", geoserver.getUser(), geoserver.getPassword());
        return result != null;
    }

    @CliCommand(value = "scripting wfs tx delete", help = "Delete a wfs transaction script.")
    public boolean deleteWfsTx(
            @CliOption(key = "name", mandatory = true, help = "The script name") String name
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/wfs/tx/" + URLUtil.encode(name);
        boolean result = HTTPUtils.delete(url, geoserver.getUser(), geoserver.getPassword());
        return result;
    }

    // App

    @CliCommand(value = "scripting app list", help = "List scripting apps.")
    public String listApps() throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/apps.json";
        String result = HTTPUtils.get(url, geoserver.getUser(), geoserver.getPassword());
        JSONObject scriptsObject = new JSONObject(result).getJSONObject("scripts");
        JSONArray jsonArray = scriptsObject.getJSONArray("script");
        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < jsonArray.length(); i++) {
            String script = jsonArray.getJSONObject(i).getString("name");
            builder.append(script).append(OsUtils.LINE_SEPARATOR);
        }
        return builder.toString();
    }

    @CliCommand(value = "scripting app get", help = "Get an app script.")
    public String getApp(
            @CliOption(key = "name", mandatory = true, help = "The app name") String name,
            @CliOption(key = "type", mandatory = true, help = "The app type (groovy, js, py)") String type,
            @CliOption(key = "file", mandatory = false, help = "The output File") File file
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/apps/" + URLUtil.encode(name) + "/main." + type;
        String result = HTTPUtils.get(url, geoserver.getUser(), geoserver.getPassword());
        if (file != null) {
            FileUtils.write(file, result);
            return file.getAbsolutePath();
        } else {
            return result;
        }
    }

    @CliCommand(value = "scripting app create", help = "Create a script app.")
    public boolean createApp(
            @CliOption(key = "name", mandatory = true, help = "The app name") String name,
            @CliOption(key = "type", mandatory = true, help = "The app type (groovy, js, py)") String type,
            @CliOption(key = "file", mandatory = true, help = "The script File") File file
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/apps/" + URLUtil.encode(name) + "/main." + type;
        String result = HTTPUtils.put(url, file, "plain/text", geoserver.getUser(), geoserver.getPassword());
        return result != null;
    }

    @CliCommand(value = "scripting app modify", help = "Modify a script app.")
    public boolean modifyApp(
            @CliOption(key = "name", mandatory = true, help = "The app name") String name,
            @CliOption(key = "type", mandatory = true, help = "The app type (groovy, js, py)") String type,
            @CliOption(key = "file", mandatory = true, help = "The script File") File file
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/apps/" + URLUtil.encode(name) + "/main." + type;
        String result = HTTPUtils.put(url, file, "plain/text", geoserver.getUser(), geoserver.getPassword());
        return result != null;
    }

    @CliCommand(value = "scripting app delete", help = "Delete a script app.")
    public boolean deleteApp(
            @CliOption(key = "name", mandatory = true, help = "The app name") String name,
            @CliOption(key = "type", mandatory = true, help = "The app type (groovy, js, py)") String type
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/scripts/apps/" + URLUtil.encode(name) + "/main." + type;
        boolean result = HTTPUtils.delete(url, geoserver.getUser(), geoserver.getPassword());
        return result;
    }

    // Session

    @CliCommand(value = "scripting session list", help = "List scripting sessions.")
    public String listSession(
            @CliOption(key = "ext", mandatory = false, help = "The script extension") String ext
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/sessions";
        if (ext != null) {
            url += "/" + URLUtil.encode(ext);
        }
        String result = HTTPUtils.get(url, geoserver.getUser(), geoserver.getPassword());
        JSONObject rootJsonObject = new JSONObject(result);
        JSONArray jsonArray = rootJsonObject.getJSONArray("sessions");
        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject jsonObject = jsonArray.getJSONObject(i);
            builder.append(jsonObject.getString("id")).append(" ")
                    .append(jsonObject.get("engine"))
                    .append(OsUtils.LINE_SEPARATOR);
        }
        return builder.toString();
    }

    @CliCommand(value = "scripting session get", help = "Get a scripting script.")
    public String getSession(
            @CliOption(key = "ext", mandatory = true, help = "The script extension") String ext,
            @CliOption(key = "name", mandatory = true, help = "The name") String name
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/sessions/" + URLUtil.encode(ext) + "/" + URLUtil.encode(name);
        String result = HTTPUtils.get(url, geoserver.getUser(), geoserver.getPassword());
        JSONObject jsonObject = new JSONObject(result);
        StringBuilder builder = new StringBuilder();
        builder.append(jsonObject.getString("id")).append(" ")
                .append(jsonObject.get("engine"))
                .append(OsUtils.LINE_SEPARATOR);
        return builder.toString();
    }

    @CliCommand(value = "scripting session create", help = "Create a scripting session.")
    public String createSession(
            @CliOption(key = "ext", mandatory = true, help = "The script extension") String ext
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/sessions/" + URLUtil.encode(ext);
        String result = HTTPUtils.post(url, "", "", geoserver.getUser(), geoserver.getPassword());
        return result;
    }

    @CliCommand(value = "scripting session run", help = "Run a script in a scripting session.")
    public String runSession(
            @CliOption(key = "ext", mandatory = true, help = "The script extension") String ext,
            @CliOption(key = "name", mandatory = true, help = "The name") String name,
            @CliOption(key = "script", mandatory = true, help = "The script") String script
    ) throws Exception {
        String url = geoserver.getUrl() + "/rest/sessions/" + URLUtil.encode(ext) + "/" + URLUtil.encode(name);
        try {
            File file = new File(script);
            if (file.exists()) {
                script = FileUtils.readFileToString(file);
            }
        } catch (Exception ex) {
            // Do nothing, just treat script as text
        }
        String result = HTTPUtils.put(url, script, "text/plain", geoserver.getUser(), geoserver.getPassword());
        return result;
    }

}
```


Now write the explanation and the single ```diff block.
