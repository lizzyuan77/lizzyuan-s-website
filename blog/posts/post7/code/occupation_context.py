"""Add descriptive occupation/hour context on EXACTLY the chart's population.
No causal decomposition: modal occupations and hours are descriptive checks.
Run after analyze.py, with the same national source archive.
"""
from pathlib import Path
import argparse,json,zipfile
import pandas as pd
import numpy as np
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);a=p.parse_args()
cols=['AGEP','SEX','SCHL','FOD1P','WAGP','WKHP','WKWN','COW','PWGTP','OCCP']
parts=[]
with zipfile.ZipFile(a.source) as z:
 for n in sorted(n for n in z.namelist() if n.endswith('.csv')):
  for c in pd.read_csv(z.open(n),usecols=cols,chunksize=100000):
   ok=c.AGEP.between(25,64)&c.SCHL.ge(21)&c.FOD1P.notna()&c.WKHP.ge(35)&c.WKWN.ge(50)&c.WAGP.gt(0)&c.COW.isin([1,2,3,4,5])&c.PWGTP.gt(0)
   parts.append(c[ok].copy())
  print('Context read:',n,flush=True)
d=pd.concat(parts,ignore_index=True)
assert len(d)==json.loads((root/'results/sample_flow.json').read_text())['eligible_workers']
labels=json.loads((root/'data/OCCP.json').read_text())['values']['item']
rows=[]
for code,s in d.groupby('FOD1P'):
 row={'code':str(int(code))}
 for sex,prefix in [(1,'male'),(2,'female')]:
  q=s[s.SEX==sex]
  if len(q)==0:continue
  w=q.PWGTP.sum(); occ=q.groupby('OCCP').PWGTP.sum().sort_values(ascending=False)
  top=str(int(occ.index[0])).zfill(4);label=labels[top].split('-',1)[-1].title()
  row.update({f'{prefix}_top_occupation':label,f'{prefix}_top_occupation_share':float(100*occ.iloc[0]/w),f'{prefix}_mean_hours':float(np.average(q.WKHP,weights=q.PWGTP)),f'{prefix}_journalist_share':float(100*q.loc[q.OCCP.eq(2810),'PWGTP'].sum()/w)})
 row['journalist_share']=float(100*s.loc[s.OCCP.eq(2810),'PWGTP'].sum()/s.PWGTP.sum());rows.append(row)
out=pd.DataFrame(rows);out.to_csv(root/'results/occupation_context.csv',index=False)
base=pd.read_csv(root/'results/majors.csv',dtype={'code':str})
# Joining the aggregate context must not change any original earnings estimate.
merged=base.merge(out,on='code',validate='one_to_one');assert len(merged)==len(base)
assert np.allclose(merged.ratio,base.ratio)
(root/'results/majors.json').write_text(merged.to_json(orient='records',indent=2,double_precision=8))
print(merged[merged.code.isin(['1902','6207','2408','6107'])][['major','male_top_occupation','female_top_occupation','male_mean_hours','female_mean_hours','journalist_share']].to_string(index=False))

manifest_path=root/'data/source_manifest.json'
manifest=json.loads(manifest_path.read_text())
manifest['occupation_metadata_url']='https://api.census.gov/data/2024/acs/acs1/pums/variables/OCCP.json'
manifest_path.write_text(json.dumps(manifest,indent=2))

# A shared category set lets readers compare women's and men's destinations.
# Keep the top three occupations for each sex, plus journalists for journalism.
# Aggregate every remaining occupation into Other, so each bar totals 100%.
shown=set(base.code)
occupation_bars={}
for code,sub in d.groupby('FOD1P'):
    code=str(int(code))
    if code not in shown:continue
    totals={sex:sub.loc[sub.SEX.eq(sex),'PWGTP'].sum() for sex in [1,2]}
    counts={sex:sub[sub.SEX.eq(sex)].groupby('OCCP').PWGTP.sum() for sex in [1,2]}
    selected=set()
    for sex in [1,2]:selected.update(counts[sex].nlargest(3).index)
    if code=='1902':selected.add(2810)
    selected=sorted(selected,key=lambda occ:-(counts[1].get(occ,0)+counts[2].get(occ,0)))
    cats=[]
    for occ in selected:
        label=labels[str(int(occ)).zfill(4)].split('-',1)[-1].title()
        cats.append({'occupation':label,'code':str(int(occ)).zfill(4),
                     'women':float(100*counts[2].get(occ,0)/totals[2]),
                     'men':float(100*counts[1].get(occ,0)/totals[1])})
    cats.append({'occupation':'All other occupations','code':'other',
                 'women':100-sum(x['women'] for x in cats),
                 'men':100-sum(x['men'] for x in cats)})
    assert abs(sum(x['women'] for x in cats)-100)<1e-8
    assert abs(sum(x['men'] for x in cats)-100)<1e-8
    occupation_bars[code]=cats
(root/'results/occupation_shares.json').write_text(json.dumps(occupation_bars,indent=2))
print('Career-destination bars saved:',len(occupation_bars),'majors')
