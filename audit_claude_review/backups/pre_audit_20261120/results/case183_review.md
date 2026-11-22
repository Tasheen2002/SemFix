# Case 183 review

quarkus-micrometer-registry updates quarkus-google-cloud-common-grpc from 1.4.0 to 2.2.0.

The gRPC update changes proto-google-common-protos from 2.14.0 to 2.22.1. Its MetricDescriptor calls LazyStringArrayList.emptyList(), which is inaccessible in retained protobuf-java 3.14.0. Quarkus integration test startup fails with IllegalAccessError.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 19 | 0 | 0 | 0 |
| BREAKING | FAILURE | 19 | 0 | 1 | 0 |

Assessment is `NON_BEHAVIORAL`. Binary linkage flag is `YES`. Independent human review is pending.

Changed POMs in the original archives are micrometer-registry-stackdriver/runtime/pom.xml. Original logs and archived reports are indexed in the evidence manifest.
