"""Build blind per-case evidence digests for the Claude second review.

Reads ONLY primary evidence: candidate inventory, PRE/BREAKING logs, evidence
archives, POM comparisons, JAR inspections and probe outputs. It deliberately
does NOT read Codex label/rationale columns, caseN_review.md, append_case_N.py,
or auto_triage labels.

Usage: python -I make_digests.py <workspace_root> <first_case> <last_case>
"""
import csv, difflib, hashlib, io, json, os, re, sys, tarfile
import xml.etree.ElementTree as ET

ROOT = sys.argv[1]
FIRST, LAST = int(sys.argv[2]), int(sys.argv[3])
OUT = os.path.join(ROOT, "audit_claude_review", "digests")
P = lambda *a: os.path.join(ROOT, *a)

cands = list(csv.DictReader(open(P("results", "test_failure_candidates.csv"), encoding="utf-8")))
# Only log-path columns are taken from the classification file.
logpaths = {}
for r in csv.DictReader(open(P("results", "behavioral_classification.csv"), encoding="utf-8")):
    logpaths[r["case_id"]] = (r["pre_log"], r["breaking_log"])

ENCODING_NOTES = []
ANSI = re.compile(r"\x1b\[[0-9;]*m")
EXC = re.compile(r"([A-Za-z_$][\w$]*\.)+[A-Z][\w$]*(Exception|Error|Failure|Throwable)\b")
LINK = re.compile(r"NoSuchMethodError|NoClassDefFoundError|ClassNotFoundException|NoSuchFieldError|"
                  r"AbstractMethodError|IncompatibleClassChangeError|UnsupportedClassVersionError|"
                  r"class file (version|has wrong version)|VerifyError|LinkageError|ServiceConfigurationError|"
                  r"cannot find symbol|cannot access|package .* does not exist|COMPILATION ERROR|IllegalAccessError")


def read_log(path):
    full = P(path)
    if not os.path.exists(full):
        return None
    raw = open(full, "rb").read()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff") or raw[:200].count(b"\x00") > 50:
        txt = raw.decode("utf-16", errors="replace")
        ENCODING_NOTES.append(path)
    else:
        txt = raw.decode("utf-8", errors="replace")
    return [ANSI.sub("", l.rstrip("\r")) for l in txt.split("\n")]


