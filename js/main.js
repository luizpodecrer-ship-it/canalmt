/* ==========================================================================
   CanalMT — comportamentos da página (JavaScript puro, sem biblioteca)
   Cada bloco é independente e só roda se o elemento existir na página.
   Serve para todas as páginas: home, editorias, notícia, busca e institucionais.
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

  /* ==== Páginas internas ==================================================== */

  /* --- Aviso curto na parte de baixo da tela -------------------------------- */
  var avisoEl = null, avisoRelogio = null;
  function avisar(texto) {
    if (!avisoEl) {
      avisoEl = document.createElement('div');
      avisoEl.className = 'aviso';
      avisoEl.setAttribute('role', 'status');
      document.body.appendChild(avisoEl);
    }
    avisoEl.textContent = texto;
    avisoEl.classList.add('visivel');
    clearTimeout(avisoRelogio);
    avisoRelogio = setTimeout(function () { avisoEl.classList.remove('visivel'); }, 3400);
  }

  /* Links e botões que só existem na versão final (ex.: página 2 da editoria).
     No WordPress, tirar o atributo data-demo e deixar o link normal. */
  document.addEventListener('click', function (e) {
    var alvo = e.target.closest && e.target.closest('[data-demo]');
    if (!alvo) return;
    e.preventDefault();
    avisar(alvo.getAttribute('data-demo'));
  });

  function copiar(texto) {
    function falhou() { avisar('Não deu para copiar. Copie o endereço na barra do navegador.'); }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(texto).then(function () { avisar('Link copiado.'); }, falhou);
    } else falhou();
  }

  /* --- Barra de leitura da notícia ------------------------------------------ */
  (function () {
    var barra = $('[data-progresso]'), materia = $('[data-materia]');
    if (!barra || !materia) return;
    var marcado = false;
    function medir() {
      var r = materia.getBoundingClientRect(), vh = window.innerHeight;
      var feito = (vh * 0.35 - r.top) / Math.max(r.height - vh * 0.5, 1);
      barra.style.transform = 'scaleX(' + Math.min(1, Math.max(0, feito)) + ')';
      marcado = false;
    }
    window.addEventListener('scroll', function () { if (!marcado) { marcado = true; requestAnimationFrame(medir); } }, { passive: true });
    window.addEventListener('resize', medir);
    medir();
  })();

  /* --- Tempo de leitura (200 palavras por minuto) --------------------------- */
  $$('[data-tempo-leitura]').forEach(function (el) {
    var alvo = $(el.getAttribute('data-tempo-leitura'));
    if (!alvo) return;
    var palavras = alvo.textContent.trim().split(/\s+/).length;
    el.textContent = Math.max(1, Math.round(palavras / 200)) + ' min de leitura';
  });

  /* --- Compartilhar: os links recebem o endereço da página ao carregar ------ */
  (function () {
    var url = location.href.split('#')[0];
    var titulo = (($('h1') || {}).textContent || document.title).trim();
    var u = encodeURIComponent(url), t = encodeURIComponent(titulo);
    var destinos = {
      whatsapp: 'https://api.whatsapp.com/send?text=' + t + '%20' + u,
      facebook: 'https://www.facebook.com/sharer/sharer.php?u=' + u,
      x: 'https://twitter.com/intent/tweet?text=' + t + '&url=' + u,
      telegram: 'https://t.me/share/url?url=' + u + '&text=' + t
    };
    $$('a[data-rede]').forEach(function (a) { a.href = destinos[a.getAttribute('data-rede')]; });
    $$('[data-copiar-link]').forEach(function (b) {
      b.addEventListener('click', function () {
        if (navigator.share && window.matchMedia('(pointer: coarse)').matches) {
          navigator.share({ title: titulo, url: url }).catch(function () {});
        } else copiar(url);
      });
    });
  })();

  /* --- Tamanho do texto da notícia (fica guardado no navegador) ------------- */
  (function () {
    var texto = $('[data-texto-materia]');
    if (!texto) return;
    var passos = [16, 18, 20, 22, 24];
    var atual = passos.indexOf(parseInt(guarda.ler('canalmt-fonte'), 10));
    var botoes = $$('[data-fonte]');
    function aplicar(salvar) {
      if (atual >= 0) texto.style.setProperty('--tam', passos[atual] + 'px');
      botoes.forEach(function (b) {
        var d = +b.getAttribute('data-fonte');
        b.disabled = (d < 0 && atual === 0) || (d > 0 && atual === passos.length - 1);
      });
      if (salvar) guarda.por('canalmt-fonte', passos[atual]);
    }
    botoes.forEach(function (b) {
      b.addEventListener('click', function () {
        if (atual < 0) atual = window.innerWidth >= 760 ? 2 : 1;
        atual = Math.min(passos.length - 1, Math.max(0, atual + (+b.getAttribute('data-fonte'))));
        aplicar(true);
        avisar('Tamanho do texto: ' + (atual + 1) + ' de ' + passos.length);
      });
    });
    aplicar(false);
  })();

  /* --- WhatsApp com máscara (65) 99999-9999 ---------------------------------- */
  $$('input[data-zap]').forEach(function (c) {
    c.addEventListener('input', function () {
      var d = c.value.replace(/\D/g, '').slice(0, 11), s = d;
      if (d.length > 2) s = '(' + d.slice(0, 2) + ') ' + d.slice(2);
      if (d.length > 6) s = '(' + d.slice(0, 2) + ') ' + d.slice(2, d.length - 4) + '-' + d.slice(-4);
      c.value = s;
    });
  });

  /* --- Formulários (Contato e Anuncie) ---------------------------------------
     Confere os campos e mostra a confirmação. No WordPress, ligar ao plugin de
     formulários (ex.: Contact Form 7) mantendo os mesmos nomes de campo. */
  $$('form[data-formulario]').forEach(function (f) {
    f.setAttribute('novalidate', '');
    function valido(c) {
      var v = c.value.trim();
      if (c.type === 'checkbox') return c.checked;
      if (c.hasAttribute('data-zap')) return v === '' ? !c.required : v.replace(/\D/g, '').length === 11;
      if (!v) return !c.required;
      if (c.type === 'email') return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
      return true;
    }
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var primeiro = null;
      $$('[required], [data-zap]', f).forEach(function (c) {
        var ok = valido(c), caixa = c.closest('.campo, .aceite');
        if (caixa) caixa.classList.toggle('erro', !ok);
        c.setAttribute('aria-invalid', ok ? 'false' : 'true');
        if (!ok && !primeiro) primeiro = c;
      });
      if (primeiro) { primeiro.focus(); avisar('Confira os campos marcados em vermelho.'); return; }
      var ok = $('[data-form-ok]', f.parentNode);
      f.hidden = true;
      if (ok) { ok.hidden = false; ok.focus(); ok.scrollIntoView({ block: 'center', behavior: poucoMovimento ? 'auto' : 'smooth' }); }
    });
    f.addEventListener('input', function (e) {
      var caixa = e.target.closest('.campo, .aceite');
      if (caixa && valido(e.target)) { caixa.classList.remove('erro'); e.target.setAttribute('aria-invalid', 'false'); }
    });
    $$('[data-form-de-novo]', f.parentNode).forEach(function (b) {
      b.addEventListener('click', function () { f.reset(); f.hidden = false; b.closest('[data-form-ok]').hidden = true; $('input, select, textarea', f).focus(); });
    });
  });

  /* --- Página de busca --------------------------------------------------------
     Aqui a busca procura nas notícias de exemplo guardadas na própria página
     (#noticias). No WordPress, a lista vem da busca do próprio site (?s=). */
  (function () {
    var lista = $('[data-busca-lista]');
    if (!lista) return;
    var dados = JSON.parse($('#noticias').textContent);
    var campo = $('#busca-pagina'), resumo = $('[data-busca-resumo]');
    var filtros = $('[data-busca-filtros]'), mais = $('[data-busca-mais]');
    var termo = new URLSearchParams(location.search).get('s');
    if (termo === null) termo = campo.value; else campo.value = termo;
    var editoria = '', limite = 10;

    function norm(t) { return t.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase(); }
    function normLetra(t) { return Array.from(t).map(function (c) { var n = norm(c); return n.length === 1 ? n : c.toLowerCase(); }).join(''); }
    function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
    function marcar(texto, palavras) {
      var base = normLetra(texto), faixas = [], i = 0, saida = '';
      palavras.forEach(function (p) {
        var k = base.indexOf(p);
        while (k >= 0) { faixas.push([k, k + p.length]); k = base.indexOf(p, k + p.length); }
      });
      faixas.sort(function (a, b) { return a[0] - b[0]; }).forEach(function (f) {
        if (f[0] < i) return;
        saida += esc(texto.slice(i, f[0])) + '<mark>' + esc(texto.slice(f[0], f[1])) + '</mark>';
        i = f[1];
      });
      return saida + esc(texto.slice(i));
    }
    function cartao(n, palavras) {
      return '<article class="card card--linha' + (n.foto ? '' : ' sem-foto') + '">' +
        (n.foto ? '<div class="card__foto"><img src="' + esc(n.foto) + '" alt="" width="800" height="500" loading="lazy"></div>' : '') +
        '<div class="card__corpo"><div class="card__meta"><span class="chapeu chapeu--linha">' + esc(n.ed) + '</span>' +
        '<time class="data">' + esc(n.data) + '</time></div>' +
        '<h2 class="card__titulo"><a href="noticia.html">' + marcar(n.titulo, palavras) + '</a></h2>' +
        (n.resumo ? '<p class="card__resumo">' + marcar(n.resumo, palavras) + '</p>' : '') + '</div></article>';
    }
    function buscar() {
      var palavras = normLetra(termo.trim()).split(/\s+/).filter(function (p) { return p.length > 1; });
      var achados = !palavras.length ? [] : dados.filter(function (n) {
        var t = normLetra(n.titulo + ' ' + n.resumo + ' ' + n.ed);
        return palavras.every(function (p) { return t.indexOf(p) >= 0; });
      });
      var conta = {};
      achados.forEach(function (n) { conta[n.ed] = (conta[n.ed] || 0) + 1; });
      if (editoria && !conta[editoria]) editoria = '';
      var vistos = editoria ? achados.filter(function (n) { return n.ed === editoria; }) : achados;

      filtros.innerHTML = achados.length < 2 ? '' :
        ['<button class="filtro" type="button" data-ed="" aria-pressed="' + !editoria + '">Todas · ' + achados.length + '</button>']
          .concat(Object.keys(conta).map(function (k) {
            return '<button class="filtro" type="button" data-ed="' + esc(k) + '" aria-pressed="' + (editoria === k) + '">' + esc(k) + ' · ' + conta[k] + '</button>';
          })).join('');
      if (!palavras.length) resumo.textContent = 'Digite pelo menos duas letras para buscar.';
      else if (achados.length) resumo.innerHTML = '<b>' + achados.length + '</b> ' + (achados.length === 1 ? 'notícia encontrada' : 'notícias encontradas') + ' para <b>' + esc(termo.trim()) + '</b>';
      else resumo.textContent = '';

      if (palavras.length && !achados.length) {
        lista.innerHTML = '<div class="vazio"><h2>Nada encontrado para “' + esc(termo.trim()) + '”</h2>' +
          '<p>Confira se a palavra está certa, tente um termo mais curto ou navegue pelas editorias.</p>' +
          '<div class="subeditorias">' + $$('.editorias__lista a').slice(1, 7).map(function (a) {
            return '<a class="filtro" href="' + a.getAttribute('href') + '">' + esc(a.textContent) + '</a>';
          }).join('') + '</div></div>';
        mais.innerHTML = '';
      } else {
        lista.innerHTML = vistos.slice(0, limite).map(function (n) { return cartao(n, palavras); }).join('');
        mais.innerHTML = vistos.length > limite ? '<button class="btn btn--escuro" type="button">Mostrar mais notícias</button>' : '';
      }
      document.title = (termo.trim() ? termo.trim() + ' · ' : '') + 'Busca | CanalMT';
    }
    filtros.addEventListener('click', function (e) {
      var b = e.target.closest('[data-ed]');
      if (!b) return;
      editoria = b.getAttribute('data-ed'); limite = 10; buscar();
    });
    mais.addEventListener('click', function (e) {
      if (!e.target.closest('button')) return;
      limite += 10; buscar();
    });
    $('[data-busca-form]').addEventListener('submit', function (e) {
      e.preventDefault();
      termo = campo.value; editoria = ''; limite = 10;
      try { history.replaceState(null, '', '?s=' + encodeURIComponent(termo.trim())); } catch (x) {}
      buscar();
    });
    buscar();
  })();
})();
