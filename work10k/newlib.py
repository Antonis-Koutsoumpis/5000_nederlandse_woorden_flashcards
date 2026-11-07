"""Authoring helpers for NEW words taken from the 10k list (newwords/nNNN.py).

Each batch file defines ROWS = [ ... ] built with:
  N(word, english, article, plural, ipa, stress, ex1_nl, ex1_en, ex2_nl, ex2_en, **kw)
  V(word, english, present_ik, past_ik, participle, auxiliary, verb_type, reflexive, separable,
    ipa, stress, ex1_nl, ex1_en, ex2_nl, ex2_en, **kw)
  A(word, english, e_form, comparative, superlative, ipa, stress, ex1_nl, ex1_en, ex2_nl, ex2_en, **kw)
  O(word, pos, english, ipa, stress, ex1_nl, ex1_en, ex2_nl, ex2_en, **kw)
kw shortcuts:
  fx  = fixed_combination ("item (gloss); item (gloss)")
  xt  = expression-type codes, one per fx item (i/c/p), optional ';+expr=p' extras (as in enrichlib)
  syn = synonyms ("a; b"), ant = antonyms ("a; b")
  fp  = "prep ~ phrase ~ example_nl with **prep** ~ example_en"
  eh  = er_het_combination, reg = register, nt = notes
  p10 = 10k-list position (default: looked up from new_candidates.csv by word)
  sense = sense number (default 1); give 2, 3 ... for extra meanings of the same word
Target words in examples are marked with **...** in both languages.
Usage: python3 newlib.py check N
"""
from __future__ import annotations
import csv, importlib.util, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from enrichlib import parse_types  # noqa: E402

COLS = ['word', 'pos', 'english', 'article', 'plural', 'adj_e_form', 'comparative', 'superlative',
        'verb_present_ik', 'verb_past_ik', 'verb_past_participle', 'auxiliary', 'verb_type',
        'reflexive', 'separable', 'has_fixed_combination', 'fixed_combination',
        'er_het_combination', 'ipa', 'stress', 'example1_nl', 'example1_en', 'example2_nl',
        'example2_en', 'register', 'notes', 'synonyms', 'antonyms', 'expression_type',
        'fixed_preposition', 'preposition_phrase', 'preposition_example_nl',
        'preposition_example_en', 'p10', 'sense']
SHORT = {"fx": "fixed_combination", "eh": "er_het_combination", "reg": "register", "nt": "notes",
         "syn": "synonyms", "ant": "antonyms"}
POS10K = {r['lemma']: int(r['pos10k']) for r in csv.DictReader(open(HERE / 'new_candidates.csv'))}


def _row(base, kw):
    for k, v in kw.items():
        base[SHORT.get(k, k)] = v
    return base


def _ex(e1, t1, e2, t2):
    return dict(example1_nl=e1, example1_en=t1, example2_nl=e2, example2_en=t2)


def N(word, en, art, pl, ipa, st, e1, t1, e2, t2, **kw):
    return _row(dict(word=word, pos="noun", english=en, article=art, plural=pl, ipa=ipa, stress=st,
                     **_ex(e1, t1, e2, t2)), kw)


def V(word, en, pres, past, part, aux, vt, refl, sep, ipa, st, e1, t1, e2, t2, **kw):
    return _row(dict(word=word, pos="verb", english=en, verb_present_ik=pres, verb_past_ik=past,
                     verb_past_participle=part, auxiliary=aux, verb_type=vt, reflexive=refl,
                     separable=sep, ipa=ipa, stress=st, **_ex(e1, t1, e2, t2)), kw)


def A(word, en, ef, comp, sup, ipa, st, e1, t1, e2, t2, **kw):
    return _row(dict(word=word, pos="adjective", english=en, adj_e_form=ef, comparative=comp,
                     superlative=sup, ipa=ipa, stress=st, **_ex(e1, t1, e2, t2)), kw)


def O(word, pos, en, ipa, st, e1, t1, e2, t2, **kw):
    return _row(dict(word=word, pos=pos, english=en, ipa=ipa, stress=st, **_ex(e1, t1, e2, t2)), kw)


def finalize(r: dict) -> tuple[dict, list[str]]:
    errs = []
    out = {c: '' for c in COLS}
    for k, v in r.items():
        if k in ('xt', 'fp'):
            continue
        if k not in out:
            errs.append(f"{r.get('word')}: unknown key {k}")
            continue
        out[k] = '' if v is None else str(v)
    w = out['word']
    out['has_fixed_combination'] = 'yes' if out['fixed_combination'] else 'no'
    try:
        out['expression_type'] = parse_types(r.get('xt', ''), out['fixed_combination'])
    except Exception as e:  # noqa: BLE001
        errs.append(f"{w}: types {e}")
    fp = r.get('fp', '')
    if fp:
        p = [x.strip() for x in fp.split('~')]
        if len(p) != 4:
            errs.append(f"{w}: fp needs 4 parts")
        else:
            prep, phr, exn, exe = p
            if not re.search(rf'\b{re.escape(prep)}\b', phr):
                errs.append(f"{w}: prep not in phrase")
            if f"**{prep}**" not in exn or exn.count('**') != 2:
                errs.append(f"{w}: prep example must mark only **{prep}**")
            out.update(fixed_preposition=prep, preposition_phrase=phr,
                       preposition_example_nl=exn, preposition_example_en=exe)
    if not out['p10']:
        if w.lower() in POS10K:
            out['p10'] = str(POS10K[w.lower()])
        else:
            errs.append(f"{w}: no 10k position (give p10=)")
    out['sense'] = out['sense'] or '1'
    for k in ('example1_nl', 'example1_en'):
        if '**' not in out[k]:
            errs.append(f"{w}: {k} lacks **target**")
    if out['pos'] == 'noun' and out['article'] not in ('de', 'het', 'de/het', ''):
        errs.append(f"{w}: article {out['article']}")
    return out, errs


def load(n: int) -> list[dict]:
    path = HERE / 'newwords' / f'n{n:03d}.py'
    spec = importlib.util.spec_from_file_location(f'n{n:03d}', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.ROWS


def check(n: int):
    rows = load(n)
    errs = []
    for r in rows:
        _, e = finalize(r)
        errs += e
    print(f"batch n{n:03d}: {len(rows)} rows")
    for e in errs:
        print("ERR", e)
    return errs


if __name__ == '__main__':
    sys.exit(1 if check(int(sys.argv[2])) else 0)
