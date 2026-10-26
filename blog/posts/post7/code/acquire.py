"""Download the official 2024 national ACS person archive (about 575 MB)."""
import argparse,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--cache',required=True);a=p.parse_args()
cache=Path(a.cache).expanduser();cache.mkdir(parents=True,exist_ok=True)
u='https://www2.census.gov/programs-surveys/acs/data/pums/2024/1-Year/csv_pus.zip'
target=cache/'csv_pus.zip'
if not target.exists():urllib.request.urlretrieve(u,target)
root=Path(__file__).resolve().parents[1]
urllib.request.urlretrieve('https://api.census.gov/data/2024/acs/acs1/pums/variables/FOD1P.json',root/'data/FOD1P.json')
urllib.request.urlretrieve('https://api.census.gov/data/2024/acs/acs1/pums/variables/OCCP.json',root/'data/OCCP.json')
print('Source archive:',target)
