# -*- coding: utf-8 -*-
"""Fotos das secoes: recorte 4:5 (ou o indicado), mesmo P&B quente do portfolio. Uso: python tools/fotos_secoes.py"""
import os, cv2, numpy as np
from PIL import Image
R = os.path.expanduser('~/Documents/PROJETOS LRGZ/Joana Coelho'); S = R + '/site/assets/img/s'
os.makedirs(S, exist_ok=True)
# nome: (arquivo, x0, y0, x1, y1 em 0..1, largura de saida, proporcao L/A, cor?)
L = {
    'retrato':    ('ig/084_0', 0, .04, 1, .86, 960, 4 / 5, 0),
    'noite':      ('hl/agenda/001', 0, .10, 1, .86, 960, 4 / 5, 0),
    'casamento':  ('ig/083_1', .08, 0, .86, 1, 720, 4 / 5, 0),
    'flash':      ('hl/flash-day/006', 0, .04, 1, .74, 720, 4 / 5, 0),
    'voucher':    ('hl/voucher/000', 0, .08, 1, .76, 720, 4 / 5, 0),
    'fidelidade': ('ig/160_0', .02, .0, .98, .60, 720, 4 / 5, 0),
    'formar':     ('hl/workshop-grupo/006', .05, .14, .98, .84, 720, 4 / 5, 0),
    'aula':       ('hl/workshop-grupo/014', 0, .1, 1, .82, 720, 4 / 5, 0),
    'aluna':      ('hl/workshop-grupo/022', 0, .14, 1, .8, 720, 4 / 5, 0),
    'tablet':     ('ig/420_0', 0, 0, 1, 1, 720, 4 / 5, 0),
    'fachada':    ('hl/est-estudio/000', 0, .10, 1, .76, 720, 4 / 5, 0),
    'dentro':     ('ig/014_0', 0, 0, 1, 1, 720, 4 / 5, 0),
    'duo':        ('hl/est-team/002', .02, .2, 1, .84, 720, 4 / 5, 0),

    'oporto':     ('ig/004_0', 0, 0, 1, 1, 720, 4 / 5, 1),
}
for n, (f, a, b, c, d, w, pr, cor) in L.items():
    im = cv2.imread(f'{R}/_ref/{f}.jpg')
    H, W = im.shape[:2]
    x0, y0, x1, y1 = int(a * W), int(b * H), int(c * W), int(d * H)
    rw, rh = x1 - x0, y1 - y0
    if rw / rh > pr:
        nw = int(rh * pr); x0 += (rw - nw) // 2; x1 = x0 + nw
    else:
        nh = int(rw / pr); y0 += (rh - nh) // 2; y1 = y0 + nh
    k = im[y0:y1, x0:x1]
    h = int(round(w / pr))
    if cor:
        o = cv2.resize(k, (w, h), interpolation=cv2.INTER_AREA)
        Image.fromarray(o[:, :, ::-1]).save(f'{S}/{n}.webp', quality=82, method=6)
    else:
        g = cv2.cvtColor(k, cv2.COLOR_BGR2GRAY).astype(np.float32)
        lo, hi = np.percentile(g, .4), np.percentile(g, 99.8)
        g = np.clip((g - lo) / (hi - lo), 0, 1)
        g = cv2.resize(g, (w, h), interpolation=cv2.INTER_AREA if k.shape[1] > w else cv2.INTER_CUBIC)
        if k.shape[1] < w:
            g = np.clip(g + .45 * (g - cv2.GaussianBlur(g, (0, 0), 1.3)), 0, 1)
        t = np.dstack([g, g * .985, g * .955])
        Image.fromarray((t * 255 + .5).astype(np.uint8)).save(f'{S}/{n}.webp', quality=82, method=6)
    print(n, k.shape[1], 'px', os.path.getsize(f'{S}/{n}.webp') // 1024, 'KB')
n = list(L)
F = Image.new('RGB', (8 * 246, 2 * 306), (20, 20, 20))
for k, x in enumerate(n):
    i = Image.open(f'{S}/{x}.webp').resize((244, 305)); F.paste(i, ((k % 8) * 246, (k // 8) * 306))
F.save(R + '/_ref/folhas/secoes.jpg', quality=86)
