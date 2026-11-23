#!/usr/bin/env python3
"""Adds the devices of a Connect IQ SDK that the HMs DIY Designer's fonts.txt does not list.

Usage: python3 tools/gen_sdk_devices.py SDK_DIR [--write]

Run after gen_devices.py and before gen_fields.py / gen_fontmetrics.py. Every SDK device that has data
field layouts and is not already in the DEV table of index.html is appended as
  name: [width, height, round, {FONT: [family, size, 0, 0, 0, 0]}, 1]
(the trailing 1 marks "known from the SDK only"). Bitmap fonts (.cft) take their size from the line
height, vector fonts (ttf) from their point size and the screen's ppi. tools/sdk_devices.json records
which SDK folder each added name comes from, for the other generators.
"""
import json, re, struct, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gen_fields import ALIAS, norm, ROOT

FONTS = [('XTINY', 'xtiny'), ('TINY', 'tiny'), ('SMALL', 'small'), ('MEDIUM', 'medium'), ('LARGE', 'large'),
         ('NR_MILD', 'numberMild'), ('NR_MEDIUM', 'numberMedium'), ('NR_HOT', 'numberHot'), ('NR_THAI_HOT', 'numberThaiHot')]

def family(fn, number):
    """Index into FAM in index.html."""
    u = fn.upper()
    if 'DEJAVUSANS_CD' in u or 'DEJAVUGARMIN' in u: return 11
    if 'ROBOTOCONDENSED' in u or 'ROBOTO_CONDENSED' in u: return 0 if 'BOLD' in u else 1
    if 'BIONIC' in u or 'BEBAS' in u or 'STEELFISH' in u or 'OSWALD' in u or 'DIGI' in u: return 2
    if 'ROBOTO' in u or 'YANTRAMANAV' in u: return 10 if ('BOLD' in u or 'BLACK' in u or number) else 9
    if 'DEJAVU' in u: return 4 if (number or 'BOLD' in u) else 3
    return 2 if number else 1

def clean(name):
    name = name.replace('®', '').replace('™', '').replace('ē', 'e').replace('–', '-')
    return re.sub(r'\s+', ' ', name).strip()

def main():
    sdk = pathlib.Path(sys.argv[1]); write = '--write' in sys.argv
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    dev = json.loads(re.search(r'const DEV = /\*DATA\*/(\{.*?\})/\*END\*/', html, re.S).group(1))
    dev = {k: v for k, v in dev.items() if len(v) < 5}            # drop earlier SDK additions, they are rebuilt
    ids = {norm(p.name): p.name for p in (sdk / 'Devices').iterdir() if (p / 'simulator.json').exists()}
    used = {ALIAS.get(n) or ids.get(norm(n)) for n in dev}
    added = {}
    for did in sorted(ids.values()):
        if did in used: continue
        sim = json.loads((sdk / 'Devices' / did / 'simulator.json').read_text(encoding='utf-8'))
        comp = json.loads((sdk / 'Devices' / did / 'compiler.json').read_text(encoding='utf-8'))
        if not any('datafields' in l for l in sim.get('layouts', [])): continue
        ww = next((s for s in sim.get('fonts', []) if s.get('fontSet') == 'ww'), None)
        if not ww: continue
        files = {f['name']: f for f in ww['fonts']}
        loc = sim['display']['location']; ppi = sim.get('ppi') or 160; fonts = {}
        for key, nm in FONTS:
            f = files.get(nm)
            if not f: continue
            number = key.startswith('NR_'); size = None
            if f.get('type') == 'ttf' or 'size' in f: size = round(f['size'] * ppi / 72)
            else:
                p = sdk / 'Fonts' / (f['filename'] + '.cft')
                if p.exists():
                    h, = struct.unpack('>H', p.read_bytes()[0x16:0x18]); size = round(h * (1 if number else .853))
                else:
                    m = re.search(r'(\d+)\D*$', f['filename']); size = int(m.group(1)) if m else None
            if size: fonts[key] = [family(f['filename'], number), max(6, size), 0, 0, 0, 0]
        if len(fonts) < 5: continue
        name = clean(comp.get('displayName') or did)
        if name in dev: name += ' (' + did + ')'
        dev[name] = [loc['width'], loc['height'], 1 if sim['display'].get('shape') == 'round' else 0, fonts, 1]
        added[name] = did
    data = json.dumps(dev, ensure_ascii=False, separators=(',', ':'))
    print(f'{len(added)} devices added from the SDK, {len(dev)} in all')
    if write:
        new, k = re.subn(r'/\*DATA\*/.*?/\*END\*/', lambda m: '/*DATA*/' + data + '/*END*/', html, flags=re.S)
        assert k == 1
        (ROOT / 'index.html').write_text(new, encoding='utf-8')
        (ROOT / 'tools' / 'sdk_devices.json').write_text(json.dumps(added, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        print('index.html and tools/sdk_devices.json updated')

if __name__ == '__main__':
    main()
