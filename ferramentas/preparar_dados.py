"""Lê as editorias baixadas do portal atual (categorias.json) e gera
ferramentas/dados.json com as notícias limpas, já com as fotos locais.
Uso: python3 ferramentas/preparar_dados.py CAMINHO/categorias.json
Baixa as fotos para img/n/ (só as que ainda não existem)."""
import json, os, re, sys, urllib.parse, urllib.request, hashlib

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MESES = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto',
         'setembro', 'outubro', 'novembro', 'dezembro']
EDITORIAS = {  # chave do arquivo baixado -> (arquivo da página, nome)
    'politica-mt': ('politica', 'Política'), 'geral': ('geral', 'Geral'),
    'geral_policia': ('policia', 'Polícia'), 'geral_economia': ('economia', 'Economia'),
    'geral_economia_agronegocio': ('agronegocio', 'Agronegócio'), 'geral_esporte': ('esporte', 'Esporte'),
    'geral_saude': ('saude', 'Saúde'), 'geral_educacao': ('educacao', 'Educação'),
    'brasil': ('brasil', 'Brasil'), 'mundo': ('mundo', 'Mundo'),
    'artigos': ('artigos', 'Artigos'), 'videos': ('videos', 'Vídeos'),
}
INICIOS = r'(?:O|A|Os|As|Em|No|Na|Nos|Nas|Um|Uma|Com|Após|Segundo|Nesta|Neste|Para|De|Do|Da|Durante|Depois|Mesmo|Ao|À)'

def data_br(t):
    m = re.match(r'(\w+) (\d+), (\d+) – (\d+):(\d+)', t)
    if not m: return '', ''
    mes = MESES.index(m.group(1)) + 1
    return f'{int(m.group(2)):02d}/{mes:02d}/{m.group(3)}', f'{m.group(4)}h{m.group(5)}'

def limpar_resumo(r):
    r = r.replace('\xa0', ' ').strip()
    if r.startswith('Fonte:'):
        corte = r.find('imagem:')
        base = corte + 8 if corte > 0 else 7
        m = re.search(r'\s(' + INICIOS + r')\s', r[base:])
        r = r[base + m.start() + 1:] if m else ''
    return re.sub(r'\s+', ' ', r).strip()

def baixar(url):
    if not url: return ''
    limpa = url.split('?')[0]
    nome = re.sub(r'[^a-z0-9]+', '-', os.path.basename(limpa).lower().rsplit('.', 1)[0])[:40].strip('-')
    nome = nome + '-' + hashlib.md5(limpa.encode()).hexdigest()[:5] + '.jpg'
    destino = os.path.join(RAIZ, 'img', 'n', nome)
    if not os.path.exists(destino):
        caminho = limpa.split('wp-content/uploads/')[1]
        fonte = ('https://i0.wp.com/www.canalmt.com.br/wp-content/uploads/' + urllib.parse.quote(caminho)
                 + '?resize=800%2C500&quality=70&strip=all&ssl=1')
        req = urllib.request.Request(fonte, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            dados = urllib.request.urlopen(req, timeout=40).read()
            if dados[:3] != b'\xff\xd8\xff': return ''
            open(destino, 'wb').write(dados)
        except Exception as e:
            print('sem foto:', fonte, e); return ''
    return 'img/n/' + nome

entrada = json.load(open(sys.argv[1], encoding='utf-8'))
saida = {}
for chave, (arquivo, nome) in EDITORIAS.items():
    bloco = entrada[chave]
    itens = []
    for i in bloco['itens']:
        data, hora = data_br(i['data'])
        titulo = i['titulo']
        if arquivo == 'videos': titulo = re.sub(r'^Veja Vídeo\s*[–-]\s*', '', titulo)
        itens.append(dict(titulo=titulo, data=data, hora=hora, resumo=limpar_resumo(i['resumo']),
                          foto=baixar(i['img']), original=i['url']))
    saida[arquivo] = dict(nome=nome, paginas=bloco['paginas'], itens=itens)
    print(arquivo, len(itens), sum(1 for x in itens if x['foto']))
json.dump(saida, open(os.path.join(RAIZ, 'ferramentas', 'dados.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
