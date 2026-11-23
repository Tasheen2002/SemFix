"""Breakage reader and code-context collector for the repair pipeline.

breakage_from_log(): reads a RAW BREAKING build log (as a new breakage arrives) and extracts failing test classes,
  exception types, error lines, project stack frames and SLF4J console lines. The dependency and versions come
  from the update itself (the bot PR), which is known for any new breakage.
code_context(): the source files the LLM needs, read from the project at the breaking commit:
  the failing test classes, project classes in the failing stack traces, and the POM(s) that declare the updated
  dependency (+ the root POM). Large files are cut to windows around the relevant lines. A size budget is enforced.
The project source is read from fix_mining/repos/<repo> at the breaking commit (identical to the BREAKING image).
"""
import json, os, re, subprocess

EXC = re.compile(r"\b((?:[a-z_][\w$]*\.)+[A-Z][\w$]*(?:Exception|Error|Failure))\b")
FRAME = re.compile(r"^\s*at ((?:[a-z_][\w$]*\.)+)([A-Z][\w$]*)(?:\$[\w$]+)?\.[\w$<>]+\(([\w$]+\.java):(\d+)\)")
FAILHDR = re.compile(r"Tests run: \d+, Failures: \d+, Errors: \d+.*?<<< (?:FAILURE|ERROR)!? *-? *(?:in )?([\w.$]+)")


def read_log(p):
    raw = open(p, "rb").read()
    t = raw.decode("utf-16", "replace") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8", "replace")
    return [re.sub(r"\x1b\[[0-9;]*m", "", l) for l in t.splitlines()]


def breakage_from_log(log_path, dependency, old_version, new_version, project_prefixes=()):
    lines = read_log(log_path)
    failing, exc, errs, frames, slf4j = [], [], [], [], []
    for i, l in enumerate(lines):
        m = FAILHDR.search(l)
        if m and m.group(1) not in failing:
            failing.append(m.group(1))
        if re.search(r"<<< (FAILURE|ERROR)!", l) and "Tests run" not in l:
            block = lines[i:i + 40]
            for b in block[1:4]:
                e = EXC.search(b)
                if e:
                    exc.append(e.group(1))
                    if b.strip()[:300] not in errs:
                        errs.append(b.strip()[:300])
                    break
            for b in block:
                f = FRAME.match(b)
                if f and (not project_prefixes or f.group(1).startswith(project_prefixes)):
                    frames.append(dict(cls=f.group(1) + f.group(2), file=f.group(3), line=int(f.group(4))))
        if l.strip().startswith("Caused by:"):
            e = EXC.search(l)
            if e:
                exc.append(e.group(1))
                if l.strip()[:300] not in errs:
                    errs.append(l.strip()[:300])
        if l.startswith("SLF4J:") and l not in slf4j:
            slf4j.append(l)
    seen, uframes = set(), []
    for f in frames:
        k = (f["cls"], f["line"])
        if k not in seen:
            seen.add(k); uframes.append(f)
    g, a = dependency.split(":")
    return dict(dependency=dependency, group_id=g, artifact_id=a, old_version=old_version, new_version=new_version,
                failing_test_classes=[c for c in failing if c != "TestSuite"] or failing,
                exception_types=list(dict.fromkeys(exc))[:8], error_lines=errs[:8], project_frames=uframes[:25], slf4j_console=slf4j[:6])


