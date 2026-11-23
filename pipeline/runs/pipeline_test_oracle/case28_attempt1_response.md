Oracle (pipeline test): returning the frozen fix.

```diff
diff --git a/src/main/resources/config/config.yaml b/src/main/resources/config/config.yaml
--- a/src/main/resources/config/config.yaml
+++ b/src/main/resources/config/config.yaml
@@ -27,7 +27,7 @@
       threshold: ERROR
       dsn: ${SENTRY_DSN:-https://example.com@dummy/1}
       environment: ${ENVIRONMENT}
-      stacktraceAppPackages: ["uk.gov.pay"]
+      inAppIncludes: ["uk.gov.pay"]
 
 worldpayDataLocation: ${WORLDPAY_DATA_LOCATION:-file:///app/data/worldpay/GENERIC2ISOCPTISSUERPREPAID.CSV}
 discoverDataLocation: ${DISCOVER_DATA_LOCATION:-file:///app/data/discover/Merchant_Marketing.csv}
```
