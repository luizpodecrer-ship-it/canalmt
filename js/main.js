/* ==========================================================================
   CanalMT — comportamentos da página (JavaScript puro, sem biblioteca)
   Cada bloco é independente e só roda se o elemento existir na página.
   ========================================================================== */
(function () {
  'use strict';
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var raiz = document.documentElement;
  var poucoMovimento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var guarda = {
    ler: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    por: function (k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  /* --- Tema claro / escuro ------------------------------------------------ */
  (function () {
    var salvo = guarda.ler('canalmt-tema');
    if (salvo) raiz.setAttribute('data-theme', salvo);
    else if (!raiz.hasAttribute('data-theme')) {
      raiz.setAttribute('data-theme', window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    }
    $$('[data-tema]').forEach(function (b) {
      b.addEventListener('click', function () {
        var novo = raiz.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        raiz.setAttribute('data-theme', novo);
        guarda.por('canalmt-tema', novo);
      });
    });
  })();

  /* --- Data e hora (fuso de Cuiabá), atualizadas a cada meio minuto ------- */
  (function () {
    function fmt(o) { o.timeZone = 'America/Cuiaba'; return new Intl.DateTimeFormat('pt-BR', o); }
    function maiuscula(t) { return t.charAt(0).toUpperCase() + t.slice(1); }
    function escrever() {
      try {
        var agora = new Date();
        var longa = fmt({ weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' }).format(agora);
        var curta = fmt({ weekday: 'short', day: 'numeric', month: 'short' }).format(agora).replace(/\./g, '').replace(' de ', ' ');
        var hora = fmt({ hour: '2-digit', minute: '2-digit' }).format(agora);
        $$('[data-data-longa]').forEach(function (e) { e.textContent = maiuscula(longa); });
        $$('[data-data-curta]').forEach(function (e) { e.textContent = maiuscula(curta); });
        $$('[data-hora]').forEach(function (e) { e.textContent = hora; });
        $$('[data-hoje]').forEach(function (e) { e.textContent = 'Cuiabá, ' + fmt({ day: 'numeric', month: 'long', year: 'numeric' }).format(agora); });
        $$('[data-ano]').forEach(function (e) { e.textContent = fmt({ year: 'numeric' }).format(agora); });
      } catch (e) {}
    }
    escrever();
    setInterval(escrever, 30000);
  })();

  /* --- Menu do celular (gaveta) ------------------------------------------- */
  (function () {
    var gaveta = $('[data-gaveta]');
    if (!gaveta) return;
    var quemAbriu = null;
    function abrir(foco) {
      gaveta.setAttribute('data-aberta', '');
      document.body.style.overflow = 'hidden';
      $$('[data-abre-menu]').forEach(function (b) { b.setAttribute('aria-expanded', 'true'); });
      var alvo = foco === 'busca' ? $('input', gaveta) : $('[data-fecha-menu].btn-icone', gaveta);
      setTimeout(function () { alvo && alvo.focus(); }, 120);
    }
    function fechar() {
      gaveta.removeAttribute('data-aberta');
      document.body.style.overflow = '';
      $$('[data-abre-menu]').forEach(function (b) { b.setAttribute('aria-expanded', 'false'); });
      quemAbriu && quemAbriu.focus();
    }
    $$('[data-abre-menu]').forEach(function (b) {
      b.addEventListener('click', function () { quemAbriu = b; abrir(b.getAttribute('data-abre-menu')); });
    });
    $$('[data-fecha-menu]', gaveta).forEach(function (b) { b.addEventListener('click', fechar); });
    document.addEventListener('keydown', function (e) {
      if (!gaveta.hasAttribute('data-aberta')) return;
      if (e.key === 'Escape') fechar();
      if (e.key === 'Tab') {              // o foco não sai da gaveta
        var itens = $$('a, button, input', gaveta);
        var pri = itens[0], ult = itens[itens.length - 1];
        if (e.shiftKey && document.activeElement === pri) { e.preventDefault(); ult.focus(); }
        else if (!e.shiftKey && document.activeElement === ult) { e.preventDefault(); pri.focus(); }
      }
    });
  })();

  /* --- Cabeçalho some ao descer e volta ao subir (celular) ---------------- */
  (function () {
    var cab = $('[data-cabecalho]'), subir = $('[data-subir]');
    var ultimo = 0, marcado = false;
    function ler() {
      var y = window.scrollY;
      if (cab) cab.classList.toggle('escondido', y > 160 && y > ultimo && window.innerWidth < 900);
      if (subir) subir.classList.toggle('visivel', y > 700);
      ultimo = y; marcado = false;
    }
    window.addEventListener('scroll', function () { if (!marcado) { marcado = true; requestAnimationFrame(ler); } }, { passive: true });
    if (subir) subir.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: poucoMovimento ? 'auto' : 'smooth' }); });
  })();

  /* --- Letreiro das últimas notícias --------------------------------------
     Duplica a lista para o movimento não ter emenda; a velocidade é a mesma
     com poucas ou muitas notícias. Para ao passar o mouse ou focar. */
  (function () {
    var t = $('[data-letreiro]');
    if (!t || poucoMovimento) return;
    $$('li', t).forEach(function (li) {
      var c = li.cloneNode(true);
      c.setAttribute('aria-hidden', 'true');
      $$('a', c).forEach(function (a) { a.tabIndex = -1; });
      t.appendChild(c);
    });
    t.style.setProperty('--duracao', Math.round(t.scrollWidth / 2 / 55) + 's');
  })();

  /* --- Carrossel de destaques ----------------------------------------------
     A rolagem é nativa (arrasta com o dedo); o script só cuida das setas,
     dos pontos e da troca automática, que para quando a pessoa interage. */
  $$('[data-destaque]').forEach(function (caixa) {
    var trilho = $('[data-trilho]', caixa), slides = $$('.slide', trilho), pontos = $('[data-pontos]', caixa);
    if (slides.length < 2) return;
    var atual = 0, relogio = null;
    function ir(i, suave) {
      atual = (i + slides.length) % slides.length;
      trilho.scrollTo({ left: atual * trilho.clientWidth, behavior: suave === false || poucoMovimento ? 'auto' : 'smooth' });
    }
    slides.forEach(function (_, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.setAttribute('aria-label', 'Destaque ' + (i + 1) + ' de ' + slides.length);
      b.addEventListener('click', function () { parar(); ir(i); });
      pontos.appendChild(b);
    });
    function marcar() {
      atual = Math.round(trilho.scrollLeft / trilho.clientWidth);
      $$('button', pontos).forEach(function (b, i) { b.setAttribute('aria-current', i === atual ? 'true' : 'false'); });
    }
    var espera;
    trilho.addEventListener('scroll', function () { clearTimeout(espera); espera = setTimeout(marcar, 60); }, { passive: true });
    marcar();
    function tocar() { if (!poucoMovimento && !relogio) relogio = setInterval(function () { ir(atual + 1); }, 6000); }
    function parar() { clearInterval(relogio); relogio = null; }
    var ant = $('[data-anterior]', caixa), prox = $('[data-proximo]', caixa);
    ant && ant.addEventListener('click', function () { parar(); ir(atual - 1); });
    prox && prox.addEventListener('click', function () { parar(); ir(atual + 1); });
    ['pointerdown', 'focusin', 'mouseenter'].forEach(function (ev) { caixa.addEventListener(ev, parar); });
    caixa.addEventListener('mouseleave', tocar);
    trilho.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); ir(atual + 1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); ir(atual - 1); }
    });
    window.addEventListener('resize', function () { ir(atual, false); });
    document.addEventListener('visibilitychange', function () { document.hidden ? parar() : tocar(); });
    tocar();
  });

  /* --- Filtros da seção Geral ----------------------------------------------
     Aqui o filtro age sobre as notícias já na página (data-cat). No WordPress
     pode continuar assim ou buscar por AJAX: basta trocar o conteúdo de
     [data-grade] e chamar de novo a função arrumar(). */
  $$('[data-geral]').forEach(function (sec) {
    var grade = $('[data-grade]', sec), vazio = $('[data-vazio]', sec), botoes = $$('[data-filtro]', sec);
    var MAX = 5;
    function arrumar(cat, nome, link) {
      var visiveis = 0;
      $$('.card', grade).forEach(function (c) {
        var mostra = (!cat || c.getAttribute('data-cat') === cat) && visiveis < MAX;
        c.hidden = !mostra;
        c.classList.remove('card--grande', 'card--lado', 'sem-linha', 'entra');
        if (!mostra) return;
        c.classList.add(visiveis === 0 ? 'card--grande' : 'card--lado');
        if (visiveis === 1) c.classList.add('sem-linha');
        void c.offsetWidth; c.classList.add('entra');
        c.style.animationDelay = (visiveis * 45) + 'ms';
        visiveis++;
      });
      vazio.hidden = visiveis > 0;
      if (!visiveis) {
        vazio.textContent = 'Nenhuma notícia de ' + nome + ' nesta página. ';
        if (link) { var a = document.createElement('a'); a.href = link; a.textContent = 'Ver tudo de ' + nome; vazio.appendChild(a); }
      }
    }
    botoes.forEach(function (b) {
      b.addEventListener('click', function () {
        botoes.forEach(function (o) { o.setAttribute('aria-pressed', o === b ? 'true' : 'false'); });
        arrumar(b.getAttribute('data-filtro'), b.textContent, b.getAttribute('data-link'));
      });
    });
    arrumar('');
    $$('.card', grade).forEach(function (c) { c.classList.remove('entra'); });   // sem animação na chegada
  });

  /* --- Vídeo: troca a capa pelo player só no toque -------------------------- */
  $$('[data-video]').forEach(function (v) {
    v.addEventListener('click', function (e) {
      var dentroDeMoldura = false;
      try { dentroDeMoldura = window.self !== window.top; } catch (x) { dentroDeMoldura = true; }
      if (dentroDeMoldura) return;        // em pré-visualização o link abre o YouTube
      e.preventDefault();
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + v.getAttribute('data-video') + '?autoplay=1&rel=0';
      f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
      f.title = $('.video__titulo', v).textContent;
      v.appendChild(f);
    });
  });

  /* --- Anúncio fixo do celular e aviso de cookies --------------------------- */
  (function () {
    var ancora = $('[data-ancora]');
    function altura() {
      var h = ancora && !ancora.hidden && window.innerWidth < 900 ? ancora.offsetHeight : 0;
      raiz.style.setProperty('--ancora', h + 'px');
    }
    if (ancora) {
      setTimeout(function () { ancora.hidden = false; altura(); }, 1500);
      $('[data-fecha-ancora]', ancora).addEventListener('click', function () { ancora.hidden = true; altura(); });
      window.addEventListener('resize', altura);
    }
    var ck = $('[data-cookies]');
    if (ck && !guarda.ler('canalmt-cookies')) {
      ck.hidden = false;
      $$('[data-cookies-ok]', ck).forEach(function (b) {
        b.addEventListener('click', function () { guarda.por('canalmt-cookies', b.getAttribute('data-cookies-ok')); ck.hidden = true; });
      });
    }
  })();
})();
