"""Compare recorded counts in behavioral_classification.csv with Maven/randomized-runner summaries in the original logs."""
import csv, re, sys, os, json
ROOT = sys.argv[1]
P = lambda *a: os.path.join(ROOT, *a)
cands = list(csv.DictReader(open(P('results','test_failure_candidates.csv'), encoding='utf-8')))
cx = {r['case_id']: r for r in csv.DictReader(open(P('results','behavioral_classification.csv'), encoding='utf-8'))}
def lines(path):
    raw = open(P(path), 'rb').read()
    t = raw.decode('utf-16', 'replace') if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else raw.decode('utf-8', 'replace')
    return [re.sub(r'\x1b\[[0-9;]*m', '', l) for l in t.splitlines()]
AGG = re.compile(r'Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)\s*$')
RND = re.compile(r'Tests summary: (\d+) suites?(?: \(\d+ ignored\))?, (\d+) tests?(?:, (\d+) failures?)?(?:, (\d+) errors?)?(?:, (\d+) ignored)?')
RND2 = re.compile(r'There were test failures: \d+ suites?, (\d+) tests?, (?:(\d+) errors?, )?(\d+) failures?(?:, (\d+) ignored)?')
def totals(path):
    L = lines(path)
    agg = []; prev = None
    for i, l in enumerate(L):
        m = AGG.search(l)
        if m and 'Time elapsed' not in l:
            v = tuple(map(int, m.groups()))
            # skip identical consecutive duplicate (same module printed twice)
            if prev is not None and v == prev[1] and i - prev[0] < 6:
                continue
            agg.append(v); prev = (i, v)
    rnd = []
    for l in L:
        m = RND.search(l)
        if m:
            g = [int(x) if x else 0 for x in m.groups()]
            rnd.append((g[1], g[2], g[3], g[4]))
    t = [sum(x[i] for x in agg) for i in range(4)]
    r = [sum(x[i] for x in rnd) for i in range(4)]
    return t, r, len(agg), len(rnd)
out = []
for n in range(1, 189):
    c = cx[cands[n-1]['case_id']]
    pt, pr, pn, prn = totals(c['pre_log'])
    bt, br, bn, brn = totals(c['breaking_log'])
    rec = dict(n=n, case_id=c['case_id'], rec_pre_tests=c['pre_tests'], rec_brk_tests=c['breaking_tests'], rec_brk_fail=c['breaking_failures'], rec_brk_err=c['breaking_errors'],
               log_pre=pt, log_brk=bt, log_pre_rnd=pr, log_brk_rnd=br, pre_modules=pn, brk_modules=bn)
    def eq(a, b):
        try: return int(a) == int(b)
        except: return False
    # use surefire totals plus randomized-runner totals
    pre_total = pt[0] + pr[0]; brk_total = bt[0] + br[0]
    brk_f = bt[1] + br[1]; brk_e = bt[2] + br[2]
    rec['log_pre_total'] = pre_total; rec['log_brk_total'] = brk_total; rec['log_brk_f'] = brk_f; rec['log_brk_e'] = brk_e
    rec['mismatch'] = [k for k, a, b in (('pre_tests', c['pre_tests'], pre_total), ('breaking_tests', c['breaking_tests'], brk_total), ('breaking_failures', c['breaking_failures'], brk_f), ('breaking_errors', c['breaking_errors'], brk_e)) if not eq(a, b)]
    out.append(rec)
json.dump(out, open(P('audit_claude_review', 'count_check.json'), 'w'), indent=1)
mm = [r for r in out if r['mismatch']]
print('cases with count mismatch:', len(mm))
for r in mm:
    print(r['n'], r['mismatch'], 'rec', (r['rec_pre_tests'], r['rec_brk_tests'], r['rec_brk_fail'], r['rec_brk_err']), 'log', (r['log_pre_total'], r['log_brk_total'], r['log_brk_f'], r['log_brk_e']), 'rnd', r['log_pre_rnd'], r['log_brk_rnd'])
