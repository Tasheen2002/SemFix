"""Create adversarial self-test patches for the repair harness (harness/selftest/patches/).
Each has a known expected verdict, so the harness can be shown not to accept non-repairs.
Usage: python -I make_selftest_patches.py <research root>
"""
import difflib, json, os, re, subprocess, sys

ROOT = sys.argv[1]
P = lambda *x: os.path.join(ROOT, *x)
cases = {c["case"]: c for c in json.load(open(P("fix_mining", "cases.json"), encoding="utf-8"))}
OUT = P("harness", "selftest", "patches"); os.makedirs(OUT, exist_ok=True)


def show(n, path):
    c = cases[n]
    r = subprocess.run(["git", "-C", P("fix_mining", "repos", c["repo"]), "show", f"{c['id']}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8")


def diff(path, old, new):
    a, b = old.splitlines(keepends=True), new.splitlines(keepends=True)
    return f"diff --git a/{path} b/{path}\n" + "".join(difflib.unified_diff(a, b, f"a/{path}", f"b/{path}", n=3))


def delete(path, old):
    lines = old.splitlines(keepends=True)
    return (f"diff --git a/{path} b/{path}\ndeleted file mode 100644\n--- a/{path}\n+++ /dev/null\n"
            f"@@ -1,{len(lines)} +0,0 @@\n" + "".join("-" + l for l in lines)
            + ("" if old.endswith("\n") else "\n\\ No newline at end of file\n"))


specs = {}
pom = show(2, "pom.xml")
specs["case2_noop.patch"] = (2, diff("pom.xml", pom, pom.replace("</project>", "<!-- no-op -->\n</project>", 1)),
                             "NOT_REPAIRED", ["TARGET_FIXED"])
rev, k = re.subn(r"(<artifactId>slf4j-api</artifactId>\s*<version>)2\.0\.4(</version>)", r"\g<1>1.7.36\g<2>", pom)
assert k == 1
specs["case2_revert_update.patch"] = (2, diff("pom.xml", pom, rev), "NOT_REPAIRED", ["UPDATE_KEPT"])
t = "src/test/java/net/masterthought/cucumber/ReportBuilderTest.java"
specs["case13_delete_failing_test.patch"] = (13, delete(t, show(13, t)), "NOT_REPAIRED", ["TARGET_FIXED", "NO_REGRESSION"])

manifest = []
for name, (n, text, verdict, failing) in specs.items():
    open(os.path.join(OUT, name), "w", encoding="utf-8", newline="").write(text)
    manifest.append(dict(case=n, patch=f"harness/selftest/patches/{name}", expected_verdict=verdict, expected_failed_checks=failing))
manifest.insert(0, dict(case=2, patch="fix_mining/fixes_v1.0/reference_fixes/case2.patch", expected_verdict="REPAIRED", expected_failed_checks=[]))
json.dump(manifest, open(P("harness", "selftest", "expected.json"), "w", encoding="utf-8"), indent=1)
print(json.dumps(manifest, indent=1))
