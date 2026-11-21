"""Monta as páginas internas do protótipo a partir da home (index.html).

O cabeçalho, o menu, a gaveta do celular, o rodapé e os avisos são copiados
do index.html, então tudo fica igual em todas as páginas. Rodar de novo
sempre que o cabeçalho ou o rodapé da home mudar:

    python3 ferramentas/montar.py

Também troca, no index.html, os endereços do site atual pelos das páginas
do protótipo, para dar para navegar entre elas (a tabela está no README).
"""
import html
import json
import os
import re
import urllib.parse

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://www.canalmt.com.br'
HOJE = '19/11/2026'

# ---------------------------------------------------------------- editorias
# arquivo -> (nome, editoria-mãe, endereço no WordPress, descrição)
EDITORIAS = {
    'politica':    ('Política', None, '/categoria/politica-mt/', 'Assembleia, prefeituras, Câmara e governo: a política de Cuiabá e de Mato Grosso.'),
    'geral':       ('Geral', None, '/categoria/geral/', 'O dia a dia de Cuiabá, de Várzea Grande e do interior de Mato Grosso.'),
    'policia':     ('Polícia', 'geral', '/categoria/geral/policia/', 'Ocorrências, investigações e segurança pública em Mato Grosso.'),
    'economia':    ('Economia', 'geral', '/categoria/geral/economia/', 'Mercado, emprego, renda e negócios em Mato Grosso e no Brasil.'),
    'agronegocio': ('Agronegócio', 'economia', '/categoria/geral/economia/agronegocio/', 'Safra, mercado e produção rural em Mato Grosso.'),
    'esporte':     ('Esporte', 'geral', '/categoria/geral/esporte/', 'Futebol mato-grossense, Brasileirão, seleção e outras modalidades.'),
    'saude':       ('Saúde', 'geral', '/categoria/geral/saude/', 'Saúde pública, campanhas de vacinação e atendimento em Mato Grosso.'),
    'educacao':    ('Educação', 'geral', '/categoria/geral/educacao/', 'Escolas, universidades, concursos e educação em Mato Grosso.'),
    'brasil':      ('Brasil', None, '/categoria/brasil/', 'As principais notícias do país.'),
    'mundo':       ('Mundo', None, '/categoria/mundo/', 'Notícias internacionais.'),
    'artigos':     ('Artigos', None, '/categoria/artigos/', 'Opinião e análise de colunistas e convidados.'),
    'videos':      ('Vídeos', None, '/categoria/videos/', 'Os vídeos do CanalMT.'),
}
FILHAS = {'geral': ['policia', 'economia', 'esporte', 'saude', 'educacao'], 'economia': ['agronegocio']}
INSTITUCIONAIS = {'quem-somos': '/quem-somos/', 'anuncie': '/anuncie/', 'contato': '/contato/'}

# endereço do site atual -> página do protótipo
MAPA = {SITE + '/': 'index.html', SITE: 'index.html'}
for arq, (_, _, url, _) in EDITORIAS.items():
    MAPA[SITE + url] = arq + '.html'
for arq, url in INSTITUCIONAIS.items():
    MAPA[SITE + url] = arq + '.html'

ICONES_NOVOS = {
    'i-whatsapp': '<symbol id="i-whatsapp" viewBox="0 0 24 24"><path d="M12 2.5a9.5 9.5 0 0 0-8.2 14.3L2.5 21.5l4.8-1.3A9.5 9.5 0 1 0 12 2.5Zm0 17.3c-1.5 0-2.9-.4-4.1-1.1l-.3-.2-2.8.8.8-2.7-.2-.3A7.8 7.8 0 1 1 12 19.8Zm4.3-5.8c-.2-.1-1.4-.7-1.6-.8-.2-.1-.4-.1-.5.1l-.7.9c-.1.2-.3.2-.5.1a6.4 6.4 0 0 1-3.2-2.8c-.2-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.7-1.7c-.2-.5-.4-.4-.5-.4h-.5a.9.9 0 0 0-.7.3 2.8 2.8 0 0 0-.9 2.1 4.9 4.9 0 0 0 1 2.6 11.2 11.2 0 0 0 4.3 3.8c1.6.7 2.2.7 3 .6.5-.1 1.4-.6 1.6-1.1.2-.6.2-1 .1-1.1l-.4-.2Z"/></symbol>',
    'i-x': '<symbol id="i-x" viewBox="0 0 24 24"><path d="M17.8 3h3.1l-6.8 7.8L22 21h-6.2l-4.9-6.4L5.3 21H2.2l7.3-8.3L2 3h6.4l4.4 5.8L17.8 3Zm-1.1 16.2h1.7L7.4 4.7H5.6l11.1 14.5Z"/></symbol>',
    'i-telegram': '<symbol id="i-telegram" viewBox="0 0 24 24"><path d="M21.4 4.2 2.9 11.3c-1.3.5-1.2 1.2-.2 1.5l4.7 1.5 1.8 5.6c.2.6.4.8.8.8s.6-.2.9-.5l2.3-2.2 4.8 3.5c.9.5 1.5.2 1.7-.8l3.1-14.6c.3-1.3-.5-1.9-1.4-1.5ZM9.7 14.6l-.4 3.9-1.4-4.6 10.5-6.6-8.7 7.3Z"/></symbol>',
    'i-link': '<symbol id="i-link" viewBox="0 0 24 24"><path d="M10 14a4.5 4.5 0 0 0 6.4 0l3.2-3.2a4.5 4.5 0 0 0-6.4-6.4l-1.1 1.1"/><path d="M14 10a4.5 4.5 0 0 0-6.4 0l-3.2 3.2a4.5 4.5 0 0 0 6.4 6.4l1.1-1.1"/></symbol>',
    'i-youtube': '<symbol id="i-youtube" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4A2.5 2.5 0 0 0 2.4 7.2 26 26 0 0 0 2 12a26 26 0 0 0 .4 4.8 2.5 2.5 0 0 0 1.8 1.8c1.6.4 7.8.4 7.8.4s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8A26 26 0 0 0 22 12a26 26 0 0 0-.4-4.8ZM10 15V9l5.2 3L10 15Z"/></symbol>',
    'i-mais': '<symbol id="i-mais" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></symbol>',
    'i-email': '<symbol id="i-email" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3.5 6.5 8.5 6.5 8.5-6.5"/></symbol>',
}

