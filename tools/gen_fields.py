#!/usr/bin/env python3
"""Builds the data-field layout table (FIELDS in index.html) from Connect IQ device files.

Usage: python3 tools/gen_fields.py DEVICES_DIR [--write]

DEVICES_DIR holds one folder per device id with a simulator.json, as in the Connect IQ SDK
(ConnectIQ/Devices). The table lists, for every device the editor knows, the data screen
layouts Garmin offers and the rectangle of each field: {device: index into sets},
sets = [[layout, ...]], layout = [name, [x, y, w, h, obscurity bits], ...]
(obscurity bits: 1 left, 2 top, 4 right, 8 bottom). --write replaces the table in index.html.
"""
import json, os, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ALIAS = {
    'Darth Vader': 'legacysagadarthvader', 'Rey': 'legacysagarey', 'Captain Marvel': 'legacyherocaptainmarvel',
    'First Avenger': 'legacyherofirstavenger', 'Descent Mk2 / Descent Mk2i': 'descentmk2', 'Edge 820 / Explore': 'edge820',
    'Edge 1000 / Explore': 'edge_1000', 'epix Gen2': 'epix2', 'fenix 3 / tactix Bravo / quatix 3': 'fenix3',
    'fenix 5 / quatix 5': 'fenix5', 'fenix 5X / tactix Charlie': 'fenix5x', 'fenix 6 Pro / 6 Sapphire': 'fenix6pro',
    'fenix 6S Pro / 6S Sapphire': 'fenix6spro', 'fenix 6X Pro / 6X Sapphire / 6X Pro Solar': 'fenix6xpro',
    'GPSMAP 66s / 66st': 'gpsmap66', 'GPSMAP 86s / 86sc / 86i / 86sci': 'gpsmap86', 'Montana 7 Series': 'montana7xx',
    'Oregon 7 Series': 'oregon7xx', 'Rino 7 Series': 'rino7xx', 'Venu Sq Music edition': 'venusqm',
    'Venu Sq 2 Music edition': 'venusq2m', 'Venu Mercedes-Benz Collection': 'venud',
    'vívoactive 3 Mercedes-Benz Collection': 'vivoactive3d', 'vívoactive 3 Music': 'vivoactive3m',
    'vívoactive 3 Music LTE': 'vivoactive3mlte', 'vívoactive HR': 'vivoactive_hr',
    'Instinct 2S / Solar / Dual Power': 'instinct2s', 'Descent G1 / G1 Solar': 'descentg1',
    'Edge 1040 / 1040 Solar': 'edge1040', 'Forerunner 955 / Solar': 'fr955',
    'Instinct 2 / Solar / Dual Power / dezl Edition': 'instinct2',
}
# devices added from the SDK by gen_sdk_devices.py: name -> SDK folder
_extra = ROOT / 'tools' / 'sdk_devices.json'
if _extra.exists(): ALIAS.update(json.loads(_extra.read_text(encoding='utf-8')))
OBS = {'left': 1, 'top': 2, 'right': 4, 'bottom': 8}

def norm(s):
    s = s.lower().replace('í', 'i').replace('forerunner', 'fr').replace(' music', 'm')
    return re.sub(r'[^a-z0-9]', '', s)

def main():
    src = pathlib.Path(sys.argv[1]); write = '--write' in sys.argv
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    ours = json.loads(re.search(r'const DEV = /\*DATA\*/(\{.*?\})/\*END\*/', html, re.S).group(1))
    ids = {norm(d): d for d in os.listdir(src) if (src / d / 'simulator.json').exists()}
    sets, index, table, missing = [], {}, {}, []
    for name, spec in ours.items():
        did = ALIAS.get(name) or ids.get(norm(name))
        if not did or not (src / did / 'simulator.json').exists():
            missing.append(name); continue
        sim = json.loads((src / did / 'simulator.json').read_text(encoding='utf-8'))
        loc = sim['display']['location']; w, h = loc['width'], loc['height']
        rnd = 0 if sim['display'].get('shape', '').startswith('rect') else 1
        if (w, h, rnd) != tuple(spec[:3]):
            print(f'SCREEN DIFFERS  {name}: editor {spec[:3]}  device file {[w, h, rnd]} ({did})')
        lay = next((l for l in sim.get('layouts', []) if 'datafields' in l), None)
        if not lay:
            missing.append(name); continue
        out = []
        for l in lay['datafields']['datafields']:
            fields = [[f['location']['x'], f['location']['y'], f['location']['width'], f['location']['height'],
                       sum(OBS.get(o, 0) for o in f.get('obscurity', []))] for f in l['fields']]
            out.append([l['name']] + fields)
        key = json.dumps(out, separators=(',', ':'))
        if key not in index:
            index[key] = len(sets); sets.append(out)
        table[name] = index[key]
    data = json.dumps({'dev': table, 'sets': sets}, separators=(',', ':'), ensure_ascii=False)
    print(f'{len(table)} of {len(ours)} devices, {len(sets)} distinct layout sets, {len(data)} bytes')
    if missing: print('no device file for:', ', '.join(missing))
    if write:
        new, n = re.subn(r'/\*FIELDS\*/.*?/\*ENDFIELDS\*/', lambda m: '/*FIELDS*/' + data + '/*ENDFIELDS*/', html, flags=re.S)
        assert n == 1, 'FIELDS marker not found in index.html'
        (ROOT / 'index.html').write_text(new, encoding='utf-8'); print('index.html updated')

if __name__ == '__main__':
    main()
