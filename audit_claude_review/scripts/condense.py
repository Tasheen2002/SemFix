"""Print condensed views of blind digests. Usage: python -I condense.py <digest_dir> <first> <last> [maxchars]"""
import os, re, sys

d, a, b = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
MAX = int(sys.argv[4]) if len(sys.argv) > 4 else 2300
for n in range(a, b + 1):
    lines = open(os.path.join(d, f"case{n:03d}.txt"), encoding="utf-8").read().splitlines()
    out, phase, diffbudget, sfb = [], "", 0, 0
    for l in lines:
        s = l.strip()
        if s.startswith("=== CASE") or s.startswith("project="):
            out.append(s if s.startswith("===") else s.replace("project=", ""))
        elif s.startswith("PRE log"):
            phase = "PRE"
        elif s.startswith("BREAKING log"):
            phase = "BRK"
        elif s.startswith("status:"):
            out.append(f"{phase} {s[:120]}")
        elif s.startswith("aggregate summaries:"):
            out.append(f"{phase} agg: {s[21:][:300]}")
        elif s.startswith("reactor:"):
            out.append(f"{phase} {s[:400]}")
        elif phase == "BRK" and s.startswith("distinct fail signatures"):
            out.append("BRK sigs: " + s[33:][:700])
        elif phase == "BRK" and s.startswith("Caused by:") and sum(1 for o in out if o.startswith(" CB")) < 3:
            out.append(" CB " + s[:220])
        elif s.startswith("linkage/compile signals:"):
            out.append(f"{phase} link: {s[25:][:200]}")
        elif phase == "BRK" and s.startswith("provider/console lines:"):
            out.append("BRK console: " + s[24:][:420])
        elif phase == "PRE" and s.startswith("provider/console lines:") and "SLF4J" in s:
            out.append("PRE console: " + s[24:][:250])
        elif phase == "BRK" and s.startswith("[ERROR]") and ("COMPILATION" in s or "cannot find symbol" in s or "Failed to execute goal" in s or ".java:[" in s):
            if sum(1 for o in out if o.startswith(" ERR")) < 4:
                out.append(" ERR " + s[:260])
        elif s.startswith("EVIDENCE"):
            out.append(s[:260])
        elif re.match(r"(pre|breaking) archive:", s):
            out.append(s[:220])
        elif s.startswith("archived non-report files"):
            out.append(s)
        elif s.startswith("DIFF "):
            out.append(s)
            diffbudget = 10
        elif diffbudget > 0 and (s.startswith("+") or s.startswith("-")) and not s.startswith(("+++", "---")):
            out.append("   " + s[:160])
            diffbudget -= 1
        elif s.startswith("BREAKING surefire"):
            sfb = 2
        elif sfb > 0 and (s.startswith("FAILURE") or s.startswith("ERROR")):
            out.append(" SF " + s[:330])
            sfb -= 1
        elif s.startswith("all_poms:"):
            out.append(s[:300])
        elif (s.startswith("JSON ") or s.startswith("LOG ")) and "/src/" not in s.split(":")[0] and "surefire-reports/" not in s.split(":")[0]:
            out.append(s[:520])
        elif s.startswith("JARS:"):
            out.append(s[:400])
    txt = "\n".join(out)
    if len(txt) > MAX:
        txt = txt[:MAX] + " ...[cut]"
    print(txt)
    print()
