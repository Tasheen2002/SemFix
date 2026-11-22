"""Read-only GitHub REST lookup of each BEHAVIORAL case's PR (state, merged, base branch, dates).
Unauthenticated (60 requests/hour); resumable: cases already in fix_mining/pr_meta.json are skipped.
Usage: python -I fetch_pr_meta.py <research root>
"""
import json, os, sys, time, urllib.request, urllib.error
ROOT = sys.argv[1]
F = lambda *a: os.path.join(ROOT, "fix_mining", *a)
cases = json.load(open(F("cases.json"), encoding="utf-8"))
path = F("pr_meta.json")
meta = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
for c in cases:
    k = str(c["case"])
    if k in meta:
        continue
    req = urllib.request.Request(f"https://api.github.com/repos/{c['slug']}/pulls/{c['pr']}",
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "research-fix-mining"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r); left = r.headers.get("X-RateLimit-Remaining")
    except urllib.error.HTTPError as e:
        print("stop:", c["case"], e.code, e.headers.get("X-RateLimit-Reset")); break
    meta[k] = dict(state=d["state"], merged=d.get("merged"), merged_at=d.get("merged_at"), closed_at=d.get("closed_at"),
                   created_at=d["created_at"], base=d["base"]["ref"], head=d["head"]["ref"], user=d["user"]["login"],
                   comments=d.get("comments"), commits=d.get("commits"), title=d["title"])
    json.dump(meta, open(path, "w", encoding="utf-8"), indent=1)
    print(k, meta[k]["state"], "merged" if meta[k]["merged"] else "", meta[k]["base"], "left", left)
    if left == "0":
        break
print(len(meta), "of", len(cases))
