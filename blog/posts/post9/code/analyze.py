"""One predeclared validation search, then an untouched 2024–2025 evaluation."""
from pathlib import Path
import json,itertools,hashlib,platform
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import mean_squared_error
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
C=json.loads((ROOT/'code/design.json').read_text());SEED=C['seed']
manifest=json.loads((ROOT/'data/manifest.json').read_text())
for name,meta in manifest['files'].items():assert hashlib.sha256((ROOT/'data'/name).read_bytes()).hexdigest()==meta['sha256']

def read(ticker):
 d=pd.read_csv(ROOT/'data'/f'{ticker}.csv',parse_dates=['Date']).sort_values('Date').set_index('Date')
 assert d.index.is_unique and (d['Adj Close']>0).all()
 return d
spy=read('SPY');spyret=spy['Adj Close'].pct_change();parts=[]
for ticker in manifest['requested_stocks']:
 d=read(ticker);p=d['Adj Close'];r=p.pct_change();f=d.rename(columns={'Open':'open','High':'high','Low':'low','Close':'close','Volume':'volume','Adj Close':'adjusted'}).copy()
 f['return']=r;f['spy_ret']=spyret
 # Preserve the class feature definitions, including the inverse momentum ratios.
 for suffix,k in [('1m',21),('3m',63),('6m',126)]:f['mom_'+suffix]=p.shift(k)/p.shift(1)-1
 f['vol_1m']=r.shift(1).rolling(22).std(ddof=1)
 f['ret_5d']=p.shift(5)/p.shift(1)-1;f['excess_ret']=r-spyret
 # Price-scale-independent predictors, all available after the signal-day close.
 for k in [5,21,63,126]:f[f'trend_{k}']=p.shift(1)/p.shift(k)-1
 f['risk_21']=r.shift(1).rolling(21).std(ddof=1)
 f['excess_21']=(p.shift(1)/p.shift(21)-1)-(spy['Adj Close'].shift(1)/spy['Adj Close'].shift(21)-1)
 f['volume_relative']=d['Volume'].shift(1)/d['Volume'].shift(1).rolling(21).mean()-1
 f['day_excess']=r-spyret
 f['target']=p.shift(-20)/p.shift(-1)-1
 f['label_end']=pd.Series(d.index,index=d.index).shift(-20)
 f['symbol']=ticker;f.index.name='date';parts.append(f.reset_index())
df=pd.concat(parts,ignore_index=True).replace([np.inf,-np.inf],np.nan).dropna().sort_values(['date','symbol']).reset_index(drop=True)
original=['open','high','low','close','volume','adjusted','return','spy_ret','mom_1m','mom_3m','mom_6m','vol_1m','ret_5d','excess_ret']
improved=['trend_5','trend_21','trend_63','trend_126','risk_21','excess_21','volume_relative','day_excess']
# Rank signals across the stocks observable on that date, never across time.
for col in improved:df[col+'_rank']=df.groupby('date')[col].rank(pct=True)
improved=[col+'_rank' for col in improved]
fit=df[(df.date<C['validation_start'])&(df.label_end<C['validation_start'])]
valid=df[(df.date>=C['validation_start'])&(df.date<C['test_start'])&(df.label_end<C['test_start'])]
train=df[(df.date<C['test_start'])&(df.label_end<C['test_start'])]
test=df[(df.date>=C['test_start'])&(df.date<C['test_signal_end_exclusive'])]
assert fit.label_end.max()<valid.date.min();assert train.label_end.max()<test.date.min()
assert len(fit)>1000 and len(valid)>1000 and len(test)>1000
print('Rows: fit',len(fit),'validation',len(valid),'refit',len(train),'test',len(test),flush=True)
def model(params):return xgb.XGBRegressor(objective='reg:squarederror',random_state=SEED,n_jobs=2,tree_method='hist',**params)
search=[]
for depth,trees,lam in itertools.product(C['candidate_depths'],C['candidate_trees'],C['candidate_lambdas']):
 pars={**C['improved_fixed'],'max_depth':depth,'n_estimators':trees,'reg_lambda':lam}
 m=model(pars);m.fit(fit[improved],fit.target)
 rmse=float(np.sqrt(mean_squared_error(valid.target,m.predict(valid[improved]))))
 search.append({'rmse':rmse,'params':pars});print('Validation',depth,trees,lam,round(rmse,5),flush=True)
