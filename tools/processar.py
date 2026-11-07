# -*- coding: utf-8 -*-
"""Portfolio: grade 4:5 em P&B com o mesmo tom, enquadrada na tatuagem; original a cores para abrir. Uso: python tools/processar.py"""
import os, sys, json, cv2, numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
import dados
R = os.path.expanduser('~/Documents/PROJETOS LRGZ/Joana Coelho'); S = R + '/site'
os.makedirs(S + '/assets/img/p', exist_ok=True); os.makedirs(S + '/assets/img/o', exist_ok=True)
AJ = {}   # id: (fx, fy, zoom) ajustes manuais
try:
    from enquadre import AJ
except ImportError:
    pass


def foco(g):
    h, w = g.shape
    e = 720 / max(h, w); s = cv2.resize(g, None, fx=e, fy=e, interpolation=cv2.INTER_AREA).astype(np.float32)
    d = np.clip(cv2.GaussianBlur(s, (0, 0), 16) - s, 0, 60)
    d[d < 12] = 0
    ys, xs = np.mgrid[0:d.shape[0], 0:d.shape[1]]
    wt = d ** 1.5 * (.25 + np.exp(-(((xs / d.shape[1] - .5) / .34) ** 2 + ((ys / d.shape[0] - .5) / .4) ** 2)))
    tot = wt.sum() + 1e-6
    return (wt * xs).sum() / tot / d.shape[1], (wt * ys).sum() / tot / d.shape[0]


def faz(p):
    arq, cat, leg = p
    f = f'{R}/_ref/ig/{arq:03d}_0.jpg'
    im = cv2.imread(f); h, w = im.shape[:2]
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    cx, cy = foco(g)
    a = AJ.get(arq, (None, None, .9))
    fx, fy, z = (a[0] if a[0] is not None else cx, a[1] if a[1] is not None else cy, a[2])
    ch = min(h, w * 5 / 4) * z; cw = ch * 4 / 5
    x0 = int(np.clip(fx * w - cw / 2, 0, w - cw)); y0 = int(np.clip(fy * h - ch / 2, 0, h - ch))
    c = g[y0:int(y0 + ch), x0:int(x0 + cw)].astype(np.float32)
    lo, hi = np.percentile(c, .4), np.percentile(c, 99.9)
    c = np.clip((c - lo) / (hi - lo), 0, 1)
    c = c ** (np.log(.62) / np.log(max(.05, float(np.median(c)))))     # mesma luz em todas
    c = cv2.resize(c, (720, 900), interpolation=cv2.INTER_AREA if cw > 720 else cv2.INTER_CUBIC)
    if cw < 720:
        c = np.clip(c + .5 * (c - cv2.GaussianBlur(c, (0, 0), 1.4)), 0, 1)
    t = np.dstack([c, c * .985, c * .955])
    Image.fromarray((t * 255 + .5).astype(np.uint8)).save(f'{S}/assets/img/p/{arq}.webp', quality=80, method=6)
    o = Image.open(f).convert('RGB'); o.thumbnail((1500, 1500), Image.LANCZOS)
    o.save(f'{S}/assets/img/o/{arq}.webp', quality=80, method=6)
    return o.size


if __name__ == '__main__':
    ids = [int(x) for x in sys.argv[1:]]
    tam = {}
    for p in dados.P:
        if not ids or p[0] in ids:
            tam[p[0]] = faz(p)
    if not ids:
        json.dump(tam, open(S + '/tools/tamanhos.json', 'w'))
    C = 10; T = 196; H = 245; n = len(dados.P)
    F = Image.new('RGB', (C * (T + 3), ((n + C - 1) // C) * (H + 3)), (25, 25, 25))
    d = ImageDraw.Draw(F)
    for k, p in enumerate(dados.P):
        i = Image.open(f'{S}/assets/img/p/{p[0]}.webp').resize((T, H), Image.LANCZOS)
        x, y = (k % C) * (T + 3), (k // C) * (H + 3); F.paste(i, (x, y)); d.rectangle((x, y, x + 30, y + 13), fill=(0, 0, 0)); d.text((x + 2, y + 1), str(p[0]), fill=(255, 230, 0))
    F.save(R + '/_ref/folhas/port.jpg', quality=86); print(F.size, sum(os.path.getsize(f'{S}/assets/img/p/{p[0]}.webp') for p in dados.P) // 1024, 'KB')
