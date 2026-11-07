"""Run the unchanged upstream profile helper in an explicit account scope."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--data-dir', required=True)
    p.add_argument('--platform', choices=['meta', 'google', 'tiktok'], required=True)
    p.add_argument('--account-id', required=True)
    p.add_argument('args', nargs=argparse.REMAINDER)
    a = p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,100}', a.account_id):
        p.error('ID de cuenta inválido')
    if not a.args or a.args[0] not in {'init', 'get', 'set', 'save-audit', 'compare'}:
        p.error('Comando no admitido; reset destructivo no expuesto')
    if a.args[0] == 'compare' and a.args[1:] != [a.platform]:
        p.error('La comparación debe coincidir con la plataforma')
    if a.args[0] == 'save-audit':
        if len(a.args) != 2: p.error('Se requiere archivo de auditoría')
        data = json.loads(Path(a.args[1]).read_text(encoding='utf-8-sig'))
        if data.get('account_id') != a.account_id or data.get('platform') != a.platform:
            p.error('La auditoría pertenece a otra cuenta o no incluye su ID')
    base = Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location('mister_ads_upstream_profile', base/'engine/scripts/profile.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    root = Path(a.data_dir).expanduser().resolve()/'engine-profiles'/f'{a.platform}-{a.account_id}'
    module.ROOT = root; module.PROFILE = root/'profile.json'; module.HISTORY = root/'history'; module.INDEX = module.HISTORY/'index.json'
    return module.main(a.args)

if __name__ == '__main__': sys.exit(main())
