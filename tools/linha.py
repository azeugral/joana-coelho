# -*- coding: utf-8 -*-
"""Transforma uma tatuagem fine line numa unica linha ordenada, como se a agulha nunca levantasse.
tinta da foto -> mascara -> esqueleto -> grafo -> percurso continuo (DFS) -> N pontos com largura e presenca.
Funcoes usadas por tools/figuras.py."""
import numpy as np, cv2
from collections import defaultdict
from scipy.ndimage import distance_transform_edt, gaussian_filter1d
from skimage.morphology import skeletonize, remove_small_objects


def tinta(bgr, sigma=26, escala=3, corpo=None):
    """Mapa de tinta 0..1 (escuro local), ampliado."""
    g = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)[:, :, 0].astype(np.float32)
    g = cv2.resize(g, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC)
    g = cv2.GaussianBlur(g, (0, 0), .8 * escala / 2)
    f = cv2.GaussianBlur(g, (0, 0), sigma * escala)
    d = np.clip(f - g, 0, None)
    if corpo is not None:
        c = cv2.resize(corpo, (d.shape[1], d.shape[0]), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255
        d *= c
    return d


def mascara(d, limiar, forte, minimo, fecho):
    """Histerese: um traco fraco so entra se tocar tinta forte; assim o poro some e o ponto real fica."""
    from skimage.filters import apply_hysteresis_threshold
    m = apply_hysteresis_threshold(d, limiar, forte)
    if fecho:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (fecho, fecho))
        m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_CLOSE, k) > 0
    n, l, s, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
    return (s[:, cv2.CC_STAT_AREA] >= minimo)[l] & (l > 0)


def _vizinhos(s):
    H, W = s.shape
    ys, xs = np.where(s)
    idx = {(y, x): i for i, (y, x) in enumerate(zip(ys.tolist(), xs.tolist()))}
    viz = [[] for _ in idx]
    for (y, x), i in idx.items():
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy or dx:
                    j = idx.get((y + dy, x + dx))
                    if j is not None:
                        viz[i].append(j)
    return ys, xs, viz


def percurso(m, podar=10):
    """Devolve lista de componentes; cada uma e um array Nx2 (x,y) continuo em DFS, ida e volta so onde precisa."""
    s = skeletonize(m)
    ys, xs, viz = _vizinhos(s)
    n = len(ys)
    # poda de ramos curtos
    grau = np.array([len(v) for v in viz])
    vivo = np.ones(n, bool)
    for i in np.where(grau == 1)[0]:
        c = [i]; p = -1; a = i
        while len(c) <= podar:
            nx = [j for j in viz[a] if j != p and vivo[j]]
            if len(nx) != 1:
                break
            p, a = a, nx[0]; c.append(a)
        if len(c) <= podar and len([j for j in viz[a] if vivo[j]]) > 2:
            for k in c[:-1]:
                vivo[k] = False
    # DFS iterativo por pixels
    vis = np.zeros(n, bool)
    comps = []
    ordem = sorted(np.where(vivo)[0].tolist(), key=lambda i: (ys[i], xs[i]))
    for ini in ordem:
        if vis[ini]:
            continue
        cam = [ini]; pilha = [(ini, iter(viz[ini]))]; vis[ini] = True
        while pilha:
            a, it = pilha[-1]
            for j in it:
                if vivo[j] and not vis[j]:
                    vis[j] = True
                    cam.append(j); pilha.append((j, iter(viz[j])))
                    break
            else:
                pilha.pop()
                if pilha:
                    cam.append(pilha[-1][0])
        # corta a volta final depois do ultimo ponto novo
        vistos = set(); ult = 0
        for k, i in enumerate(cam):
            if i not in vistos:
                vistos.add(i); ult = k
        cam = cam[:ult + 1]
        if len(cam) >= 2:
            comps.append(np.stack([xs[cam], ys[cam]], 1).astype(np.float32))
    return comps


def costura(comps):
    """Ordena componentes por vizinho mais proximo e devolve (pontos, pena) com pena=0 nos saltos."""
    r = list(comps)
    r.sort(key=lambda c: c[0][1])
    atual = r.pop(0)
    P = [atual]; pena = [np.ones(len(atual))]
    while r:
        fim = P[-1][-1]
        d = [min(np.hypot(*(c[0] - fim)), np.hypot(*(c[-1] - fim))) for c in r]
        i = int(np.argmin(d)); c = r.pop(i)
        if np.hypot(*(c[-1] - fim)) < np.hypot(*(c[0] - fim)):
            c = c[::-1]
        k = max(2, int(np.hypot(*(c[0] - fim)) / 2))
        ponte = np.linspace(fim, c[0], k, dtype=np.float32)
        P.append(ponte); pena.append(np.zeros(k))
        P.append(c); pena.append(np.ones(len(c)))
    return np.concatenate(P), np.concatenate(pena)


def reamostra(p, pena, N, suave=1.4, ponte=.12):
    """Uniformiza em N pontos pelo comprimento. Suaviza o serrilhado do esqueleto."""
    # suaviza cada trecho de tinta sozinho, sem misturar com a ponte vizinha
    q = p.copy()
    borda = np.flatnonzero(np.diff(pena)) + 1
    for a, b in zip(np.r_[0, borda], np.r_[borda, len(p)]):
        if pena[a] > .5 and b - a > 3:
            q[a:b, 0] = gaussian_filter1d(p[a:b, 0], suave, mode='nearest')
            q[a:b, 1] = gaussian_filter1d(p[a:b, 1], suave, mode='nearest')
    passo = np.hypot(*np.diff(q, axis=0).T)
    peso = np.where((pena[1:] > .5) & (pena[:-1] > .5), 1, ponte)   # ponte gasta poucos pontos
    d = np.r_[0, np.cumsum(passo * peso)]
    d = np.maximum.accumulate(d + np.arange(len(d)) * 1e-5)
    u = np.linspace(0, d[-1], N)
    x = np.interp(u, d, q[:, 0]); y = np.interp(u, d, q[:, 1])
    a = np.interp(u, d, pena)
    return np.stack([x, y], 1), (a > .5).astype(np.float32), d[-1]


def linhas(bgr, limiar=9, forte=16, escala=3, N=30000, corpo=None, minimo=60, sigma=26, suave=6, fecho=0, zona=None, podar=14, fura=None):
    d = tinta(bgr, sigma=sigma, escala=escala, corpo=corpo)
    if zona is not None:
        z = np.zeros(d.shape, np.uint8)
        cv2.fillPoly(z, [(np.array(zona, np.float32) * [d.shape[1], d.shape[0]]).astype(np.int32)], 1)
        d = d * z
    for x, y, r in (fura or []):
        cv2.circle(d, (int(x * d.shape[1]), int(y * d.shape[0])), int(r * d.shape[1]), 0, -1)
    m = mascara(d, limiar, forte, minimo, fecho)
    comps = percurso(m, podar)
    p, pena = costura(comps)
    q, a, L = reamostra(p, pena, N, suave)
    dt = distance_transform_edt(m)
    H, W = m.shape
    xi = np.clip(q[:, 0].astype(int), 0, W - 1); yi = np.clip(q[:, 1].astype(int), 0, H - 1)
    larg = dt[yi, xi]
    forca = np.clip(cv2.GaussianBlur(d, (0, 0), 1.5)[yi, xi] / (np.percentile(d[m], 90) + 1e-6), .25, 1)
    return dict(p=q, pena=a, larg=larg, forca=forca, L=L, m=m, d=d)
