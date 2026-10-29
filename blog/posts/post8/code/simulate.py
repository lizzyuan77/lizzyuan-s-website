"""Seeded binary-survey simulation; no real survey data or external downloads."""
from pathlib import Path
import csv, json, math, platform, zipfile
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
SEED=20261028; B=4000; M=2000; H=100000
OUT=ROOT/'results'; OUT.mkdir(exist_ok=True)
all_results={}
summary=[]
for n in [100,200,500,1000]:
 rng=np.random.default_rng(np.random.SeedSequence([SEED,n]))
 # A genuine random sample from the known simulation population.
 sample=rng.binomial(1,.55,size=n)
 k=int(sample.sum())
 with (OUT/f'poll_n{n}.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['respondent','yes']);w.writerows(enumerate(sample.tolist(),1))
 boot_indices=rng.integers(0,n,size=(B,n))
 boot=sample[boot_indices].mean(axis=1)
 lo,hi=np.quantile(boot,[.025,.975],method='linear')
 # Outer loop: NEW samples from a known population (true yes probability .55).
 counts=rng.binomial(n,.55,size=M)
 # Inner loop: bootstrap each outer sample, with replacement. For binary data,
 # the number of yes answers in a resample is exactly Binomial(n, count/n).
 # This is the same resampling law without materializing millions of index arrays.
 intervals=[]
 level_intervals={90:[],95:[],99:[]}
 for chunk in np.array_split(counts,20):
  bs=rng.binomial(n,chunk[:,None]/n,size=(len(chunk),B))/n
  intervals.extend(np.quantile(bs,[.025,.975],axis=1,method='linear').T.tolist())
  for level in [90,95,99]:
   alpha=1-level/100
   level_intervals[level].extend(np.quantile(bs,[alpha/2,1-alpha/2],axis=1,method='linear').T.tolist())
 intervals=np.array(intervals)
 covered=(intervals[:,0]<=.55+1e-12)&(intervals[:,1]>=.55-1e-12)
 null=rng.binomial(n,.5,size=H)
 obs_distance=abs(k/n-.5)
 extreme=np.abs(null-n/2)>=abs(k-n/2)
 pv=float(extreme.mean())
 # Exact binomial reference used to validate the Monte Carlo p-value and to
 # define a conservative two-sided 5% rejection region on a discrete lattice.
 pmf=np.array([math.comb(n,j)*(.5**n) for j in range(n+1)])
 distances=np.abs(np.arange(n+1)-n/2)
 exact=float(pmf[distances>=abs(k-n/2)].sum())
 critical=next(d for d in range(n//2+1) if pmf[distances>=d].sum()<=.05)
 reject=distances>=critical
 mcse=math.sqrt(pv*(1-pv)/H)
 assert abs(pv-exact)<6*math.sqrt(max(exact*(1-exact),1e-9)/H)
 assert .91<covered.mean()<.98
 assert lo<=k/n<=hi
 assert abs(pmf.sum()-1)<1e-10
 examples=[]
 for indices in boot_indices[:8]:
  ids,freq=np.unique(indices,return_counts=True)
  order=np.argsort(-freq,kind='stable')[:5]
  examples.append(dict(first_draws=[int(j)+1 for j in indices[:12]],unique_people=len(ids),
    repeated=[dict(id=int(ids[j])+1,times=int(freq[j]),yes=int(sample[ids[j]])) for j in order]))
 levels={}
 for level,ivs in level_intervals.items():
  flags=[a<=.55+1e-12 and b>=.55-1e-12 for a,b in ivs]
  levels[str(level)]=dict(coverage=sum(flags)/M,intervals=[dict(sample=i+1,estimate=int(counts[i])/n,lo=a,hi=b,covers=flags[i]) for i,(a,b) in enumerate(ivs)])
 row=dict(n=n,yes=k,observed=k/n,bootstrap_B=B,ci=[float(lo),float(hi)],
  sample_answers=sample.tolist(),bootstrap_rates=boot.tolist(),resample_examples=examples,coverage_levels=levels,
  null_checkpoints={str(h):np.bincount(null[:h],minlength=n+1).tolist() for h in [100,1000,10000,100000]},
  bootstrap_counts=np.bincount(np.rint(boot*n).astype(int),minlength=n+1).tolist(),
  coverage=float(covered.mean()),coverage_M=M,coverage_mcse=float(math.sqrt(covered.mean()*(1-covered.mean())/M)),
  intervals=[dict(sample=i+1,estimate=int(counts[i])/n,lo=float(intervals[i,0]),hi=float(intervals[i,1]),covers=bool(covered[i])) for i in range(M)],
  null_counts=np.bincount(null,minlength=n+1).tolist(),null_H=H,pvalue=pv,pvalue_mcse=mcse,exact_pvalue=exact,
  critical_low=(n/2-critical)/n,critical_high=(n/2+critical)/n,
  rejection_probability=float(pmf[reject].sum()),null_extreme_count=int(extreme.sum()))
 all_results[str(n)]=row
 summary.append({key:row[key] for key in ['n','yes','coverage','pvalue','exact_pvalue','rejection_probability']})
 with (OUT/f'coverage_n{n}.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=row['intervals'][0]);w.writeheader();w.writerows(row['intervals'])
 print(n, 'CI',row['ci'],'coverage',row['coverage'],'p',pv,'exact',exact,flush=True)
(OUT/'simulation.json').write_text(json.dumps(dict(seed=SEED,B=B,M=M,H=H,cases=all_results),separators=(',',':')))
with (OUT/'summary.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=summary[0]);w.writeheader();w.writerows(summary)
r=all_results['500']; large=all_results['1000']
(OUT/'text_values.json').write_text(json.dumps(dict(observed=f'{100*r["observed"]:.1f}',yes=str(r['yes']),ci_low=f'{100*r["ci"][0]:.1f}',ci_high=f'{100*r["ci"][1]:.1f}',coverage=f'{100*r["coverage"]:.1f}',covered=f"{sum(x['covers'] for x in r['intervals']):,}",pvalue=f'{r["pvalue"]:.4f}',large_pvalue=f'{large["pvalue"]:.4f}'),indent=2))
(OUT/'environment.json').write_text(json.dumps(dict(python=platform.python_version(),numpy=np.__version__,seed=SEED,B=B,M=M,H=H),indent=2))
# Self-contained explorer: all displayed numbers come from the saved simulation.
template=(ROOT/'code/chart_template.html').read_text()
(OUT/'chart.html').write_text(template.replace('__DATA__',(OUT/'simulation.json').read_text()))
# Explicit allowlist; no unrelated local data enter the downloadable bundle.
with zipfile.ZipFile(ROOT/'research.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in ['index.qmd','README.md','post.css']:
  if (ROOT/name).exists():z.write(ROOT/name,name)
 for folder in ['code','results','vendor']:
  for path in sorted((ROOT/folder).glob('*')):
   if path.is_file() and path.suffix in ['.py','.txt','.html','.json','.csv','.js']:
    z.write(path,path.relative_to(ROOT))
print('Built all simulations, explorer, and research.zip.')
