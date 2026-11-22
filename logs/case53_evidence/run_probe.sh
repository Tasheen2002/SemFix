set -eu
mkdir /tmp/probe
for spec in pre/plexus-io-3.2.0.jar breaking/plexus-io-3.3.0.jar; do
echo "$spec"
cp="/evidence/$spec:/root/.m2/repository/org/codehaus/plexus/plexus-container-default/2.1.1/plexus-container-default-2.1.1.jar:/root/.m2/repository/org/codehaus/plexus/plexus-classworlds/2.6.0/plexus-classworlds-2.6.0.jar:/root/.m2/repository/org/apache/xbean/xbean-reflect/3.7/xbean-reflect-3.7.jar:/root/.m2/repository/org/codehaus/plexus/plexus-utils/3.4.1/plexus-utils-3.4.1.jar:/root/.m2/repository/commons-io/commons-io/2.11.0/commons-io-2.11.0.jar:/root/.m2/repository/org/apache/commons/commons-compress/1.21/commons-compress-1.21.jar:/root/.m2/repository/org/iq80/snappy/snappy/0.4/snappy-0.4.jar:/root/.m2/repository/org/tukaani/xz/1.9/xz-1.9.jar:/root/.m2/repository/com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar:/root/.m2/repository/junit/junit/4.13.2/junit-4.13.2.jar:/root/.m2/repository/org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar:"
javac -cp "$cp" -d /tmp/probe /evidence/DirectoryProbe.java
java -cp "/tmp/probe:$cp" DirectoryProbe
done
