"""Build research.zip from an explicit allowlist. Run from the post6 folder.

Only code, aggregate results and documentation are packaged. PSID microdata
(data/) are never included: PSID's conditions of use do not allow
redistribution.
"""
from pathlib import Path
import zipfile

ROOT = Path(".")
FILES = ["README.md", "index.qmd", "post.css"]
FOLDERS = {"code": {".py", ".sql", ".txt"},
           "results": {".csv", ".png", ".txt", ".yml", ".md"}}

with zipfile.ZipFile("research.zip", "w", compression=zipfile.ZIP_DEFLATED) as out:
    for name in FILES:
        out.write(ROOT / name, Path("post6") / name)
    for folder, suffixes in FOLDERS.items():
        for p in sorted((ROOT / folder).glob("*")):
            if p.is_file() and p.suffix in suffixes:
                out.write(p, Path("post6") / p)
    names = out.namelist()

assert not any(n.startswith("post6/data") for n in names), "microdata must not be packaged"
print(f"research.zip created with {len(names)} files")