def summarize_log(lines, breaking):
    out = []
    if lines is None:
        return ["  LOG MISSING"]
    out.append(f"  lines={len(lines)}")
    status = [l for l in lines if re.search(r"BUILD (SUCCESS|FAILURE)", l)]
    out.append("  status: " + (" | ".join(s.strip() for s in status[-3:]) or "NONE (no BUILD line)"))
    # reactor summary
    for i, l in enumerate(lines):
        if "Reactor Summary" in l:
            block = []
            for m in lines[i + 1:i + 60]:
                if re.search(r"(SUCCESS|FAILURE|SKIPPED)\s*\[", m) or re.search(r"(SUCCESS|FAILURE|SKIPPED)$", m.strip()):
                    block.append(m.replace("[INFO] ", "").strip())
                elif "BUILD" in m:
                    break
            out.append("  reactor: " + "; ".join(re.sub(r"\.{2,}", " ", b) for b in block)[:900])
            break
    # aggregate test summaries (lines without ' - in ' / ' in ')
    aggs = [l for l in lines if re.search(r"Tests run: \d+, Failures: \d+, Errors: \d+, Skipped: \d+\s*$", l)]
    if aggs:
        out.append("  aggregate summaries: " + " || ".join(a.replace("[INFO] ", "").replace("[ERROR] ", "").replace("[WARNING] ", "").strip() for a in aggs[:12]))
    tn = [l for l in lines if re.search(r"Total tests run:|Tests run: \d+, Failures: \d+, Errors: \d+, Skipped: \d+, Time", l) and ("FAIL" in l or "ERROR" in l)]
    if tn:
        out.append("  failing classes: " + " || ".join(re.sub(r"\[\w+\]\s*", "", x).strip()[:220] for x in tn[:10]))
    # failed tests sections
    for key in ("Failed tests:", "Tests in error:", "[ERROR] Failures:", "[ERROR] Errors:", "Tests run:.*FAILURE"):
        pass
    for i, l in enumerate(lines):
        s = l.strip()
        if re.match(r"\[(ERROR|INFO|WARNING)\]\s+(Failures|Errors|Failed tests|Tests in error):\s*$", s) or s in ("Failed tests:", "Tests in error:"):
            blk = [lines[j].replace("[ERROR]", "").strip() for j in range(i, min(i + 14, len(lines))) if lines[j].strip() and "Tests run:" not in lines[j]]
            out.append("  section: " + " | ".join(blk)[:1200])
    if breaking or True:
        errs = [l for l in lines if l.startswith("[ERROR]") and not re.search(r"<<< (ERROR|FAILURE)!|Tests run:|Help 1|re-run Maven|full stack trace|-X switch|For more information|^\[ERROR\]\s*$|Please refer|dump files|cwiki|After correcting|mvn <args>|-rf :|^\[ERROR\]\s+(Errors|Failures):|^\[ERROR\]\s+\S+[.#]\S+.*»|^\[ERROR\]\s+(Run \d|  )", l)]
        if errs:
            out.append("  first [ERROR] lines:")
            seen = set()
            for e in errs:
                k = e[:160]
                if k in seen:
                    continue
                seen.add(k)
                out.append("    " + e[:260])
                if len(seen) >= 10:
                    break
        # first failure/error test blocks
        n = 0
        fbseen = {}
        for i, l in enumerate(lines):
            if re.search(r"<<< (FAILURE|ERROR)!", l) and "Tests run" not in l:
                sig = next((m.strip()[:120] for m in lines[i + 1:i + 3] if m.strip()), "")
                if sig in fbseen:
                    fbseen[sig] += 1
                    continue
                fbseen[sig] = 1
                n += 1
                out.append("  FAILBLOCK: " + l.strip()[:220])
                for m in lines[i + 1:i + 7]:
                    if m.strip():
                        out.append("      " + m.strip()[:260])
                causes = []
                for m in lines[i + 1:i + 300]:
                    if "<<< " in m and ("FAILURE" in m or "ERROR" in m):
                        break
                    if m.strip().startswith("Caused by:"):
                        causes.append(m.strip()[:260])
                for c in causes[:4]:
                    out.append("      " + c)
                if n >= 4:
                    break
        if len(fbseen) > 0:
            out.append("  distinct fail signatures (count): " + " || ".join(f"{v}x {k}" for k, v in list(fbseen.items())[:8]))
        sl = []
        for l in lines:
            if re.match(r"\s*(SLF4J|SLF4J\(\w\)|log4j:|ERROR StatusLogger|WARNING: An illegal|LOGBACK)", l) or "StatusLogger" in l:
                k = l.strip()[:200]
                if k not in sl:
                    sl.append(k)
            if len(sl) >= 10:
                break
        if sl:
            out.append("  provider/console lines: " + " | ".join(sl))
        link = sorted({m.group(0) for l in lines for m in [LINK.search(l)] if m})
        if link:
            out.append("  linkage/compile signals: " + ", ".join(link))
        excs = {}
        for l in lines:
            for m in EXC.finditer(l):
                excs[m.group(0)] = excs.get(m.group(0), 0) + 1
        if excs:
            out.append("  exception names: " + ", ".join(f"{k}x{v}" for k, v in sorted(excs.items(), key=lambda x: -x[1])[:14]))
    return out


def tar_members(path):
    res = {}
    try:
        with tarfile.open(path) as t:
            for m in t.getmembers():
                if m.isfile():
                    data = t.extractfile(m).read()
                    res[m.name] = data
    except Exception as e:
        res["__error__"] = str(e).encode()
    return res