e = html.escape


def ler(caminho):
    return open(os.path.join(RAIZ, caminho), encoding='utf-8').read()


def gravar(caminho, texto):
    open(os.path.join(RAIZ, caminho), 'w', encoding='utf-8').write(texto)


# ------------------------------------------------- 1. ajusta o index.html
def trocar_links(h):
    h = re.sub(r'href="' + re.escape(SITE) + r'/tags/[^"]+">(?P<n>[^<]*)</a>',
               lambda m: 'href="busca.html?s=' + urllib.parse.quote(m.group('n').strip()) + '">' + m.group('n') + '</a>', h)

    def link(m):
        url = m.group(1)
        if url in MAPA:
            return 'href="' + MAPA[url] + '"'
        if re.match(re.escape(SITE) + r'/20\d\d/', url):
            return 'href="noticia.html"'
        return m.group(0)
    h = re.sub(r'href="(' + re.escape(SITE) + r'[^"]*)"', link, h)
    h = h.replace('action="' + SITE + '/" method="get" target="_blank"', 'action="busca.html" method="get"')
    return h


index = ler('index.html')
index = trocar_links(index)
for nome, simbolo in ICONES_NOVOS.items():
    if 'id="' + nome + '"' not in index:
        index = index.replace('</svg>\n\n<a class="pular"', '  ' + simbolo + '\n</svg>\n\n<a class="pular"', 1)
gravar('index.html', index)

CABECA = index[:index.index('<body>')]
TOPO = index[index.index('<body>'):index.index('<main id="conteudo">')]
FIM = index[index.index('</main>') + len('</main>'):]
DADOS = json.load(open(os.path.join(RAIZ, 'ferramentas', 'dados.json'), encoding='utf-8'))


def pagina(arquivo, titulo, descricao, ativo, conteudo):
    cab = CABECA.replace('<title>CanalMT novo portal</title>', '<title>' + e(titulo) + '</title>')
    cab = re.sub(r'<meta name="description" content="[^"]*">',
                 '<meta name="description" content="' + e(descricao) + '">', cab)
    topo = TOPO.replace(' aria-current="page"', '')
    if ativo:
        topo = topo.replace('<li><a href="' + ativo + '">', '<li><a href="' + ativo + '" aria-current="page">')
    texto = cab + topo + '<main id="conteudo">\n' + conteudo.strip('\n') + '\n</main>' + FIM
    if arquivo == '404.html':  # o servidor mostra esta página em qualquer endereço: caminhos a partir da raiz
        texto = re.sub(r'(href|src)="(?!https?:|mailto:|#|/)([^"]+)"', r'\1="/\2"', texto)
    gravar(arquivo, texto)


# --------------------------------------------------------- 2. peças comuns
SETA = '<svg><use href="#i-seta"/></svg>'


def iso(data, hora=''):
    d, m, a = data.split('/')
    if hora:
        return f'{a}-{m}-{d}T{hora.replace("h", ":")}-04:00'
    return f'{a}-{m}-{d}'


def quando(n):
    return n['data'] + (' · ' + n['hora'] if n.get('hora') else '')


def trilha(itens):
    partes = ['<li><a href="index.html">Início</a></li>']
    for rotulo, href in itens[:-1]:
        partes.append(f'<li><a href="{href}">{e(rotulo)}</a></li>')
    partes.append(f'<li><span aria-current="page">{e(itens[-1][0])}</span></li>')
    return '<nav aria-label="Você está em"><ol class="trilha">' + ''.join(partes) + '</ol></nav>'


