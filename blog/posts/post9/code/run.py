"""Rebuild analysis and figures using the included price snapshot."""
from pathlib import Path
import importlib.util,os,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
env=os.environ.copy()
env.setdefault("MPLCONFIGDIR",str(Path(tempfile.gettempdir())/"blog9-matplotlib"))
# macOS XGBoost wheels need OpenMP. Reuse the library bundled with sklearn,
# confined to these child processes; no system library installation is needed.
if sys.platform=='darwin':
 spec=importlib.util.find_spec('sklearn')
 folder=Path(spec.origin).parent/'.dylibs' if spec else None
 if folder and (folder/'libomp.dylib').exists():env['DYLD_LIBRARY_PATH']=str(folder)+(':'+env['DYLD_LIBRARY_PATH'] if env.get('DYLD_LIBRARY_PATH') else '')
for name in ['analyze.py','present.py']:
 subprocess.run([sys.executable,str(HERE/name)],env=env,check=True)
