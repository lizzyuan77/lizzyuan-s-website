"""Independent checks of saved forecasts, split dates and portfolio bookkeeping."""
from pathlib import Path
import json
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results'
s=json.loads((R/'summary.json').read_text())
assert s['split']['fit']['last_label_end']<s['split']['validation']['signal_start']
assert s['split']['refit']['last_label_end']<s['split']['test']['signal_start']
pred=pd.read_csv(R/'test_predictions.csv');metrics=pd.read_csv(R/'prediction_metrics.csv')
assert pred[['date','symbol']].duplicated().sum()==0
for _,r in metrics.iterrows():assert np.isclose(np.sqrt(np.mean((pred[r.model]-pred.target)**2)),r.rmse)
h=pd.read_csv(R/'holdings.csv');p=pd.read_csv(R/'portfolio_returns.csv')
for (name,entry),g in h.groupby(['model','entry']):
 row=p[(p.model==name)&(p.entry==entry)].iloc[0]
 assert np.isclose(g.weight.sum(),1)
 assert np.isclose((g.weight*g['return']).sum(),row.gross_return)
 assert row.signal<entry<row.exit
 if name in ['Class model','Revised model']:assert len(g)==10 and np.allclose(g.weight,.1)
for name,g in p.groupby('model'):
 g=g.sort_values('entry');assert len(g)==24
 assert (g.exit.iloc[:-1].to_numpy()==g.entry.iloc[1:].to_numpy()).all()
 assert np.all(g.net_25bps<=g.net_10bps+1e-12) and np.all(g.net_10bps<=g.net_0bps+1e-12)
 first=g.iloc[0];last=g.iloc[-1]
 assert np.isclose(first.dollars_traded,1)
 assert np.isclose(first.net_10bps,(1-.001)*(1+first.gross_return)-1)
 entry_turnover=last.dollars_traded-1
 assert np.isclose(last.net_10bps,(1-entry_turnover*.001)*(1+last.gross_return)*.999-1)
 gmetrics=pd.read_csv(R/'investment_metrics.csv');r=gmetrics[(gmetrics.model==name)&(gmetrics.cost_bps==10)].iloc[0]
 assert np.isclose(r.annual_volatility,g.net_10bps.std(ddof=1)*np.sqrt(12))
 assert np.isclose(r.end_1000,1000*np.prod(1+g.net_10bps))
print('PASS: split purging, predictions, weights, shared dates, cost accounting and annualization.')

curve=pd.read_csv(R/'boosting_learning_curve.csv')
assert set(curve['sample'])=={'2022 training','2023 validation'}
assert set(curve.trees)=={0,1,5,10,20,40,60,100,150,200,250,300}
assert curve.rmse.notna().all() and (curve.rmse>0).all()
print('PASS: course learning curve contains only training and validation diagnostics.')
