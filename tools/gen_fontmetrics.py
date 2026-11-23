#!/usr/bin/env python3
"""Builds the character-width table (METRICS in index.html) from the Connect IQ SDK fonts.

Usage: python3 tools/gen_fontmetrics.py SDK_DIR [--write]

SDK_DIR holds Devices/<id>/simulator.json and Fonts/*.cft, as in a Connect IQ SDK installation
(ConnectIQ). Only numbers are taken from the fonts: line height, ascent and the advance width of
each character. No glyph images are read or stored.

.cft layout (big-endian), as far as this tool needs it:
  0x04 u32 size (the file size in newer files), 0x08 u32 offset of the character map, 0x0c u32 offset of the glyph table,
  0x10 u32 offset of the glyph data, 0x16 u16 line height, 0x18 u16 ascent.
  Character map: 12 bytes, then u32 range count, then [first code, last code, first glyph index].
  Glyph table: one u32 per glyph; the low byte is the advance width, the high bits locate the
  glyph data (their split differs between file versions, so only the low byte is used).

Vector fonts (.ttf) are read from their own tables (head, hhea, hmtx, cmap, glyf bounding boxes) and scaled to
the size a device uses: point size x ppi / 72. Their entries carry a fourth number, the glyph height in pixels.

Output: {"fonts": [[height, ascent, hex(, glyph height)], ...], "dev": {device: [font index or -1] * 9}}
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
    height, ascent = struct.unpack('>HH', b[0x16:0x1a])
    n, = struct.unpack('>I', b[o_map + 12:o_map + 16])
    if o_map + 16 + n * 12 != o_gl: raise ValueError('unexpected character map')
    count = (o_data - o_gl) // 4
    glyph = struct.unpack('>%dI' % count, b[o_gl:o_gl + count * 4])
    width = {}
    for i in range(n):
        first, last, g = struct.unpack('>III', b[o_map + 16 + i * 12:o_map + 28 + i * 12])
        for c in range(first, last + 1):
            if g + c - first < count: width[c] = glyph[g + c - first] & 0xff
    digits = [width[c] for c in range(48, 58) if c in width]
    if not width or max(width.values()) > 2.2 * height or (digits and max(digits) - min(digits) > max(2, 0.35 * max(digits))):
        raise ValueError('implausible widths')
    return height, ascent, width

def read_ttf(path):
    """Units per em, ascent, descent, {code: advance}, {code: glyph top} of a TrueType font (numbers only, no outlines kept)."""
    b = path.read_bytes(); n, = struct.unpack('>H', b[4:6]); tab = {}
    for i in range(n):
        tag, _, off, ln = struct.unpack('>4sIII', b[12 + i * 16:28 + i * 16]); tab[tag.decode()] = (off, ln)
    head = tab['head'][0]; upm, = struct.unpack('>H', b[head + 18:head + 20]); loca_long, = struct.unpack('>h', b[head + 50:head + 52])
    hhea = tab['hhea'][0]; asc, desc = struct.unpack('>hh', b[hhea + 4:hhea + 8]); nh, = struct.unpack('>H', b[hhea + 34:hhea + 36])
    hm = tab['hmtx'][0]; adv = [struct.unpack('>H', b[hm + i * 4:hm + i * 4 + 2])[0] for i in range(nh)]
    cm = tab['cmap'][0]; nsub, = struct.unpack('>H', b[cm + 2:cm + 4]); gid = {}
    subs = [struct.unpack('>HHI', b[cm + 4 + i * 8:cm + 12 + i * 8]) for i in range(nsub)]
    for plat, enc, off in sorted(subs, key=lambda s: (s[0] != 3, s[1] != 1)):          # prefer Windows Unicode BMP
        o = cm + off; fmt, = struct.unpack('>H', b[o:o + 2])
        if fmt == 4:
            segx2, = struct.unpack('>H', b[o + 6:o + 8]); seg = segx2 // 2
            ends = struct.unpack('>%dH' % seg, b[o + 14:o + 14 + segx2]); s0 = o + 16 + segx2
            starts = struct.unpack('>%dH' % seg, b[s0:s0 + segx2]); deltas = struct.unpack('>%dh' % seg, b[s0 + segx2:s0 + 2 * segx2])
            ro = s0 + 2 * segx2; ranges = struct.unpack('>%dH' % seg, b[ro:ro + segx2])
            for i in range(seg):
                for c in range(starts[i], min(ends[i], 0xfffe) + 1):
                    if c > 255: break
                    if ranges[i] == 0: g = (c + deltas[i]) & 0xffff
                    else:
                        q = ro + i * 2 + ranges[i] + (c - starts[i]) * 2; g, = struct.unpack('>H', b[q:q + 2])
                        if g: g = (g + deltas[i]) & 0xffff
                    if g: gid[c] = g
            break
    if not gid: raise ValueError('no usable character map')
    loca, glyf = tab['loca'][0], tab['glyf'][0]
    def top(g):
        if loca_long: a, z = struct.unpack('>II', b[loca + g * 4:loca + g * 4 + 8])
        else: a, z = [v * 2 for v in struct.unpack('>HH', b[loca + g * 2:loca + g * 2 + 4])]
        return struct.unpack('>h', b[glyf + a + 8:glyf + a + 10])[0] if z > a else 0
    width = {c: adv[min(g, nh - 1)] for c, g in gid.items()}
    return upm, asc, desc, width, {c: top(gid[c]) for c in (48, 72) if c in gid}

def main():
    sdk = pathlib.Path(sys.argv[1]); write = '--write' in sys.argv
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    ours = json.loads(re.search(r'const DEV = /\*DATA\*/(\{.*?\})/\*END\*/', html, re.S).group(1))
    ids = {norm(p.name): p.name for p in (sdk / 'Devices').iterdir() if (p / 'simulator.json').exists()}
    fonts, index, table, missing, bad, ttfs = [], {}, {}, set(), set(), {}
    for name in ours:
        did = ALIAS.get(name) or ids.get(norm(name))
        if not did or not (sdk / 'Devices' / did / 'simulator.json').exists(): continue
        sim = json.loads((sdk / 'Devices' / did / 'simulator.json').read_text(encoding='utf-8'))
        ww = next((s for s in sim.get('fonts', []) if s.get('fontSet') == 'ww'), None)
        if not ww: continue
        files = {f['name']: f for f in ww['fonts']}; ppi = sim.get('ppi') or 160
        row = []
        for n in NAMES:
            f = files.get(n); fn = f['filename'] if f else None
            ttf = sdk / 'Fonts' / (str(fn) + '.ttf')
            if f and 'size' in f and ttf.exists():
                # a vector font: its em size in pixels is the point size at the screen's ppi; widths, line and glyph heights follow from the font's own tables
                px = f['size'] * ppi / 72; key = '%s@%.2f' % (fn, px)
                if key not in index and key not in bad:
                    try:
                        if fn not in ttfs: ttfs[fn] = read_ttf(ttf)
                        upm, asc, desc, w, tops = ttfs[fn]; s = px / upm
                        glyph = tops.get(48 if n.startswith('number') else 72) or tops.get(48) or asc * .75
                        index[key] = len(fonts)
                        fonts.append([round((asc - desc) * s), round(asc * s), ''.join('%02x' % min(round(w.get(c, 0) * s), 255) for c in CHARS), round(glyph * s)])
                    except Exception as e:
                        bad.add(key); print('cannot read', fn, e)
                row.append(index.get(key, -1)); continue
            path = sdk / 'Fonts' / (str(fn) + '.cft')
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
    if missing: print('font files not found:', ', '.join(sorted(missing)))
    print('devices without metrics:', ', '.join(n for n in ours if n not in table))
    print(f'{len(table)} of {len(ours)} devices, {len(fonts)} fonts, {len(data)} bytes; {len(missing)} font files not found, {len(bad)} unreadable')
    if write:
        new, k = re.subn(r'/\*METRICS\*/.*?/\*ENDMETRICS\*/', lambda m: '/*METRICS*/' + data + '/*ENDMETRICS*/', html, flags=re.S)
        assert k == 1, 'METRICS marker not found in index.html'
        (ROOT / 'index.html').write_text(new, encoding='utf-8'); print('index.html updated')

if __name__ == '__main__':
    main()
