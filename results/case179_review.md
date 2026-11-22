# Case 179 review

jcabi-ssh updates sshd-core from 2.9.2 to 2.10.0.

SSHD Core 2.10.0 requires CancelOption, absent from retained SSHD Common 2.9.2. The reports contain two missing-class errors and one connection reset.

| Original run | Maven outcome | Reported tests | Failures | Errors | Skipped |
|---|---|---:|---:|---:|---:|
| PRE | SUCCESS | 5 | 0 | 0 | 0 |
| BREAKING | FAILURE | 5 | 0 | 3 | 0 |

Recorded assessment is `NON_BEHAVIORAL`. Binary linkage flag is `YES`. Independent human review is pending.

Changed POMs in the image comparison are pom.xml. The affected report classpaths list sshd-core-2.9.2.jar in PRE and sshd-core-2.10.0.jar in BREAKING.

Original logs and archived reports are indexed in the evidence manifest.
