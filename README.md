# CanalMT — novo portal (front-end)

Layout em HTML, CSS e JavaScript puros do novo portal de notícias CanalMT, pronto para receber o painel do WordPress.
Não há etapa de build: abra `index.html` no navegador.

## Arquivos

| Caminho | O que é |
|---|---|
| `index.html` | Página inicial |
| `css/style.css` | Todo o estilo, com índice no topo e variáveis (cores, fontes, cantos) em `:root` |
| `js/main.js` | Comportamentos, em blocos independentes (tema, data e hora, menu, carrossel, filtros, vídeo, anúncio fixo, cookies) |
| `img/` | Fotos de exemplo tiradas do portal atual (no WordPress vêm das notícias) |

## Para quem vai montar o tema WordPress

- **Menus:** os links são os mesmos do portal atual. Editorias em `.editorias__lista` (e repetidas na gaveta do celular e no rodapé); institucionais em `.cabecalho__links`.
- **Notícias:** todo cartão é um `<article class="card">` com variações `card--lado`, `card--grande` e `card--texto` (sem foto). O cartão funciona com ou sem `.card__foto`.
- **Carrossel de manchetes:** cada destaque é um `<article class="slide">` dentro de `[data-trilho]`; pontos e setas são criados pelo script.
- **Filtros da seção Geral:** agem sobre os cartões da página pelo atributo `data-cat`. Para trocar por AJAX, substitua o conteúdo de `[data-grade]` e chame a função `arrumar()` (ver comentário no `main.js`).
- **Vídeo:** `<a class="video" data-video="ID_DO_YOUTUBE">`; o player só carrega no clique.
- **Data e hora:** preenchidas pelo script no fuso `America/Cuiaba`.
- **Tema claro/escuro:** atributo `data-theme` em `<html>`, guardado em `localStorage`.

## Espaços de publicidade

Cada espaço é `<div class="anuncio anuncio--FORMATO" data-posicao="NOME">`. Troque o conteúdo interno pelo código do banner; a altura já fica reservada.

| `data-posicao` | Computador | Celular |
|---|---|---|
| `topo`, `meio-1`, `meio-2`, `rodape` | 1080 × 110 | 320 × 100 |
| `lateral-cima`, `lateral-baixo` | 300 × 250 | 300 × 250 |
| `celular-meio` | não aparece | 300 × 250 |
| `celular-fixo` (pé da tela, com fechar) | não aparece | 320 × 50 |

## Fontes

Figtree (títulos, peso 600) e Source Sans 3 (texto), pelo Google Fonts.
