"""Run after analysis/maps to build the downloadable replication archive."""
from pathlib import Path
import zipfile
root=Path('.')
included_files={'README.md','METHODOLOGY.md','RUBRIC_REVIEW.md','index.qmd','post.css'}
included_directories={'code','data','results'}
with zipfile.ZipFile('research.zip','w',compression=zipfile.ZIP_DEFLATED) as out:
    for p in sorted(root.rglob('*')):
        selected=(len(p.parts)==1 and p.name in included_files) or p.parts[0] in included_directories
        if selected and p.is_file() and not any(x.startswith('.') or x=='__pycache__' for x in p.parts) and p.suffix not in ['.html','.pyc']:
            out.write(p,Path('post5')/p)
print('research.zip created')
