# -*- coding: utf-8 -*-
"""Grade de cor do site: uma luz so para fotos de origens diferentes, sem inventar cor em foto P&B.
Tira a dominante, puxa a pele para quente, segura a saturacao alta e usa o mesmo preto quente do P&B."""
import cv2, numpy as np


def croma(bgr):
    """Mediana da saturacao: perto de 0 = foto ja e P&B."""
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB).astype(np.float32) - [0, 128, 128]
    return float(np.median(np.hypot(lab[..., 1], lab[..., 2])))


def nitidez(rgb, k=.45, s=1.3):
    return np.clip(rgb + k * (rgb - cv2.GaussianBlur(rgb, (0, 0), s)), 0, 1)


def grade(bgr, mediana=None):
    """bgr uint8 -> rgb float 0..1"""
    lab = cv2.cvtColor(bgr.astype(np.float32) / 255, cv2.COLOR_BGR2LAB)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    # dominante: tons claros e quase neutros deviam ser marfim
    lim = np.percentile(L, 70)
    m = (L > lim) & (np.hypot(a, b) < 22)
    if m.sum() > 400:
        a = a + np.clip(1.0 - np.median(a[m]), -7, 7) * .75
        b = b + np.clip(5.0 - np.median(b[m]), -9, 9) * .75
    # saturacao contida: sobe a pele, segura os excessos
    C = np.hypot(a, b) + 1e-4
    N = np.where(C < 26, C * .84, 21.8 + (C - 26) * .3)
    a, b = a * N / C, b * N / C
    # luz: mesmos pontos e mediana do portfolio
    l = L / 100
    lo, hi = np.percentile(l, .4), np.percentile(l, 99.8)
    l = np.clip((l - lo) / max(hi - lo, 1e-3), 0, 1)
    if mediana:
        l = l ** (np.log(mediana) / np.log(np.clip(np.median(l), .08, .92)))
    l = np.clip(l + .08 * np.sin((l - .5) * 2 * np.pi) * -.5, 0, 1)
    # preto quente, igual ao das fotos P&B
    sombra = (1 - l) ** 3
    a = a + sombra * .8; b = b + sombra * 2.4
    out = cv2.cvtColor(np.dstack([l * 100, a, b]).astype(np.float32), cv2.COLOR_LAB2RGB)
    return np.clip(out, 0, 1)
