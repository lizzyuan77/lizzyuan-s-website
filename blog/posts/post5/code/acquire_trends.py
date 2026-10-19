"""Download five ACS 1-year cross sections; no API key is required.
Run from post5. Cache exact source strings for selected geographic rows/columns.
"""
import csv
import io
import json
import urllib.request
from pathlib import Path

YEARS = [2019, 2021, 2022, 2023, 2024]
CELLS = {
    'B20017': [3, 6],
    'B24010': [1, 2, 20, 153, 171],
    'B24022': [2, 8, 38, 44],
}
manifest = []
for year in YEARS:
    target = Path('data/trends') / str(year)
    target.mkdir(parents=True, exist_ok=True)
    base = (f'https://www2.census.gov/programs-surveys/acs/summary_file/{year}/prototype/1YRData/'
            if year == 2019 else
            f'https://www2.census.gov/programs-surveys/acs/summary_file/{year}/table-based-SF/data/1YRData/')
    for table, cells in CELLS.items():
        filename = f'acsdt1y{year}-{table.lower()}.dat'
        url = base + filename
        meta_url = f'https://api.census.gov/data/{year}/acs/acs1/groups/{table}.json'
        local_raw = (Path('data') / filename if table == 'B20017' else
                     Path('data') / f'acsdt1y{year}-{table.lower()}-states.dat')
        if year == 2024 and local_raw.exists():
            raw = local_raw.read_text()
        else:
            with urllib.request.urlopen(url, timeout=90) as response:
                raw = response.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(raw), delimiter='|')
        selected = [r for r in reader if r['GEO_ID'] == '0100000US' or r['GEO_ID'].startswith('0400000US')]
        assert len(selected) == 53, (year, table, len(selected))
        columns = ['GEO_ID'] + [f'{table}_{kind}{cell:03d}' for cell in cells for kind in ['E', 'M']]
        with open(target / f'{table}.csv', 'w', newline='') as out:
            writer = csv.DictWriter(out, fieldnames=columns, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(selected)
        with urllib.request.urlopen(meta_url, timeout=90) as response:
            metadata = json.load(response)
        variable_ids = [f'{table}_{cell:03d}{kind}' for cell in cells for kind in ['E', 'M']]
        keep = {k: metadata['variables'][k] for k in variable_ids}
        # Confirm semantic definitions, rather than trusting matching cell numbers.
        if table == 'B20017':
            for cell in [3, 6]:
                assert 'Worked full-time, year-round' in keep[f'{table}_{cell:03d}E']['label']
        if table in ['B24010', 'B24022']:
            tech_cells = [20, 171] if table == 'B24010' else [8, 44]
            for cell in tech_cells:
                assert 'Computer and mathematical occupations' in keep[f'{table}_{cell:03d}E']['label']
        if table == 'B24022':
            assert 'full-time, year-round' in keep[f'{table}_008E']['concept'].lower()
        (target / f'{table}-metadata.json').write_text(json.dumps({'source_url': meta_url, 'variables': keep}, indent=2))
        manifest.append({'year': year, 'table': table, 'data_url': url, 'metadata_url': meta_url,
                         'retained_rows': 53, 'retained_columns': columns, 'retrieved': '2026-10-19'})
    print(f'{year}: three tables cached; definitions and 53 geographic rows verified.')
Path('data/trends/source-manifest.json').write_text(json.dumps(manifest, indent=2))