def anuncio(posicao, rotulo, formato='retangulo', medida='300 × 250'):
    return (f'<div class="anuncio anuncio--{formato}" data-posicao="{posicao}"><span>'
            f'<span class="anuncio__rotulo">{rotulo}</span><span class="anuncio__medida">{medida}</span></span></div>')


FAIXA_MEDIDA = '<span class="so-desktop">1080 × 110</span><span class="so-celular">320 × 100</span>'


def faixa(posicao, rotulo):
    return ('<div class="container anuncio-faixa">\n  ' +
            anuncio(posicao, rotulo, 'faixa', FAIXA_MEDIDA) + '\n</div>')


def card_linha(n, editoria, nivel='h2', abre=False, play=False):
    classes = 'card ' + ('card--abre' if abre else 'card--linha') + ('' if n['foto'] else ' sem-foto')
    foto = ''
    if n['foto']:
        preguica = '' if abre else ' loading="lazy"'
        foto = (f'<div class="card__foto"><img src="{n["foto"]}" alt="" width="800" height="500"{preguica}>'
                + ('<span class="card__play" aria-hidden="true"><svg><use href="#i-play"/></svg></span>' if play else '')
                + '</div>')
    resumo = f'<p class="card__resumo">{e(n["resumo"])}</p>' if n['resumo'] else ''
    return (f'<article class="{classes}">{foto}<div class="card__corpo">'
            f'<div class="card__meta"><span class="chapeu chapeu--linha">{e(editoria)}</span>'
            f'<time class="data" datetime="{iso(n["data"])}">{quando(n)}</time></div>'
            f'<{nivel} class="card__titulo"><a href="noticia.html">{e(n["titulo"])}</a></{nivel}>{resumo}'
            f'</div></article>')


def lateral():
    ultimas = DADOS['geral']['itens'][:5]
    itens = ''.join(
        f'<li><time datetime="{iso(n["data"], n["hora"])}"><b>{n["hora"]}</b>{n["data"][:5]}</time>'
        f'<a href="noticia.html">{e(n["titulo"])}</a></li>' for n in ultimas)
    return f'''<aside class="lateral" aria-label="Lateral">
    {anuncio("lateral-cima", "Publicidade · Lateral 1")}
    <div class="lateral__fixo">
      <section class="painel" aria-labelledby="t-recentes">
        <div class="secao__topo"><h2 class="secao__titulo" id="t-recentes" style="font-size:20px">Últimas notícias</h2></div>
        <ol class="recentes">{itens}</ol>
      </section>
      {anuncio("lateral-baixo", "Publicidade · Lateral 2")}
    </div>
  </aside>'''


def paginacao(arquivo, total):
    """Cápsula com as páginas no computador; no celular, "Página 1 de N" com setas
    e o botão "Carregar mais notícias" (no protótipo, só mostram um aviso)."""
    def fmt(n):
        return f'{n:,}'.replace(',', '.')

    def num(n):
        return f'<a class="so-largo" href="{arquivo}.html" data-demo="Na versão final, abre a página {fmt(n)}.">{fmt(n)}</a>'
    partes = ['<span class="paginacao__seta desligado" aria-disabled="true" aria-label="Página anterior"><svg><use href="#i-voltar"/></svg></span>',
              '<span aria-current="page">1</span>']
    partes += [num(n) for n in range(2, min(total, 4) + 1)]
    if total > 5:
        partes.append('<span class="reticencias so-largo" aria-hidden="true">…</span>')
    if total > 4:
        partes.append(num(total))
    partes.append(f'<span class="paginacao__info">Página <b>1</b> de <b>{fmt(total)}</b></span>')
    if total > 1:
        partes.append(f'<a class="paginacao__seta" href="{arquivo}.html" aria-label="Próxima página" data-demo="Na versão final, abre a página 2."><svg><use href="#i-seta"/></svg></a>')
    else:
        partes.append('<span class="paginacao__seta desligado" aria-disabled="true" aria-label="Próxima página"><svg><use href="#i-seta"/></svg></span>')
    mais = ''
    if total > 1:
        mais = ('<button class="btn btn--escuro so-celular" type="button" data-demo="Na versão final, as próximas notícias aparecem aqui mesmo, sem trocar de página.">'
                'Carregar mais notícias<svg aria-hidden="true"><use href="#i-mais"/></svg></button>')
    return ('<div class="paginacao-bloco">' + mais + '<nav class="paginacao" aria-label="Páginas">' + ''.join(partes) + '</nav></div>')


