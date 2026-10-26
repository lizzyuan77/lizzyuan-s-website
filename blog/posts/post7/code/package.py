"""Package publishable files; never include the 575 MB microdata archive."""
from pathlib import Path
import zipfile
root=Path(__file__).resolve().parents[1]
allowed={'code':{'.py','.html','.txt'},'data':{'.json'},'results':{'.json','.csv','.html'},'vendor':{'.js'}}
with zipfile.ZipFile(root/'research.zip','w',compression=zipfile.ZIP_DEFLATED) as z:
 for n in ['index.qmd','README.md']:z.write(root/n,Path('post7')/n)
 for folder,suffixes in allowed.items():
  for p in sorted((root/folder).iterdir()):
   if p.is_file() and p.suffix in suffixes:z.write(p,Path('post7')/p.relative_to(root))
print('Research package created.')
