# -*- coding: utf-8 -*-
"""Auditoria: estouro, corte de texto, corte de fonte, simetria no eixo, grades e erros, em 13 tamanhos + teste funcional.
Uso: python tools/auditar.py [url]"""
import sys
from urllib.parse import unquote
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf8')
URL = next((a for a in sys.argv[1:] if a.startswith('http')), 'http://localhost:8910/')
VPS = [(320, 568, 1), (360, 640, 1), (360, 740, 1), (390, 844, 1), (430, 932, 1), (600, 900, 1), (768, 1024, 1), (844, 390, 1), (1024, 768, 0), (1280, 720, 0), (1440, 900, 0), (1920, 1080, 0), (2560, 1300, 0)]
ARG = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required']
JS = r"""
() => {
  const W = document.documentElement.clientWidth, H = innerHeight, out = [];
  if (document.documentElement.scrollWidth > W) out.push('ESTOURO pagina ' + document.documentElement.scrollWidth + '>' + W);
  const cv = document.createElement('canvas').getContext('2d');
  document.querySelectorAll('h1 span,h2,h3,p,a,button,span,blockquote,cite,li,label,legend,figcaption').forEach(el => {
    if (el.closest('[hidden],.saltar,.menu,.lb,.peca')) return;
    const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') return;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) return;
    const nome = el.tagName + '.' + el.className + ' "' + (el.textContent || '').trim().slice(0, 26) + '"';
    if (r.right > W + 1 || r.left < -1) out.push('FORA ' + nome + ' ' + Math.round(r.left) + '-' + Math.round(r.right));
    if (el.scrollWidth > el.clientWidth + 1 && cs.display !== 'inline' && el.clientWidth > 0) out.push('CORTE-X ' + nome + ' ' + el.scrollWidth + '>' + el.clientWidth);
    /* corte de fonte: acento e descendente precisam caber na caixa quando ha overflow escondido */
    if (cs.overflow !== 'visible' && el.scrollHeight > el.clientHeight + 1 && el.clientHeight > 0) out.push('CORTE-Y ' + nome);
    const lh = parseFloat(cs.lineHeight), fs = parseFloat(cs.fontSize);
    if (lh && lh / fs < 1.12 && el.textContent.trim() && !el.children.length) out.push('ENTRELINHA ' + nome + ' ' + (lh / fs).toFixed(2));
  });
  const eixo = W / 2, cen = s => { const r = document.querySelector(s).getBoundingClientRect(); return (r.left + r.right) / 2; };
  ['.marca', '.fio-v', '.cab h2', '.grade', '.rod-jc'].forEach(s => { if (Math.abs(cen(s) - eixo) > 1.5) out.push('EIXO ' + s + ' ' + (cen(s) - eixo).toFixed(1)); });
  /* hero */
  const h = document.querySelector('.hero').getBoundingClientRect(), bts = [...document.querySelectorAll('.hero-grade .bt')].map(b => b.getBoundingClientRect());
  bts.forEach(b => { if (b.bottom > h.bottom - 2) out.push('HERO botao cortado'); });
  if (Math.abs(bts[0].top - bts[1].top) > 1 || Math.abs(bts[0].width - bts[1].width) > 1 || Math.abs(bts[0].height - bts[1].height) > 1) out.push('HERO botoes desiguais');
  if (Math.abs((bts[0].left + bts[1].right) / 2 - eixo) > 1.5) out.push('HERO botoes fora do eixo');
  const n = [...document.querySelectorAll('.ne,.nd')].map(e => e.getBoundingClientRect()), barra = document.querySelector('.topo').getBoundingClientRect().bottom;
  if (Math.abs(n[0].top - n[1].top) > 1) out.push('HERO nome desalinhado');
  if (Math.min(n[0].top, n[1].top) < barra - 1) out.push('HERO nome sob a barra');
  if (n[0].left < 0 || n[1].right > W) out.push('HERO nome cortado');
  const larga = W / h.height > 1.05;
  const tx = [...document.querySelectorAll('.hero-txt')].map(e => e.getBoundingClientRect());
  if (Math.abs(tx[0].top - tx[1].top) > 1) out.push('HERO textos desalinhados');
  const lim = larga ? W * .24 : 0, cy = larga ? h.height * .47 : h.height * .555, sc = larga ? h.height * .36 : Math.min(h.height * .25, W * .62);
  if (larga) { if (tx[0].right > eixo - lim || bts[0].right > eixo - lim) out.push('HERO texto sobre a arte'); }
  else {
    if (Math.max(tx[0].bottom, tx[1].bottom) > cy - sc + 2) out.push('HERO texto sobre a arte ' + Math.round(tx[0].bottom) + ' > ' + Math.round(cy - sc));
    if (bts[0].top < cy + sc - 2) out.push('HERO botao sobre a arte');
    if (n[0].bottom > .27 * h.height + 2) out.push('HERO fio sobre o nome');
    if (bts[0].top < .86 * h.height - 2) out.push('HERO fio sobre botao');
    if (tx.length && (tx[0].width + tx[1].width) && tx[0].height !== tx[1].height) out.push('HERO textos com alturas diferentes');
  }
  /* grades */
  const lin = s => { const m = {}; [...document.querySelectorAll(s)].filter(e => !e.closest('[hidden]') && !e.hidden).forEach(e => { const r = e.getBoundingClientRect(); (m[Math.round(r.top)] = m[Math.round(r.top)] || []).push(r); }); return Object.values(m); };
  ['.grade .peca', '.exp img', '.acad-fotos img', '.est-fotos img'].forEach(s => lin(s).forEach(l => { const w0 = l[0].width, h0 = l[0].height; if (l.some(r => Math.abs(r.width - w0) > 1.2 || Math.abs(r.height - h0) > 1.2)) out.push('GRADE ' + s); const a = l[0].left, b = l[l.length - 1].right; if (Math.abs((a + b) / 2 - eixo) > 1.5 && l.length > 1) out.push('GRADE fora do eixo ' + s); }));
  return [...new Set(out)];
}
"""
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=ARG)
    tot = 0
    for w, h, tq in VPS:
        c = b.new_context(viewport={'width': w, 'height': h}, has_touch=bool(tq), is_mobile=bool(tq), device_scale_factor=1)
        g = c.new_page(); er = []
        g.on('pageerror', lambda e: er.append('JS ' + str(e)[:200]))
        g.on('console', lambda m: er.append('CON ' + m.text[:160]) if m.type == 'error' else None)
        g.on('response', lambda r: er.append(f'{r.status} ' + r.url[-50:]) if r.status >= 400 else None)
        g.goto(URL, wait_until='load'); g.wait_for_timeout(1200)
        o = g.evaluate(JS) + er
        print(f'{w}x{h}', 'ok' if not o else '')
        for x in o: print('   ', x)
        tot += len(o); c.close()
    print('TOTAL auditoria', tot)
    R = []
    def ok(n, v, x=''):
        R.append(bool(v)); print('OK ' if v else 'FALHOU', n, x)
    c = b.new_context(viewport={'width': 1440, 'height': 900}); g = c.new_page()
    g.goto(URL); g.wait_for_timeout(1500)
    vis = lambda: g.evaluate("[...document.querySelectorAll('.peca')].filter(p=>!p.hidden).length")
    ok('canvas ativo', g.evaluate("document.querySelector('#fio').width") == 1440)
    ok('12 de cara', vis() == 12)
    g.evaluate("document.querySelector('.filtros button[data-cat=animais]').scrollIntoView({block:'center',behavior:'instant'})")
    g.click('.filtros button[data-cat=animais]'); g.wait_for_timeout(200)
    na = vis(); ok('filtro', 0 < na < 38, na)
    g.click('.filtros button[data-cat=todas]'); g.wait_for_timeout(200)
    g.click('#ver-todos'); g.wait_for_timeout(200)
    ok('ver todos', vis() == 38)
    g.click('.peca:not([hidden]) >> nth=2'); g.wait_for_timeout(700)
    ok('lightbox abre', not g.evaluate("document.querySelector('#lb').hidden"))
    ok('lightbox foto', g.evaluate("(()=>{const i=document.querySelector('#lb-img');return i.complete&&i.naturalWidth>0})()"))
    l0 = g.inner_text('#lb-leg'); g.keyboard.press('ArrowRight'); g.wait_for_timeout(300)
    ok('seta teclado', g.inner_text('#lb-leg') != l0)
    ok('todas as fotos do lightbox existem', g.evaluate("""async()=>{const r=await Promise.all(PECAS.map(p=>fetch('assets/img/o/'+p.id+'.webp',{method:'HEAD'}).then(x=>x.ok)));return r.every(Boolean)}"""))
    leg = g.inner_text('#lb-leg'); g.click('#lb-quero'); g.wait_for_timeout(1300)
    ok('quero uma assim', leg in g.inner_text('#f-ref') and g.evaluate("document.querySelector('#lb').hidden"))
    g.evaluate("document.querySelector('[data-canal=wa]').scrollIntoView({block:'center',behavior:'instant'})"); g.wait_for_timeout(200)
    g.click('[data-canal=wa]'); g.wait_for_timeout(200)
    ok('erro sem nome', not g.evaluate("document.querySelector('#f-erro').hidden"))
    g.fill('#f-nome', 'Teste'); g.fill('#f-ideia', 'Uma borboleta'); g.click('.ops[data-nome=zona] button:nth-child(2)'); g.click('.ops[data-nome=local] button:nth-child(3)')
    with c.expect_page() as pop: g.click('[data-canal=wa]')
    u = unquote(pop.value.url).replace('+', ' '); pop.value.close()
    ok('whatsapp', '351936230331' in u and 'borboleta' in u and 'Antebraço' in u and 'Luxemburgo' in u and leg in u, u[:80])
    c.close()
    c = b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True); g = c.new_page()
    g.goto(URL); g.wait_for_timeout(2500)
    ok('video no celular', g.evaluate("(()=>{const v=document.querySelector('#fio-v');return !!v&&!v.paused&&v.loop&&v.muted})()"))
    g.tap('.menu-bt'); g.wait_for_timeout(200)
    ok('menu abre', not g.evaluate("document.querySelector('#menu').hidden"))
    g.tap('.menu a[href="#sobre"]'); g.wait_for_timeout(1200)
    ok('menu fecha e rola', g.evaluate("document.querySelector('#menu').hidden && scrollY>500"))
    c.close()
    c = b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True); g = c.new_page()
    g.add_init_script("HTMLMediaElement.prototype.play=function(){return Promise.reject(new DOMException('x','NotAllowedError'))}")
    g.goto(URL); g.wait_for_timeout(1500)
    ok('pouca energia cai no shader', g.evaluate("!document.querySelector('#fio-v') && document.querySelector('#fio').width>300"))
    c.close()
    print('FUNCIONAL', sum(R), '/', len(R))
    b.close()
