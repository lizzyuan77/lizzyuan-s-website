"""Compute weighted, comparable major statistics from 2024 ACS 1-year PUMS.
Run: python code/analyze.py --source /path/to/csv_pus.zip
Only aggregate statistics are saved. Uses both national person-file parts.
"""
import argparse, json, zipfile, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--source',required=True);args=parser.parse_args()
source=Path(args.source)
cols=['AGEP','SEX','SCHL','FOD1P','WAGP','ADJINC','WKHP','WKWN','COW','PWGTP']+[f'PWGTP{i}' for i in range(1,81)]
chunks=[];flow={'all_person_records':0,'age_25_64_bachelors_plus':0,'eligible_workers':0}
with zipfile.ZipFile(source) as z:
 for name in sorted(n for n in z.namelist() if n.endswith('.csv')):
  for chunk in pd.read_csv(z.open(name),usecols=cols,chunksize=100000):
   flow['all_person_records']+=len(chunk)
   d=chunk[chunk.AGEP.between(25,64)&chunk.SCHL.ge(21)&chunk.FOD1P.notna()]
   flow['age_25_64_bachelors_plus']+=len(d)
   d=d[d.WKHP.ge(35)&d.WKWN.ge(50)&d.WAGP.gt(0)&d.COW.isin([1,2,3,4,5])&d.PWGTP.gt(0)].copy()
   flow['eligible_workers']+=len(d);d['earnings']=d.WAGP*d.ADJINC/1e6;chunks.append(d)
  print('Read',name,flush=True)
d=pd.concat(chunks,ignore_index=True); del chunks
assert d.SEX.isin([1,2]).all()
labels=json.loads((ROOT/'data/FOD1P.json').read_text())['values']['item']
# Author-created display families. Full mapping is reproducible here.
families={
 'Science, computing & engineering':{'13','14','21','24','25','36','37','38','40','50','51'},
 'Business':{'62'},'Education':{'23'},'Health':{'61'},
 'Social sciences & public service':{'15','29','32','41','48','49','52','53','54','55'},
 'Arts, humanities & other':{'11','19','20','22','26','33','34','35','56','57','59','60','64'}}
assert len(set.union(*families.values()))==sum(map(len,families.values()))

def medians(s):
 s=s.sort_values('earnings',kind='stable'); values=s.earnings.to_numpy();w=s[['PWGTP']+[f'PWGTP{i}' for i in range(1,81)]].to_numpy(float)
 # Retain signed replicate weights as supplied by Census (never truncate them).
 # Quantile convention: first cumulative-weight crossing of half the total.
 assert (w[:,0]>0).all()
 totals=w.sum(axis=0);assert (totals>0).all()
 indices=(np.cumsum(w,axis=0)>=totals/2).argmax(axis=0)
 return values[indices],totals

rows=[];excluded=[]
for code,s in d.groupby('FOD1P'):
 code=str(int(code)); counts=s.SEX.value_counts()
 if min(counts.get(1,0),counts.get(2,0))<100:
  excluded.append({'code':code,'major':labels[code],'men_n':int(counts.get(1,0)),'women_n':int(counts.get(2,0))});continue
 men,mw=medians(s[s.SEX==1]);women,fw=medians(s[s.SEX==2]);ratios=100*women/men;shares=100*fw/(mw+fw)
 se=lambda a:float(np.sqrt(4/80*np.sum((a[1:]-a[0])**2)))
 family=next((g for g,codes in families.items() if code[:2] in codes),None);assert family
 rows.append({'code':code,'major':labels[code].title(),'family':family,'male_earnings':float(men[0]),'female_earnings':float(women[0]),'ratio':float(ratios[0]),'ratio_se':se(ratios),'ratio_moe90':1.645*se(ratios),'female_share':float(shares[0]),'male_n':int(counts[1]),'female_n':int(counts[2]),'male_population':float(mw[0]),'female_population':float(fw[0]),'female_earnings_moe90':1.645*se(women),'male_earnings_moe90':1.645*se(men)})
out=pd.DataFrame(rows);out['distance_from_parity']=(out.ratio-100).abs();out=out.sort_values(['distance_from_parity','major'])
assert len(out.code)==len(set(out.code));assert out.female_share.between(0,100).all();assert np.isfinite(out.ratio).all()
# Zero SDR variance can arise from a flat/heaped median; do not display it as certainty.
out.loc[out.ratio_se.eq(0),'ratio_moe90']=np.nan
out.to_csv(ROOT/'results/majors.csv',index=False);pd.DataFrame(excluded).to_csv(ROOT/'results/excluded_majors.csv',index=False)
records=json.loads(out.to_json(orient='records',double_precision=8));(ROOT/'results/majors.json').write_text(json.dumps(records,indent=2))
flow['negative_replicate_weight_cells']=int((d[[f'PWGTP{i}' for i in range(1,81)]].to_numpy()<0).sum())
flow.update({'displayed_majors':len(out),'excluded_majors':len(excluded),'displayed_sample':int(out.male_n.sum()+out.female_n.sum())})
(ROOT/'results/sample_flow.json').write_text(json.dumps(flow,indent=2))
manifest={'source_url':'https://www2.census.gov/programs-surveys/acs/data/pums/2024/1-Year/csv_pus.zip','retrieved':'2026-10-25','sha256':hashlib.file_digest(open(source,'rb'),'sha256').hexdigest(),'source_bytes':source.stat().st_size,'families':{k:sorted(v) for k,v in families.items()},'python_libraries':{'numpy':np.__version__,'pandas':pd.__version__}}
(ROOT/'data/source_manifest.json').write_text(json.dumps(manifest,indent=2))
print(flow);print(out[['major','ratio','female_earnings','female_share']].head(12).round(1).to_string(index=False))
print('Highest female earnings:',out.sort_values('female_earnings',ascending=False)[['major','ratio','female_earnings']].head(6).round(1).to_string(index=False))
