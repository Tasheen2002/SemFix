# Case 104 review

open-pdf-sign updates dss-pades-pdfbox from 5.9 to 5.10.2. The root POM version is the sole archived source/POM change, and only this JAR changes on the affected test classpath. Other DSS modules, including dss-pades, remain at 5.9.

PRE succeeds with five tests and no failures, errors or skips. BREAKING fails with five tests and one error, with no failures or skips. Maven and three fresh Surefire reports per phase agree. SignerTest.testSignPdf reports NoSuchMethodError for PdfBoxSignatureService.checkDocumentPermissions(PdfDocumentReader).

Disassembly of the resolved updated PdfBoxSignatureService shows calls to the PdfDocumentReader signature. Its retained AbstractPDFSignatureService superclass in dss-pades 5.9 declares the older checkDocumentPermissions(DSSDocument, String) signature; the old PDFBox 5.9 implementation uses that older signature. This is an incompatible mix of DSS module versions and supports a non-behavioral binary-linkage assessment. It is not evidence of changed PDF signing behavior through compatible methods.

Both original Docker images were run. The command's tee pipeline masks Maven failure in the container exit code; explicit Maven outcomes and fresh XML establish the result. This is an agent assessment pending independent human review. No repair or substitution control was run.
