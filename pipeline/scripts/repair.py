"""Automated repair pipeline: breakage -> retrieval (RAG) -> prompt -> LLM -> patch -> harness -> feedback -> retry.

Per case:
  1. read the BREAKING log (symptoms only) and the update (dependency, old/new version)
  2. collect code context from the project at the breaking commit
  3. retrieve similar past cases from the KB (condition `rag`), leakage-safe at --level (default L2); none for `no_rag`
  4. up to --attempts times: build prompt (+ feedback from the previous attempt), ask the LLM, extract the diff,
     evaluate it with harness/scripts/evaluate_patch.py; stop at REPAIRED
  5. record everything in pipeline/runs/<label>/case<N>.json (retrieved ids, prompt sizes, model, patches, verdicts)

Providers: manual (no key: prompts to files, answers read from files), claude (Anthropic SDK), oracle (pipeline test
only: returns the frozen fix). --dry-run builds and saves the prompts only (no LLM, no Docker).
Usage:
  python -I repair.py <root> --cases 13,28 --condition rag --provider manual --label trial1 [--dry-run]
  python -I repair.py <root> --cases all --condition no_rag --provider claude --model claude-opus-5-5 --label expA
"""
import argparse, csv, datetime, json, os, re, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("root"); ap.add_argument("--cases", required=True); ap.add_argument("--label", required=True)
ap.add_argument("--condition", choices=["rag", "no_rag"], default="rag"); ap.add_argument("--level", default="L2", choices=["L1", "L2", "L3"])
ap.add_argument("--k", type=int, default=3); ap.add_argument("--no-researcher-written", action="store_true")
ap.add_argument("--provider", choices=["manual", "claude", "oracle", "oracle_retry"], default="manual")
ap.add_argument("--model"); ap.add_argument("--effort", default="high"); ap.add_argument("--attempts", type=int, default=3)
ap.add_argument("--context-budget", type=int, default=60000); ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()
ROOT = a.root
P = lambda *x: os.path.join(ROOT, *x)
sys.path.insert(0, P("pipeline", "scripts")); sys.path.insert(0, P("kb", "scripts"))
from context import Repo, breakage_from_log, code_context, read_log
from prompt import build_prompt
import retrieve

cases = {c["case"]: c for c in json.load(open(P("fix_mining", "cases.json"), encoding="utf-8"))}
cls = {r["case_id"]: r for r in csv.DictReader(open(P("results", "classification_v1.0", "behavioral_classification.csv"), encoding="utf-8"))}
index = {int(r["case_number"]): r for r in csv.DictReader(open(P("fix_mining", "fixes_v1.0", "fix_index.csv"), encoding="utf-8"))}
KB = retrieve.load(ROOT); IX = retrieve.Index(KB); KBN = {e["case_number"]: e for e in KB}
todo = sorted(cases) if a.cases == "all" else [int(x) for x in a.cases.split(",")]
run_dir = P("pipeline", "runs", a.label); os.makedirs(os.path.join(run_dir, "patches"), exist_ok=True)

DIFF = re.compile(r"```diff\s*\n(.*?)```", re.S)


def extract_patch(text):
    if not text:
        return None
    blocks = DIFF.findall(text)
    if not blocks:
        return None
    p = blocks[-1]
    p = re.sub(r"^(?!diff --git)(---|\+\+\+) (?!a/|b/|/dev/null)(\S+)", lambda m: f"{m.group(1)} {'a' if m.group(1) == '---' else 'b'}/{m.group(2)}", p, flags=re.M)
    return p if p.endswith("\n") else p + "\n"


def error_excerpt(log_path, limit=60):
    lines = read_log(log_path)
    keep = []
    for i, l in enumerate(lines):
        if re.search(r"<<< (FAILURE|ERROR)!|COMPILATION ERROR|\[ERROR\] /|error: (patch failed|corrupt patch|while searching)|APPLY_FAILED", l):
            keep += lines[i:i + 6]
        if len(keep) > limit:
            break
    return "\n".join(keep[:limit])


def provider_for(n):
    if a.provider == "manual":
        from llm_manual import ManualProvider
        return ManualProvider(run_dir)
    if a.provider in ("oracle", "oracle_retry"):
        from llm_manual import OracleProvider, OracleRetryProvider
        cls_ = OracleProvider if a.provider == "oracle" else OracleRetryProvider
        return cls_(open(P("fix_mining", "fixes_v1.0", index[n]["patch"]), encoding="utf-8").read())
    from llm_claude import ClaudeProvider, DEFAULT_MODEL
    return ClaudeProvider(model=a.model or DEFAULT_MODEL, effort=a.effort)


