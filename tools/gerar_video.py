# -*- coding: utf-8 -*-
"""Grava o hero do celular (laco fechado em 1080x1920) e os posteres. Uso: python tools/gerar_video.py [poster] [video] [fps]"""
import base64, io, json, shutil, subprocess, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
S = Path(__file__).resolve().parent.parent
ff = shutil.which('ffmpeg')
Q = [a for a in sys.argv[1:] if not a.isdigit()] or ['poster', 'video']
FPS = next((int(a) for a in sys.argv[1:] if a.isdigit()), 30)
b64 = lambda f, m: f'data:{m};base64,' + base64.b64encode((S / f).read_bytes()).decode()
meta = json.loads((S / 'assets/hero/fio.json').read_text())
(S / 'assets/video').mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
    g = b.new_page(viewport={'width': 400, 'height': 400})
    g.set_content('<body style="margin:0"><canvas id=c></canvas></body>')
    g.add_script_tag(content=(S / 'assets/js/fio.js').read_text(encoding='utf8'))
    g.evaluate("""async(a)=>{window.T=fioHero(document.getElementById('c'),{guardar:true});
      const r=await fetch(a.bin);T.pontos(await r.arrayBuffer(),a.meta);
      for(let i=0;i<a.meta.fig.length;i++){if(!a.tex[i])continue;const m=new Image();m.src=a.tex[i];await m.decode();T.textura(i,m)}}""",
        dict(bin=b64('assets/hero/fio.bin', 'application/octet-stream'), meta=meta, tex=[b64(f"assets/hero/{f['tex']}.webp", 'image/webp') if f['tex'] else None for f in meta['fig']]))

    def foto(t, W, H, q=.96):
        d = g.evaluate(f"(T.desenha({t},{W / 3},{H / 3},3,2,.55),document.getElementById('c').toDataURL('image/jpeg',{q}))")
        return base64.b64decode(d.split(',', 1)[1])
    if 'poster' in Q:
        for n, W, H, t in (('pe', 1080, 1920, 7), ('deitado', 1920, 1080, 7)):
            Image.open(io.BytesIO(foto(t, W, H))).save(S / f'assets/img/hero-{n}.webp', quality=84, method=6)
            print('poster', n, flush=True)
    if 'poster' in Q:
        fn = b64('assets/fonts/fahkwang-300-latin.woff2', 'font/woff2')
        fundo = 'data:image/jpeg;base64,' + base64.b64encode(foto(1.8, 1200, 700)).decode()
        o = b.new_page(viewport={'width': 1200, 'height': 630})
        o.set_content(f'''<style>@font-face{{font-family:F;src:url({fn})}}body{{margin:0;width:1200px;height:630px;background:url({fundo}) 0 -50px;overflow:hidden;position:relative}}
          p{{position:absolute;left:0;right:0;bottom:44px;margin:0;text-align:center;font:300 58px/1.2 F;color:#1b1815}}</style><p>Joana Coelho</p>''')
        o.wait_for_timeout(500); o.screenshot(path=str(S / 'assets/img/og.jpg'), type='jpeg', quality=88); o.close(); print('og', flush=True)
    if 'video' in Q:
        mp4 = S / 'assets/video/hero-pe.mp4'; n = round(g.evaluate('fioCiclo') * FPS)
        enc = subprocess.Popen([ff, '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                                '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-color_range', 'tv', '-r', str(FPS), '-movflags', '+faststart', '-an', str(mp4)], stdin=subprocess.PIPE)
        t0 = time.time()
        for i in range(n):
            enc.stdin.write(foto(i / FPS, 1080, 1920))
            if i % 60 == 0: print(i, n, round(time.time() - t0), 's', flush=True)
        enc.stdin.close(); enc.wait()
        print(mp4.name, round(mp4.stat().st_size / 1e6, 2), 'MB', flush=True)
    b.close()
