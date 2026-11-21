# CanalMT — novo portal (front-end)

Layout em HTML, CSS e JavaScript puros do novo portal de notícias CanalMT, pronto para receber o painel do WordPress.
Não há etapa de build: abra `index.html` no navegador.

## Arquivos

| Caminho | O que é |
|---|---|
| `index.html` | Página inicial |
| `noticia.html` | Modelo da página de notícia (todas as manchetes do protótipo abrem aqui) |
| `politica.html`, `geral.html`, `policia.html`, `economia.html`, `agronegocio.html`, `esporte.html`, `saude.html`, `educacao.html`, `brasil.html`, `mundo.html`, `artigos.html`, `videos.html` | Páginas de editoria, com as notícias reais do portal atual |
| `busca.html` | Resultado da busca (`?s=termo`) |
| `quem-somos.html`, `anuncie.html`, `contato.html` | Institucionais |
| `404.html` | Página não encontrada |
| `ferramentas/` | Só para o protótipo: `montar.py` copia cabeçalho e rodapé da home para as outras páginas; `dados.json` são as notícias de exemplo |
| `css/style.css` | Todo o estilo, com índice no topo e variáveis (cores, fontes, cantos) em `:root` |
| `js/main.js` | Comportamentos, em blocos independentes (tema, data e hora, menu, carrossel, filtros, vídeo, anúncio fixo, cookies) |
| `img/` | Fotos de exemplo tiradas do portal atual (no WordPress vêm das notícias) |

## Páginas do protótipo e modelos do WordPress

| Protótipo | Modelo no tema | Endereço no WordPress |
|---|---|---|
| `index.html` | `front-page.php` | `/` |
| `noticia.html` | `single.php` | `/AAAA/MM/DD/titulo/` |
| páginas de editoria | `category.php` | `/categoria/politica-mt/`, `/categoria/geral/` … (mesmos do menu atual) |
| `busca.html` | `search.php` | `/?s=termo` |
| `quem-somos.html`, `anuncie.html`, `contato.html` | `page.php` ou modelos de página | `/quem-somos/`, `/anuncie/`, `/contato/` |
| `404.html` | `404.php` | qualquer endereço inexistente |

Cabeçalho e rodapé são idênticos em todas as páginas: viram `header.php` e `footer.php`.
Links marcados com `data-demo` (paginação) só mostram um aviso no protótipo; no tema, tirar o atributo.

## Para quem vai montar o tema WordPress

- **Menus:** os links são os mesmos do portal atual. Editorias em `.editorias__lista` (e repetidas na gaveta do celular e no rodapé); institucionais em `.cabecalho__links`.
- **Notícias:** todo cartão é um `<article class="card">` com variações `card--lado`, `card--grande` e `card--texto` (sem foto). O cartão funciona com ou sem `.card__foto`.
- **Carrossel de manchetes:** cada destaque é um `<article class="slide">` dentro de `[data-trilho]`; pontos e setas são criados pelo script.
- **Filtros da seção Geral:** agem sobre os cartões da página pelo atributo `data-cat`. Para trocar por AJAX, substitua o conteúdo de `[data-grade]` e chame a função `arrumar()` (ver comentário no `main.js`).
- **Vídeo:** `<a class="video" data-video="ID_DO_YOUTUBE">`; o player só carrega no clique.
- **Data e hora:** preenchidas pelo script no fuso `America/Cuiaba`.
- **Página da notícia:** barra de leitura (`[data-progresso]`), tempo de leitura calculado, compartilhar (WhatsApp, Facebook, X, Telegram, copiar link) e botões A−/A+ para o tamanho do texto. O anúncio `noticia-meio` entra depois do 3º parágrafo.
- **Formulários (Contato e Anuncie):** a validação está no `main.js`; ligar ao plugin de formulários mantendo os nomes dos campos.
- **Tema claro/escuro:** atributo `data-theme` em `<html>`, guardado em `localStorage`.

## Espaços de publicidade

Cada espaço é `<div class="anuncio anuncio--FORMATO" data-posicao="NOME">`. Troque o conteúdo interno pelo código do banner; a altura já fica reservada.

| `data-posicao` | Computador | Celular |
|---|---|---|
| `topo`, `meio-1`, `meio-2`, `rodape` | 1080 × 110 | 320 × 100 |
| `lateral-cima`, `lateral-baixo` | 300 × 250 | 300 × 250 |
| `noticia-meio` (dentro do texto da notícia) | 300 × 250 | 300 × 250 |
| `celular-meio` | não aparece | 300 × 250 |
| `celular-fixo` (pé da tela, com fechar) | não aparece | 320 × 50 |

## Redes sociais

Instagram, Facebook e YouTube aparecem no topo (computador), na gaveta do menu (celular), no rodapé e nos cartões de contato (Quem Somos, Anuncie, Contato).
Endereços em uso: `instagram.com/canalmt`, `facebook.com/canalmt` e `youtube.com/@canalmt`. Para trocar, editar o bloco `redes-canal` do `index.html` e a função `contato_itens()` em `ferramentas/montar.py`, e rodar `python3 ferramentas/montar.py`.

## Fontes

- **Inter** (títulos, menu, botões e números), pesos 400 e 700, pelo Google Fonts.
- **Aeonik** (texto corrido), pesos 400 e 700. É fonte paga da CoType Foundry e não está no Google Fonts: com a licença web, colocar `aeonik-regular.woff2` e `aeonik-bold.woff2` em `fonts/` e liberar o `@font-face` comentado no topo de `css/style.css`. Até lá, o texto cai para a Inter.
