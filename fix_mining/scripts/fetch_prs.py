"""Fetch refs/pull/<n>/head for each BEHAVIORAL case into fix_mining/repos/<org>_<proj> and write fix_mining/cases.json."""
import csv, json, os, re, subprocess, sys
ROOT = sys.argv[1]
R = lambda *a: os.path.join(ROOT, *a)
fin = [r for r in csv.DictReader(open(R("results", "final_classification_rule_based.csv"), encoding="utf-8")) if r["rule_based_label"] == "BEHAVIORAL"]
cases = []
for r in fin:
    d = json.load(open(R("bump", "data", "benchmark", r["case_id"] + ".json"), encoding="utf-8"))
    u = d["updatedDependency"]; pr = int(re.search(r"/pull/(\d+)", d["url"]).group(1))
    repo = R("fix_mining", "repos", f"{d['projectOrganisation']}_{d['project']}")
    git = lambda *a: subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, encoding="utf-8", errors="replace")
    git("fetch", "-q", "origin", f"+refs/pull/{pr}/head:refs/bump/pr-{pr}")
    head = git("rev-parse", "-q", "--verify", f"refs/bump/pr-{pr}").stdout.strip()
    has_b = git("cat-file", "-e", d["breakingCommit"] + "^{commit}").returncode == 0
    if not has_b: git("fetch", "-q", "origin", d["breakingCommit"]); has_b = git("cat-file", "-e", d["breakingCommit"] + "^{commit}").returncode == 0
    cases.append(dict(case=int(r["case_number"]), id=r["case_id"], repo=os.path.basename(repo), slug=f"{d['projectOrganisation']}/{d['project']}",
                      pr=pr, url=d["url"], group=u["dependencyGroupID"], artifact=u["dependencyArtifactID"], old=u["previousVersion"], new=u["newVersion"],
                      pr_head=head, breaking_present=has_b, related_group=r["related_group"], duplicate_of=r["possible_duplicate_of"], behavior_category=r["behavior_change_category"]))
    print(r["case_number"], cases[-1]["slug"], pr, "head" if head else "NO-PR-REF", "breaking" if has_b else "NO-BREAKING", "head==breaking" if head == d["breakingCommit"] else "")
cases.sort(key=lambda c: c["case"])
json.dump(cases, open(R("fix_mining", "cases.json"), "w", encoding="utf-8"), indent=1)
