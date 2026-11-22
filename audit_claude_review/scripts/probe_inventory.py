import csv, os, collections, sys
rows = list(csv.DictReader(open('audit_claude_review/claude_audit.csv', encoding='utf-8')))
PROBE = ('probe', 'control', 'subclass', 'fixed_date', 'class_origin', 'discovery', 'lexer', 'annotation', 'directory', 'html_', 'text_', 'Probe')
fam = collections.defaultdict(list)
for r in rows:
    n = int(r['case_number']); g = r['related_group'].split(' | ')[0]
    ev = f'logs/case{n}_evidence'; found = set()
    if os.path.isdir(ev):
        for f in os.listdir(ev):
            if any(p in f for p in PROBE): found.add(f)
    fam[g].append((n, r['claude_label_post_comparison'][:3], sorted(found)[:4]))
for g, v in fam.items():
    print('##', g, len(v), 'cases:', [n for n, *_ in v])
    print('   probes:', [(n, p) for n, l, p in v if p] or 'none')
