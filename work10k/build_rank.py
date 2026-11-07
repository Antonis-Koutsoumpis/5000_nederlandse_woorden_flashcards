"""Map words to positions in the 10k list (Liam Rosen / Fonzie-byte).

Outputs:
  ours_pos.csv  : our existing words with best 10k position (or blank)
  new_lemmas.csv: lemmas from the 10k list that are not in our list, with position,
                  forms, and flags (proper-noun-only, etc.)
"""
import pandas as pd, simplemma, re, json
SRC='/home/claude/fonzie-byte/10_000-most-used-words-in-dutch/'
full=[w.strip() for w in open(SRC+'10.000 meestgebruikte woorden in het Nederlands.txt',encoding='utf-8') if w.strip()]
# position = first occurrence (case-insensitive) in the full list
pos={}; cased={}
for i,w in enumerate(full,1):
    lw=w.lower()
    pos.setdefault(lw,i)
    cased.setdefault(lw,set()).add(w)
d=pd.read_csv('/home/claude/5000_nederlandse_woorden_flashcards/data/5000_woorden.csv',dtype=str,keep_default_na=False,encoding='utf-8-sig')
ourwords=sorted(set(d.word))
norm=lambda w: w.lower().replace('’',"'")
ourlow={}
for w in ourwords: ourlow.setdefault(norm(w),[]).append(w)
best={}; forms={}
newl={}
for lw,p in pos.items():
    lem=simplemma.lemmatize(lw,lang='nl').lower()
    cands=[lw,lem]
    hit=None
    for c in cands:
        c=c.replace('_','')
        if c in ourlow: hit=ourlow[c]; break
    if hit:
        for h in hit:
            if h not in best or p<best[h]: best[h]=p
            forms.setdefault(h,[]).append(lw)
    else:
        e=newl.setdefault(lem,{'lemma':lem,'pos10k':p,'forms':[]})
        e['pos10k']=min(e['pos10k'],p); e['forms'].append(lw)
rows=[{'word':w,'pos10k':best.get(w,''),'forms':' '.join(forms.get(w,[]))} for w in ourwords]
pd.DataFrame(rows).to_csv('ours_pos.csv',index=False)
out=[]
for lem,e in newl.items():
    # proper-noun-only: every form appears only capitalized in the full list
    capital_only=all(all(v[0].isupper() for v in cased[f]) for f in e['forms'])
    out.append({**e,'forms':' '.join(e['forms']),'capital_only':capital_only})
pd.DataFrame(out).sort_values('pos10k').to_csv('new_lemmas.csv',index=False)
print('ours with pos:',len(best),'of',len(ourwords),'| new lemmas:',len(out),'| capital-only:',sum(o['capital_only'] for o in out))
