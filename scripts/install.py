"""Install the Codex edition without replacing existing skills. No network/dependencies."""
import argparse
import hashlib
from pathlib import Path
import shutil
import tempfile

def install(source, root):
    source=Path(source).resolve(); root=Path(root).expanduser().resolve()
    if not (source/'SKILL.md').is_file(): raise ValueError('Falta SKILL.md')
    target=root/'mister-ads'
    if target.exists(): raise ValueError('Ya existe mister-ads; revisar versión antes de sustituir')
    files=[p for p in source.rglob('*') if p.is_file()]
    if any(p.is_symlink() for p in source.rglob('*')): raise ValueError('No se admiten enlaces simbólicos')
    root.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.mister-ads-install-',dir=root) as temp:
        staged=Path(temp)/'mister-ads'; shutil.copytree(source,staged)
        for p in files:
            if hashlib.sha256(p.read_bytes()).digest()!=hashlib.sha256((staged/p.relative_to(source)).read_bytes()).digest(): raise ValueError('Integridad de copia fallida')
        staged.rename(target)
    return target

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--skills-dir',required=True)
    args=p.parse_args()
    print(install(Path(__file__).resolve().parents[1]/'codex/skills/mister-ads',args.skills_dir))
