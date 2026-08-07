# Quickstart

## Instale para desenvolvimento

```bash
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

## Busque precedentes

```python
from nanojuris import NanoJurisClient

client = NanoJurisClient()
page = client.search(
    "ICMS consumidor final",
    courts=["STF", "STJ"],
    types=["RG", "RR"],
    page_size=5,
)

print(page.total)
print(page.results[0].to_dict())
```

Extrair inteiro teor publico quando a fonte disponibiliza o documento:

```python
document = client.get_document("tjsp-cjsg-20787558-0", source="tjsp_cjsg")
print(document.sha256, document.byte_size)
print(document.text[:1000])
```

No `tjsp_cjsg`, o documento canonico entrega texto limpo para leitura por
agentes, mantendo hash, tamanho, URL, trace e metadados do HTML publico
original.

## Use a CLI

```bash
nanojuris buscar "ICMS consumidor final" --orgaos STF,STJ --tipos RG,RR --limite 5
```

Exporte campos objetivos de extracao em CSV:

```bash
nanojuris buscar "ICMS consumidor final" --orgaos STF,STJ --tipos RG,RR --limite 5 --formato csv
```

Exporte registros canonicos em JSONL:

```bash
nanojuris buscar "ICMS consumidor final" --orgaos STF,STJ --tipos RG,RR --limite 5 --formato canonical-jsonl
```

## Consulte decisoes vinculadas

```bash
nanojuris precedente stf-rg-615
```

## Liste catalogo BNP/Pangea

```bash
nanojuris parametros --catalogo
```

## Consulte sugestoes publicas

```bash
nanojuris sugestoes "icms"
```

## Descubra fontes e capacidades

```bash
nanojuris fontes
nanojuris diagnostico --fonte tjsp_cjsg
nanojuris tribunais --ramo state --uf SP
nanojuris tribunais --sistema esaj_cjsg
nanojuris tribunais --implementados
```

Em Python:

```python
from nanojuris import NanoJurisClient

client = NanoJurisClient()

for source in client.list_sources():
    print(source.source, source.document_types, source.extracted_fields)
```

O catalogo brasileiro tambem esta disponivel diretamente:

```python
from nanojuris import get_court, list_courts

print(get_court("tj-sp").name)
print([court.code for court in list_courts(branch="state", state="SP")])
print([court.code for court in list_courts(source_system="esaj_cjsg")])
```

## Rode uma demo de juridimetria

```bash
python examples/idpj_jurimetry_demo.py
```

Essa demo pesquisa `incidente de desconsideracao da personalidade juridica`,
resume fontes consultadas, fontes puladas, erros e uma amostra de campos uteis.
Veja tambem [jurimetry-idpj-demo.md](jurimetry-idpj-demo.md).

## Use a camada de aquisicao

```python
from nanojuris import FetchRequest, HttpFetcher

fetcher = HttpFetcher()
content = fetcher.fetch(
    FetchRequest(
        source="example",
        url="https://example.test/jurisprudencia",
        endpoint="/jurisprudencia",
    )
)

print(content.access_status)
print(content.sha256)
```

## Persista registros canonicos localmente

```python
from nanojuris import CanonicalDecision, SQLiteStore

with SQLiteStore("nanojuris.db") as store:
    store.save(
        CanonicalDecision(
            id="dec-1",
            source="tjsp_cjsg",
            court="TJSP",
            case_number="0003938-14.2017.8.26.0323",
        )
    )

    print(store.count(kind="decision"))
```

Tambem e possivel buscar e salvar em uma unica chamada:

```python
from nanojuris import NanoJurisClient, SQLiteStore

client = NanoJurisClient()

with SQLiteStore("nanojuris.db") as store:
    records = client.search_and_store("ICMS", store=store)
    print(len(records))
```

Via CLI:

```bash
nanojuris buscar "ICMS" --store nanojuris.db --label "Pesquisa ICMS"
nanojuris store stats nanojuris.db
nanojuris store query nanojuris.db --kind decision --tribunal TJSP
nanojuris store query nanojuris.db --kind decision --tribunal TJSP --compacto
nanojuris store get nanojuris.db decision dec-1
nanojuris store get nanojuris.db decision dec-1 --compacto
nanojuris store runs nanojuris.db
nanojuris store records nanojuris.db run-...
nanojuris store records nanojuris.db run-... --compacto
nanojuris store export nanojuris.db run-... --formato markdown
nanojuris store export nanojuris.db run-... --formato csv
nanojuris store export nanojuris.db run-... --formato jsonl --limite 100 --offset 100
nanojuris documento tjsp-cjsg-20787558-0 --fonte tjsp_cjsg
nanojuris documento tjsp-cjsg-20787558-0 --fonte tjsp_cjsg --compacto
nanojuris documento "0003938-14.2017.8.26.0323" --fonte tjsp_esaj_cpopg
nanojuris documento "0003938-14.2017.8.26.0323" --fonte tjsp_esaj_cpopg --compacto
```

Formatos recomendados por publico:

- advogados: `markdown` para revisao e compartilhamento;
- jurimetristas e analistas de dados: `csv` ou `jsonl`;
- desenvolvedores: `jsonl` para pipelines incrementais;
- agentes de IA: `json` quando precisarem do envelope com metadados do run.
- inteiro teor: `documento`/`get_document` quando a fonte publica permitir acesso
    direto, com hash e trace para auditoria.

Para bases grandes, avance com `--offset` mantendo o mesmo `run_id`. Isso deixa a
coleta reproduzivel para jurimetria, BI e agentes.

Um fluxo SDK completo, offline e sem rede, esta em
[../examples/sdk_workflow.py](../examples/sdk_workflow.py).

## Consulte processo publico no TJSP/e-SAJ

```bash
nanojuris documento "0003938-14.2017.8.26.0323" --fonte tjsp_esaj_cpopg
nanojuris documento "0003938-14.2017.8.26.0323" --fonte tjsp_esaj_cpopg --compacto
nanojuris buscar "0003938-14.2017.8.26.0323" --fonte tjsp_esaj_cpopg --formato markdown
```

Esse provider usa a rota publica `cpopg/search.do`, segue o redirect oficial
para `show.do` e retorna dados objetivos como classe, assunto, foro, vara, juiz,
partes e movimentacoes publicas. Autos restritos, login e captcha continuam fora
do escopo de automacao.

## Busque no TJSP/CJSG

```bash
nanojuris buscar "infanticidio" --fonte tjsp_cjsg --tipos acordao --limite 5
```

Se a fonte exigir captcha, o NanoJuris retorna erro claro e nao tenta contornar
o controle de acesso.
