# -*- coding: utf-8 -*-
"""Refaz a assinatura como 2 tracos de caneta na ordem real (centro + largura), a partir da mascara do cartao.
Sai: _ref/ass.json (tracos) e assets/img/jc.svg (preenchido, largura variavel)."""
import os, json, cv2, numpy as np
from scipy.interpolate import splprep, splev
from scipy.ndimage import gaussian_filter1d, distance_transform_edt
from skimage.morphology import skeletonize
R = os.path.expanduser('~/Documents/PROJETOS LRGZ/Joana Coelho')
m = np.load(R + '/_ref/ass-mask.npy').astype(np.uint8)
m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
H, W = m.shape
dt = distance_transform_edt(m)
sk = skeletonize(m > 0)
ys, xs = np.where(sk)
P = np.stack([xs, ys], 1).astype(np.float32)
f = 1.0235  # 2047/2000: pontos lidos na imagem exibida
# tracos na ordem da caneta (pontos lidos na imagem de 2000 px)
A = [(500, 702), (400, 725), (290, 740), (205, 700), (180, 630), (225, 500), (340, 330), (520, 140), (690, 30), (790, 15), (850, 60), (878, 170),
     (860, 370), (800, 590), (730, 790), (670, 960), (610, 1060), (500, 1230), (370, 1370), (220, 1440), (90, 1430), (20, 1340), (60, 1230), (200, 1130),
     (400, 1060), (640, 1012), (800, 990), (1100, 955), (1500, 915), (1950, 882)]
B = [(1840, 830), (1920, 740), (1975, 640), (1920, 570), (1800, 530), (1600, 525), (1300, 590), (1000, 680), (800, 780), (745, 860), (735, 930), (770, 1000), (860, 1060), (1050, 1120), (1250, 1155), (1460, 1178)]


def traco(pts, passos=900):
    p = np.array(pts, float) * f
    tck, _ = splprep(p.T, s=0, k=3)
    u = np.linspace(0, 1, passos)
    x, y = splev(u, tck)
    c = np.stack([x, y], 1)
    # cola no eixo medial e suaviza; perto do cruzamento confia mais na spline
    for it in range(3):
        d = ((c[:, None, :] - P[None, ::2, :]) ** 2).sum(2)
        j = d.argmin(1)
        s = P[::2][j]
        dd = np.sqrt(d[np.arange(len(c)), j])
        pe = np.clip(1 - dd / 40, 0, 1)[:, None]
        c = c * (1 - pe) + s * pe
        c = np.stack([gaussian_filter1d(c[:, 0], 9, mode='nearest'), gaussian_filter1d(c[:, 1], 9, mode='nearest')], 1)
    w = dt[np.clip(c[:, 1].astype(int), 0, H - 1), np.clip(c[:, 0].astype(int), 0, W - 1)]
    w = np.clip(w, 3, 21)
    # o cruzamento engrossa a medicao: limita pela mediana local
    from scipy.ndimage import median_filter
    w = median_filter(w, 61, mode='nearest')
    w = gaussian_filter1d(w, 18, mode='nearest')
    # pontas afinam como caneta
    n = len(w); t = np.arange(n)
    e = np.minimum(np.clip(t / 26, 0, 1), np.clip((n - 1 - t) / 26, 0, 1)) ** .6
    w = w * (.25 + .75 * e)
    return c, w


tr = [traco(A, 1300), traco(B, 800)]
# passa pra preenchido
def poli(c, w):
    t = np.gradient(c, axis=0); t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-9
    n = np.stack([-t[:, 1], t[:, 0]], 1)
    a = c + n * w[:, None]; b = c - n * w[:, None]
    q = np.concatenate([a[::3], b[::-1][::3]])
    return 'M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in q) + 'Z'

d = ''.join(poli(c, w) for c, w in tr)
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"><path fill="currentColor" d="{d}"/></svg>'
os.makedirs(R + '/site/assets/img', exist_ok=True)
open(R + '/site/assets/img/jc.svg', 'w').write(svg)
json.dump({'w': W, 'h': H, 't': [{'c': np.round(c, 1).tolist(), 'l': np.round(w, 2).tolist()} for c, w in tr]}, open(R + '/_ref/ass.json', 'w'))
# conferencia
v = np.zeros((H, W, 3), np.uint8); v[m > 0] = (70, 70, 70)
for c, w in tr:
    t = np.gradient(c, axis=0); t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-9
    n = np.stack([-t[:, 1], t[:, 0]], 1)
    pol = np.concatenate([c + n * w[:, None], (c - n * w[:, None])[::-1]]).astype(np.int32)
    ov = v.copy(); cv2.fillPoly(ov, [pol], (120, 220, 255)); v = cv2.addWeighted(ov, .7, v, .3, 0)
cv2.imwrite(R + '/_ref/folhas/ass-conf.jpg', cv2.resize(v, (1200, int(1200 * H / W))))
print(len(svg))
