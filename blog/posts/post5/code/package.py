"""Run after analysis/maps to build the downloadable replication archive."""
from pathlib import Path
import zipfile
root=Path('.')
with zipfile.ZipFile('research.zip','w',compression=zipfile.ZIP_DEFLATED) as out:
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.name!='research.zip' and not any(x.startswith('.') or x=='__pycache__' for x in p.parts) and p.suffix not in ['.html','.pyc']:
            out.write(p,Path('post5')/p)
print('research.zip created')
