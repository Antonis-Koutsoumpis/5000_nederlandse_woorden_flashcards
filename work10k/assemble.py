"""Build data/woorden.csv from the frozen 5000 list + enrichment + new 10k words.

  python3 work10k/assemble.py          (run from anywhere)

Ordering: each word (all its meanings together) is placed at its position in the 10k list
(best position of any form); words missing from the 10k list use the position estimated from
their old rank (estimate.py, option B). Ties: existing words first, then by old rank / 10k position.
Ranks are then renumbered 1..N and ids rebuilt as RRRR-S (S = meaning number).
"""
import glob, os, re, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
os.chdir(HERE)
sys.path.insert(0, HERE)
import enrichlib  # noqa: E402
import newlib  # noqa: E402

NEW_COLS = ['synonyms', 'antonyms', 'expression_type', 'fixed_preposition', 'preposition_phrase',
            'preposition_example_nl', 'preposition_example_en', 'source']
SRC_BOTH = "5000 list + 10k list"
SRC_OLD = "5000 list only (position estimated)"
SRC_NEW = "10k list (new)"

base = enrichlib.load()
BASE_COLS = list(base.columns)
errs = []

# --- enrichment for existing rows
enr = {}
files = sorted(glob.glob('enrich/e*.txt'))
for f in files:
    n = int(re.search(r'e(\d+)', f).group(1))
    out, e = enrichlib.parse_file(n)
    enr.update(out)
    errs += [f"e{n:03d}: {x}" for x in e]
for c in NEW_COLS[:-1]:
    base[c] = base['id'].map(lambda i, c=c: enr.get(i, {}).get(c, ''))
missing_enr = (~base['id'].isin(enr)).sum()

# --- positions for existing words
rk = pd.read_csv('ours_ranked.csv', dtype={'old_rank': int})
pos = {(r.word, r.old_rank): (float(r.position), bool(r.estimated)) for r in rk.itertuples()}
groups = []
for old_rank, g in base.groupby(base['rank'].astype(int), sort=False):
    w = g['word'].iloc[0]
    p, est = pos[(w, old_rank)]
    g = g.copy()
    g['source'] = SRC_OLD if est else SRC_BOTH
    g['_sense'] = g['id'].str.split('-').str[1]
    groups.append(((p, 0, old_rank), g))

# --- new words
existing = set(base['word'].str.lower())
new_rows = []
for f in sorted(glob.glob('newwords/n*.py')):
    n = int(re.search(r'n(\d+)', f).group(1))
    for r in newlib.load(n):
        out, e = newlib.finalize(r)
        errs += [f"n{n:03d}: {x}" for x in e]
        new_rows.append(out)
if new_rows:
    nd = pd.DataFrame(new_rows)
    dup = nd[nd['word'].str.lower().isin(existing)]['word'].unique()
    if len(dup):
        errs.append(f"new words already in list: {list(dup)}")
    nd = nd[~nd['word'].str.lower().isin(existing)]
    nd['source'] = SRC_NEW
    for w, g in nd.groupby('word', sort=False):
        p10 = int(g['p10'].iloc[0])
        g = g.copy()
        g['_sense'] = g['sense']
        groups.append(((float(p10), 1, p10), g))
n_new = sum(1 for k, _ in groups if k[1] == 1)

# --- order, renumber
groups.sort(key=lambda kg: kg[0])
parts = []
for new_rank, (_, g) in enumerate(groups, 1):
    g = g.copy()
    g['rank'] = str(new_rank)
    g['id'] = [f"{new_rank:04d}-{s}" for s in g['_sense']]
    parts.append(g)
df = pd.concat(parts, ignore_index=True)


def band(r):
    r = int(r)
    if r <= 2000:
        return "0-2000"
    lo = (r - 1) // 1000 * 1000
    return f"{lo}-{lo + 1000}"


df['frequency_band'] = df['rank'].map(band)
cols = BASE_COLS + NEW_COLS
df = df.reindex(columns=cols).fillna('')
if df['id'].duplicated().any():
    errs.append(f"duplicate ids: {df[df['id'].duplicated()]['id'].tolist()[:10]}")

out_path = os.path.join(ROOT, 'data', 'woorden.csv')
df.to_csv(out_path, index=False, encoding='utf-8-sig')
# --- docs with current counts
for tmpl, dest in (('templates/README.md.tmpl', os.path.join(ROOT, 'README.md')),
                   ('templates/codebook.md.tmpl', os.path.join(ROOT, 'data', 'codebook.md'))):
    txt = open(tmpl, encoding='utf-8').read()
    txt = txt.replace('WORDS_N', f"{df['rank'].nunique():,}").replace('ROWS_N', f"{len(df):,}")
    open(dest, 'w', encoding='utf-8').write(txt)

print(f"wrote {out_path}: {len(df)} rows, {df['rank'].nunique()} words "
      f"({n_new} new), rows without enrichment: {missing_enr}")
print(df['source'].value_counts().to_string())
for e in errs:
    print("ERR", e)
sys.exit(1 if errs else 0)
