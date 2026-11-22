#!/bin/sh
# Targeted verification checks for the Claude AI second review.
# Each check: fresh --rm container from the original BREAKING image, unique name, Maven exit code captured
# directly (no tee). Output: audit_claude_review/reruns/case<N>_<check>.log and runs.jsonl
# Usage: sh run_checks.sh <workspace_root> <case>... (cases: 104 105 116 122 143 178 3 21 71 30 69)
set -u
ROOT="$1"; shift
OUT="$ROOT/audit_claude_review/reruns"; mkdir -p "$OUT"
cid() { python -I -c "import csv,sys;print([r['case_id'] for r in csv.DictReader(open(sys.argv[1],encoding='utf-8'))][int(sys.argv[2])-1])" "$ROOT/results/test_failure_candidates.csv" "$1"; }

# Maven command per case; MVN_OFFLINE first, then online fallback if a plugin is missing from the image's .m2
cmd_for() {
  case "$1" in
    104) echo "mvn -B dependency:tree -Dincludes=eu.europa.ec.joinup.sd-dss" ;;
    105) echo "mvn -B -DskipTests test-compile dependency:tree -Dincludes=org.apache.logging.log4j" ;;
    122|143|3|21) echo "mvn -B -DskipTests test-compile dependency:tree -Dincludes=com.fasterxml.jackson.core" ;;
    178) echo "mvn -B dependency:tree -Dincludes=org.springframework" ;;
    71) echo "mvn -B -DskipTests test-compile dependency:tree -Dincludes=com.google.flogger" ;;
    116) echo "mvn -B test -pl maven-plugin -am -Dsurefire.trimStackTrace=false; E=\$?; echo MAVEN_TEST_EXIT=\$E; echo '=== dumpstreams ==='; find . -path '*maven-plugin/target/surefire-reports*' \\( -name '*.dumpstream' -o -name '*.dump' \\) -exec sh -c 'echo \"## {}\"; head -c 20000 {}' \\; ; echo '=== junit on test classpath ==='; mvn -B -o dependency:tree -pl maven-plugin -Dincludes=junit:junit; exit \$E" ;;
    # Single-change controls (POM edited inside the throwaway container only; updated dependency retained)
    30) echo "sed -i 's#</dependencies>#<dependency><groupId>org.eclipse.persistence</groupId><artifactId>org.eclipse.persistence.asm</artifactId><version>9.4.0</version></dependency></dependencies>#' pom.xml; echo CONTROL_EDIT_COUNT=\$(grep -c org.eclipse.persistence.asm pom.xml); grep -n -A1 'persistence.moxy' pom.xml; mvn -B test" ;;
    69) echo "sed -i 's#<version>22.0.0</version>#<version>22.1.0</version>#' pom.xml; echo CONTROL_EDIT:; grep -n -B2 '22.1.0' pom.xml; mvn -B test" ;;
    *) echo "" ;;
  esac
}
check_name() { case "$1" in 116) echo "vintage_discovery";; 30) echo "asm_provider_control";; 69) echo "graaljs_alignment_control";; *) echo "dependency_tree";; esac; }

for n in "$@"; do
  id=$(cid "$n"); img="ghcr.io/chains-project/breaking-updates:${id}-breaking"
  name="audit-claude-case${n}-$(check_name "$n")"
  log="$OUT/case${n}_$(check_name "$n").log"
  if ! docker image inspect "$img" >/dev/null 2>&1; then
    echo "{\"case\": $n, \"image\": \"$img\", \"status\": \"IMAGE_NOT_PRESENT\"}" >> "$OUT/runs.jsonl"; echo "case $n: image not present"; continue
  fi
  imgid=$(docker image inspect "$img" --format '{{.Id}}')
  c=$(cmd_for "$n")
  start=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  # Offline first; if Maven fails for a missing plugin/artifact, retry online and record that.
  docker run --rm --name "$name" --entrypoint sh "$imgid" -c "echo '### OFFLINE ATTEMPT'; $(echo "$c" | sed 's/^mvn /mvn -o /'); echo MAVEN_EXIT=\$?" > "$log" 2>&1
  if grep -qE "MAVEN_EXIT=[1-9]" "$log" && grep -qiE "offline|Cannot access|Could not resolve|plugin .* or one of its dependencies could not be resolved" "$log"; then
    docker run --rm --name "$name-online" --entrypoint sh "$imgid" -c "echo '### ONLINE ATTEMPT'; $c; echo MAVEN_EXIT=\$?" >> "$log" 2>&1
  fi
  end=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  ex=$(grep -oE "MAVEN_EXIT=[0-9]+" "$log" | tail -1 | cut -d= -f2)
  printf '{"case": %s, "case_id": "%s", "check": "%s", "image_id": "%s", "container": "%s", "start": "%s", "end": "%s", "maven_exit": "%s", "log": "audit_claude_review/reruns/%s"}\n' \
    "$n" "$id" "$(check_name "$n")" "$imgid" "$name" "$start" "$end" "$ex" "$(basename "$log")" >> "$OUT/runs.jsonl"
  echo "case $n done: maven_exit=$ex"
done
