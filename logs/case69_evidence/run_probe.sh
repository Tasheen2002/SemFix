#!/bin/sh
set -eu
echo pre
if java -cp /root/.m2/repository/org/graalvm/js/js/22.0.0/js-22.0.0.jar:/root/.m2/repository/org/graalvm/regex/regex/22.0.0/regex-22.0.0.jar:/root/.m2/repository/org/graalvm/truffle/truffle-api/22.0.0/truffle-api-22.0.0.jar:/root/.m2/repository/org/graalvm/sdk/graal-sdk/22.0.0/graal-sdk-22.0.0.jar:/evidence/pre/js-scriptengine-22.0.0.jar /evidence/ScriptEngineProbe.java; then status=0; else status=$?; fi
echo exit=$status
test "$status" -eq 0
echo breaking
if java -cp /root/.m2/repository/org/graalvm/js/js/22.0.0/js-22.0.0.jar:/root/.m2/repository/org/graalvm/regex/regex/22.0.0/regex-22.0.0.jar:/root/.m2/repository/org/graalvm/truffle/truffle-api/22.0.0/truffle-api-22.0.0.jar:/root/.m2/repository/org/graalvm/sdk/graal-sdk/22.0.0/graal-sdk-22.0.0.jar:/evidence/breaking/js-scriptengine-22.1.0.jar /evidence/ScriptEngineProbe.java; then status=0; else status=$?; fi
echo exit=$status
test "$status" -eq 1
