# MCP Roadmap

NanoJuris deve oferecer um MCP local opcional para agentes de IA consumirem
jurisprudencia brasileira de forma auditavel. O MCP nao deve interpretar merito
juridico, recomendar tese ou redigir argumentos. Ele deve expor dados, fontes,
documentos e traces.

## Principios

- Toda resposta deve ser JSON serializavel.
- Toda resposta de fonte deve incluir `SourceTrace` quando houver consulta.
- Toda resposta extraida deve incluir `ExtractionTrace` quando houver parsing.
- Respostas longas devem ser paginadas.
- Tools nao devem contornar captcha, login, segredo de justica ou acesso
  restrito.
- O servidor MCP deve ser dependencia opcional via `nanojuris[mcp]`.

## Camadas implementadas

NanoJuris separa MCP em duas camadas:

- `nanojuris.mcp_tools`: funcoes puras, testaveis sem servidor MCP e sem rede
  obrigatoria;
- `nanojuris.mcp_server`: wrapper opcional baseado em FastMCP, disponivel com
  `nanojuris[mcp]`.

Rodar servidor MCP:

```bash
nanojuris-mcp
```

Ou em Python:

```python
from nanojuris.mcp_server import create_server

server = create_server()
server.run()
```

## Tools implementadas

### `list_sources`

Retorna `ProviderCapabilities` de todas as fontes registradas.

Uso esperado:

- descobrir fontes nacionais disponiveis;
- verificar formatos e campos extraidos;
- permitir que agentes escolham a fonte correta antes da busca.

### `list_courts`

Retorna o catalogo brasileiro de tribunais conhecido pela NanoJuris,
independentemente de o provider ja estar implementado.

Parametros principais:

- `branch`: `state`, `federal`, `labor`, `superior`, `constitutional`,
  `electoral`, `military` ou `national_council`;
- `state`: UF, como `SP`;
- `source_system`: familia tecnica, como `esaj_cjsg`, `eproc`, `pje` ou
  `datajud`;
- `implemented`: `true` para listar apenas tribunais com provider no core.

Uso esperado: agentes podem descobrir o universo oficial brasileiro antes de
escolher provider, filtro de busca ou estrategia de coleta.

### `source_diagnostics`

Retorna `ProviderCapabilities` de uma fonte especifica, com limitacoes e status
de acesso possiveis.

### `search_jurisprudence`

Executa busca paginada em uma fonte e retorna resultados normalizados.

Parametros minimos:

- `source`
- `text`
- `courts`
- `types`
- `number`
- `page`
- `page_size`
- `canonical`

O tamanho de pagina e limitado de forma conservadora para uso por agentes.

### `export_results`

Exporta resultados em formato textual:

- `json`
- `jsonl`
- `canonical-jsonl`
- `csv`
- `markdown`

### `get_document`

Recupera um inteiro teor publico como `CanonicalDocument` quando o provider
suporta a fonte e o documento esta acessivel sem bypass.

Parametros:

- `document_id`
- `source`

Use para agentes que precisam anexar texto bruto auditavel, hash, tamanho,
trace de fonte e status de acesso antes de qualquer etapa posterior.

### `store_stats`

Retorna contagens agregadas de um store SQLite local criado pela NanoJuris.

Parametro minimo:

- `db_path`

### `store_query`

Consulta registros canonicos salvos em um store SQLite local.

Parametros principais:

- `db_path`
- `kind`
- `source`
- `court`
- `case_number`
- `subject`
- `rapporteur`
- `decision_type`
- `precedent_type`
- `publication_date_from`
- `publication_date_to`
- `limit`

O limite e restringido de forma conservadora para uso por agentes.

### `store_get`

Recupera um registro canonico salvo por tipo e id.

Parametros minimos:

- `db_path`
- `kind`
- `record_id`

### `store_runs`

Lista buscas salvas em um store SQLite local.

Parametros principais:

- `db_path`
- `limit`

### `store_run`

Recupera metadados de uma busca salva.

Parametros minimos:

- `db_path`
- `run_id`

### `store_run_records`

Recupera registros canonicos vinculados a uma busca salva.

Parametros principais:

- `db_path`
- `run_id`
- `limit`
- `offset`

A resposta inclui `total`, `has_more` e `next_offset` para agentes percorrerem
runs grandes com controle de estado.

### `store_export_run`

Exporta registros vinculados a uma busca salva em formato textual.

Parametros principais:

- `db_path`
- `run_id`
- `output_format`: `json`, `jsonl`, `csv` ou `markdown`
- `limit`
- `offset`

Use `json` para agentes que precisam do envelope com metadados do run, `jsonl`
para processamento incremental, `csv` para analise tabular e `markdown` para
revisao humana.

A resposta tambem inclui `total`, `has_more` e `next_offset`.

## Tools planejadas

### `get_decision`

Recupera decisao ou precedente por identificador publico/canonico quando a fonte
suportar.

### `get_document`

Recupera documento publico associado a uma decisao quando disponivel, respeitando
status de acesso.

## Ordem de implementacao MCP

1. Reusar `ProviderCapabilities` em `list_sources` e `source_diagnostics`.
  Implementado.
2. Reusar `NanoJurisClient.search` em `search_jurisprudence`. Implementado.
3. Reusar canonical mappers para respostas de dados objetivos. Implementado.
4. Adicionar limites de pagina, tamanho e timeout por tool. Implementado para
  tamanho de pagina.
5. Cobrir tools com testes sem rede. Implementado.
6. Expor store local para agentes. Implementado com `store_stats`,
  `store_query`, `store_get`, `store_runs`, `store_run`,
  `store_run_records` e `store_export_run`.
7. Implementar `get_decision` e `get_document`.
8. Adicionar exemplos de configuracao em clientes MCP.
