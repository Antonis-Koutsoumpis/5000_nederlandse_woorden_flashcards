"""Option B: estimate a 10k-list position for our words missing from that list,
from their current rank, using the median 10k position of words with similar ranks."""
import pandas as pd, numpy as np
d=pd.read_csv('/home/claude/5000_nederlandse_woorden_flashcards/data/5000_woorden.csv',dtype=str,keep_default_na=False,encoding='utf-8-sig')
wr=d.groupby('word')['rank'].first().astype(int)
o=pd.read_csv('ours_pos.csv',keep_default_na=False)
o['old_rank']=o.word.map(wr)
o['pos10k']=pd.to_numeric(o.pos10k,errors='coerce')
known=o.dropna(subset=['pos10k']).sort_values('old_rank')
def est(r,win=150):
    s=known[(known.old_rank>=r-win)&(known.old_rank<=r+win)].pos10k
    return float(s.median())
grid=np.arange(1,5001,25); g=np.maximum.accumulate([est(r) for r in grid])
o['est_pos']=np.interp(o.old_rank,grid,g)
o['position']=o.pos10k.fillna(o.est_pos)
o['estimated']=o.pos10k.isna()
o.to_csv('ours_ranked.csv',index=False)
for r in (1,500,1000,1500,2000,3000,4000,4900): print(r, round(np.interp(r,grid,g)))
print(o[o.estimated].sort_values('old_rank').head(15)[['word','old_rank','position']].to_string())
