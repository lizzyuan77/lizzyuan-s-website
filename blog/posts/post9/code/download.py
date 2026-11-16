"""Download a dated, cached Yahoo Finance snapshot for the class stock universe."""
from pathlib import Path
import json,re,hashlib,time
import pandas as pd
import yfinance as yf
ROOT=Path(__file__).resolve().parents[1]
cfg=json.loads((ROOT/'code/design.json').read_text())
text=(ROOT/'code/class_reference.R').read_text()
block=text.split('tickers <- c(',1)[1].split('\n)',1)[0]
tickers=re.findall(r'"([A-Z]+)"',block)
assert len(tickers)==len(set(tickers))
(ROOT/'data').mkdir(exist_ok=True)
frames=[];failures=[]
for i,ticker in enumerate(tickers+['SPY']):
 path=ROOT/'data'/f'{ticker}.csv'
 if path.exists():
  print(ticker,'cached',flush=True);continue
 try:
  df=yf.download(ticker,start=cfg['data_start'],end=cfg['data_end_exclusive'],auto_adjust=False,actions=False,progress=False,threads=False,multi_level_index=False)
  if df.empty:raise ValueError('No observations returned')
  df=df.reset_index();df.to_csv(path,index=False)
  print(ticker,len(df),flush=True)
 except Exception as e:
  failures.append({'ticker':ticker,'error':str(e)});print(ticker,'FAILED',str(e),flush=True)
 time.sleep(.25)
files=sorted((ROOT/'data').glob('*.csv'))
manifest={'provider':'Yahoo Finance via yfinance','retrieved_utc':pd.Timestamp.now(tz='UTC').isoformat(),'start':cfg['data_start'],'end_exclusive':cfg['data_end_exclusive'],'requested_stocks':tickers,'failures':failures,'files':{p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files}}
(ROOT/'data/manifest.json').write_text(json.dumps(manifest,indent=2))
assert (ROOT/'data/SPY.csv').exists(),'SPY is required'
assert not failures,'Review failed downloads before analysis; no silent exclusions.'
