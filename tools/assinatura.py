# -*- coding: utf-8 -*-
"""Extrai a assinatura JC do cartao de visita (destaque Voucher): endireita, isola o dourado e vetoriza."""
import os, cv2, numpy as np, potrace
R = os.path.expanduser('~/Documents/PROJETOS LRGZ/Joana Coelho')
im = cv2.imread(R + '/_ref/hl/voucher/000.jpg')
# recorte do cartao
x0, y0, x1, y1 = 600, 1240, 1179, 1660
c = im[y0:y1, x0:x1]
sc = 5
big = cv2.resize(c, None, fx=sc, fy=sc, interpolation=cv2.INTER_LANCZOS4)
ang = 6.1
H, W = big.shape[:2]
M = cv2.getRotationMatrix2D((W / 2, H / 2), ang, 1)
rot = cv2.warpAffine(big, M, (W, H), flags=cv2.INTER_CUBIC, borderValue=(245, 245, 245))
cv2.imwrite(R + '/_ref/folhas/ass-rot.jpg', rot)
g = cv2.cvtColor(rot, cv2.COLOR_BGR2GRAY).astype(np.float32)
fundo = cv2.GaussianBlur(g, (0, 0), 40)
d = fundo - g
d = cv2.GaussianBlur(d, (0, 0), 1.8)
m = (d > 24).astype(np.uint8)
n, l, s, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
i = 1 + int(np.argmax(s[1:, cv2.CC_STAT_AREA]))
m2 = (l == i).astype(np.uint8)
ys, xs = np.where(m2)
print('caixa', xs.min(), xs.max(), ys.min(), ys.max(), 'area', m2.sum())
m2 = m2[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
cv2.imwrite(R + '/_ref/folhas/ass-mask.png', m2 * 255)
np.save(R + '/_ref/ass-mask.npy', m2)
