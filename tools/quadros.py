# -*- coding: utf-8 -*-
"""Folha de quadros do hero para conferencia. Uso: python tools/quadros.py W H t1 t2 ..."""
import base64, sys, io, json
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
S = Path(__file__).resolve().parent.parent
W, H = int(sys.argv[1]), int(sys.argv[2]); TS = [float(x) for x in sys.argv[3:]]
b64 = lambda f, m: f'data:{m};base64,' + base64.b64encode((S / f).read_bytes()).decode()
meta = json.loads((S / 'assets/hero/fio.json').read_text())
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    g = b.new_page(viewport={'width': 400, 'height': 400})
    er = []; g.on('pageerror', lambda e: er.append(str(e)[:900])); g.on('console', lambda m: er.append(m.text[:300]) if m.type in ('error', 'warning') else None)
    g.set_content('<body style="margin:0"><canvas id=c></canvas></body>')
    g.add_script_tag(content=(S / 'assets/js/fio.js').read_text(encoding='utf8'))
    g.evaluate("""async(a)=>{window.T=fioHero(document.getElementById('c'),{guardar:true});
      const r=await fetch(a.bin);T.pontos(await r.arrayBuffer(),a.meta);
      for(let i=0;i<a.meta.fig.length;i++){if(!a.tex[i])continue;const m=new Image();m.src=a.tex[i];await m.decode();T.textura(i,m)}}""",
        dict(bin=b64('assets/hero/fio.bin', 'application/octet-stream'), meta=meta, tex=[b64(f"assets/hero/{f['tex']}.webp", 'image/webp') if f['tex'] else None for f in meta['fig']]))
    cols = min(4, len(TS)); ims = []
    for t in TS:
        d = g.evaluate(f"(T.desenha({t},{W},{H},1),document.getElementById('c').toDataURL('image/jpeg',.93))")
        ims.append(Image.open(io.BytesIO(base64.b64decode(d.split(',', 1)[1]))))
    print(er[:6])
    b.close()
tw = 1960 // cols; th = int(tw * H / W); rows = (len(ims) + cols - 1) // cols
F = Image.new('RGB', (cols * tw, rows * th))
for k, i in enumerate(ims): F.paste(i.resize((tw, th), Image.LANCZOS), ((k % cols) * tw, (k // cols) * th))
F.save(r'C:\Users\dslru\Documents\PROJETOS LRGZ\Joana Coelho\_ref\folhas\quadros.jpg', quality=88); print(F.size)
