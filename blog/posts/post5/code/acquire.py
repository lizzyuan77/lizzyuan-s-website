"""Refresh public inputs from Census; run from post5. No API key required.
S2401 is retained from the original 2024 ACS API response downloaded for Blog 4.
To refresh S2401 use a Census API key outside source control; see README.
"""
from pathlib import Path
import urllib.request
import zipfile
import json
import tempfile
root=Path('data');root.mkdir(exist_ok=True)
base='https://www2.census.gov/programs-surveys/acs/summary_file/2024/table-based-SF/data/1YRData/'
for table in ['b20017','b19013']:
    name=f'acsdt1y2024-{table}.dat'
    urllib.request.urlretrieve(base+name,root/name)
    urllib.request.urlretrieve(f'https://api.census.gov/data/2024/acs/acs1/groups/{table.upper()}.json',root/f'{table.upper()}-metadata.json')
    assert (root/name).read_text().startswith('GEO_ID|')
    json.load(open(root/f'{table.upper()}-metadata.json'))
for table in ['b24010','b24020','b24022']:
    name=f'acsdt1y2024-{table}.dat'
    with tempfile.TemporaryDirectory() as temp:
        raw=Path(temp)/name
        urllib.request.urlretrieve(base+name,raw)
        lines=raw.read_text().splitlines()
        # Preserve original source lines; retain US and every state-level row.
        selected=[s for s in lines[1:] if s.startswith('0400000US') or s.startswith('0100000US|')]
        assert len(selected)==53 # US, 50 states, DC and Puerto Rico
        (root/f'acsdt1y2024-{table}-states.dat').write_text(lines[0]+'\n'+'\n'.join(selected)+'\n')
    urllib.request.urlretrieve(f'https://api.census.gov/data/2024/acs/acs1/groups/{table.upper()}.json',root/f'{table.upper()}-metadata.json')
b=root/'boundaries';b.mkdir(exist_ok=True)
name='cb_2024_us_state_20m.zip'
urllib.request.urlretrieve('https://www2.census.gov/geo/tiger/GENZ2024/shp/'+name,b/name)
with zipfile.ZipFile(b/name) as f:
    for member in f.namelist():
        if Path(member).name != member: raise ValueError('Unexpected archive path')
    f.extractall(b)
print('Public Census inputs refreshed. S2401 remains the included cached response.')
