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
(OUT/'text_values.json').write_text(json.dumps(dict(observed=f'{100*r["observed"]:.1f}',yes=str(r['yes']),ci_low=f'{100*r["ci"][0]:.1f}',ci_high=f'{100*r["ci"][1]:.1f}',coverage=f'{100*r["coverage"]:.1f}',covered=f"{sum(x['covers'] for x in r['intervals']):,}",pvalue=f'{r["pvalue"]:.4f}',large_pvalue=f'{large["pvalue"]:.4f}',extreme_count=f'{r["null_extreme_count"]:,}',null_draws=f'{r["null_H"]:,}',observed_distance=f'{100*abs(r["observed"]-.5):.1f}',critical_distance=f'{100*(r["critical_high"]-.5):.1f}'),indent=2))
(OUT/'environment.json').write_text(json.dumps(dict(python=platform.python_version(),numpy=np.__version__,seed=SEED,B=B,M=M,H=H),indent=2))
# Each experiment has its own page; shared data keep downloads small.
template=(ROOT/'code/chart_template.html').read_text()
(OUT/'simulation-data.js').write_text('window.SIM_DATA='+(OUT/'simulation.json').read_text()+';')
pages=[
 ('bootstrap','bootstrap.html','1. Build a bootstrap confidence interval','Start with one random sample. Reuse its observed responses to estimate how much its result could vary.','First draw the reference sample. Then add resamples, watch the histogram grow, and read the middle 95%. Try a different confidence level.'),
 ('coverage','coverage.html','2. Does a 95% interval catch the truth?','A confidence interval is a method with repeated-sampling performance. We can check that performance because our fictional population has known support of 55%.','Reveal ten intervals, then add 100 or play batches. Complete 2,000 and count how many contain the fixed truth. Try 90% and 99% confidence.'),
 ('null','hypothesis-test.html','3. Test a hypothesis with simulation','Suppose support is exactly 50%. How often would that population produce a poll at least as far from a tie as our observed result?','Build the null distribution in batches. Compare the observed statistic with the shaded rejection region; orange bars contribute to the p-value.'),
 ('poll','sampling.html','Extra. Why do samples disagree?','Even unbiased polls give different answers when they draw different people. This extra experiment explores that sampling variation.','Draw one poll, then add 20 or play batches. Watch the distribution develop around 55%, then compare sample sizes.')
]
for idx,(view,filename,title,intro,instruction) in enumerate(pages):
 nav='<nav class="page-nav" aria-label="Experiment pages">'+''.join('<a href="'+f+'"'+(' aria-current="page"' if v==view else '')+'>'+('Extra' if v=='poll' else str(i+1))+'</a>' for i,(v,f,*_) in enumerate(pages))+'</nav>'
 footer='<nav class="page-nav" aria-label="Continue learning">'
 if idx:footer+='<a href="'+pages[idx-1][1]+'">← Previous experiment</a>'
 if idx<len(pages)-1:footer+='<a href="'+pages[idx+1][1]+'">Next: '+pages[idx+1][2]+' →</a>'
 else:footer+='<a href="../index.html#what-should-we-learn">Return to the takeaway →</a>'
 footer+='</nav>'
 html=template
 for key,value in {'PAGE_TITLE':title,'INTRO':intro,'INSTRUCTION':instruction,'INITIAL_VIEW':view,'NAV':nav,'FOOTER':footer}.items():html=html.replace('__'+key+'__',value)
 (OUT/filename).write_text(html)
 if idx==0:(OUT/'chart.html').write_text(html) # Preserve the original demo URL.
# Explicit allowlist; no unrelated local data enter the downloadable bundle.
with zipfile.ZipFile(ROOT/'research.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in ['index.qmd','README.md','post.css']:
  if (ROOT/name).exists():z.write(ROOT/name,name)
 for folder in ['code','results','vendor']:
  for path in sorted((ROOT/folder).glob('*')):
   if path.is_file() and path.suffix in ['.py','.txt','.html','.json','.csv','.js']:
    z.write(path,path.relative_to(ROOT))
print('Built all simulations, explorer, and research.zip.')