class Repo:
    """Read-only view of a repository at one revision. File contents come from one persistent
    `git cat-file --batch` process (one git process per file is very slow on Windows), cached."""
    def __init__(self, path, rev):
        self.path, self.rev = path, rev
        self.files = subprocess.run(["git", "-C", path, "ls-tree", "-r", "--name-only", rev], capture_output=True, text=True).stdout.splitlines()
        self._proc, self._cache = None, {}

    def show(self, f):
        if f in self._cache:
            return self._cache[f]
        if self._proc is None:
            self._proc = subprocess.Popen(["git", "-C", self.path, "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self._proc.stdin.write(f"{self.rev}:{f}\n".encode("utf-8")); self._proc.stdin.flush()
        hdr = self._proc.stdout.readline().decode("utf-8", "replace").split()
        if len(hdr) < 3 or hdr[1] != "blob":
            if len(hdr) >= 3:                      # a tree or other object: consume its bytes
                self._proc.stdout.read(int(hdr[2])); self._proc.stdout.read(1)
            self._cache[f] = None
            return None
        data = self._proc.stdout.read(int(hdr[2])); self._proc.stdout.read(1)
        self._cache[f] = data.decode("utf-8", "replace")
        return self._cache[f]

    def close(self):
        if self._proc:
            self._proc.stdin.close(); self._proc.wait(); self._proc = None

    def find_class(self, fqcn):
        tail = fqcn.replace(".", "/").split("$")[0] + ".java"
        hits = [f for f in self.files if f.endswith("/" + tail) or f == tail]
        if not hits:   # simple name (surefire sometimes prints only the class name)
            simple = "/" + fqcn.split(".")[-1].split("$")[0] + ".java"
            hits = [f for f in self.files if f.endswith(simple)]
        return sorted(hits, key=len)[:1]


def window(text, lines_of_interest, radius=40, max_lines=400):
    L = text.splitlines()
    if len(L) <= max_lines or not lines_of_interest:
        return "\n".join(L[:max_lines]) + ("" if len(L) <= max_lines else f"\n... ({len(L) - max_lines} more lines omitted)")
    keep = set()
    for n in lines_of_interest:
        keep.update(range(max(0, n - 1 - radius), min(len(L), n + radius)))
    keep.update(range(0, min(40, len(L))))            # package + imports
    out, last = [], -2
    for i in sorted(keep):
        if i != last + 1:
            out.append(f"... (lines {last + 2}-{i} omitted)")
        out.append(L[i]); last = i
    return "\n".join(out)


GENERIC = {"java", "javax", "jdk", "sun", "org", "com", "net", "io", "ch", "de", "uk", "fr", "nl", "lang", "util", "impl",
           "internal", "core", "classic", "helpers", "api", "spi", "common", "commons", "base", "main", "test", "tests",
           "apache", "google", "github", "jvm", "reflect", "exc", "exception", "databind", "junit", "jupiter", "hamcrest",
           "mockito", "assertj", "matchers", "static", "annotation", "function", "stream", "time", "nio"}
RESOURCE_EXT = (".yml", ".yaml", ".properties", ".xml", ".json", ".nq", ".nt", ".ttl", ".txt", ".conf", ".html", ".csv", ".sql")


def _pkg_words(text):
    """Package segments of fully qualified names in text: 'ch.qos.logback.classic.Logger' -> {'logback'}."""
    out = set()
    for pkg in re.findall(r"\b((?:[a-z][\w]*\.)+)[A-Z]", text):
        out.update(p for p in pkg.strip(".").split(".") if len(p) > 3 and p not in GENERIC)
    return out


def code_context(repo, breakage, budget_chars=60000):
    """[(path, kind, text)] within budget, in priority order:
    1. POM(s) declaring the updated dependency (+ root POM); large POMs are windowed around the dependency, the
       libraries named in the error and the third-party libraries the failing tests import, plus <properties>
    2. the failing test classes (windowed around failing lines when large)
    3. resource files (config, expected outputs) that contain an identifier from the error message or whose name
       the failing tests mention
    4. project classes in the failing stack traces
    """
    items, used = [], 0

    def add(path, kind, text):
        nonlocal used
        if text is None or any(p == path for p, _, _ in items):
            return
        if used + len(text) > budget_chars:
            text = text[:max(0, budget_chars - used)] + "\n... (truncated: context budget reached)"
        if text.strip():
            items.append((path, kind, text)); used += len(text)

    frames_by_file = {}
    for fr in breakage["project_frames"]:
        for f in repo.find_class(fr["cls"]):
            frames_by_file.setdefault(f, []).append(fr["line"])
    test_files = [f for t in breakage["failing_test_classes"] for f in repo.find_class(t)]
    test_src = {f: (repo.show(f) or "") for f in test_files}
    imports = " ".join(l for s in test_src.values() for l in s.splitlines() if l.startswith("import "))
    errors = " ".join(breakage["error_lines"] + breakage["slf4j_console"])

    # 1. build files
    art = breakage["artifact_id"]
    poms = [f for f in repo.files if f == "pom.xml" or f.endswith("/pom.xml")]
    declaring = [f for f in poms if art in (repo.show(f) or "")]
    words = {w for w in {art, breakage["group_id"]} | _pkg_words(errors) | _pkg_words(imports.replace("import ", "").replace(";", ".X"))
             if len(w) > 3}
    for f in (["pom.xml"] if "pom.xml" in poms else []) + declaring:
        text = repo.show(f) or ""
        if len(text) > 20000:
            L = text.splitlines()
            hits = [i + 1 for i, l in enumerate(L) if any(w in l for w in words)]
            props = [i + 1 for i, l in enumerate(L) if "<properties>" in l]
            text = window(text, hits + props, radius=12, max_lines=0) if hits else text[:20000]
        add(f, "build file (declares the updated dependency)" if f in declaring else "root build file", text)

    # 2. failing tests
    for f in test_files:
        add(f, "failing test", window(test_src[f], frames_by_file.get(f, [])))

    # 3. resources: identifiers from the error message, or names the failing tests mention
    idents = {t for t in re.findall(r"[A-Za-z_][\w]{7,}", errors) if re.search(r"[a-z][A-Z]|_", t)}
    resources = [f for f in repo.files if "/resources/" in "/" + f and f.endswith(RESOURCE_EXT) and "/target/" not in "/" + f]
    picked = []
    for f in resources:
        stem = f.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        by_name = len(stem) >= 5 and any(stem in s for s in test_src.values())
        if not by_name and not idents:
            continue
        text = repo.show(f)
        if text is None or len(text) > 30000:
            continue
        if by_name or any(t in text for t in idents):
            picked.append((0 if any(t in text for t in idents) else 1, f, text, by_name))
    for _, f, text, by_name in sorted(picked)[:6]:
        add(f, "resource file " + ("named in the failing test" if by_name else "containing an identifier from the error"), text)

    # 4. stack-trace classes
    for f, ls in frames_by_file.items():
        add(f, "class in the failing stack trace", window(repo.show(f) or "", ls))
    return items
