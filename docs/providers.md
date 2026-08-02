# Providers

## `bnp_pangea`

Provider inicial do NanoJuris.

Endpoints publicos usados:

```text
GET  /parametros
GET  /sugestoes?texto=<termo>
POST /precedentes
GET  /precedentes/{id}/decisoes
```

### Contrato publico

O provider expoe tres niveis de acesso:

```python
client.get_parameters()
client.get_catalog()
client.list_suggestions("icms")
```

`get_parameters()` retorna o JSON bruto da fonte, util para auditoria tecnica.
`get_catalog()` converte orgaos e especies para modelos estaveis:

```text
ProviderCatalog
  courts: list[ProviderOption]
  species: list[ProviderOption]
  species_groups: list[dict]
  source_trace: SourceTrace
```

`list_suggestions()` usa o endpoint de sugestoes referenciado pelo frontend. Se
a fonte responder `404`, o recurso e tratado como indisponivel e retorna lista
vazia, sem interromper buscas ou catalogo.

Campos de filtro:

```text
buscaGeral
todasPalavras
quaisquerPalavras
semPalavras
trechoExato
atualizacaoDesde
atualizacaoAte
cancelados
ordenacao
nr
orgaos
tipos
pagina
tamanhoPagina
```

### Orgaos

Os orgaos sao identificados por siglas publicas como:

```text
STF
STJ
TST
STM
TNU
TRF01..TRF06
TJSP
TRT02
```

Alguns orgaos podem aparecer marcados pela fonte como `semPrecedentes`. O
NanoJuris representa isso como `ProviderOption.disabled`.

### Especies

Especies comuns ja cobertas por fixtures:

```text
RG    Tema de Repercussao Geral
RR    Recurso Especial Repetitivo
IAC   Incidente de Assuncao de Competencia
IRDR  Incidente de Resolucao de Demandas Repetitivas
SUM   Sumula
SV    Sumula Vinculante
```

### CLI

Parametros brutos:

```bash
nanojuris parametros
```

Catalogo normalizado:

```bash
nanojuris parametros --catalogo
```

Sugestoes, quando disponiveis:

```bash
nanojuris sugestoes "icms"
```

Busca:

```bash
nanojuris buscar "ICMS" --orgaos STF,STJ --tipos RG,RR --limite 5
```

### Testes live opcionais

Os testes live ficam desligados por padrao e consultam fonte publica real apenas
quando explicitamente habilitados:

```bash
$env:NANOJURIS_RUN_LIVE = "1"
python -m pytest -m live
```

## Planejados

- `tjsp_cjsg`
- `stj`
- `stf`
- `tse`
- `trf4`
- `tst`
