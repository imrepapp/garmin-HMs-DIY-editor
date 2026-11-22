#!/usr/bin/env python3
"""Build the device and font table from the HMs DIY Designer's fonts.txt.

Usage:  python3 tools/gen_devices.py /path/to/fonts.txt
The result is written between the /*DATA*/ ... /*END*/ markers in index.html.
fonts.txt comes from https://github.com/hundsmiachn/Garmin_HMsDIY
"""
import json, re, sys, pathlib

# Screen sizes (width, height, round). fonts.txt does not contain them.
RES = [
    (r'^Edge 10[34]0', (282, 470, 0)), (r'^Edge 130', (230, 303, 0)),
    (r'^Edge (520|820)', (200, 265, 0)), (r'^Edge [58]30', (246, 322, 0)),
    (r'^Edge (Explore|1000)', (240, 400, 0)),
    (r'^(GPSMAP|Oregon|Rino)', (240, 400, 0)), (r'^Montana', (480, 800, 0)),
    (r'^(epix$|Forerunner 920XT|v.voactive$)', (205, 148, 0)), (r'^v.voactive HR', (148, 205, 0)),
    (r'^Forerunner (230|235|630|735xt)', (215, 180, 0)),
    (r'^Venu Sq 2', (320, 360, 0)), (r'^Venu Sq', (240, 240, 0)),
    (r'^Instinct 2S', (163, 156, 0)), (r'^(Instinct 2|Descent G1)', (176, 176, 0)),
    (r'^(epix Gen2|Venu 2$|Venu 2 plus|D2 Air X10|D2 Mach 1)', (416, 416, 1)),
    (r'^Venu 2S', (360, 360, 1)), (r'^(Venu|D2 Air)', (390, 390, 1)),
    (r'^(fenix 6X|fenix 7X|Enduro|Descent Mk2 /)', (280, 280, 1)),
    (r'^(fenix 6$|fenix 6 Pro|fenix 7$|Approach S62|v.voactive 4$|Darth Vader|First Avenger|Forerunner 255$|Forerunner 255 Music|Forerunner 955)', (260, 260, 1)),
    (r'^(fenix 3|fenix 5S$|fenix Chronos|D2 Bravo|v.voactive 4S|Captain Marvel|Rey|Forerunner 255s)', (218, 218, 1)),
    (r'^Forerunner (45|55)$', (208, 208, 1)),
    (r'', (240, 240, 1)),
]
FAM = ['ROBOTO_COND_BOLD', 'ROBOTO_COND_REG', 'BEBASNEUE_REG', 'DEJAVUSANS', 'DEJAVUSANS_BOLD',
       'DEJAVUSANS_COND', 'DEJAVUSANS_COND_BOLD', 'STEELFISH_REG', 'STEELFISH_BOLD']

def main(path):
    txt = pathlib.Path(path).read_text(encoding='cp1252')
    fnt, dev = {}, {}
    for line in txt.splitlines():
        line = line.split('//')[0].strip()
        m = re.match(r'^"([^"]+)"\s*-\s*"([A-Z_]+)"\s*==>\s*(\S+)', line)
        if m:
            name = m.group(1).strip(' -')
            dev.setdefault(name, {})[m.group(2)] = m.group(3)
            continue
        p = [x.strip() for x in line.split(';')]
        if len(p) >= 7 and p[0].startswith('FNT_') and not line.startswith('#'):
            fnt[p[0]] = [FAM.index(p[1].replace('IDR_FNT_', ''))] + [int(x) for x in p[2:7]]
    out = {}
    for name, fonts in dev.items():
        res = next(r for pat, r in RES if re.search(pat, name))
        out[name] = [res[0], res[1], res[2], {k: fnt[v] for k, v in fonts.items() if v in fnt}]
    return json.dumps(out, ensure_ascii=False, separators=(',', ':'))

if __name__ == '__main__':
    data = main(sys.argv[1])
    html = pathlib.Path(__file__).resolve().parent.parent / 'index.html'
    if html.exists():
        s = html.read_text(encoding='utf-8')
        s2 = re.sub(r'/\*DATA\*/.*?/\*END\*/', lambda m: '/*DATA*/' + data + '/*END*/', s, flags=re.S)
        html.write_text(s2, encoding='utf-8')
        print('index.html updated,', len(data), 'bytes')
    else:
        print(data)
