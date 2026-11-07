import pandas as pd
from wordfreq import zipf_frequency as z
n=pd.read_csv('new_lemmas.csv',keep_default_na=False)
ours=pd.read_csv('ours_pos.csv',keep_default_na=False)
ourlow=set(ours.word.str.lower().str.replace('’',"'"))
n['lemma']=n.lemma.str.replace('_','',regex=False)
n=n[~n.lemma.isin(ourlow)]
foreign=n.lemma.map(lambda w: z(w,'en')>z(w,'nl')+0.5 or z(w,'fr')>z(w,'nl')+0.5)
keep=n[(n.capital_only.astype(str)!='True') & ~foreign & (n.lemma.str.len()>1)]
keep=keep.sort_values('pos10k').reset_index(drop=True)
keep.to_csv('new_candidates.csv',index=False)
print(len(keep))