for n in todo:
    c = cases[n]; kbe = KBN[n]
    out_json = os.path.join(run_dir, f"case{n}.json")
    if os.path.exists(out_json) and not a.dry_run:
        prev = json.load(open(out_json, encoding="utf-8"))
        if prev.get("final_verdict") not in (None, "AWAITING_MANUAL_RESPONSE"):
            print(f"case {n}: done ({prev['final_verdict']}), skipping"); continue
    log_path = P(cls[c["id"]]["breaking_log"])
    prefixes = tuple(sorted({".".join(t.split(".")[:3]) + "." for t in kbe["breakage"]["failing_test_classes"] if t.count(".") >= 3}))
    breakage = breakage_from_log(log_path, f"{c['group']}:{c['artifact']}", c["old"], c["new"], prefixes)
    repo = Repo(P("fix_mining", "repos", c["repo"]), c["id"])
    ctx = code_context(repo, breakage, a.context_budget); repo.close()
    examples, retrieved = [], []
    if a.condition == "rag":
        q = dict(case_number=n, breakage=dict(kbe["breakage"], **{k: breakage[k] for k in ("failing_test_classes", "exception_types", "error_lines", "slf4j_console")}),
                 leakage=kbe["leakage"])
        retrieved = IX.retrieve(q, a.level, a.k, "hybrid", not a.no_researcher_written)
        examples = [KBN[r["case_number"]] for r in retrieved]
    rec = dict(case=n, label=a.label, condition=a.condition, level=a.level, k=a.k, include_researcher_written=not a.no_researcher_written,
               provider=a.provider, model=a.model, effort=a.effort, date=datetime.date.today().isoformat(),
               retrieved=[dict(case=r["case_number"], mechanism=r["mechanism"], fix_author=r["fix_author"], score=r["score"]) for r in retrieved],
               context_files=[dict(path=p, kind=k, chars=len(t)) for p, k, t in ctx], breakage=breakage, attempts=[])
    prov = provider_for(n); feedback = None; final = None
    for k in range(1, a.attempts + 1):
        system, user = build_prompt(breakage, ctx, examples, feedback)
        tag = f"case{n}_attempt{k}"
        if a.dry_run:
            os.makedirs(os.path.join(run_dir, "prompts"), exist_ok=True)
            open(os.path.join(run_dir, "prompts", tag + ".md"), "w", encoding="utf-8").write(f"<!-- SYSTEM -->\n{system}\n\n<!-- USER -->\n{user}\n")
            rec["attempts"].append(dict(attempt=k, prompt_chars=len(system) + len(user))); final = "DRY_RUN"; break
        prov.tag = tag
        os.makedirs(os.path.join(run_dir, "prompts"), exist_ok=True)
        open(os.path.join(run_dir, "prompts", tag + ".md"), "w", encoding="utf-8").write(f"<!-- SYSTEM -->\n{system}\n\n<!-- USER -->\n{user}\n")
        resp = prov.complete(system, user)
        att = dict(attempt=k, prompt_chars=len(system) + len(user), llm={x: v for x, v in resp.items() if x != "text"})
        if resp.get("stop_reason") == "awaiting_manual_response":
            att["status"] = f"waiting for {resp['awaiting']}"; rec["attempts"].append(att); final = "AWAITING_MANUAL_RESPONSE"; break
        open(os.path.join(run_dir, f"{tag}_response.md"), "w", encoding="utf-8").write(resp["text"] or "")
        patch = extract_patch(resp["text"])
        if patch is None:
            att["verdict"] = "NO_PATCH_IN_RESPONSE"; rec["attempts"].append(att)
            feedback = dict(failed_checks=["APPLIES"], build=dict(status="NONE", tests=0, failures=0, errors=0),
                            apply_error="your answer contained no ```diff block")
            continue
        pf = os.path.join(run_dir, "patches", f"{tag}.patch")
        open(pf, "w", encoding="utf-8", newline="\n").write(patch)
        hl = f"{a.label}__attempt{k}"
        subprocess.run([sys.executable, "-I", P("harness", "scripts", "evaluate_patch.py"), ROOT, "--case", str(n), "--patch", pf, "--label", hl])
        hres = json.load(open(P("harness", "runs", hl, f"case{n}.json"), encoding="utf-8"))
        att.update(verdict=hres["verdict"], failed_checks=hres["failed_checks"], patch=os.path.relpath(pf, ROOT),
                   harness_result=f"harness/runs/{hl}/case{n}.json", flaky=hres.get("flaky", False))
        rec["attempts"].append(att)
        if hres["verdict"] == "REPAIRED":
            final = "REPAIRED"; break
        if hres["verdict"] == "INCONCLUSIVE":
            final = "INCONCLUSIVE"; break          # infrastructure problem: do not spend LLM attempts on it
        feedback = dict(hres, error_excerpt=error_excerpt(P(hres["log"])),
                        apply_error=None if hres["checks"]["APPLIES"] is True else error_excerpt(P(hres["log"])))
    rec["final_verdict"] = final or "NOT_REPAIRED"
    rec["attempts_used"] = len(rec["attempts"])
    json.dump(rec, open(out_json, "w", encoding="utf-8"), indent=1)
    print(f"case {n} [{a.label}/{a.condition}/{a.provider}] {rec['final_verdict']}  attempts={rec['attempts_used']}  "
          f"retrieved={[r['case'] for r in rec['retrieved']]}  context={len(ctx)} files / {sum(len(t) for _, _, t in ctx)} chars", flush=True)