def surefire_failures(members, limit=10):
    out = []
    for name, data in members.items():
        if not (name.endswith(".xml") and ("surefire-reports" in name or "failsafe-reports" in name or "test-results" in name) and "TEST-" in os.path.basename(name)):
            continue
        try:
            root = ET.fromstring(data)
        except Exception:
            continue
        for tc in root.iter("testcase"):
            for kind in ("failure", "error"):
                for el in tc.findall(kind):
                    msg = (el.get("message") or "").replace("\n", " ")[:300]
                    txt = el.text or ""
                    causes = [l.strip() for l in txt.splitlines() if l.strip().startswith("Caused by:")]
                    frames = [l.strip() for l in txt.splitlines() if l.strip().startswith("at ")][:4]
                    out.append(f"    {kind.upper()} {tc.get('classname')}#{tc.get('name')} type={el.get('type')} msg={msg}")
                    for c in causes[:3]:
                        out.append("       " + c[:250])
                    for fr in frames:
                        out.append("       " + fr[:200])
    if len(out) > limit * 6:
        out = out[:limit * 6] + [f"    ... truncated ({len(out)} lines)"]
    return out


def source_diff(pre, brk):
    out = []
    skip = lambda n: ("surefire-reports" in n or "failsafe-reports" in n or n.endswith(".class") or "/target/" in "/" + n)
    pk = {k for k in pre if not skip(k)}
    bk = {k for k in brk if not skip(k)}
    added, removed = sorted(bk - pk), sorted(pk - bk)
    changed = sorted(k for k in pk & bk if hashlib.sha256(pre[k]).digest() != hashlib.sha256(brk[k]).digest())
    out.append(f"  archived non-report files: pre={len(pk)} breaking={len(bk)} changed={len(changed)} added={len(added)} removed={len(removed)}")
    if added:
        out.append("  added: " + ", ".join(added[:15]))
    if removed:
        out.append("  removed: " + ", ".join(removed[:15]))
    budget = 90
    for k in changed[:12]:
        a = pre[k].decode("utf-8", "replace").splitlines()
        b = brk[k].decode("utf-8", "replace").splitlines()
        d = [l for l in difflib.unified_diff(a, b, "pre/" + k, "breaking/" + k, n=1, lineterm="")]
        out.append(f"  DIFF {k} ({len(d)} lines):")
        for l in d[2:2 + min(budget, 40)]:
            out.append("    " + l[:200])
        budget -= min(len(d), 40)
        if budget <= 0:
            out.append("    ... diff budget exhausted")
            break
    return out


def compact_json(path, limit=1500):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        return f"(unreadable: {e})"

    def scrub(x, depth=0):
        if isinstance(x, dict):
            return {k: scrub(v, depth + 1) for k, v in x.items() if k not in ("command", "sha256", "image_id", "image_digests", "class_sha256")
                    and not re.search(r"assess|label|classif|conclu|interpret|verdict|behavioral|rationale", k, re.I)}
        if isinstance(x, list):
            return [scrub(v, depth + 1) for v in x[:12]]
        if isinstance(x, str) and len(x) > 300:
            return x[:300] + "..."
        return x
    s = json.dumps(scrub(d), separators=(",", ":"))
    return s[:limit] + ("..." if len(s) > limit else "")


