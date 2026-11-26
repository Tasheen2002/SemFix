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
`org.mockito:mockito-core` was updated from `4.11.0` to `5.1.0`. The project compiles, but tests now fail.

## Failure (from the build log)
Failing test classes: com.google.api.gax.tracing.OpencensusTracerFactoryTest, com.google.api.gax.tracing.OpencensusTracerTest
Exception types: (none)
Error lines:
Project stack frames:
- com.google.api.gax.tracing.OpencensusTracerFactoryTest (OpencensusTracerFactoryTest.java:106)
- com.google.api.gax.tracing.OpencensusTracerTest (OpencensusTracerTest.java:158)

## Similar past breakages and their validated fixes (from the knowledge base)
They come from OTHER projects. Use them for the idea of the fix; adapt it to this project's files.

### Past case 1: org.mockito:mockito-core 4.11.0 -> 5.3.1 (pholser/junit-quickcheck)
Symptom: java.lang.AssertionError
  java.lang.AssertionError: expected:<[3, 6]> but was:<[]>
Behavior change: Default mock maker changed subclass -> inline
Fix (RESEARCHER_WRITTEN, written by the researchers (validated, but not the project's own fix); validated: all tests pass): Restore Mockito's pre-5 default mock maker for the tests (documented Mockito 5 migration option: mockito-extensions/org.mockito.plugins.MockMaker = mock-maker-subclass).
```diff
diff --git a/core/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker b/core/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker
new file mode 100644
--- /dev/null
+++ b/core/src/test/resources/mockito-extensions/org.mockito.plugins.MockMaker
@@ -0,0 +1,1 @@
+mock-maker-subclass
```


## Project files (at the breaking commit)
### pom.xml  (build file (declares the updated dependency))
```
<?xml version='1.0' encoding='UTF-8'?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.google.api</groupId>
  <artifactId>gax-parent</artifactId>
  <packaging>pom</packaging>
  <version>2.20.1</version><!-- {x-version-update:gax:current} -->
  <name>GAX (Google Api eXtensions) for Java (Parent)</name>
  <url>https://github.com/googleapis/gax-java</url>
  <description>Google Api eXtensions for Java (Parent)</description>

  <parent>
    <groupId>com.google.cloud</groupId>
    <artifactId>google-cloud-shared-config</artifactId>
    <version>1.5.5</version>
  </parent>

  <developers>
    <developer>
      <id>GoogleAPIs</id>
      <name>GoogleAPIs</name>
      <email>googleapis@googlegroups.com</email>
      <organization>Google LLC</organization>
      <organizationUrl>https://www.google.com</organizationUrl>
    </developer>
  </developers>

  <scm>
    <connection>scm:git:https://github.com/googleapis/gax-java.git</connection>
    <url>https://github.com/googleapis/gax-java</url>
  </scm>

  <licenses>
    <license>
      <name>BSD</name>
      <url>https://github.com/googleapis/gax-java/blob/master/LICENSE</url>
    </license>
  </licenses>

  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.source>1.8</maven.compiler.source>
    <maven.compiler.target>1.8</maven.compiler.target>
    <auto-value.version>1.10.1</auto-value.version>
  </properties>

  <modules>
    <module>gax</module>
    <module>gax-grpc</module>
    <module>gax-httpjson</module>
    <module>gax-bom</module>
  </modules>

  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>com.google.api</groupId>
        <artifactId>api-common</artifactId>
        <version>2.3.1</version>
      </dependency>
      <dependency>
        <groupId>com.google.auth</groupId>
        <artifactId>google-auth-library-credentials</artifactId>
        <version>1.14.0</version>
      </dependency>
      <dependency>
        <groupId>org.threeten</groupId>
        <artifactId>threetenbp</artifactId>
        <version>1.6.5</version>
      </dependency>
      <dependency>
        <groupId>com.google.auth</groupId>
        <artifactId>google-auth-library-oauth2-http</artifactId>
        <version>1.14.0</version>
        <exclusions>
          <exclusion>
            <groupId>com.google.errorprone</groupId>
            <artifactId>error_prone_annotations</artifactId>
          </exclusion>
        </exclusions>
      </dependency>
      <dependency>
        <groupId>com.google.code.findbugs</groupId>
        <artifactId>jsr305</artifactId>
        <version>3.0.2</version>
      </dependency>
      <dependency>
        <groupId>com.google.guava</groupId>
        <artifactId>guava</artifactId>
        <version>31.1-jre</version>
        <exclusions>
          <exclusion>
            <groupId>com.google.errorprone</groupId>
            <artifactId>error_prone_annotations</artifactId>
          </exclusion>
        </exclusions>
      </dependency>
      <dependency>
        <groupId>io.opencensus</groupId>
        <artifactId>opencensus-api</artifactId>
        <version>0.31.1</version>
      </dependency>
      <dependency>
        <groupId>com.google.auto.value</groupId>
        <artifactId>auto-value-annotations</artifactId>
        <version>${auto-value.version}</version>
      </dependency>
      <dependency>
        <groupId>com.google.auto.value</groupId>
        <artifactId>auto-value</artifactId>
        <version>${auto-value.version}</version>
      </dependency>
      <dependency>
        <groupId>junit</groupId>
        <artifactId>junit</artifactId>
        <version>4.13.2</version>
      </dependency>
      <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-core</artifactId>
        <version>5.1.0</version>
      </dependency>
      <dependency>
        <groupId>com.google.api</groupId>
        <artifactId>gax</artifactId>
        <version>2.20.1</version> <!-- {x-version-update:gax:current} -->
      </dependency>
      <dependency>
        <groupId>com.google.api</groupId>
        <artifactId>gax</artifactId>
        <version>2.20.1</version> <!-- {x-version-update:gax:current} -->
        <type>test-jar</type>
        <classifier>testlib</classifier>
      </dependency>
      <dependency>
        <groupId>com.google.api.grpc</groupId>
        <artifactId>proto-google-common-protos</artifactId>
        <version>2.11.0</version>
      </dependency>
      <dependency>
        <groupId>com.google.api.grpc</groupId>
        <artifactId>grpc-google-common-protos</artifactId>
        <version>2.11.0</version>
      </dependency>
      <dependency>
        <groupId>io.grpc</groupId>
        <artifactId>grpc-bom</artifactId>
        <version>1.51.1</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
      <dependency>
        <groupId>com.google.code.gson</groupId>
        <artifactId>gson</artifactId>
        <version>2.10</version>
      </dependency>
      <dependency>
        <groupId>org.graalvm.sdk</groupId>
        <artifactId>graal-sdk</artifactId>
        <version>22.3.0</version>
      </dependency>
      <dependency>
        <groupId>com.google.http-client</groupId>
        <artifactId>google-http-client-bom</artifactId>
        <version>1.42.3</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
      <dependency>
        <groupId>com.google.protobuf</groupId>
        <artifactId>protobuf-bom</artifactId>
        <version>3.21.12</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
    </dependencies>
  </dependencyManagement>

  <!-- Test Dependencies -->
  <dependencies>
    <dependency>
      <groupId>junit</groupId>
      <artifactId>junit</artifactId>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>org.mockito</groupId>
      <artifactId>mockito-core</artifactId>
      <scope>test</scope>
    </dependency>
    <dependency>
      <groupId>com.google.truth</groupId>
      <artifactId>truth</artifactId>
      <version>1.1.3</version>
      <exclusions>
        <exclusion>
          <groupId>org.checkerframework</groupId>
          <artifactId>checker-qual</artifactId>
        </exclusion>
        <exclusion>
          <groupId>com.google.errorprone</groupId>
          <artifactId>error_prone_annotations</artifactId>
        </exclusion>
      </exclusions>
      <scope>test</scope>
    </dependency>
  </dependencies>

  <build>
    <resources>
      <resource>
        <directory>src/main/resources</directory>
        <filtering>true</filtering>
      </resource>
    </resources>
    <plugins>
      <plugin>
        <artifactId>maven-compiler-plugin</artifactId>
        <configuration>
          <annotationProcessorPaths>
            <path>
              <groupId>com.google.auto.value</groupId>
              <artifactId>auto-value</artifactId>
              <version>${auto-value.version}</version>
            </path>
          </annotationProcessorPaths>
          <release>8</release>
          <compilerArgs>
            <arg>-Xlint:unchecked</arg>
            <arg>-Xlint:deprecation</arg>
          </compilerArgs>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <executions>
          <execution>
            <goals>
              <goal>test-jar</goal>
            </goals>
            <configuration>
              <skip>true</skip>
            </configuration>
          </execution>
        </executions>
      </plugin>
      <plugin>
        <groupId>com.coveo</groupId>
        <artifactId>fmt-maven-plugin</artifactId>
        <executions>
          <execution>
            <phase>validate</phase>
            <goals>
              <goal>check</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
    </plugins>
  </build>

  <profiles>
    <profile>
      <!-- profile for nexus-staging:release invocation -->
      <id>release-staging-repository</id>
      <build>
        <plugins>
          <plugin>
            <!-- The root project runs nexus-staging:release task -->
            <groupId>org.sonatype.plugins</groupId>
            <artifactId>nexus-staging-maven-plugin</artifactId>
            <version>1.6.13</version>
            <extensions>true</extensions>
            <configuration>
              <serverId>sonatype-nexus-staging</serverId>
              <nexusUrl>https://google.oss.sonatype.org/</nexusUrl>
              <autoReleaseAfterClose>false</autoReleaseAfterClose>
            </configuration>
          </plugin>
        </plugins>
      </build>
    </profile>
  </profiles>
</project>
```

### gax/src/test/java/com/google/api/gax/tracing/OpencensusTracerFactoryTest.java  (failing test)
```
/*
 * Copyright 2019 Google LLC
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 *     * Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above
 * copyright notice, this list of conditions and the following disclaimer
 * in the documentation and/or other materials provided with the
 * distribution.
 *     * Neither the name of Google LLC nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
package com.google.api.gax.tracing;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.ArgumentMatchers.nullable;
import static org.mockito.ArgumentMatchers.same;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.api.gax.tracing.ApiTracerFactory.OperationType;
import com.google.common.collect.ImmutableMap;
import io.grpc.Context;
import io.opencensus.trace.AttributeValue;
import io.opencensus.trace.Span;
import io.opencensus.trace.SpanBuilder;
import io.opencensus.trace.Tracer;
import io.opencensus.trace.unsafe.ContextUtils;
import java.util.Map;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;
import org.mockito.Mock;
import org.mockito.junit.MockitoJUnit;
import org.mockito.junit.MockitoRule;

@RunWith(JUnit4.class)
public class OpencensusTracerFactoryTest {
  @Rule public final MockitoRule mockitoRule = MockitoJUnit.rule();
  @Mock private Tracer internalTracer;
  @Mock private SpanBuilder spanBuilder;
  @Mock private Span span;
  private final Map<String, String> defaultSpanAttributes = ImmutableMap.of();

  @Before
  public void setUp() {
    when(internalTracer.spanBuilderWithExplicitParent(anyString(), nullable(Span.class)))
        .thenReturn(spanBuilder);

    when(spanBuilder.setRecordEvents(true)).thenReturn(spanBuilder);

    when(spanBuilder.startSpan()).thenReturn(span);
  }

  @Test
  public void testSpanNamePassthrough() {
    OpencensusTracerFactory factory =
        new OpencensusTracerFactory(internalTracer, ImmutableMap.<String, String>of());

    factory.newTracer(
        BaseApiTracer.getInstance(), SpanName.of("FakeClient", "FakeMethod"), OperationType.Unary);

    verify(internalTracer)
        .spanBuilderWithExplicitParent(eq("FakeClient.FakeMethod"), nullable(Span.class));
  }

  @Test
  public void testImplicitParentSpan() {
    OpencensusTracerFactory factory =
        new OpencensusTracerFactory(internalTracer, defaultSpanAttributes);

    Span parentSpan = mock(Span.class);
    Context origContext = ContextUtils.withValue(Context.current(), parentSpan).attach();

    try {
      factory.newTracer(
          BaseApiTracer.getInstance(),
          SpanName.of("FakeClient", "FakeMethod"),
          OperationType.Unary);
    } finally {
      Context.current().detach(origContext);
    }

    verify(internalTracer).spanBuilderWithExplicitParent(anyString(), same(parentSpan));
  }

  @Test
  public void testExplicitParent() {
    OpencensusTracerFactory factory =
        new OpencensusTracerFactory(internalTracer, defaultSpanAttributes);

    Span parentSpan = mock(Span.class);
    OpencensusTracer parentTracer =
        new OpencensusTracer(internalTracer, parentSpan, OperationType.Unary);

    factory.newTracer(parentTracer, SpanName.of("FakeClient", "FakeMethod"), OperationType.Unary);

    verify(internalTracer).spanBuilderWithExplicitParent(anyString(), same(parentSpan));
  }

  @Test
  public void testExplicitParentOverridesImplicit() {
    OpencensusTracerFactory factory =
        new OpencensusTracerFactory(internalTracer, defaultSpanAttributes);

    Span parentSpan = mock(Span.class);
    OpencensusTracer parentTracer =
        new OpencensusTracer(internalTracer, parentSpan, OperationType.Unary);

    Context origContext = ContextUtils.withValue(Context.current(), parentSpan).attach();

    try {
      factory.newTracer(parentTracer, SpanName.of("FakeClient", "FakeMethod"), OperationType.Unary);
    } finally {
      Context.current().detach(origContext);
    }

    verify(internalTracer).spanBuilderWithExplicitParent(anyString(), same(parentSpan));
  }

  @Test
  public void testSpanAttributes() {
    OpencensusTracerFactory factory =
        new OpencensusTracerFactory(internalTracer, ImmutableMap.of("gax.version", "1.2.3"));

    factory.newTracer(
        BaseApiTracer.getInstance(), SpanName.of("FakeClient", "FakeMethod"), OperationType.Unary);

    verify(span, times(1))
        .putAttributes(
            ImmutableMap.of("gax.version", AttributeValue.stringAttributeValue("1.2.3")));
  }
}
```

### gax/src/test/java/com/google/api/gax/tracing/OpencensusTracerTest.java  (failing test)
```
/*
 * Copyright 2019 Google LLC
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 *
 *     * Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above
 * copyright notice, this list of conditions and the following disclaimer
 * in the documentation and/or other materials provided with the
 * distribution.
 *     * Neither the name of Google LLC nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
package com.google.api.gax.tracing;

import static com.google.common.truth.Truth.assertThat;
import static org.mockito.Mockito.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoMoreInteractions;

import com.google.api.gax.retrying.ServerStreamingAttemptException;
import com.google.api.gax.rpc.ApiException;
import com.google.api.gax.rpc.DeadlineExceededException;
import com.google.api.gax.rpc.NotFoundException;
import com.google.api.gax.rpc.StatusCode.Code;
import com.google.api.gax.rpc.testing.FakeStatusCode;
import com.google.api.gax.tracing.ApiTracerFactory.OperationType;
import com.google.common.collect.ImmutableMap;
import io.opencensus.trace.AttributeValue;
import io.opencensus.trace.EndSpanOptions;
import io.opencensus.trace.Span;
import io.opencensus.trace.Status;
import io.opencensus.trace.Status.CanonicalCode;
import io.opencensus.trace.Tracer;
import java.util.Map;
import org.junit.Before;
import org.junit.Rule;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;
import org.mockito.ArgumentCaptor;
import org.mockito.Captor;
import org.mockito.Mock;
import org.mockito.junit.MockitoJUnit;
import org.mockito.junit.MockitoRule;
import org.mockito.quality.Strictness;
import org.threeten.bp.Duration;

@RunWith(JUnit4.class)
public class OpencensusTracerTest {
  @Rule
  public final MockitoRule mockitoRule = MockitoJUnit.rule().strictness(Strictness.STRICT_STUBS);

  @Mock private Tracer internalTracer;
  @Mock private Span span;
  @Captor private ArgumentCaptor<Map<String, AttributeValue>> attributeCaptor;

  private OpencensusTracer tracer;

  @Before
  public void setUp() {
    tracer = new OpencensusTracer(internalTracer, span, OperationType.Unary);
  }

  @Test
  public void testUnarySuccessExample() {
    tracer.attemptStarted(0);
    tracer.connectionSelected("1");
    ApiException error0 =
        new DeadlineExceededException(
            "deadline exceeded", null, new FakeStatusCode(Code.DEADLINE_EXCEEDED), true);
    tracer.attemptFailed(error0, Duration.ofMillis(5));

    tracer.attemptStarted(1);
    tracer.connectionSelected("2");
    tracer.attemptSucceeded();
    tracer.operationSucceeded();

    // Attempt 0
    verify(span)
        .addAnnotation(
            "Attempt failed, scheduling next attempt",
            ImmutableMap.of(
                "attempt", AttributeValue.longAttributeValue(0),
                "delay ms", AttributeValue.longAttributeValue(5),
                "status", AttributeValue.stringAttributeValue("DEADLINE_EXCEEDED"),
                "status message", AttributeValue.stringAttributeValue("deadline exceeded"),
                "connection", AttributeValue.stringAttributeValue("1")));

    // Attempt 1
    verify(span)
        .addAnnotation(
            "Attempt succeeded",
            ImmutableMap.of(
                "attempt", AttributeValue.longAttributeValue(1),
                "connection", AttributeValue.stringAttributeValue("2")));

    verify(span)
        .putAttributes(ImmutableMap.of("attempt count", AttributeValue.longAttributeValue(2)));
    verify(span).end();

    verifyNoMoreInteractions(span);
  }

  @Test
  public void testBatchExample() {
    tracer.batchRequestSent(100, 1000);
    tracer.attemptStarted(0);
    tracer.connectionSelected("1");
    tracer.attemptSucceeded();
    tracer.operationSucceeded();

    verify(span).putAttribute("batch count", AttributeValue.longAttributeValue(100));
    verify(span).putAttribute("batch size", AttributeValue.longAttributeValue(1000));
  }

  @Test
  public void testLongRunningExample() {
    tracer = new OpencensusTracer(internalTracer, span, OperationType.LongRunning);

    // Initial poll of the initial rpc
    tracer.attemptStarted(0);
    tracer.attemptFailed(null, Duration.ofMillis(5));

    // Initial rpc finished
    tracer.lroStartSucceeded();

    // First real poll
    tracer.attemptStarted(1);
    tracer.attemptSucceeded();
    tracer.operationSucceeded();

    // Attempt 0 - initial poll of the initial rpc
    verify(span)
        .addAnnotation(
            "Scheduling next poll",
            ImmutableMap.of(
                "attempt", AttributeValue.longAttributeValue(0),
                "delay ms", AttributeValue.longAttributeValue(5),
                "status", AttributeValue.stringAttributeValue("OK")));

    verify(span).addAnnotation("Operation started", ImmutableMap.<String, AttributeValue>of());

    // Attempt 1 - first real poll
    verify(span)
        .addAnnotation(
            "Polling completed", ImmutableMap.of("attempt", AttributeValue.longAttributeValue(1)));

    verify(span)
        .putAttributes(ImmutableMap.of("attempt count", AttributeValue.longAttributeValue(2)));
    verify(span).end();

    verifyNoMoreInteractions(span);
  }

  @Test
  public void testRetriesExhaustedExample() {
    tracer.attemptStarted(0);
    tracer.connectionSelected("1");
    ApiException error0 =
        new DeadlineExceededException(
            "deadline exceeded", null, new FakeStatusCode(Code.DEADLINE_EXCEEDED), false);
    tracer.attemptFailedRetriesExhausted(error0);
    tracer.operationFailed(error0);

    verify(span)
        .addAnnotation(
            "Attempts exhausted",
            ImmutableMap.of(
                "attempt", AttributeValue.longAttributeValue(0),
                "status", AttributeValue.stringAttributeValue("DEADLINE_EXCEEDED"),
                "status message", AttributeValue.stringAttributeValue("deadline exceeded"),
                "connection", AttributeValue.stringAttributeValue("1")));

    verify(span)
        .putAttributes(ImmutableMap.of("attempt count", AttributeValue.longAttributeValue(1)));

    verify(span)
        .end(
            EndSpanOptions.builder()
                .setStatus(Status.DEADLINE_EXCEEDED.withDescription("deadline exceeded"))
                .build());

    verifyNoMoreInteractions(span);
  }

  @Test
  public void testCancellationExample() {
    tracer.attemptStarted(0);
    tracer.connectionSelected("1");
    tracer.attemptCancelled();
    tracer.operationCancelled();

    verify(span)
        .addAnnotation(
            "Attempt cancelled",
            ImmutableMap.of(
                "attempt", AttributeValue.longAttributeValue(0),
                "connection", AttributeValue.stringAttributeValue("1")));

    verify(span)
        .putAttributes(ImmutableMap.of("attempt count", AttributeValue.longAttributeValue(1)));

    verify(span)
        .end(
            EndSpanOptions.builder()
                .setStatus(Status.CANCELLED.withDescription("Cancelled by caller"))
                .build());
    verifyNoMoreInteractions(span);
  }

  @Test
  public void testFailureExample() {
    tracer.attemptStarted(0);
    tracer.connectionSelected("1");
    ApiException error0 =
        new NotFoundException("not found", null, new FakeStatusCode(Code.NOT_FOUND), false);
    tracer.attemptPermanentFailure(error0);
    tracer.operationFailed(error0);

    verify(span)
        .addAnnotation(
            "Attempt failed, error not retryable",
            ImmutableMap.of(
                "attempt", AttributeValue.longAttributeValue(0),
                "status", AttributeValue.stringAttributeValue("NOT_FOUND"),
                "status message", AttributeValue.stringAttributeValue("not found"),
                "connection", AttributeValue.stringAttributeValue("1")));

    verify(span)
        .putAttributes(ImmutableMap.of("attempt count", AttributeValue.longAttributeValue(1)));

    verify(span)
        .end(
            EndSpanOptions.builder()
                .setStatus(Status.NOT_FOUND.withDescription("not found"))
                .build());
    verifyNoMoreInteractions(span);
  }

  @Test
  public void testResponseCount() {
    // Initial attempt got 2 messages, then failed
    tracer.attemptStarted(0);
    tracer.responseReceived();
    tracer.responseReceived();
    tracer.attemptFailed(new RuntimeException(), Duration.ofMillis(1));

    // Next attempt got 1 message, then successfully finished the attempt and the logical operation.
    tracer.attemptStarted(1);
    tracer.responseReceived();
    tracer.attemptSucceeded();
    tracer.operationSucceeded();

    verify(span)
        .addAnnotation(eq("Attempt failed, scheduling next attempt"), attributeCaptor.capture());
    assertThat(attributeCaptor.getValue())
        .containsEntry("attempt response count", AttributeValue.longAttributeValue(2));

    verify(span).addAnnotation(eq("Attempt succeeded"), attributeCaptor.capture());
    assertThat(attributeCaptor.getValue())
        .containsEntry("attempt response count", AttributeValue.longAttributeValue(1));

    verify(span).putAttributes(attributeCaptor.capture());
    assertThat(attributeCaptor.getValue())
        .containsEntry("total response count", AttributeValue.longAttributeValue(3));
  }

  @Test
  public void testRequestCount() {
    // Initial attempt sent 2 messages, then failed
    tracer.attemptStarted(0);
    tracer.requestSent();
    tracer.requestSent();
    tracer.attemptFailed(new RuntimeException(), Duration.ofMillis(1));

    // Next attempt sent 1 message, then successfully finished the attempt and the logical
    // operation.
    tracer.attemptStarted(1);
    tracer.requestSent();
    tracer.attemptSucceeded();
    tracer.operationSucceeded();

    verify(span)
        .addAnnotation(eq("Attempt failed, scheduling next attempt"), attributeCaptor.capture());
    assertThat(attributeCaptor.getValue())
        .containsEntry("attempt request count", AttributeValue.longAttributeValue(2));

    verify(span).addAnnotation(eq("Attempt succeeded"), attributeCaptor.capture());
    assertThat(attributeCaptor.getValue())
        .containsEntry("attempt request count", AttributeValue.longAttributeValue(1));

    verify(span).putAttributes(attributeCaptor.capture());
    assertThat(attributeCaptor.getValue())
        .containsEntry("total request count", AttributeValue.longAttributeValue(3));
  }

  @Test
  public void testAttemptNumber() {
    tracer.attemptStarted(0);
    tracer.attemptFailed(new RuntimeException(), Duration.ofMillis(1));
    tracer.attemptStarted(1);
    tracer.attemptSucceeded();
    tracer.operationSucceeded();

    verify(span)
        .addAnnotation(eq("Attempt failed, scheduling next attempt"), attributeCaptor.capture());
    assertThat(attributeCaptor.getValue())
        .containsEntry("attempt", AttributeValue.longAttributeValue(0));

    verify(span).addAnnotation(eq("Attempt succeeded"), attributeCaptor.capture());
    assertThat(attributeCaptor.getValue())
        .containsEntry("attempt", AttributeValue.longAttributeValue(1));

    verify(span).putAttributes(attributeCaptor.capture());
    assertThat(attributeCaptor.getValue())
        .containsEntry("attempt count", AttributeValue.longAttributeValue(2));
  }

  @Test
  public void testStatusCode() {
    tracer.attemptStarted(0);
    tracer.attemptFailed(
        new DeadlineExceededException(
            "deadline exceeded", null, new FakeStatusCode(Code.DEADLINE_EXCEEDED), true),
        Duration.ofMillis(1));

    tracer.attemptStarted(1);
    ApiException permanentError =
        new NotFoundException("not found", null, new FakeStatusCode(Code.NOT_FOUND), false);
    tracer.attemptPermanentFailure(permanentError);
    tracer.operationFailed(permanentError);

    verify(span)
        .addAnnotation(eq("Attempt failed, scheduling next attempt"), attributeCaptor.capture());
    assertThat(attributeCaptor.getValue())
        .containsEntry("status", AttributeValue.stringAttributeValue("DEADLINE_EXCEEDED"));

    verify(span)
        .addAnnotation(eq("Attempt failed, error not retryable"), attributeCaptor.capture());
    assertThat(attributeCaptor.getValue())
        .containsEntry("status", AttributeValue.stringAttributeValue("NOT_FOUND"));
  }

  @Test
  public void testErrorConversion() {
    for (Code code : Code.values()) {
      ApiException error = new ApiException("fake message", null, new FakeStatusCode(code), false);
      Status opencensusStatus = OpencensusTracer.convertErrorToStatus(error);
      assertThat(opencensusStatus.getDescription()).isEqualTo("fake message");
      assertThat(opencensusStatus.getCanonicalCode().toString()).isEqualTo(code.toString());
    }
  }

  @Test
  public void testStreamingErrorConversion() {
    ServerStreamingAttemptException error =
        new ServerStreamingAttemptException(
            new DeadlineExceededException(
                "timeout", null, new FakeStatusCode(Code.DEADLINE_EXCEEDED), true),
            true,
            true);
    Status opencensusStatus = OpencensusTracer.convertErrorToStatus(error);
    assertThat(opencensusStatus.getDescription()).isEqualTo("timeout");
    assertThat(opencensusStatus.getCanonicalCode()).isEqualTo(CanonicalCode.DEADLINE_EXCEEDED);
  }
}
```


Now write the explanation and the single ```diff block.
