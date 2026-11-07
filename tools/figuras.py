# -*- coding: utf-8 -*-
"""Figuras do hero. Cada tatuagem real vira:
  - a tinta verdadeira extraida da foto (canal R) + mapa de quando a agulha passa em cada pixel (canal G);
  - uma linha unica ordenada de N pontos, que e o fio que atravessa de uma figura para a outra.
Saida: assets/hero/fio.bin + assets/hero/<nome>.webp + assets/hero/fio.json. Uso: python tools/figuras.py"""
import os, sys, json, cv2, numpy as np
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(__file__))
import linha
R = os.path.expanduser('~/Documents/PROJETOS LRGZ/Joana Coelho')
S = R + '/site'
N = 20000
ALT = 1400   # altura da textura de tinta


def pv(pts, w, h):
    """zona em pixels da caixa -> 0..1"""
    return [(x / w, y / h) for x, y in pts]


# centro e meia caixa na foto original; ang em graus (positivo gira anti-horario); tira = manchas removidas da pele (x,y,r na foto)
FIG = {
    'borboleta': dict(a='320_0', c=(530, 560), mw=190, mh=525, ang=-4.2, lim=5.5, forte=15, esc=4, sig=14, suave=7, fecho=7, min=24, topo=1.,
                      tira=[(375, 545, 34), (842, 336, 20)],
                      zona=pv([(125, 32), (225, 32), (232, 120), (205, 130), (205, 320), (320, 380), (360, 520), (360, 700), (235, 760), (215, 960), (150, 960), (130, 760), (0, 700), (0, 520), (60, 400), (160, 320), (160, 130), (120, 120)], 360, 1000),
                      fura=[(44 / 360, .495, .05), (329 / 360, .305, .04), (339 / 360, .825, .05), (129 / 360, .875, .05), (54 / 360, .79, .05), (269 / 360, .97, .05), (92 / 360, .10, .0)]),
    'fenix':     dict(a='007_0', c=(622, 978), mw=172, mh=226, ang=0, lim=5.5, forte=13, esc=6, sig=13, suave=10, fecho=9, min=150, topo=.9,
                      zona=pv([(50, 200), (135, 36), (210, 36), (270, 125), (420, 190), (560, 182), (760, 20), (940, 200), (940, 800), (790, 900), (700, 1250), (500, 1250), (340, 1140), (130, 650), (40, 380)], 1000, 1256),
                      fura=[(.08, .05, .09), (.06, .1, .06), (.25, .18, .02)]),
    'lotus':     dict(a='201_0', c=(866, 884), mw=224, mh=622, ang=0, lim=4.8, forte=13, esc=3, sig=14, suave=6, fecho=5, min=16, topo=1.,
                      zona=pv([(150, 28), (190, 28), (190, 85), (330, 110), (330, 300), (262, 330), (232, 362), (232, 985), (140, 985), (128, 362), (98, 330), (30, 300), (30, 110), (150, 85)], 360, 1000)),
}