search.sort(key=lambda d:(d['rmse'],d['params']['n_estimators'],d['params']['max_depth']))
selected=search[0]['params'];(OUT/'validation_search.json').write_text(json.dumps(search,indent=2))
# Teaching diagnostic: successive corrections using class settings, trained only
# on 2022. The validation curve uses 2023; no 2024-2025 labels enter this figure.
teaching=model(C['original']);teaching.fit(fit[original],fit.target)
curve=[]
for trees in [0,1,5,10,20,40,60,100,150,200,250,300]:
 for name,frame in [('2022 training',fit),('2023 validation',valid)]:
  yhat=np.full(len(frame),fit.target.mean()) if trees==0 else teaching.predict(frame[original],iteration_range=(0,trees))
  curve.append({'trees':trees,'sample':name,'rmse':float(np.sqrt(mean_squared_error(frame.target,yhat)))})
pd.DataFrame(curve).to_csv(OUT/'boosting_learning_curve.csv',index=False)
# This is the first use of the held-out test labels. Settings are now frozen.
pred=test[['date','symbol','label_end','target']].copy();models={}
for name,cols,pars in [('Class model',original,C['original']),('Revised model',improved,selected)]:
 m=model(pars);m.fit(train[cols],train.target);pred[name]=m.predict(test[cols]);models[name]=m;m.save_model(OUT/(name.replace(' ','_').lower()+'.json'))
pred['Historical mean']=float(train.target.mean());pred.to_csv(OUT/'test_predictions.csv',index=False)
metrics=[]
for name in ['Class model','Revised model','Historical mean']:
 error=pred[name]-pred.target
 daily_ic=pred.groupby('date').apply(lambda g:g[name].rank().corr(g.target.rank()) if g[name].nunique()>1 else np.nan)
 metrics.append({'model':name,'rmse':float(np.sqrt(np.mean(error**2))),'mae':float(np.mean(np.abs(error))),'r2_vs_mean':float(1-np.sum(error**2)/np.sum((pred.target-pred['Historical mean'])**2)),'mean_rank_correlation':float(daily_ic.mean()) if daily_ic.notna().any() else None,'observations':len(pred)})
pd.DataFrame(metrics).to_csv(OUT/'prediction_metrics.csv',index=False)
# Monthly portfolios: both models get identical dates, execution lag and allocation.
calendar=spy.index
signals=pd.Series(calendar,index=calendar).groupby(calendar.to_period('M')).first()
signals=signals[(signals>=C['test_start'])&(signals<'2026-02-01')]
entries={s:calendar[calendar.get_loc(s)+1] for s in signals}
stock_prices=pd.DataFrame({t:read(t)['Adj Close'] for t in manifest['requested_stocks']})
periods=[];holdings=[]
for i,signal in enumerate(signals.iloc[:-1]):
 if signal>=pd.Timestamp(C['test_signal_end_exclusive']):continue
 entry=entries[signal];exit=entries[signals.iloc[i+1]];g=pred[pred.date==signal].set_index('symbol')
 assert len(g)>=10
 for name in ['Class model','Revised model','Equal-weight universe','SPY buy-and-hold']:
  if name=='SPY buy-and-hold':w=pd.Series({'SPY':1.});ret=pd.Series({'SPY':float(spy.loc[exit,'Adj Close']/spy.loc[entry,'Adj Close']-1)})
  else:
   chosen=g.sort_values([name],ascending=False).head(10).index if name in models else g.index
   w=pd.Series(1/len(chosen),index=chosen);ret=stock_prices.loc[exit,chosen]/stock_prices.loc[entry,chosen]-1
   assert ret.notna().all()
  gross=float(w.dot(ret));periods.append({'model':name,'signal':signal,'entry':entry,'exit':exit,'gross_return':gross,'weights':w,'asset_returns':ret})
  for sym,weight in w.items():holdings.append({'model':name,'signal':signal,'entry':entry,'exit':exit,'symbol':sym,'weight':weight,'return':ret[sym]})
