/* A linha nunca levanta.
   Um unico fio de N pontos cai no eixo do hero, escreve a assinatura da Joana, volta a ser fio e tece as tatuagens dela;
   em cada figura a tinta verdadeira assenta por onde a agulha passou. Luz de janela na parede, como nos stories dela.
   WebGL2 no computador; o MP4 do celular e gravado desta mesma funcao (tools/gerar_video.py). */
(function () {
  const VS_TELA = `#version 300 es
  out vec2 v; void main(){ vec2 p=vec2((gl_VertexID<<1)&2, gl_VertexID&2); v=p; gl_Position=vec4(p*2.-1.,0,1); }`;

  /* parede + luz de janela */
  const FS_PAREDE = `#version 300 es
  precision highp float; in vec2 v; out vec4 C;
  uniform vec2 R; uniform vec2 ciclo; uniform float grao;
  float h(vec2 p){ p=fract(p*vec2(123.34,456.21)); p+=dot(p,p+45.32); return fract(p.x*p.y); }
  float n(vec2 p){ vec2 i=floor(p),f=fract(p); f=f*f*(3.-2.*f); return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y); }
  float fbm(vec2 p){ float a=.5,s=0.; for(int i=0;i<4;i++){ s+=a*n(p); p=p*2.03+7.1; a*=.5; } return s; }
  float caixa(vec2 p, vec2 c, vec2 m, float b){ vec2 d=abs(p-c)-m; return smoothstep(b,-b,max(d.x,d.y)); }
  void main(){
    float M=min(R.x,R.y); vec2 p=(v*R-.5*R)/M;
    vec2 q=p;
    float ret=R.x/R.y;
    /* a janela entra de baixo, inclinada; em retrato sobe para caber */
    mat2 r=mat2(.86,-.5,.5,.86);
    vec2 w=r*(q-vec2(.34*min(ret,1.6),-.42)+.018*ciclo);
    w.x+=w.y*.34;
    float b=.028+.05*smoothstep(-.2,.6,-w.y);
    float luz=0.;
    for(int i=0;i<3;i++) for(int j=0;j<2;j++){
      vec2 c=vec2(-.46+float(i)*.47,.02+float(j)*.5);
      luz+=caixa(w,c,vec2(.215,.225),b);
    }
    /* sombra de folhas balancando */
    vec2 f=q*2.3+vec2(.22*ciclo.x,.16*ciclo.y);
    float fol=smoothstep(.40,.62,fbm(f+vec2(fbm(f*1.7+ciclo*.3),0.)*1.3));
    luz*=1.-.52*fol;
    float vinh=smoothstep(1.5,.2,length(p*vec2(.74,1.)));
    vec3 sombra=vec3(.694,.640,.586), claro=vec3(.962,.930,.884);
    float base=.30+.32*vinh+.06*fbm(q*1.1+3.);
    vec3 col=mix(sombra,claro,clamp(base+.62*luz,0.,1.));
    /* reboco fino */
    col*=1.+grao*(.05*(fbm(v*R/2.6)-.5)+.02*(h(v*R)-.5));
    C=vec4(col,1);
  }`;

  /* tinta real: R=densidade, G=instante em que a agulha passa */
  const VS_TINTA = `#version 300 es
  in vec2 a; out vec2 v; uniform vec4 Q; /* cx cy sx sy em clip */
  void main(){ v=a; gl_Position=vec4(Q.xy+(a*2.-1.)*Q.zw*vec2(1,-1),0,1); }`;
  const FS_TINTA = `#version 300 es
  precision highp float; in vec2 v; out vec4 C; uniform sampler2D T; uniform float r; uniform vec3 cor;
  void main(){ vec4 t=texture(T,v); float k=smoothstep(t.g,t.g+.035,r*1.04); float a=t.r*k; C=vec4(cor*a,a); }`;

  /* fio: fita de N pontos, ler a textura de pontos */
  const VS_FIO = `#version 300 es
  precision highp float; precision highp sampler2DArray;
  uniform sampler2DArray P; uniform float N,fig,w,gota,rasto,larg,proprio; uniform vec2 R,cc,off,faixa; uniform float sc,t; uniform float inicio;
  out float l; out float af;
  const int W=1024;
  vec2 fio0(float s){ /* o fio em repouso: reta no eixo, respirando pouco */
    float y=mix(-R.y*.56,R.y*.56,s);
    float e=smoothstep(0.,.12,s)*smoothstep(1.,.88,s);
    float x=e*(sin(s*9.+t*1.3)*.0065+sin(s*23.-t*1.9)*.0022)*R.y*(1.-pow(abs(w*2.-1.),3.));
    return vec2(x,y);
  }
  vec4 ponto(int i){ return texelFetch(P,ivec3(i%W,i/W,int(fig)),0); }
  vec2 pos(int i, out float pe, out float wd){
    i=clamp(i,0,int(N)-1);
    vec4 d=ponto(i); float s=float(i)/(N-1.);
    pe=d.w; wd=d.z;
    /* onda ao longo do fio: comeca por cima */
    float u=clamp((w*1.5-s*.5),0.,1.); u=u*u*(3.-2.*u);
    vec2 a=fio0(s), b=d.xy*vec2(1,-1)*sc;
    float cur=sin(u*3.1416);
    vec2 c=vec2(sin(s*40.+t)+sin(s*97.-t*.7),cos(s*33.-t*.8))*cur*.012*R.y;
    return mix(a,b,u)+c;
  }
  void main(){
    int id=gl_VertexID/2; float lado=float(gl_VertexID&1)*2.-1.;
    float pe,wd,x1,x2; vec2 p=pos(id,pe,wd), a=pos(id-3,x1,x2), b=pos(id+3,x1,x2);
    vec2 d=b-a; float L=length(d); d=L>1e-4?d/L:vec2(0,1);
    float s0=float(id)/(N-1.); float u0=clamp((w*1.5-s0*.5),0.,1.); u0=u0*u0*(3.-2.*u0);
    float pr=proprio*wd*sc/500.*u0*u0; /* largura propria, so na assinatura */
    float meia=max(larg,pr*.92)+.32;
    vec2 n=vec2(-d.y,d.x);
    vec2 q=p+cc+n*lado*meia+off;
    /* cai do alto no comeco */
    float yt=(R.y*.56-p.y)/(R.y*1.12);
    float vis=smoothstep(gota,gota-.02,yt);
    /* no celular o fio passa por tras do nome e dos botoes: fica so na faixa da arte */
    float yTela=.5-(p.y+cc.y)/R.y;
    vis*=smoothstep(faixa.x,faixa.x+.03,yTela)*smoothstep(faixa.y,faixa.y-.03,yTela);
    l=lado*meia;
    af=vis*mix(1.,pe,smoothstep(.75,.98,w))*rasto;
    /* fita: vale o meia em px */
    gl_Position=vec4(q/(R*.5),0,1);
    gl_Position.xy*=1.;
    v_m=meia;
  }`.replace('out float l; out float af;', 'out float l; out float af; out float v_m;');
  const FS_FIO = `#version 300 es
  precision highp float; in float l; in float af; in float v_m; out vec4 C; uniform vec3 cor; uniform float suave;
  void main(){ float d=v_m-abs(l); float a=clamp(d/suave,0.,1.)*af; if(a<.004) discard; C=vec4(cor*a,a); }`;

  function prog(gl, vs, fs) {
    const p = gl.createProgram();
    for (const [t, s] of [[gl.VERTEX_SHADER, vs], [gl.FRAGMENT_SHADER, fs]]) {
      const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o);
      if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o));
      gl.attachShader(p, o);
    }
    gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
    const u = {}; const n = gl.getProgramParameter(p, gl.ACTIVE_UNIFORMS);
    for (let i = 0; i < n; i++) { const a = gl.getActiveUniform(p, i); u[a.name] = gl.getUniformLocation(p, a.name); }
    return { p, u };
  }

  /* tempo: 4 figuras, D segundos cada */
  const D = 8;
  const CICLO = D * 4;
  const liso = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
  const lento = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * t * (t * (6 * t - 15) + 10); };
  function estado(T) {
    const t = ((T % CICLO) + CICLO) % CICLO, f = Math.floor(t / D), s = t - f * D;
    const tece = lento(0, 2.2, s), desfia = lento(D - 2, D - .05, s);
    const w = tece * (1 - desfia);
    if (f === 0) return { f, w, r: 0, rasto: 1 };       /* assinatura: so o fio */
    const r = liso(1.5, 3.3, s) * (1 - liso(D - 3, D - 2, s));
    const rasto = 1 - liso(2.7, 3.5, s) * (1 - liso(D - 3.3, D - 2.6, s));
    return { f, w, r, rasto };
  }

  /* Onde a arte fica. Tudo no eixo. Vale tambem para o MP4. */
  function moldura(W, H, dados) {
    const larga = W / H > 1.05;
    const cy = larga ? H * .47 : H * .555;
    const sc = larga ? H * .36 : Math.min(H * .25, W * .62);
    const lim = W * (larga ? .24 : .44);
    return { cx: W / 2, cy, sc, lim, faixa: larga ? [-1, 2] : [.27, .86] };
  }

  window.fioHero = function (canvas, op) {
    op = op || {};
    const gl = canvas.getContext('webgl2', { alpha: false, antialias: false, premultipliedAlpha: false, preserveDrawingBuffer: !!op.guardar, powerPreference: 'high-performance' });
    if (!gl) return null;
    const parede = prog(gl, VS_TELA, FS_PAREDE), tinta = prog(gl, VS_TINTA, FS_TINTA), fio = prog(gl, VS_FIO, FS_FIO);
    const vazio = gl.createVertexArray();
    const vaoQ = gl.createVertexArray(); gl.bindVertexArray(vaoQ);
    const bq = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, bq);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([0, 0, 1, 0, 0, 1, 1, 1]), gl.STATIC_DRAW);
    const la = gl.getAttribLocation(tinta.p, 'a'); gl.enableVertexAttribArray(la); gl.vertexAttribPointer(la, 2, gl.FLOAT, false, 0, 0);
    gl.bindVertexArray(null);
    let N = 0, meta = null; const tex = [], pronto = { pontos: false };
    let texP = null;

    function pontos(buf, m) {
      meta = m; N = m.n; const k = m.fig.length, dv = new DataView(buf);
      const Wt = 1024, Ht = Math.ceil(N / Wt), arr = new Float32Array(Wt * Ht * k * 4);
      for (let f = 0; f < k; f++) {
        const o = f * N * 6;
        for (let i = 0; i < N; i++) {
          const j = (f * Wt * Ht + i) * 4;
          arr[j] = dv.getInt16(o + i * 4, true) / 16000;
          arr[j + 1] = dv.getInt16(o + i * 4 + 2, true) / 16000;
          arr[j + 2] = dv.getUint8(o + N * 4 + i) / 32;
          arr[j + 3] = dv.getUint8(o + N * 5 + i);
        }
      }
      texP = gl.createTexture(); gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D_ARRAY, texP);
      gl.texImage3D(gl.TEXTURE_2D_ARRAY, 0, gl.RGBA32F, Wt, Ht, k, 0, gl.RGBA, gl.FLOAT, arr);
      gl.texParameteri(gl.TEXTURE_2D_ARRAY, gl.TEXTURE_MIN_FILTER, gl.NEAREST); gl.texParameteri(gl.TEXTURE_2D_ARRAY, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
      pronto.pontos = true;
    }
    function textura(i, img) {
      const t = gl.createTexture(); gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, t);
      gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL, gl.NONE);
      gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
      gl.generateMipmap(gl.TEXTURE_2D);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      const an = gl.getExtension('EXT_texture_filter_anisotropic'); if (an) gl.texParameterf(gl.TEXTURE_2D, an.TEXTURE_MAX_ANISOTROPY_EXT, 8);
      tex[i] = t;
    }

    function desenha(T, Wc, Hc, dpr, gota, grao) {
      const W = Math.round(Wc * dpr), H = Math.round(Hc * dpr);
      if (canvas.width !== W || canvas.height !== H) { canvas.width = W; canvas.height = H; }
      gl.viewport(0, 0, W, H);
      gl.disable(gl.BLEND);
      const a = 2 * Math.PI * T / CICLO;
      gl.useProgram(parede.p); gl.bindVertexArray(vazio);
      gl.uniform2f(parede.u.R, W, H); gl.uniform2f(parede.u.ciclo, Math.cos(a), Math.sin(a)); gl.uniform1f(parede.u.grao, grao === undefined ? 1 : grao);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      if (!pronto.pontos) return;
      const e = estado(T), mf = meta.fig[e.f], asp = mf.asp;
      const m = moldura(Wc, Hc);
      /* escala propria: nenhuma figura passa do limite lateral */
      let sc = m.sc * dpr;
      if (e.f === 0) sc = Math.min(sc * 1.32, m.lim * dpr / .62);
      else sc = Math.min(sc, m.lim * dpr / asp);
      gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
      const cx = 0, cy = (H / 2 - m.cy * dpr);
      if (mf.tex && e.r > .001 && tex[e.f]) {
        gl.useProgram(tinta.p); gl.bindVertexArray(vaoQ);
        gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, tex[e.f]); gl.uniform1i(tinta.u.T, 1);
        gl.uniform4f(tinta.u.Q, 0, cy / (H / 2), sc * asp / (W / 2), sc / (H / 2));
        gl.uniform1f(tinta.u.r, e.r); gl.uniform3f(tinta.u.cor, .105, .09, .08);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
      }
      gl.useProgram(fio.p); gl.bindVertexArray(vazio);
      gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D_ARRAY, texP); gl.uniform1i(fio.u.P, 0);
      const un = fio.u;
      gl.uniform1f(un.N, N); gl.uniform1f(un.proprio, e.f === 0 ? 1 : 0); gl.uniform1f(un.fig, e.f); gl.uniform1f(un.w, e.w); gl.uniform1f(un.t, T * 2 * Math.PI / CICLO * 4);
      gl.uniform2f(un.R, W, H); gl.uniform2f(un.cc, cx, cy); gl.uniform1f(un.sc, sc); gl.uniform1f(un.gota, gota === undefined ? 2 : gota); gl.uniform2f(un.faixa, m.faixa[0], m.faixa[1]);
      gl.uniform1f(fio.u.suave, 1.4);
      if (e.rasto > .002) {
        /* sombra do fio na parede */
        gl.uniform2f(un.off, 2 * dpr, -3 * dpr); gl.uniform1f(un.larg, 1.4 * dpr); gl.uniform1f(un.rasto, e.rasto * .08);
        gl.uniform3f(fio.u.cor, .22, .16, .12); gl.uniform1f(fio.u.suave, 2.6 * dpr);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, N * 2);
        gl.uniform2f(un.off, 0, 0); gl.uniform1f(un.larg, .46 * dpr + .08); gl.uniform1f(un.rasto, e.rasto);
        gl.uniform1f(fio.u.suave, 1.4);
        /* a assinatura e dourada; a tatuagem, tinta */
        const o = e.f === 0 ? e.w : 0;
        gl.uniform3f(fio.u.cor, .105 + o * .36, .09 + o * .30, .08 + o * .10);
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, N * 2);
      }
    }

    return { desenha, pontos, textura, ciclo: CICLO, gl };
  };
  window.fioCiclo = CICLO;
})();
