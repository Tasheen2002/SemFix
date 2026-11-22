#!/bin/sh
set -eu

file=orcid-message-listener/src/main/java/org/orcid/listener/solr/OrcidRecordToSolrDocument.java
original='LocalDate localDate = LocalDate.now();'
fixed='LocalDate localDate = LocalDate.of(2024, 12, 31);'
test "$(grep -Fc "$original" "$file")" -eq 1
sed -i 's/LocalDate localDate = LocalDate.now();/LocalDate localDate = LocalDate.of(2024, 12, 31);/' "$file"
grep -Fn "$fixed" "$file"
java -version
mvn -version

case "${1:?expected pre or breaking}" in
    pre)
        exec mvn clean test -B
        ;;
    breaking)
        exec mvn -B -pl orcid-core -am clean test -Dtest=org.orcid.core.SourceInActivitiesTest -Dsurefire.failIfNoSpecifiedTests=false
        ;;
    *)
        exit 2
        ;;
esac
