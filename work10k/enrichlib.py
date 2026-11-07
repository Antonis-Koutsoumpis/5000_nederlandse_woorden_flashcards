"""Enrichment of existing rows: synonyms, antonyms, expression types, fixed prepositions.

Batch file enrich/eNNN.txt covers rows (N-1)*100 .. N*100-1 of data/5000_woorden.csv (file order).
One line per row:  id|synonyms|antonyms|types|prep ~ prep_phrase ~ prep_ex_nl ~ prep_ex_en
  Trailing fields may be omitted ('0001-1' alone = nothing to add).
  types: one code per fixed_combination item, comma-separated (i=idiom, c=collocation,
         p=phrasal verb), optionally followed by ';' and extra expressions 'expr=p' (';'-separated),
         e.g. 'c,i;+deelnemen aan=p'. Leave empty if no items and no extras.
  prep fields: leave empty when the word has no fixed preposition.
Usage: python3 enrichlib.py show N | check N
"""
import sys, re, pandas as pd
CSV='/home/claude/5000_nederlandse_woorden_flashcards/data/5000_woorden.csv'
CODES={'i':'idiom','c':'collocation','p':'phrasal verb'}

def load():
    return pd.read_csv(CSV,dtype=str,keep_default_na=False,encoding='utf-8-sig')

def split_items(text):
    items,depth,cur=[],0,''
    for ch in str(text):
        if ch=='(': depth+=1
        elif ch==')': depth=max(depth-1,0)
        if ch==';' and depth==0: items.append(cur.strip()); cur=''
        else: cur+=ch
    if cur.strip(): items.append(cur.strip())
    return [i for i in items if i]

def dutch_part(item): return re.sub(r'\s*\(.*$','',item).strip()

def rows(n):
    d=load(); return d.iloc[(n-1)*100:n*100]

def show(n):
    for r in rows(n).itertuples():
        items=[dutch_part(i) for i in split_items(r.fixed_combination)]
        extra=f" sep={r.separable}" if r.pos=='verb' else ''
        print(f"{r.id}|{r.word}|{r.pos}|{r.english[:45]}|{' ¦ '.join(items)}{extra}")

def parse_types(code, fc):
    items=[dutch_part(i) for i in split_items(fc)]
    main,_,ext=code.partition(';')
    codes=[c.strip() for c in main.split(',') if c.strip()]
    if len(codes)!=len(items):
        raise ValueError(f"{len(codes)} codes for {len(items)} items")
    out=[f"{e} = {CODES[c]}" for e,c in zip(items,codes)]
    for x in [x.strip() for x in ext.split(';') if x.strip()]:
        e,_,c=x.lstrip('+').rpartition('=')
        out.append(f"{e.strip()} = {CODES[c.strip()]}")
    return ' | '.join(out)

def parse_file(n):
    sub=rows(n); fc=dict(zip(sub.id,sub.fixed_combination))
    out={}; errs=[]
    for ln,line in enumerate(open(f'enrich/e{n:03d}.txt',encoding='utf-8'),1):
        line=line.rstrip('\n')
        if not line.strip() or line.startswith('#'): continue
        f=[x.strip() for x in line.split('|')]
        if len(f)>5: errs.append(f"line {ln}: {len(f)} fields"); continue
        f+=['']*(5-len(f))
        i,syn,ant,typ,pb=f
        p=[x.strip() for x in pb.split('~')] if pb else []
        if p and len(p)!=4: errs.append(f"{i}: prep block needs 4 parts"); p=[]
        prep,phr,exn,exe=p if p else ['']*4
        if i not in fc: errs.append(f"{i}: not in batch"); continue
        try: t=parse_types(typ,fc[i])
        except Exception as e: errs.append(f"{i}: types {e}"); t=''
        if prep:
            if not re.search(rf'\b{re.escape(prep)}\b',phr): errs.append(f"{i}: prep not in phrase")
            if f"**{prep}**" not in exn: errs.append(f"{i}: example lacks **{prep}**")
            if exn.count('**')!=2: errs.append(f"{i}: mark only the answer preposition")
            if not exe: errs.append(f"{i}: no English example")
        out[i]=dict(synonyms=syn,antonyms=ant,expression_type=t,fixed_preposition=prep,
                    preposition_phrase=phr,preposition_example_nl=exn,preposition_example_en=exe)
    missing=[i for i in fc if i not in out]
    if missing: errs.append(f"missing ids: {missing[:10]} ({len(missing)})")
    return out,errs

if __name__=='__main__':
    cmd,n=sys.argv[1],int(sys.argv[2])
    if cmd=='show': show(n)
    else:
        out,errs=parse_file(n)
        print(f"batch e{n:03d}: {len(out)} rows, {sum(bool(v['fixed_preposition']) for v in out.values())} preps, "
              f"{sum(bool(v['synonyms']) for v in out.values())} with synonyms")
        for e in errs: print("ERR",e)
