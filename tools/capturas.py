# -*- coding: utf-8 -*-
"""Capturas da pagina inteira. Uso: python tools/capturas.py [url]  -> _ref/folhas/cap-*.jpg"""
import io, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
R = Path(__file__).resolve().parent.parent.parent
URL = next((a for a in sys.argv[1:] if a.startswith('http')), 'http://localhost:8910/')
ARG = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required']
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=ARG)
    for n, w, h, m in (('pc', 1440, 900, False), ('cel', 390, 844, True)):
        c = b.new_context(viewport={'width': w, 'height': h}, is_mobile=m, has_touch=m, device_scale_factor=1)
        g = c.new_page(); g.goto(URL, wait_until='load'); g.wait_for_timeout(13500)
        g.screenshot(path=str(R / f'_ref/folhas/cap-{n}-hero.jpg'), quality=88, type='jpeg')
        g.evaluate("""async()=>{document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager');
          document.querySelectorAll('.rv,.fio-v').forEach(e=>e.classList.add('ve'));
          document.documentElement.style.scrollBehavior='auto';document.querySelector('.topo').style.position='absolute';
          await Promise.all([...document.images].map(i=>i.complete?0:new Promise(r=>{i.onload=i.onerror=r})));}""")
        g.wait_for_timeout(1400)
        total = g.evaluate('document.documentElement.scrollHeight')
        ims = []; y = 0
        while y < total:
            g.evaluate(f"window.scrollTo(0,{y})"); g.wait_for_timeout(350)
            ims.append(Image.open(io.BytesIO(g.screenshot(type='png'))).convert('RGB')); y += h
        F = Image.new('RGB', (w, total)); y = 0
        for k, i in enumerate(ims):
            F.paste(i, (0, min(y, total - h))); y += h
        alt = 2400 if n == 'pc' else 1700; k = 0
        for y in range(0, total, alt):
            F.crop((0, y, w, min(y + alt, total))).save(R / f'_ref/folhas/cap-{n}-{k}.jpg', quality=86); k += 1
        print(n, total, k, 'partes'); c.close()
    b.close()