# ------------------------------------------------ 3. páginas de editoria
for arq, (nome, mae, url, descricao) in EDITORIAS.items():
    itens = DADOS[arq]['itens']
    caminho = []
    if mae:
        avo = EDITORIAS[mae][1]
        if avo:
            caminho.append((EDITORIAS[avo][0], avo + '.html'))
        caminho.append((EDITORIAS[mae][0], mae + '.html'))
    caminho.append((nome, arq + '.html'))
    filhas = FILHAS.get(arq, [])
    sub = ''
    if filhas:
        sub = ('<nav class="subeditorias" aria-label="Dentro de ' + e(nome) + '">' +
               ''.join(f'<a class="filtro" href="{f}.html">{EDITORIAS[f][0]}</a>' for f in filhas) + '</nav>')

    if arq == 'videos':
        lista = ('<div class="grade-3">' +
                 ''.join(card_linha(n, 'Vídeo', 'h2', play=True).replace('card card--linha', 'card') for n in itens) +
                 '</div>')
    else:
        blocos = [card_linha(itens[0], nome, abre=True)]
        for k, n in enumerate(itens[1:], start=1):
            blocos.append(card_linha(n, nome))
            if k == 4:
                blocos.append('<div class="anuncio-lista so-celular">' + anuncio('celular-meio', 'Publicidade') + '</div>')
        lista = '<div class="arquivo">\n        ' + '\n        '.join(blocos) + '\n      </div>'

    conteudo = f'''
<div class="container">
  {trilha(caminho)}
  <header class="pagina-topo">
    <h1 class="pagina-topo__titulo">{e(nome)}</h1>
    <p class="pagina-topo__texto">{e(descricao)}</p>
    {sub}
  </header>
</div>

<div class="container corpo">
  <div>
    <section class="secao" aria-label="Notícias de {e(nome)}">
      {lista}
      {paginacao(arq, DADOS[arq]['paginas'])}
    </section>
  </div>
  {lateral()}
</div>

{faixa("rodape", "Publicidade · Rodapé")}
'''
    pagina(arq + '.html', f'{nome} | CanalMT', f'{descricao} Notícias de {nome} no CanalMT.', arq + '.html', conteudo)


# ------------------------------------------------------- 4. página da notícia
MATERIA = json.load(open(os.path.join(RAIZ, 'ferramentas', 'materia.json'), encoding='utf-8'))
pars = [t for tag, t in MATERIA]
fonte = pars.pop()  # "Fonte: Débora Siqueira | Assessoria/Sedec"
corpo = []
for k, t in enumerate(pars):
    if t == 'Além do desemprego':
        corpo.append(f'<h2>{e(t)}</h2>')
        continue
    if t.startswith('“'):
        fala, quem = t.rsplit('”', 1)
        corpo.append(f'<blockquote><p>{e(fala)}”</p><footer>Mayran Beckman, secretária de Estado de Desenvolvimento Econômico</footer></blockquote>')
    else:
        corpo.append(f'<p>{e(t)}</p>')
    if k == 2:
        corpo.append('<div class="anuncio-meio">' + anuncio('noticia-meio', 'Publicidade') + '</div>')
    if k == 5:
        corpo.append('''<aside class="numeros" aria-label="Em números">
          <p class="numeros__titulo">Em números</p>
          <dl>
            <div><dt>2,6%</dt><dd>taxa de desemprego em Mato Grosso</dd></div>
            <div><dt>5,2%</dt><dd>média nacional no mesmo trimestre</dd></div>
            <div><dt>2,08 mi</dt><dd>pessoas trabalhando no estado</dd></div>
            <div><dt>67,2%</dt><dd>nível de ocupação</dd></div>
          </dl>
        </aside>''')
texto_materia = '\n        '.join(corpo)
TITULO = 'Mato Grosso registra mais de 2 milhões de pessoas ocupadas e tem a 3ª menor taxa de desemprego do país'


def botoes_compartilhar():
    return '''<div class="compartilhar">
            <a class="btn-icone zap" data-rede="whatsapp" href="#" target="_blank" rel="noopener" aria-label="Compartilhar no WhatsApp"><svg><use class="i-cheio" href="#i-whatsapp"/></svg></a>
            <a class="btn-icone" data-rede="facebook" href="#" target="_blank" rel="noopener" aria-label="Compartilhar no Facebook"><svg><use class="i-cheio" href="#i-facebook"/></svg></a>
            <a class="btn-icone" data-rede="x" href="#" target="_blank" rel="noopener" aria-label="Compartilhar no X"><svg><use class="i-cheio" href="#i-x"/></svg></a>
            <a class="btn-icone" data-rede="telegram" href="#" target="_blank" rel="noopener" aria-label="Compartilhar no Telegram"><svg><use class="i-cheio" href="#i-telegram"/></svg></a>
            <button class="btn-icone" type="button" data-copiar-link aria-label="Copiar o link da notícia"><svg><use href="#i-link"/></svg></button>
          </div>'''


