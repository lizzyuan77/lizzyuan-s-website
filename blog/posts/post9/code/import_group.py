"""Optional: normalize the user-provided HTML-as-XLS group history to start at 100."""
from pathlib import Path
from html.parser import HTMLParser
import argparse,json,hashlib
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
class Table(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=[];self.cell=None
 def handle_starttag(self,t,a):
  if t=='tr':self.row=[]
  if t in ['td','th']:self.cell=''
 def handle_data(self,d):
  if self.cell is not None:self.cell+=d
 def handle_endtag(self,t):
  if t in ['td','th'] and self.cell is not None:self.row.append(self.cell.strip());self.cell=None
  if t=='tr' and self.row:self.rows.append(self.row)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);args=parser.parse_args()
 raw=args.source.read_bytes();table=Table();table.feed(raw.decode('utf-8-sig'))
 df=pd.DataFrame(table.rows[1:],columns=table.rows[0]);date=pd.to_datetime(df.Date,format='%m/%d/%Y');value=df['Account Value'].str.replace('$','',regex=False).str.replace(',','',regex=False).astype(float)
 d=pd.DataFrame({'date':date,'account_index':value}).sort_values('date');assert d.date.is_unique
 d['account_index']=100*d.account_index/d.account_index.iloc[0];d.to_csv(ROOT/'data/group_history_indexed.csv',index=False)
 (ROOT/'data/group_source.json').write_text(json.dumps({'source':'User-provided group performance-history export, 2026-11-10','source_sha256':hashlib.sha256(raw).hexdigest(),'format':'HTML table supplied with .xls extension','normalization':'Account value divided by first observed value, times 100. Original balances are not required for replication.','user_confirmation':'Not based on XGBoost picks; no changes during the period. Analysis assumes no external deposits/withdrawals.','dates':'Preserved exactly as exported, including Saturday labels. No matched-market comparison or annualized return is inferred from this file.'},indent=2))
if __name__=='__main__':main()
