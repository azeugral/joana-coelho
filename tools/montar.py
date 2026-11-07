# -*- coding: utf-8 -*-
"""Monta index.html a partir de tools/modelo.html + dados.py, com previa embutida em cada foto. Uso: python tools/montar.py"""
import base64, html, io, json, sys, time
from pathlib import Path
from PIL import Image
S = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(S / 'tools'))
import dados


def previa(f):
    i = Image.open(f).convert('RGB').resize((16, 20), Image.LANCZOS)
    b = io.BytesIO(); i.save(b, 'WEBP', quality=36)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()


def ops(lista):
    return ''.join(f'<button type="button" role="radio" aria-checked="false">{x}</button>' for x in lista)


def tile(i, p):
    a, cat, leg = p
    e = html.escape(leg, quote=True)
    return (f'<button class="peca" type="button" data-i="{i}" data-cat="{cat}" aria-label="Abrir: {e}" style="background-image:url({previa(S / f"assets/img/p/{a}.webp")})">'
            f'<img src="assets/img/p/{a}.webp?v={{{{V}}}}" alt="{e}" width="720" height="900" loading="lazy" draggable="false"></button>')


jc = (S / 'assets/img/jc.svg').read_text(encoding='utf8').replace('<svg ', '<svg aria-hidden="true" focusable="false" ')
filtros = ''.join(f'<button type="button" data-cat="{c}" aria-pressed="{"true" if c == "todas" else "false"}">{n}</button>' for c, n in dados.CATS)
pecas = [dict(id=p[0], leg=p[2]) for p in dados.P]
h = (S / 'tools/modelo.html').read_text(encoding='utf8')
for k, v in {
    '{{JC}}': jc, '{{FILTROS}}': filtros, '{{GRADE}}': ''.join(tile(i, p) for i, p in enumerate(dados.P)),
    '{{PECAS}}': json.dumps(pecas, ensure_ascii=False),
    '{{ZONAS}}': ops(['Braço', 'Antebraço', 'Mão', 'Costas', 'Peito', 'Perna', 'Pescoço', 'Outra']),
    '{{TAMANHOS}}': ops(['Até 5 cm', '5 a 10 cm', '10 a 20 cm', 'Maior']),
    '{{LOCAIS}}': ops(['Leça da Palmeira', 'Santa Maria da Feira', 'Luxemburgo']),
}.items():
    h = h.replace(k, v)
h = h.replace('{{V}}', str(int(time.time()) // 60))
(S / 'index.html').write_text(h, encoding='utf8')
print('index.html', round(len(h) / 1024), 'KB')