relacionadas = [n for n in DADOS['geral']['itens'] if n['foto'] and not n['titulo'].startswith('Mato Grosso registra')][:3]
leia = ''.join(
    f'<article class="card"><div class="card__foto"><img src="{n["foto"]}" alt="" width="800" height="500" loading="lazy"></div>'
    f'<time class="data" datetime="{iso(n["data"])}">{n["data"]}</time>'
    f'<h3 class="card__titulo"><a href="noticia.html">{e(n["titulo"])}</a></h3></article>' for n in relacionadas)
tags = ''.join(f'<a href="busca.html?s={urllib.parse.quote(t)}">{t}</a>' for t in ['Mato Grosso', 'IBGE', 'Emprego', 'Economia'])

conteudo = f'''
<div class="progresso" aria-hidden="true"><span data-progresso></span></div>
<div class="container">
  {trilha([("Geral", "geral.html"), ("Economia", "economia.html"), ("Notícia", "noticia.html")])}
</div>

<div class="container corpo">
  <article class="materia" data-materia>
    <header class="materia__cabeca">
      <a class="chapeu" href="economia.html">Economia</a>
      <h1 class="materia__titulo">{e(TITULO)}</h1>
      <p class="linha-fina">Taxa de 2,6% é metade da média nacional, segundo a PNAD Contínua do IBGE. Só Santa Catarina e Mato Grosso do Sul têm índices menores.</p>
      <div class="materia__meta">
        <p class="autoria"><b>Débora Siqueira</b><span>Assessoria/Sedec · <time datetime="2026-11-18T17:16-04:00">18/11/2026 às 17h16</time> · <span data-tempo-leitura="[data-texto-materia]">4 min de leitura</span></span></p>
        <div class="ferramentas">
          {botoes_compartilhar()}
          <div class="tamanho" role="group" aria-label="Tamanho do texto">
            <button type="button" data-fonte="-1" aria-label="Diminuir o texto">A−</button>
            <button type="button" data-fonte="1" aria-label="Aumentar o texto">A+</button>
          </div>
        </div>
      </div>
    </header>

    <figure class="materia__foto">
      <img src="img/materia-cuiaba.jpg" alt="Rua de comércio no centro de Cuiabá, com pedestres e lojas" width="1200" height="800" fetchpriority="high">
      <figcaption>Foto: Assessoria/Sedec</figcaption>
    </figure>

    <div class="materia__texto" data-texto-materia>
        {texto_materia}
        <p class="fonte">{e(fonte)}</p>
    </div>

    <div class="tags"><span class="tags__rotulo">Assuntos</span>{tags}</div>
    <div class="compartilhar-fim">
      <p>Compartilhe esta notícia</p>
      <a class="btn btn--zap" data-rede="whatsapp" href="#" target="_blank" rel="noopener"><span class="btn__bola"><svg aria-hidden="true"><use href="#i-whatsapp"/></svg></span>Mandar no WhatsApp</a>
      {botoes_compartilhar()}
    </div>
  </article>
  {lateral()}
</div>

<section class="secao container" aria-labelledby="t-leia">
  <div class="secao__topo">
    <h2 class="secao__titulo" id="t-leia">Leia também</h2>
    <a class="secao__mais" href="geral.html">Mais de Geral {SETA}</a>
  </div>
  <div class="grade-3">{leia}</div>
</section>

{faixa("rodape", "Publicidade · Rodapé")}
'''
pagina('noticia.html', TITULO + ' | CanalMT',
       'Taxa de 2,6% é metade da média nacional, segundo a PNAD Contínua do IBGE.', 'economia.html', conteudo)


# ---------------------------------------------------------------- 5. busca
vistos, base = set(), []
for arq, (nome, *_r) in EDITORIAS.items():
    for n in DADOS[arq]['itens']:
        if n['titulo'] in vistos:
            continue
        vistos.add(n['titulo'])
        base.append(dict(titulo=n['titulo'], resumo=n['resumo'], data=n['data'], foto=n['foto'],
                         ed='Vídeo' if arq == 'videos' else nome))
base.sort(key=lambda n: tuple(reversed(n['data'].split('/'))), reverse=True)
dados_busca = json.dumps(base, ensure_ascii=False).replace('</', '<\\/')

conteudo = f'''
<div class="container">
  {trilha([("Busca", "busca.html")])}
  <header class="pagina-topo busca-topo">
    <h1 class="pagina-topo__titulo">Busca</h1>
    <form class="busca-grande" role="search" action="busca.html" method="get" data-busca-form>
      <svg aria-hidden="true"><use href="#i-busca"/></svg>
      <label class="so-leitor" for="busca-pagina">O que você procura?</label>
      <input id="busca-pagina" type="search" name="s" value="Cuiabá" placeholder="Digite um assunto, nome ou cidade" autocomplete="off">
      <button class="btn btn--amarelo" type="submit">Buscar</button>
    </form>
    <p class="busca-resumo" data-busca-resumo aria-live="polite"></p>
    <div class="filtros" data-busca-filtros role="group" aria-label="Filtrar por editoria"></div>
  </header>
</div>

<div class="container corpo">
  <div>
    <section class="secao" aria-label="Resultados da busca">
      <div class="arquivo" data-busca-lista></div>
      <div class="mais-noticias" data-busca-mais></div>
    </section>
  </div>
  {lateral()}
</div>

{faixa("rodape", "Publicidade · Rodapé")}
<script type="application/json" id="noticias">{dados_busca}</script>
'''
pagina('busca.html', 'Busca | CanalMT', 'Busque notícias no CanalMT.', None, conteudo)