def caixa(f):
    im = cv2.imread(f'{R}/_ref/ig/{f["a"]}.jpg')
    if f.get('tira'):
        m = np.zeros(im.shape[:2], np.uint8)
        for x, y, r in f['tira']:
            cv2.circle(m, (x, y), r, 255, -1)
        im = cv2.inpaint(im, m, 9, cv2.INPAINT_TELEA)
    cx, cy = f['c']
    M = cv2.getRotationMatrix2D((cx, cy), f['ang'], 1)
    M[0, 2] += f['mw'] - cx; M[1, 2] += f['mh'] - cy
    return cv2.warpAffine(im, M, (2 * f['mw'], 2 * f['mh']), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def faz(nome):
    f = FIG[nome]
    c = caixa(f)
    e = f['esc']
    r = linha.linhas(c, limiar=f['lim'], forte=f['forte'], escala=e, N=N, sigma=f['sig'], minimo=f['min'], suave=f['suave'], fecho=f['fecho'], zona=f.get('zona'), fura=f.get('fura'), podar=6 * e)
    d, m, p = r['d'], r['m'], r['p']
    Hu, Wu = d.shape
    # tinta verdadeira: densidade so onde a mascara confirmou
    malha = cv2.GaussianBlur(cv2.dilate(m.astype(np.uint8), np.ones((3 * e, 3 * e), np.uint8)).astype(np.float32), (0, 0), e)
    topo = np.percentile(d[m], 97)
    a = np.clip((d - f['lim'] * .55) / (topo - f['lim'] * .55), 0, 1) ** .86 * malha
    # tamanho final
    W = int(round(ALT * c.shape[1] / c.shape[0])) & ~1
    tinta = cv2.resize(a, (W, ALT), interpolation=cv2.INTER_AREA if Wu > W else cv2.INTER_CUBIC)
    # mapa de tempo: indice do ponto de tinta mais proximo
    idx = np.flatnonzero(r['pena'] > .5)
    arv = cKDTree(p[idx][::2])
    gy, gx = np.mgrid[0:ALT // 2, 0:W // 2]
    q = np.stack([(gx + .5) * Wu / (W // 2), (gy + .5) * Hu / (ALT // 2)], 1) if False else np.stack([(gx.ravel() + .5) * Wu / (W // 2), (gy.ravel() + .5) * Hu / (ALT // 2)], 1)
    _, j = arv.query(q, workers=-1)
    t = (idx[::2][j] / N).reshape(gx.shape).astype(np.float32)
    t = cv2.resize(cv2.GaussianBlur(t, (0, 0), 1.2), (W, ALT), interpolation=cv2.INTER_LINEAR)
    os.makedirs(S + '/assets/hero', exist_ok=True)
    tex = np.dstack([np.zeros_like(tinta), t, tinta])  # BGR: R=tinta, G=tempo
    cv2.imwrite(f'{S}/assets/hero/{nome}.webp', (tex * 255 + .5).astype(np.uint8), [cv2.IMWRITE_WEBP_QUALITY, 94])
    # normaliza o fio: y em -1..1 pela altura da caixa, x proporcional
    q = (p - [Wu / 2, Hu / 2]) / (Hu / 2) * f['topo']
    print(nome, W, ALT, 'L', int(r['L']), 'saltos%', round(100 * (1 - r['pena'].mean()), 1), 'tinta%', round(100 * float((tinta > .1).mean()), 1))
    # conferencia
    v = cv2.resize(c, (W, ALT))
    pap = np.full((ALT, W, 3), 200, np.float32) * np.array([.86, .93, 1.])
    tin = pap * (1 - tinta[..., None]) + 28 * tinta[..., None]
    fio = np.full((ALT, W, 3), 240, np.uint8)
    s = ALT / Hu
    pts = (p * s * 8).astype(np.int32)
    for i in range(1, N):
        if r['pena'][i] > .5 and r['pena'][i - 1] > .5:
            cv2.line(fio, tuple(pts[i - 1]), tuple(pts[i]), (30, 30, 30), 1, cv2.LINE_AA, 3)
    cv2.imwrite(f'{R}/_ref/folhas/fig-{nome}.jpg', np.hstack([v, tin.astype(np.uint8), fio]), [cv2.IMWRITE_JPEG_QUALITY, 88])
    return dict(p=q.astype(np.float32), pena=r['pena'], larg=np.clip(r['larg'] / e, 0, 8).astype(np.float32), asp=W / ALT, topo=f['topo'], tex=nome)


def assinatura():
    a = json.load(open(R + '/_ref/ass.json'))
    tr = [(np.array(t['c'], np.float32), np.array(t['l'], np.float32)) for t in a['t']]
    L = [np.hypot(*np.diff(c, axis=0).T).sum() for c, _ in tr]
    ponte = 3000
    nA = int((N - 400) * L[0] / sum(L)); nB = N - 400 - nA
    def rs(c, l, n):
        d = np.r_[0, np.cumsum(np.hypot(*np.diff(c, axis=0).T))]; u = np.linspace(0, d[-1], n)
        return np.stack([np.interp(u, d, c[:, 0]), np.interp(u, d, c[:, 1])], 1), np.interp(u, d, l)
    pA, lA = rs(*tr[0], nA); pB, lB = rs(*tr[1], nB)
    br = np.linspace(pA[-1], pB[0], 400)
    p = np.concatenate([pA, br, pB]); l = np.r_[lA, np.zeros(400), lB]; pena = np.r_[np.ones(nA), np.zeros(400), np.ones(nB)]
    W, H = a['w'], a['h']
    esc = .62 / (W / 2)                 # meia largura .62 da unidade
    q = (p - [W / 2, H / 2]) * esc
    return dict(p=q.astype(np.float32), pena=pena, larg=(l * esc * 500).astype(np.float32), asp=W / H, topo=1, tex=None)


saida = [assinatura()] + [faz(n) for n in FIG]
# binario: Int16 x,y (1/16000) + Uint8 largura (1/32) + Uint8 pena, por figura
b = bytearray()
meta = dict(n=N, fig=[])
for f in saida:
    xy = np.clip(np.round(f['p'] * 16000), -32767, 32767).astype(np.int16)
    b += xy.tobytes()
    b += np.clip(np.round(f['larg'] * 32), 0, 255).astype(np.uint8).tobytes()
    b += (f['pena'] > .5).astype(np.uint8).tobytes()
    meta['fig'].append(dict(asp=round(float(f['asp']), 4), tex=f['tex']))
open(S + '/assets/hero/fio.bin', 'wb').write(bytes(b))
json.dump(meta, open(S + '/assets/hero/fio.json', 'w'))
print('fio.bin', round(len(b) / 1e6, 2), 'MB')
