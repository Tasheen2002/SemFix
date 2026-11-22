"""Trace each BEHAVIORAL case's dependency on the project's default branch after the breaking commit.

Per case:
- start from the merge-base of the default branch and the breaking commit;
- read the dependency's version in every pom.xml there (effective version = highest explicit one);
- walk the first-parent commits on the default branch that touch a pom.xml (one `git log --raw` call)
  and update the changed POMs (read through one persistent `git cat-file --batch` per repository);
- record each change of the effective version and the first commit where it is >= newVersion (landing commit);
- for the landing commit, record the files changed (by kind) and the other dependency changes in its POMs.
Output: fix_mining/version_trace.json (or version_trace_partial.json when case numbers are given).
Read-only: git object reads only, no checkout, no build.
Usage: python -I trace_versions.py <research root> [comma-separated case numbers]
"""
import json, os, re, subprocess, sys

ROOT = sys.argv[1]
F = lambda *a: os.path.join(ROOT, "fix_mining", *a)


def git(repo, *a):
    return subprocess.run(["git", "-C", F("repos", repo), *a], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


class Blobs:
    """One persistent `git cat-file --batch` per repository, with a cache."""
    def __init__(self, repo):
        self.p = subprocess.Popen(["git", "-C", F("repos", repo), "cat-file", "--batch"],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.cache = {}

    def read(self, spec):
        if spec in self.cache:
            return self.cache[spec]
        self.p.stdin.write((spec + "\n").encode()); self.p.stdin.flush()
        hdr = self.p.stdout.readline().decode().split()
        if len(hdr) < 3:
            self.cache[spec] = None
            return None
        data = self.p.stdout.read(int(hdr[2])); self.p.stdout.read(1)
        self.cache[spec] = data.decode("utf-8", "replace") if hdr[1] == "blob" else None
        return self.cache[spec]


BLOBS = {}


def show(repo, rev, path):
    if repo not in BLOBS:
        BLOBS[repo] = Blobs(repo)
    return BLOBS[repo].read(f"{rev}:{path}")


def vkey(v):
    """Comparable key: numeric parts compare numerically; a qualifier-only part sorts below numbers."""
    out = []
    for p in re.split(r"[.\-_]", v or ""):
        m = re.match(r"(\d+)(.*)", p)
        out.append((1, int(m.group(1)), m.group(2).lower()) if m else (0, 0, p.lower()))
    return out


def ge(a, b):
    return vkey(a) >= vkey(b)


PROP = re.compile(r"\$\{([^}]+)\}")
BAD = (None, "ABSENT", "MANAGED")


def parse_pom(pom):
    """{group:artifact: version} for every dependency/plugin block, properties resolved within the file."""
    out = {}
    if pom is None:
        return out
    pom = re.sub(r"<!--.*?-->", "", pom, flags=re.S)
    pm = re.search(r"<properties>(.*?)</properties>", pom, re.S)
    props = dict(re.findall(r"<([\w.\-]+)>\s*([^<]*?)\s*</\1>", pm.group(1))) if pm else {}
    for blk in re.findall(r"<(?:dependency|plugin)>(.*?)</(?:dependency|plugin)>", pom, re.S):
        a = re.search(r"<artifactId>\s*(.*?)\s*</artifactId>", blk)
        g = re.search(r"<groupId>\s*(.*?)\s*</groupId>", blk)
        if not a:
            continue
        v = re.search(r"<version>\s*(.*?)\s*</version>", blk)
        v = v.group(1) if v else "MANAGED"
        for _ in range(3):
            m = PROP.search(v)
            if not m or m.group(1) not in props:
                break
            v = v.replace(m.group(0), props[m.group(1)])
        k = f"{g.group(1) if g else '?'}:{a.group(1)}"
        if k not in out or out[k] == "MANAGED":
            out[k] = v
    return out


def dep_version(pom, group, artifact):
    return parse_pom(pom).get(f"{group}:{artifact}", "ABSENT")


def effective(state):
    vs = [v for v in state.values() if v not in BAD and "${" not in v]
    if vs:
        return max(vs, key=vkey)
    return "MANAGED" if "MANAGED" in state.values() else "ABSENT"


def classify_path(p):
    q = "/" + p
    if is_pom(p):
        return "pom"
    if "/src/test/" in q:
        return "test"
    if "/src/main/" in q:
        return "main"
    if p.startswith(".github/") or p.endswith((".yml", ".yaml")):
        return "ci"
    return "other"


def is_pom(p):
    return p == "pom.xml" or p.endswith("/pom.xml")


def pom_changes(repo, default, base):
    """[(commit, date, author, subject, {pom_path: new blob oid or None if deleted})], first-parent, oldest first."""
    out, cur = [], None
    raw = git(repo, "log", "--first-parent", "--reverse", "--no-renames", "--raw", "--no-abbrev",
              "--format=@@%H%x09%cI%x09%an%x09%s", default, "^" + base, "--", "pom.xml", "*/pom.xml")
    for l in raw.splitlines():
        if l.startswith("@@"):
            h, d, a, s = (l[2:].split("\t") + ["", "", ""])[:4]
            cur = [h, d, a, s, {}]; out.append(cur)
        elif l.startswith(":") and cur is not None:
            meta, path = l.split("\t", 1)
            if is_pom(path):
                f = meta.split()
                cur[4][path] = None if f[4].startswith("D") else f[3]
    return out


cases = json.load(open(F("cases.json"), encoding="utf-8"))
only = set(map(int, sys.argv[2].split(","))) if len(sys.argv) > 2 else None
out = []
for c in cases:
    if only and c["case"] not in only:
        continue
    repo, b, key = c["repo"], c["id"], f"{c['group']}:{c['artifact']}"
    show(repo, "HEAD", "pom.xml")  # start the reader
    default = git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD").strip() or "origin/HEAD"
    pom_path = [l for l in git(repo, "show", "--format=", "--name-only", b).splitlines() if is_pom(l)][0]
    merged = subprocess.run(["git", "-C", F("repos", repo), "merge-base", "--is-ancestor", b, default]).returncode == 0
    base = git(repo, "merge-base", default, b).strip()
    poms = {p: dep_version(show(repo, base, p), c["group"], c["artifact"])
            for p in git(repo, "ls-tree", "-r", "--name-only", base).splitlines() if is_pom(p)}
    base_version = effective(poms)
    revs = pom_changes(repo, default, base)
    trace, landing = [], None
    prev = base_version
    for h, date, author, subj, changed in revs:
        for p, oid in changed.items():
            poms[p] = dep_version(BLOBS[repo].read(oid) if oid else None, c["group"], c["artifact"])
        v = effective(poms)
        if v != prev:
            trace.append(dict(commit=h, date=date, author=author, subject=subj[:120], version=v))
            prev = v
        if v not in BAD and ge(v, c["new"]):
            landing = dict(commit=h, date=date, author=author, subject=subj[:200], version=v)
            break
    rec = dict(case=c["case"], slug=c["slug"], artifact=key, old=c["old"], new=c["new"], pom_path=pom_path,
               default_branch=default, merge_base=base, breaking_merged_into_default=merged,
               pom_commits_scanned=len(revs), base_version=base_version, version_changes=trace)
    if landing:
        h = landing["commit"]
        parents = git(repo, "rev-list", "--parents", "-n1", h).split()[1:]
        files = [l for l in git(repo, "diff", "--name-only", parents[0], h).splitlines() if l]
        d0, d1 = {}, {}
        for p in [f for f in files if is_pom(f)]:
            d0.update(parse_pom(show(repo, parents[0], p)))
            d1.update(parse_pom(show(repo, h, p)))
        other = {k: [d0.get(k), d1.get(k)] for k in sorted(set(d0) | set(d1)) if d0.get(k) != d1.get(k) and k != key}
        landing.update(is_merge=len(parents) > 1, files=files, file_kinds=sorted({classify_path(f) for f in files}),
                       other_dependency_changes_in_pom=other)
    rec["landing"] = landing
    head_poms = [p for p in git(repo, "ls-tree", "-r", "--name-only", default).splitlines() if is_pom(p)]
    rec["head_version"] = effective({p: dep_version(show(repo, default, p), c["group"], c["artifact"]) for p in head_poms})
    rec["head_date"] = git(repo, "log", "-1", "--format=%cI", default).strip()
    out.append(rec)
    L = landing or {}
    print(c["case"], c["slug"], f"{c['old']}->{c['new']}", "| merged" if merged else "| not-merged",
          f"| base {base_version} | scanned {len(revs)}",
          "| landing", (L["commit"][:10], L["date"][:10], L["version"], L["file_kinds"], len(L["other_dependency_changes_in_pom"])) if L else "NONE",
          "| HEAD", rec["head_version"], rec["head_date"][:10], flush=True)

dst = F("version_trace_partial.json") if only else F("version_trace.json")
json.dump(out, open(dst, "w", encoding="utf-8"), indent=1)
for b in BLOBS.values():
    b.p.stdin.close()