# ---------------------------------------------------------- 6. institucionais
def contato_itens():
    return f'''<a class="contato-item" href="mailto:contato@canalmt.com.br">
          <span class="contato-item__icone"><svg><use href="#i-email"/></svg></span>
          <span><small>E-mail</small><b>contato@canalmt.com.br</b></span>
        </a>
        <a class="contato-item" href="https://www.instagram.com/canalmt/" target="_blank" rel="noopener">
          <span class="contato-item__icone"><svg><use href="#i-instagram"/></svg></span>
          <span><small>Instagram</small><b>@canalmt</b></span>
        </a>
        <a class="contato-item" href="https://www.facebook.com/canalmt" target="_blank" rel="noopener">
          <span class="contato-item__icone"><svg><use class="i-cheio" href="#i-facebook"/></svg></span>
          <span><small>Facebook</small><b>facebook.com/canalmt</b></span>
        </a>
        <a class="contato-item" href="https://www.youtube.com/@canalmt" target="_blank" rel="noopener">
          <span class="contato-item__icone"><svg><use class="i-cheio" href="#i-youtube"/></svg></span>
          <span><small>YouTube</small><b>youtube.com/@canalmt</b></span>
        </a>'''


grade_editorias = ''.join(
    f'<a href="{a}.html">{EDITORIAS[a][0]}<svg><use href="#i-seta"/></svg></a>'
    for a in ['politica', 'geral', 'policia', 'economia', 'agronegocio', 'esporte', 'saude', 'educacao', 'brasil', 'mundo', 'artigos', 'videos'])

conteudo = f'''
<div class="container">
  {trilha([("Quem Somos", "quem-somos.html")])}
  <header class="pagina-topo">
    <h1 class="pagina-topo__titulo">Quem Somos</h1>
  </header>
  <div class="inst">
    <div class="prosa">
      <p class="nota-rascunho"><b>Texto provisório.</b> Substituir pelo texto oficial do CanalMT (história, equipe e linha editorial).</p>
      <p class="inst__lead">Compromisso com a informação.</p>
      <p>O CanalMT é um portal de notícias de Cuiabá e de Mato Grosso. Acompanhamos a política, a economia, o agronegócio, a segurança, a saúde, a educação e o esporte do estado, e também o que acontece no Brasil e no mundo.</p>
      <p>Nosso trabalho é levar a notícia de forma clara e fácil de ler, no celular ou no computador.</p>
      <h2>O que você encontra aqui</h2>
      <div class="editorias-grade">{grade_editorias}</div>
    </div>
    <aside class="inst__lado">
      <section class="painel" aria-labelledby="t-fale">
        <div class="secao__topo"><h2 class="secao__titulo" id="t-fale" style="font-size:20px">Fale com a gente</h2></div>
        {contato_itens()}
        <div class="painel__acoes">
          <a class="btn btn--escuro" href="contato.html">Enviar mensagem</a>
          <a class="btn btn--amarelo" href="anuncie.html">Anunciar no CanalMT</a>
        </div>
      </section>
    </aside>
  </div>
</div>
{faixa("rodape", "Publicidade · Rodapé")}
'''
pagina('quem-somos.html', 'Quem Somos | CanalMT', 'Conheça o CanalMT, portal de notícias de Cuiabá e de Mato Grosso.', None, conteudo)

FORMATOS = [
    ('Topo', '1080 × 110 no computador · 320 × 100 no celular', 'Todas as páginas, logo abaixo do menu'),
    ('Meio da página inicial', '1080 × 110 no computador · 320 × 100 no celular', 'Entre as seções da página inicial'),
    ('Lateral', '300 × 250', 'Página inicial, editorias, busca e notícias (duas posições)'),
    ('Dentro da notícia', '300 × 250', 'No meio do texto das notícias'),
    ('Fixo no celular', '320 × 50', 'Preso no pé da tela do celular, com botão de fechar'),
    ('Rodapé', '1080 × 110 no computador · 320 × 100 no celular', 'Antes do rodapé, em todas as páginas'),
]
lista_formatos = ''.join(
    f'<li><span class="num">{k}</span><span><b>{n}</b><small>{m}</small><small>{o}</small></span></li>'
    for k, (n, m, o) in enumerate(FORMATOS, start=1))
opcoes = ''.join(
    f'<label class="opcao"><input type="checkbox" name="formatos" value="{n}"><span>{n}</span></label>'
    for n, _, _ in FORMATOS)

