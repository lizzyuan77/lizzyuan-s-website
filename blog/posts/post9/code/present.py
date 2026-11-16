"""Generate the article figures, compact tables, metadata and replication ZIP."""
from pathlib import Path
import json,zipfile,runpy
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
runpy.run_path(str(ROOT/'code/illustrate_boosting.py'))
s=json.loads((OUT/'summary.json').read_text());pm=pd.read_csv(OUT/'prediction_metrics.csv');im=pd.read_csv(OUT/'investment_metrics.csv');pr=pd.read_csv(OUT/'portfolio_returns.csv',parse_dates=['entry','exit'])
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#42392f','text.color':'#42392f','xtick.color':'#42392f','ytick.color':'#42392f','figure.facecolor':'#fffcf5','axes.facecolor':'#fffcf5','savefig.facecolor':'#fffcf5'})
colors={'Class model':'#936044','Revised model':'#526f61','Historical mean':'#a49476','Equal-weight universe':'#af8662','SPY buy-and-hold':'#605b7b'}
curve=pd.read_csv(OUT/'boosting_learning_curve.csv')
fig,ax=plt.subplots(figsize=(8.4,3.7))
for label,color in [('2022 training','#936044'),('2023 validation','#526f61')]:
 g=curve[curve['sample']==label]
 ax.plot(g.trees,100*g.rmse,label=label,color=color,linewidth=2.4,marker='o',markersize=4)
ax.set_xlabel('Trees added in sequence (0 = start with the training average)')
ax.set_ylabel('Forecast error (percentage points)')
ax.set_title('More corrections help the training fit. Do they help new data?',loc='left',fontweight='bold',fontsize=12,pad=15)
ax.grid(alpha=.17);ax.legend(frameon=False);ax.set_ylim(bottom=0)
fig.text(.02,.01,'Class settings; fit on 2022, checked on 2023. The final 2024–2025 test is not used here.',fontsize=9,color='#6f6558')
fig.tight_layout(rect=[0,.07,1,1]);fig.savefig(OUT/'boosting-steps.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(8.4,4.5))
for name in ['Class model','Revised model','Equal-weight universe','SPY buy-and-hold']:
 g=pr[pr.model==name];x=[g.entry.iloc[0],*g.exit];y=np.r_[1000,1000*np.cumprod(1+g.net_10bps)]
 ax.plot(x,y,label=name,color=colors[name],linewidth=2.3 if name!='Equal-weight universe' else 1.8,linestyle='--' if name=='Equal-weight universe' else '-')
ax.set_ylabel('Value of $1,000');ax.set_title('Higher ending wealth came with a bumpier ride',loc='left',fontweight='bold',pad=14);ax.grid(alpha=.18);ax.legend(frameon=False,ncols=2,fontsize=9,loc='upper left');ax.set_ylim(900,2100)
import matplotlib.dates as mdates
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6));ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
fig.text(.02,.01,'Monthly values, Jan 3, 2024–Jan 5, 2026. Costs: 0.10% of every dollar bought or sold.',fontsize=9,color='#6f6558');fig.tight_layout(rect=[0,.06,1,1]);fig.savefig(OUT/'wealth.png',dpi=180);plt.close(fig)
net=im[im.cost_bps==10].set_index('model');p=pm.set_index('model');vals={'class_rmse':f'{100*p.loc["Class model","rmse"]:.2f}','revised_rmse':f'{100*p.loc["Revised model","rmse"]:.2f}','mean_rmse':f'{100*p.loc["Historical mean","rmse"]:.2f}','rmse_reduction':f'{100*(1-p.loc["Revised model","rmse"]/p.loc["Class model","rmse"]):.1f}','mean_improvement':f'{100*(1-p.loc["Revised model","rmse"]/p.loc["Historical mean","rmse"]):.2f}','revised_end':f'{net.loc["Revised model","end_1000"]:,.0f}','class_end':f'{net.loc["Class model","end_1000"]:,.0f}','spy_end':f'{net.loc["SPY buy-and-hold","end_1000"]:,.0f}','revised_vol':f'{100*net.loc["Revised model","annual_volatility"]:.1f}','spy_vol':f'{100*net.loc["SPY buy-and-hold","annual_volatility"]:.1f}','revised_high_cost_end':f'{im[(im.model=="Revised model")&(im.cost_bps==25)].end_1000.iloc[0]:,.0f}'}
# Group history is a separate user-provided portfolio, not a model backtest.
group=pd.read_csv(ROOT/'data/group_history_indexed.csv',parse_dates=['date']).sort_values('date')
v=group.account_index;draw=v/v.cummax()-1
vals.update(group_loss=f'{100*(1-v.iloc[-1]/v.iloc[0]):.1f}',group_drawdown=f'{-100*draw.min():.1f}')
(OUT/'group_summary.json').write_text(json.dumps({'observations':len(group),'start':str(group.date.iloc[0].date()),'end':str(group.date.iloc[-1].date()),'change':float(v.iloc[-1]/v.iloc[0]-1),'maximum_observed_drawdown':float(draw.min()),'model_link':'Separate from XGBoost; not pooled with the 2024-2025 backtest.'},indent=2))
(OUT/'text_values.json').write_text(json.dumps(vals,indent=2))
lines=['| Strategy | Ending $1,000 | Annualized volatility |','|---|---:|---:|']
for name in ['Class model','Revised model','Equal-weight universe','SPY buy-and-hold']:
 r=net.loc[name];lines.append(rf'| {name} | \${r.end_1000:,.0f} | {100*r.annual_volatility:.1f}% |')
(OUT/'investment_table.qmd').write_text('\n'.join(lines)+'\n')
with zipfile.ZipFile(ROOT/'research.zip','w',zipfile.ZIP_DEFLATED) as z:
 for folder in ['code','data','results','includes']:
  for f in sorted((ROOT/folder).glob('*')):
   if f.is_file() and f.suffix in ['.py','.R','.json','.csv','.png','.qmd','.txt']:z.write(f,f.relative_to(ROOT))
 for name in ['index.qmd','README.md','post.css','.gitignore']:
  if (ROOT/name).exists():z.write(ROOT/name,name)
print('Figures, metadata, table and research.zip generated.')
