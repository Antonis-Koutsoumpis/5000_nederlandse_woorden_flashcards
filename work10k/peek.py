import csv, sys, pandas as pd
d = set(pd.read_csv('../data/woorden.csv', encoding='utf-8-sig', dtype=str).word.str.lower())
r = [x['lemma'] for x in csv.DictReader(open('new_candidates.csv'))]
i = r.index(sys.argv[1]) + 1
n = int(sys.argv[2]) if len(sys.argv) > 2 else 75
out = []
for w in r[i:i+n]:
    f = [c for c in (w, w[:-1], w[:-2], w[:-3]) if c in d]
    out.append(w + ('[DUP:' + f[0] + ']' if f else ''))
print(' '.join(out))