conteudo = f'''
<div class="container">
  {trilha([("Anuncie", "anuncie.html")])}
  <header class="pagina-topo">
    <h1 class="pagina-topo__titulo">Anuncie</h1>
    <p class="pagina-topo__texto">Sua marca nas páginas de notícias de Cuiabá e de Mato Grosso, no computador e no celular.</p>
  </header>

  <section class="secao" aria-labelledby="t-onde">
    <div class="secao__topo"><h2 class="secao__titulo" id="t-onde">Onde o seu anúncio aparece</h2></div>
    <div class="formatos">
      <div class="maquete" aria-hidden="true">
        <div class="maquete__tela">
          <div class="mq mq--cheia"></div>
          <div class="mq mq--ad mq--cheia">1</div>
          <div class="mq" style="display:grid;grid-template-rows:1fr 18px 1fr;gap:5px;background:none">
            <div class="mq"></div><div class="mq mq--ad">2</div><div class="mq"></div>
          </div>
          <div class="mq--lado"><div class="mq mq--ad" style="aspect-ratio:6/5">3</div><div class="mq" style="min-height:22px"></div><div class="mq mq--ad">3</div></div>
          <div class="mq mq--ad mq--cheia">6</div>
        </div>
        <div class="maquete__celular">
          <div class="mq"></div>
          <div class="mq mq--ad">1</div>
          <div class="mq"></div>
          <div class="mq mq--ad">4</div>
          <div class="mq"></div>
          <div class="mq mq--ad">5</div>
        </div>
      </div>
      <ol class="lista-formatos">{lista_formatos}</ol>
    </div>
  </section>

  <section class="secao" aria-labelledby="t-como">
    <div class="secao__topo"><h2 class="secao__titulo" id="t-como">Como anunciar</h2></div>
    <ol class="passos">
      <li><b>Fale com a gente</b><p>Mande o formulário abaixo ou escreva para contato@canalmt.com.br.</p></li>
      <li><b>Escolha formatos e período</b><p>Montamos com você a proposta com as posições e as datas.</p></li>
      <li><b>Envie a arte</b><p>Em GIF, JPG ou PNG, nos tamanhos da lista acima.</p></li>
    </ol>
  </section>

  <div class="inst">
    <section class="painel" aria-labelledby="t-form-anuncie">
      <div class="secao__topo"><h2 class="secao__titulo" id="t-form-anuncie">Peça uma proposta</h2></div>
      <form class="form" data-formulario action="#" method="post">
        <div class="form__linha">
          <div class="campo"><label for="a-nome">Seu nome</label><input id="a-nome" name="nome" autocomplete="name" required><span class="campo__erro">Escreva o seu nome.</span></div>
          <div class="campo"><label for="a-empresa">Empresa</label><input id="a-empresa" name="empresa" autocomplete="organization" required><span class="campo__erro">Escreva o nome da empresa.</span></div>
        </div>
        <div class="form__linha">
          <div class="campo"><label for="a-email">E-mail</label><input id="a-email" name="email" type="email" autocomplete="email" required><span class="campo__erro">Escreva um e-mail válido, como nome@empresa.com.br.</span></div>
          <div class="campo"><label for="a-zap">WhatsApp</label><input id="a-zap" name="whatsapp" type="tel" inputmode="numeric" autocomplete="tel" placeholder="(65) 99999-9999" data-zap required><span class="campo__erro">Escreva o DDD e os 9 números, como (65) 99999-9999.</span></div>
        </div>
        <fieldset class="campo">
          <legend>Formatos de interesse <span class="dica">(opcional, pode marcar mais de um)</span></legend>
          <div class="opcoes">{opcoes}</div>
        </fieldset>
        <div class="campo"><label for="a-msg">Mensagem <span class="dica">(opcional)</span></label><textarea id="a-msg" name="mensagem" placeholder="Período, público, campanha…"></textarea></div>
        <label class="aceite"><input type="checkbox" name="privacidade" required><span>Li e aceito a <a href="https://wp.me/PcJ7Tz-flt">Política de Privacidade</a>.</span></label>
        <div><button class="btn btn--amarelo" type="submit">Enviar pedido{SETA}</button></div>
      </form>
      <div class="form__ok" data-form-ok tabindex="-1" hidden>
        <h2>Pedido conferido</h2>
        <p>Esta é a pré-visualização do site: nada foi enviado. No site final, o pedido vai direto para contato@canalmt.com.br.</p>
        <p><button class="btn btn--escuro" type="button" data-form-de-novo>Preencher de novo</button></p>
      </div>
    </section>
    <aside class="inst__lado">
      <section class="painel" aria-labelledby="t-comercial">
        <div class="secao__topo"><h2 class="secao__titulo" id="t-comercial" style="font-size:20px">Comercial</h2></div>
        {contato_itens()}
      </section>
    </aside>
  </div>
</div>
{faixa("rodape", "Publicidade · Rodapé")}
'''
pagina('anuncie.html', 'Anuncie | CanalMT', 'Anuncie no CanalMT: formatos, tamanhos e como pedir uma proposta.', None, conteudo)

