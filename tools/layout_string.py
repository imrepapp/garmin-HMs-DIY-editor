#!/usr/bin/env python3
"""Reference encoder for the HMs DIY layout string (generation "C", Designer 3.4.2).

Usage:  python3 tools/layout_string.py layout.xml            print the string
        python3 tools/layout_string.py --check DIR           verify *_config_string.txt files
                                                             against the XML next to them

The same algorithm is implemented in index.html (encodeLayout); this script exists to
cross-check it. Known-good pairs: the Edge 1040 layouts in pull request #2 of
https://github.com/hundsmiachn/Garmin_HMsDIY
"""
import glob, html, json, pathlib, re, sys

_T = json.load(open(pathlib.Path(__file__).with_name('types.json'), encoding='utf-8'))
VID = {v[0]: v[1] for _, lst in _T['values'] for v in lst}
GID = {g[0]: g[1] for g in _T['graphics']}
FONTS='XTINY TINY SMALL MEDIUM LARGE NR_MILD NR_MEDIUM NR_HOT NR_THAI_HOT S_XTINY S_TINY S_SMALL S_MEDIUM S_LARGE S_NR_MILD S_NR_MEDIUM S_NR_HOT S_NR_THAI_HOT'.split()
def w85(v):
    v&=0xffffffff; s=''
    for _ in range(5): s=chr(33+v%85)+s; v//=85
    return s.translate(str.maketrans('<>&#\\','wxyz{'))   # the five characters the Designer replaces
def I(a,k): 
    try: return int(a.get(k,'0'))
    except: return 0
B=lambda a,k: a.get(k)=='true'
def encode(els):
    out='C'
    for a in els:
        t=a['type']
        if t=='0':
            vid=VID[a['eletype']]; fixed=B(a,'fixedtext')
            txt='' if 0<vid<10 else a.get('text','')
            w1=0|((0 if fixed else vid)&255)<<3|(vid&255)<<11|(I(a,'nr_values')&0x1fff)<<19
            w2=int(a['color'],16)&0xffffff|(len(txt.encode('utf-16le'))//2&255)<<24
            w3=(I(a,'x')+50)&1023|((I(a,'y')+50)&1023)<<10|(FONTS.index(a['font'])&31)<<20|(I(a,'precision')&3)<<25|(I(a,'halignment')&3)<<27|B(a,'maxonly')<<30|B(a,'daynight')<<31
            out+=w85(w1)+w85(w2)+w85(w3)+w85(0)+txt
        elif t=='1':
            g=GID[a['eletype']]; x,y,x2,y2,r,st=[I(a,k) for k in('x','y','x2','y2','radius','stroke')]
            w1=1|(g&255)<<3|(VID[a['valuetype']]&255)<<11|(I(a,'nr_values')&0x1fff)<<19
            w2=int(a['color'],16)&0xffffff; w3=(x+50)&1023|((y+50)&1023)<<10; w4=0
            S=(st&255)<<24
            if g==0: w2|=S; w3|=((x2+50)&1023)<<20; w4=(y2+50)&1023
            elif g==1: w2|=S; w3|=(r&1023)<<20
            elif g==2: w3|=(r&1023)<<20
            elif g in(3,4,5,6):
                if g==3: w2|=S
                w3|=((x2-x)&1023)<<20; w4=(y2-y)&1023
            elif g in(7,8): w2|=S; w3|=(r&1023)<<20; w4=x2&1023|(y2&1023)<<10
            elif g in(9,10): w2|=S; w3|=(r&1023)<<20; w4=y2&1023
            elif 11<=g<=14: w2|=S; w3|=((x2-x)&1023)<<20; w4=(y2-y)&1023|(r&1023)<<10|B(a,'minval')<<20
            w3|=B(a,'maxonly')<<30|B(a,'daynight')<<31
            out+=w85(w1)+w85(w2)+w85(w3)+w85(w4)
        elif t=='2':
            rows=[]
            for i in range(10):
                k='%02d'%i
                if 'valDC'+k not in a: break
                rows.append((int(a['valDC'+k]),a['colDC'+k],B(a,'hideDC'+k),B(a,'blinkDC'+k)))
            if not rows: continue
            out+=w85(2|(int(a['replDC'],16)&0xffffff)<<3|(len(rows)&15)<<27)
            for i,(v,c,h,bl) in enumerate(rows):
                out+=w85(int(c,16)&0xffffff|(B(a,'invertcolor') and i==0)<<25|h<<26|bl<<27)
                out+=w85((-v)&0xfffff|0x100000 if v<0 else v&0xfffff)
    return out
def read_elements(path):
    b = open(path, 'rb').read()
    try: t = b.decode('utf-8-sig')
    except UnicodeDecodeError: t = b.decode('cp1252')
    return [{k: html.unescape(v) for k, v in re.findall(r'(\w+)="([^"]*)"', e)}
            for e in re.findall(r'<LayoutElement ([^>]*)/>', t)]

if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--check':
        bad = 0
        for f in sorted(glob.glob(sys.argv[2] + '/**/*config_string.txt', recursive=True)):
            want = open(f, encoding='utf-8').read().rstrip('\r\n')
            want = want.replace('\\', '{')   # strings made before the Designer replaced the backslash
            xml = glob.glob(f.rsplit('/', 1)[0] + '/*.xml')[0]
            ok = encode(read_elements(xml)) == want
            bad += not ok
            print('OK  ' if ok else 'DIFF', f)
        sys.exit(1 if bad else 0)
    print(encode(read_elements(sys.argv[1])))
