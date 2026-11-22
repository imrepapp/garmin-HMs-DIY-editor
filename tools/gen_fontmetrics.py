#!/usr/bin/env python3
"""Builds the character-width table (METRICS in index.html) from the Connect IQ SDK fonts.

Usage: python3 tools/gen_fontmetrics.py SDK_DIR [--write]

SDK_DIR holds Devices/<id>/simulator.json and Fonts/*.cft, as in a Connect IQ SDK installation
(ConnectIQ). Only numbers are taken from the fonts: line height, ascent and the advance width of
each character. No glyph images are read or stored.

.cft layout (big-endian), as far as this tool needs it:
  0x04 u32 file size, 0x08 u32 offset of the character map, 0x0c u32 offset of the glyph table,
  0x10 u32 offset of the glyph data, 0x16 u16 line height, 0x18 u16 ascent.
  Character map: 12 bytes, then u32 range count, then [first code, last code, first glyph index].
  Glyph table: one u32 per glyph = data offset << 16 | flag << 15 | advance width.

Output: {"fonts": [[height, ascent, hex], ...], "dev": {device: [font index or -1] * 9}}
with the nine fonts in the order XTINY TINY SMALL MEDIUM LARGE NR_MILD NR_MEDIUM NR_HOT NR_THAI_HOT;
hex holds two digits per character for the codes in CHARS (00 = the font lacks the character).
"""
import json, re, struct, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gen_fields import ALIAS, norm, ROOT

NAMES = ['xtiny', 'tiny', 'small', 'medium', 'large', 'numberMild', 'numberMedium', 'numberHot', 'numberThaiHot']
CHARS = list(range(32, 127)) + [176]          # ASCII and the degree sign

def read_cft(path):
    b = path.read_bytes()
    size, o_map, o_gl, o_data = struct.unpack('>IIII', b[4:20])
    if size != len(b): raise ValueError('unexpected size field')
    height, ascent = struct.unpack('>HH', b[0x16:0x1a])
    n, = struct.unpack('>I', b[o_map + 12:o_map + 16])
    if o_map + 16 + n * 12 != o_gl: raise ValueError('unexpected character map')
    count = (o_data - o_gl) // 4
    glyph = struct.unpack('>%dI' % count, b[o_gl:o_gl + count * 4])
    width = {}
    for i in range(n):
        first, last, g = struct.unpack('>III', b[o_map + 16 + i * 12:o_map + 28 + i * 12])
        for c in range(first, last + 1):
            if g + c - first < count: width[c] = glyph[g + c - first] & 0x7fff
    return height, ascent, width

def main():
    sdk = pathlib.Path(sys.argv[1]); write = '--write' in sys.argv
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    ours = json.loads(re.search(r'const DEV = /\*DATA\*/(\{.*?\})/\*END\*/', html, re.S).group(1))
    ids = {norm(p.name): p.name for p in (sdk / 'Devices').iterdir() if (p / 'simulator.json').exists()}
    fonts, index, table, missing, bad = [], {}, {}, set(), set()
    for name in ours:
        did = ALIAS.get(name) or ids.get(norm(name))
        if not did or not (sdk / 'Devices' / did / 'simulator.json').exists(): continue
        sim = json.loads((sdk / 'Devices' / did / 'simulator.json').read_text(encoding='utf-8'))
        ww = next((s for s in sim.get('fonts', []) if s.get('fontSet') == 'ww'), None)
        if not ww: continue
        files = {f['name']: f['filename'] for f in ww['fonts']}
        row = []
        for n in NAMES:
            fn = files.get(n); path = sdk / 'Fonts' / (str(fn) + '.cft')
            if fn and fn not in index and fn not in missing and fn not in bad:
                if not path.exists(): missing.add(fn)
                else:
                    try:
                        h, a, w = read_cft(path)
                        index[fn] = len(fonts); fonts.append([h, a, ''.join('%02x' % min(w.get(c, 0), 255) for c in CHARS)])
                    except Exception as e:
                        bad.add(fn); print('cannot read', fn, e)
            row.append(index.get(fn, -1))
        if any(i >= 0 for i in row): table[name] = row
    data = json.dumps({'fonts': fonts, 'dev': table}, separators=(',', ':'), ensure_ascii=False)
    print(f'{len(table)} of {len(ours)} devices, {len(fonts)} fonts, {len(data)} bytes; {len(missing)} font files not found, {len(bad)} unreadable')
    if write:
        new, k = re.subn(r'/\*METRICS\*/.*?/\*ENDMETRICS\*/', lambda m: '/*METRICS*/' + data + '/*ENDMETRICS*/', html, flags=re.S)
        assert k == 1, 'METRICS marker not found in index.html'
        (ROOT / 'index.html').write_text(new, encoding='utf-8'); print('index.html updated')

if __name__ == '__main__':
    main()
