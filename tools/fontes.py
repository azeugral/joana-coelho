# -*- coding: utf-8 -*-
"""Baixa Fahkwang e Gantari do Google Fonts (woff2 latin + latin-ext)."""
import re, urllib.request, pathlib
O = pathlib.Path(__file__).resolve().parent.parent / 'assets/fonts'; O.mkdir(parents=True, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'}
for fam, q in (('Fahkwang', 'ital,wght@0,300;0,400;1,300'), ('Gantari', 'wght@300..600')):
    css = urllib.request.urlopen(urllib.request.Request(f'https://fonts.googleapis.com/css2?family={fam}:{q}&display=swap', headers=UA)).read().decode()
    for sub, b in re.findall(r'/\* ([\w-]+) \*/\s*@font-face \{(.*?)\}', css, re.S):
        if sub not in ('latin', 'latin-ext'):
            continue
        st = re.search(r'font-style: (\w+)', b).group(1); wg = re.search(r'font-weight: ([\d ]+)', b).group(1).strip().replace(' ', '-')
        u = re.search(r'url\((.*?)\)', b).group(1)
        n = f'{fam.lower()}-{wg}{"i" if st == "italic" else ""}-{sub}.woff2'
        (O / n).write_bytes(urllib.request.urlopen(urllib.request.Request(u, headers=UA)).read()); print(n, (O / n).stat().st_size // 1024)