pd.DataFrame(holdings).to_csv(OUT/'holdings.csv',index=False)
rows=[]
for name in ['Class model','Revised model','Equal-weight universe','SPY buy-and-hold']:
 history=[d for d in periods if d['model']==name];drift=pd.Series(dtype=float)
 for i,d in enumerate(history):
  w=d['weights'];union=w.index.union(drift.index);traded=float((w.reindex(union,fill_value=0)-drift.reindex(union,fill_value=0)).abs().sum())
  # At the final exit, close all remaining positions; charge that liquidation too.
  sell=1. if i==len(history)-1 else 0.
  row={k:v for k,v in d.items() if k not in ['weights','asset_returns']};row['dollars_traded']=traded+sell
  for bps in C['cost_bps_per_dollar_traded']:
   row[f'net_{bps}bps']=(1-traded*bps/10000)*(1+d['gross_return'])*(1-sell*bps/10000)-1
  rows.append(row);drift=w*(1+d['asset_returns'])/(1+d['gross_return'])
port=pd.DataFrame(rows).sort_values(['model','entry']);port.to_csv(OUT/'portfolio_returns.csv',index=False)
performance=[]
for name,g in port.groupby('model',sort=False):
 assert len(g)==24
 for bps in C['cost_bps_per_dollar_traded']:
  r=g[f'net_{bps}bps'].to_numpy();wealth=np.cumprod(1+r);years=(g.exit.max()-g.entry.min()).days/365.25
  draw=wealth/np.maximum.accumulate(np.r_[1,wealth])[1:]-1
  performance.append({'model':name,'cost_bps':bps,'total_return':float(wealth[-1]-1),'cagr':float(wealth[-1]**(1/years)-1),'annual_volatility':float(np.std(r,ddof=1)*np.sqrt(12)),'sharpe_zero_rf':float(np.mean(r)/np.std(r,ddof=1)*np.sqrt(12)),'max_drawdown_monthly':float(draw.min()),'end_1000':float(1000*wealth[-1]),'mean_monthly_dollars_traded':float(g.dollars_traded.mean())})
pd.DataFrame(performance).to_csv(OUT/'investment_metrics.csv',index=False)
split={name:{'rows':len(d),'signal_start':str(d.date.min().date()),'signal_end':str(d.date.max().date()),'last_label_end':str(d.label_end.max().date())} for name,d in [('fit',fit),('validation',valid),('refit',train),('test',test)]}
summary={'selected_params':selected,'universe_stocks':len(manifest['requested_stocks']),'common_test_stocks':int(test.symbol.nunique()),'split':split,'portfolio_start':str(port.entry.min().date()),'portfolio_end':str(port.exit.max().date()),'prediction_metrics':metrics,'investment_metrics':performance,'limitations':['Fixed class stock list introduces survivor/selection bias; not a point-in-time universe.','Prices are a retrospectively adjusted Yahoo snapshot; not a point-in-time vendor archive.','Only 24 out-of-sample monthly holdings; no significance or durable alpha claim.','Trading costs are illustrative 0/10/25 basis points per dollar bought or sold, not estimated actual costs.','Class settings are ported to Python XGBoost; library differences mean no bit-for-bit R replication.','Forecasts target the class 19-session next-close-to-t+20 return; monthly holdings have variable lengths and do not equal those forecast labels.']}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2));(OUT/'environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'xgboost':xgb.__version__},indent=2))
print(json.dumps(summary,indent=2),flush=True)