for n in range(FIRST, LAST + 1):
    c = cands[n - 1]
    cid = c["case_id"]
    L = []
    L.append(f"=== CASE {n} {cid}")
    L.append(f"  project={c['organisation']}/{c['project']} dep={c['dependency_group']}:{c['dependency_artifact']} {c['previous_version']} -> {c['new_version']} scope={c['dependency_scope']} type={c['version_update_type']} java={c['java_version']}")
    L.append(f"  PR={c['pull_request_url']}")
    pre_log, brk_log = logpaths.get(cid, (None, None))
    L.append(f"  PRE log {pre_log}:")
    L += summarize_log(read_log(pre_log) if pre_log else None, False)
    L.append(f"  BREAKING log {brk_log}:")
    L += summarize_log(read_log(brk_log) if brk_log else None, True)
    ev = P("logs", f"case{n}_evidence")
    if os.path.isdir(ev):
        files = []
        for dp, dn, fn in os.walk(ev):
            for f in fn:
                files.append(os.path.relpath(os.path.join(dp, f), ev).replace("\\", "/"))
        L.append(f"  EVIDENCE logs/case{n}_evidence: " + ", ".join(sorted(files))[:1500])
        for ph in ("pre", "breaking"):
            s = os.path.join(ev, ph, "archive_summary.json")
            if os.path.exists(s):
                d = json.load(open(s, encoding="utf-8"))
                tot = [0, 0, 0, 0]
                for r in d.get("reports", []):
                    cc = r.get("counts", {})
                    for i, k in enumerate(("tests", "failures", "errors", "skipped")):
                        tot[i] += int(cc.get(k, 0) or 0)
                L.append(f"  {ph} archive: exit={d.get('container_state', {}).get('ExitCode')} cmd={' '.join(d.get('command', []))[:160]} reports={d.get('report_count')} sum(t,f,e,s)={tot}")
        pre_t = os.path.join(ev, "pre", "artifacts.tar")
        brk_t = os.path.join(ev, "breaking", "artifacts.tar")
        if os.path.exists(pre_t) and os.path.exists(brk_t):
            pm, bm = tar_members(pre_t), tar_members(brk_t)
            L += source_diff(pm, bm)
            sf = surefire_failures(bm)
            if sf:
                L.append("  BREAKING surefire failures/errors:")
                L += sf
            spre = surefire_failures(pm, 3)
            if spre:
                L.append("  PRE surefire failures/errors:")
                L += spre
        cmp_ = os.path.join(ev, "all_poms_comparison.json")
        if os.path.exists(cmp_):
            d = json.load(open(cmp_, encoding="utf-8"))
            L.append(f"  all_poms: count={d.get('pom_count_per_phase')} changed={d.get('changed_poms')}")
            for k, v in list(d.get("diffs", {}).items())[:6]:
                dl = [x for x in v.splitlines() if x.startswith(("+", "-")) and not x.startswith(("+++", "---"))]
                L.append(f"    {k}: " + " / ".join(x.strip() for x in dl[:16])[:900])
        for f in sorted(files):
            if f.endswith(".json") and not f.endswith(("archive_summary.json", "sha256_manifest.json", "all_poms_sha256.json", "all_poms_comparison.json")):
                L.append(f"  JSON {f}: " + compact_json(os.path.join(ev, f), 1400))
            elif f.endswith(".log") or f.endswith(".txt") and "javap" not in f:
                try:
                    txt = open(os.path.join(ev, f), encoding="utf-8", errors="replace").read().splitlines()
                    key = [x for x in txt if re.search(r"Exception|Error|PROBE|RESULT|selected|Tests run|BUILD|=", x)][:10]
                    L.append(f"  LOG {f} ({len(txt)} lines): " + " | ".join(ANSI.sub("", x).strip()[:200] for x in key))
                except Exception:
                    pass
            elif f.endswith("jars/") or "/jars/" in f:
                pass
        jars = sorted(f for f in files if "/jars/" in f)
        if jars:
            L.append("  JARS: " + ", ".join(jars))
    else:
        L.append(f"  EVIDENCE: no logs/case{n}_evidence directory")
    with open(os.path.join(OUT, f"case{n:03d}.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print(n, len(L))
open(os.path.join(OUT, "_utf16_logs.txt"), "w", encoding="utf-8").write("\n".join(sorted(set(ENCODING_NOTES))) + "\n")
