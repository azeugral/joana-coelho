(function () {
  const $ = (s, r) => (r || document).querySelector(s), $$ = (s, r) => [...(r || document).querySelectorAll(s)];
  document.documentElement.classList.add('js');
  const calmo = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- hero ---------- */
  const hero = $('.hero'), cv = $('#fio'), vid = $('#fio-v');
  let motor = null, rodando = false, visivel = true, t0 = 0, intro = 0, HW = 0, HH = 0;
  const mede = () => { const r = hero.getBoundingClientRect(); HW = r.width; HH = r.height; };
  function quadro(now) {
    if (!rodando) return;
    requestAnimationFrame(quadro);
    if (!t0) t0 = now;
    const s = (now - t0) / 1000;
    const dpr = Math.min(devicePixelRatio || 1, 2);
    motor.desenha(calmo ? 4 : s, HW, HH, dpr, calmo ? 2 : Math.min(2, s * 1.1));
  }
  const liga = () => { if (motor && !rodando && visivel && !document.hidden) { rodando = true; requestAnimationFrame(quadro); } };
  const desliga = () => { rodando = false; };

  async function iniciaShader(tInicial) {
    try {
      motor = window.fioHero(cv);
      if (!motor) throw 0;
      mede();
      const [meta, buf] = await Promise.all([fetch('assets/hero/fio.json').then(r => r.json()), fetch('assets/hero/fio.bin').then(r => r.arrayBuffer())]);
      motor.pontos(buf, meta);
      meta.fig.forEach((f, i) => { if (!f.tex) return; const m = new Image(); m.src = `assets/hero/${f.tex}.webp`; m.decode().then(() => motor.textura(i, m)).catch(() => {}); });
      if (tInicial) t0 = performance.now() - tInicial * 1000;
      liga();
      new ResizeObserver(() => { const l = HW; mede(); if (Math.abs(l - HW) > 1 && !rodando) motor.desenha(4, HW, HH, Math.min(devicePixelRatio || 1, 2), 2); }).observe(hero);
      new IntersectionObserver(e => { visivel = e[0].isIntersecting; visivel ? liga() : desliga(); }).observe(hero);
      document.addEventListener('visibilitychange', () => document.hidden ? desliga() : liga());
    } catch (e) { hero.style.background = 'var(--parede) url(assets/img/hero-pe.webp) center/cover'; }
  }
  const usaVideo = matchMedia('(pointer:coarse)').matches && innerWidth / innerHeight < .62;
  if (usaVideo && !calmo) {
    vid.hidden = false; cv.style.display = 'none';
    vid.src = 'assets/video/hero-pe.mp4';
    const p = vid.play();
    /* Pouca Energia no iOS recusa o play: entra o mesmo hero em shader */
    if (p) p.catch(() => { vid.remove(); cv.style.display = ''; iniciaShader(); });
  } else { vid.remove(); iniciaShader(); }

  /* ---------- topo e menu ---------- */
  const topo = $('.topo'), menu = $('#menu'), mbt = $('.menu-bt');
  const solido = () => topo.classList.toggle('solido', scrollY > innerHeight * .82 || !menu.hidden);
  addEventListener('scroll', solido, { passive: true }); solido();
  const abreMenu = a => { menu.hidden = !a; mbt.setAttribute('aria-expanded', a); mbt.textContent = a ? 'Fechar' : 'Menu'; document.body.style.overflow = a ? 'hidden' : ''; solido(); };
  mbt.addEventListener('click', () => abreMenu(menu.hidden));
  $$('a', menu).forEach(a => a.addEventListener('click', () => abreMenu(false)));
  addEventListener('keydown', e => { if (e.key === 'Escape' && !menu.hidden) abreMenu(false); });

  /* ---------- entrada ---------- */
  const alvos = $$('.fio-v,.cab h2,.cab>p,.assinatura blockquote,.assin-sub,.sobre-foto,.sobre-txt>*:not(.fio-v),.exp article,.acad-fotos img,.acad-cols article,.est-fotos img,.est-cols article,.agenda figure,.agenda>div>*:not(.fio-v),.vozes blockquote,.passos fieldset');
  alvos.forEach(e => { if (!e.classList.contains('fio-v')) e.classList.add('rv'); });
  if ('IntersectionObserver' in window && !calmo) {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('ve'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -6% 0px' });
    alvos.forEach(e => io.observe(e));
  } else alvos.forEach(e => e.classList.add('ve'));

  /* ---------- portfolio ---------- */
  const P = window.PECAS, grade = $('#grade'), tiles = $$('.peca', grade), maisBt = $('#ver-todos');
  let cat = 'todas', todos = false, lista = [];
  const limite = () => (innerWidth <= 640 ? 8 : innerWidth <= 960 ? 9 : 12);
  function mostra() {
    lista = [];
    const lim = limite();
    tiles.forEach(t => {
      const ok = cat === 'todas' || t.dataset.cat === cat;
      const pos = lista.length;
      const v = ok && (cat !== 'todas' || todos || pos < lim);
      t.hidden = !v;
      if (ok && v) lista.push(+t.dataset.i);
    });
    maisBt.parentElement.hidden = cat !== 'todas' || todos;
  }
  mostra();
  addEventListener('resize', () => { if (!todos) mostra(); }, { passive: true });
  $$('.filtros button').forEach(b => b.addEventListener('click', () => {
    $$('.filtros button').forEach(x => x.setAttribute('aria-pressed', x === b)); cat = b.dataset.cat; todos = false; mostra();
  }));
  maisBt.addEventListener('click', () => { todos = true; mostra(); });

  /* ---------- lightbox ---------- */
  const lb = $('#lb'), lbImg = $('#lb-img'), lbLeg = $('#lb-leg');
  let at = 0, volta = null;
  function vai(i) {
    at = (i + lista.length) % lista.length;
    const p = P[lista[at]];
    lbImg.src = `assets/img/o/${p.id}.webp`; lbImg.alt = p.leg; lbLeg.textContent = p.leg;
    const n = P[lista[(at + 1) % lista.length]]; new Image().src = `assets/img/o/${n.id}.webp`;
  }
  const abre = i => { volta = document.activeElement; lb.hidden = false; document.body.style.overflow = 'hidden'; vai(i); $('.lb-x').focus(); };
  const fecha = () => { lb.hidden = true; document.body.style.overflow = ''; lbImg.removeAttribute('src'); if (volta) volta.focus({ preventScroll: true }); };
  tiles.forEach(t => t.addEventListener('click', () => abre(lista.indexOf(+t.dataset.i))));
  $('.lb-x').addEventListener('click', fecha);
  $('.lb-e').addEventListener('click', () => vai(at - 1));
  $('.lb-d').addEventListener('click', () => vai(at + 1));
  lb.addEventListener('click', e => { if (e.target === lb) fecha(); });
  addEventListener('keydown', e => {
    if (lb.hidden) return;
    if (e.key === 'Escape') fecha();
    if (e.key === 'ArrowLeft') vai(at - 1);
    if (e.key === 'ArrowRight') vai(at + 1);
    if (e.key === 'Tab') {
      const f = $$('button', lb), i = f.indexOf(document.activeElement);
      e.preventDefault(); f[(i + (e.shiftKey ? -1 : 1) + f.length) % f.length].focus();
    }
  });
  let tx = null;
  lb.addEventListener('touchstart', e => { tx = e.touches.length === 1 ? e.touches[0].clientX : null; }, { passive: true });
  lb.addEventListener('touchend', e => { if (tx === null) return; const d = e.changedTouches[0].clientX - tx; if (Math.abs(d) > 48) vai(at + (d < 0 ? 1 : -1)); tx = null; }, { passive: true });

  /* ---------- pedido ---------- */
  const form = $('#form'), escolha = {};
  let ref = '';
  $$('.ops').forEach(g => {
    const bs = $$('button', g), nome = g.dataset.nome;
    bs.forEach((b, i) => {
      b.setAttribute('tabindex', i ? '-1' : '0');
      const marca = () => { const novo = b.getAttribute('aria-checked') !== 'true'; bs.forEach(x => x.setAttribute('aria-checked', 'false')); b.setAttribute('aria-checked', novo); escolha[nome] = novo ? b.textContent : ''; bs.forEach(x => x.tabIndex = -1); b.tabIndex = 0; };
      b.addEventListener('click', marca);
      b.addEventListener('keydown', e => {
        const d = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[e.key];
        if (d) { e.preventDefault(); const n = bs[(i + d + bs.length) % bs.length]; n.focus(); n.click(); }
      });
    });
  });
  $('#lb-quero').addEventListener('click', () => {
    const p = P[lista[at]]; ref = p.leg; const r = $('#f-ref'); r.hidden = false; r.textContent = 'Referência escolhida: ' + p.leg;
    fecha(); $('#marcar').scrollIntoView();
  });
  $$('[data-assunto]').forEach(a => a.addEventListener('click', () => { const i = $('#f-ideia'); if (!i.value) i.value = 'Quero saber mais sobre os workshops da J.CO Fineline Academy.'; }));
  function mensagem() {
    const v = n => form.elements[n].value.trim(), L = ['Olá Joana!'];
    if (v('nome')) L.push('Chamo-me ' + v('nome') + '.');
    if (v('ideia')) L.push('Ideia: ' + v('ideia'));
    if (ref) L.push('Referência: ' + ref + ' (site)');
    if (escolha.zona) L.push('Zona: ' + escolha.zona);
    if (escolha.tamanho) L.push('Tamanho: ' + escolha.tamanho);
    if (escolha.local) L.push('Onde: ' + escolha.local);
    if (v('dia')) L.push('Disponibilidade: ' + v('dia'));
    return L.join('\n');
  }
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const canal = e.submitter && e.submitter.dataset.canal, erro = $('#f-erro'), ok = form.elements.nome.value.trim() && (form.elements.ideia.value.trim() || ref);
    erro.hidden = !!ok;
    if (!ok) { (form.elements.nome.value.trim() ? form.elements.ideia : form.elements.nome).focus(); return; }
    const m = mensagem();
    if (canal === 'ig') {
      try { await navigator.clipboard.writeText(m); $('#f-copia').hidden = false; } catch (x) {}
      window.open('https://ig.me/m/joanacoelho.tattoo', '_blank', 'noopener');
    } else window.open('https://wa.me/351936230331?text=' + encodeURIComponent(m), '_blank', 'noopener');
  });
})();
