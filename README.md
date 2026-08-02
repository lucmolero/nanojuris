<p align="center">
  <strong>NanoJuris</strong>
</p>

<h1 align="center">Jurisprudencia publica brasileira para Python e agentes de IA</h1>

<p align="center">
  Busque, normalize e audite precedentes e jurisprudencia publica com rastreabilidade.
</p>

<p align="center">
  <a href="https://github.com/lucmolero/nanojuris/actions/workflows/ci.yml">
    <img src="https://github.com/lucmolero/nanojuris/actions/workflows/ci.yml/badge.svg" alt="CI" />
  </a>
  <a href="https://github.com/lucmolero/nanojuris/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT" />
  </a>
  <a href="https://github.com/lucmolero/nanojuris">
    <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+" />
  </a>
</p>

<p align="center">
  <a href="https://github.com/lucmolero/nanojuris/actions">Actions</a>
  ·
  <a href="docs/quickstart.md">Quickstart</a>
  ·
  <a href="docs/architecture.md">Arquitetura</a>
  ·
  <a href="docs/responsible-use.md">Uso responsavel</a>
</p>

## O que e

NanoJuris e uma biblioteca Python open source para consulta, normalizacao e
auditoria de jurisprudencia publica brasileira.

O projeto nasce com o provider `bnp_pangea`, que consulta a API publica usada
pelo frontend do Banco Nacional de Precedentes/Pangea. A arquitetura foi
desenhada para receber fontes JSON e HTML legadas. O provider `tjsp_cjsg`
consulta a pesquisa publica de jurisprudencia do TJSP/CJSG quando a fonte nao
exige controle de acesso.

## Por que existe

Advogados, pesquisadores e times de tecnologia juridica precisam de dados de
jurisprudencia em formato confiavel, rastreavel e facil de integrar com
automacoes e agentes de IA.

NanoJuris entrega:

- modelos tipados;
- provider BNP/Pangea funcional;
- cliente Python simples;
- CLI;
- exportacao JSON, JSONL e Markdown;
- rastreabilidade de fonte;
- governanca de uso responsavel.

## Instalacao local

```bash
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

## Primeiro uso em Python

```python
from nanojuris import NanoJurisClient

client = NanoJurisClient()

page = client.search(
    "ICMS consumidor final",
    courts=["STF", "STJ"],
    types=["RG", "RR"],
    page_size=5,
)

for result in page.results:
    print(result.court, result.type, result.number)
    print(result.thesis)
```

## Primeiro uso via CLI

```bash
nanojuris buscar "ICMS consumidor final" --orgaos STF,STJ --tipos RG,RR --limite 5
```

Markdown:

```bash
nanojuris buscar "ICMS consumidor final" --orgaos STF,STJ --formato markdown
```

JSONL:

```bash
nanojuris buscar "ICMS consumidor final" --formato jsonl
```

## Provider inicial

### `bnp_pangea`

Fonte: Banco Nacional de Precedentes/Pangea.

Recursos:

- parametros publicos de orgaos e especies;
- catalogo normalizado de tribunais e especies;
- sugestoes publicas de pesquisa;
- busca textual de precedentes;
- agregacoes por tribunal e especie;
- detalhes de decisoes vinculadas quando disponiveis;
- rastreabilidade de endpoint, filtro e data de coleta.

Catalogo normalizado:

```bash
nanojuris parametros --catalogo
```

Sugestoes, quando o endpoint publico estiver disponivel:

```bash
nanojuris sugestoes "icms"
```

Teste live opcional:

```bash
$env:NANOJURIS_RUN_LIVE = "1"
python -m pytest -m live
```

### `tjsp_cjsg`

Fonte: Consulta de Jurisprudencia do TJSP/CJSG.

Recursos:

- busca completa via formulario publico;
- parser HTML de resultados;
- extracao de numero do processo/recurso, relator, comarca, orgao julgador,
  classe, assunto e ementa;
- identificadores `cdAcordao` e `cdForo`;
- URL publica de inteiro teor quando disponivel;
- deteccao de captcha/controle de acesso sem bypass.

Exemplo:

```bash
nanojuris buscar "infanticidio" --fonte tjsp_cjsg --tipos acordao --limite 5
```

Se o TJSP exigir captcha, o provider interrompe a operacao com erro claro.

## Filosofia tecnica

NanoJuris nao tenta burlar fontes publicas. O projeto deve:

- preferir APIs publicas e oficiais;
- detectar controles de acesso e parar;
- aplicar timeout e limites;
- separar extracao de interpretacao juridica;
- preservar fonte, endpoint e query usada;
- manter fixtures sem dados sensiveis.

## Roadmap

- `v0.1`: BNP/Pangea, CLI, modelos, testes e docs.
- `v0.2`: TJSP/CJSG com parser HTML e tratamento de captcha.
- `v0.3`: STJ.
- `v0.4`: STF.
- `v0.5`: MCP local para agentes de IA.
- `v0.6`: TSE/TREs.
- `v0.7`: TRF4 e TST.

## Projeto independente

NanoJuris nao e produto oficial do CNJ, TJSP, STJ, STF ou qualquer tribunal. A
biblioteca organiza consultas a fontes publicas ou legitimamente acessiveis ao
usuario.