conteudo = f'''
<div class="container">
  {trilha([("Contato", "contato.html")])}
  <header class="pagina-topo">
    <h1 class="pagina-topo__titulo">Contato</h1>
    <p class="pagina-topo__texto">Mande uma sugestão de pauta, uma correção ou a sua dúvida para a redação.</p>
  </header>
  <div class="inst">
    <section class="painel" aria-label="Formulário de contato">
      <form class="form" data-formulario action="#" method="post">
        <div class="form__linha">
          <div class="campo"><label for="c-nome">Seu nome</label><input id="c-nome" name="nome" autocomplete="name" required><span class="campo__erro">Escreva o seu nome.</span></div>
          <div class="campo"><label for="c-email">E-mail</label><input id="c-email" name="email" type="email" autocomplete="email" required><span class="campo__erro">Escreva um e-mail válido, como nome@email.com.</span></div>
        </div>
        <div class="form__linha">
          <div class="campo"><label for="c-zap">WhatsApp <span class="dica">(opcional)</span></label><input id="c-zap" name="whatsapp" type="tel" inputmode="numeric" autocomplete="tel" placeholder="(65) 99999-9999" data-zap><span class="campo__erro">Escreva o DDD e os 9 números, como (65) 99999-9999.</span></div>
          <div class="campo"><label for="c-assunto">Assunto</label>
            <select id="c-assunto" name="assunto" required>
              <option value="">Escolha o assunto</option>
              <option>Sugestão de pauta</option>
              <option>Correção de informação</option>
              <option>Quero anunciar</option>
              <option>Outro assunto</option>
            </select><span class="campo__erro">Escolha o assunto.</span></div>
        </div>
        <div class="campo"><label for="c-msg">Mensagem</label><textarea id="c-msg" name="mensagem" required></textarea><span class="campo__erro">Escreva a sua mensagem.</span></div>
        <label class="aceite"><input type="checkbox" name="privacidade" required><span>Li e aceito a <a href="https://wp.me/PcJ7Tz-flt">Política de Privacidade</a>.</span></label>
        <div><button class="btn btn--amarelo" type="submit">Enviar mensagem{SETA}</button></div>
      </form>
      <div class="form__ok" data-form-ok tabindex="-1" hidden>
        <h2>Mensagem conferida</h2>
        <p>Esta é a pré-visualização do site: nada foi enviado. No site final, a mensagem vai direto para contato@canalmt.com.br.</p>
        <p><button class="btn btn--escuro" type="button" data-form-de-novo>Escrever outra</button></p>
      </div>
    </section>
    <aside class="inst__lado">
      <section class="painel" aria-labelledby="t-outros">
        <div class="secao__topo"><h2 class="secao__titulo" id="t-outros" style="font-size:20px">Outros canais</h2></div>
        {contato_itens()}
        <div class="painel__acoes"><a class="btn btn--escuro" href="anuncie.html">Quero anunciar</a></div>
      </section>
    </aside>
  </div>
</div>
{faixa("rodape", "Publicidade · Rodapé")}
'''
pagina('contato.html', 'Contato | CanalMT', 'Fale com a redação do CanalMT.', None, conteudo)

ultimas = ''.join(card_linha(n, 'Geral', 'h3') for n in DADOS['geral']['itens'][:4])
conteudo = f'''
<div class="container">
  <div class="erro404">
    <p class="erro404__codigo" aria-hidden="true">404</p>
    <h1 class="pagina-topo__titulo">Página não encontrada</h1>
    <p class="pagina-topo__texto">O endereço pode ter mudado ou a notícia saiu do ar. Busque o assunto ou volte para a página inicial.</p>
    <form class="busca-grande" role="search" action="busca.html" method="get">
      <svg aria-hidden="true"><use href="#i-busca"/></svg>
      <label class="so-leitor" for="busca-404">Buscar no CanalMT</label>
      <input id="busca-404" type="search" name="s" placeholder="Digite um assunto, nome ou cidade" autocomplete="off">
      <button class="btn btn--amarelo" type="submit">Buscar</button>
    </form>
    <a class="btn btn--escuro" href="index.html">Ir para a página inicial</a>
  </div>
  <section class="secao" aria-labelledby="t-404">
    <div class="secao__topo"><h2 class="secao__titulo" id="t-404">Últimas notícias</h2><a class="secao__mais" href="geral.html">Ver tudo {SETA}</a></div>
    <div class="arquivo">{ultimas}</div>
  </section>
</div>
'''
pagina('404.html', 'Página não encontrada | CanalMT', 'Página não encontrada no CanalMT.', None, conteudo)

print('páginas montadas')
