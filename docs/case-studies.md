# Case Studies: Real-World Extraction Workflows

Este documento registra simulacoes praticas de uso da NanoJuris por tres
publicos-alvo: advogados usando agentes de IA, pesquisadores de jurimetria e
desenvolvedores criando sistemas. O objetivo e identificar o que a biblioteca ja
resolve, o que ainda falta e o que deve mudar para virar um projeto open source
premium de extracao de dados juridicos.

As simulacoes abaixo foram executadas localmente com um provider controlado,
sem rede, exercitando as APIs reais do pacote: `NanoJurisClient`, canonical
mappers, CSV exporter, `ProviderCapabilities` e `SQLiteStore`.

Para transformar estes cenarios em validacao pratica de backlog, use tambem a
matriz detalhada em [use-case-validation-matrix.md](use-case-validation-matrix.md).

## Resultado observado da simulacao

Resumo da execucao local:

```json
{
  "lawyer": {
    "search_total": 2,
    "first_result_id": "tjsp-cjsg-20787558-0",
    "first_summary_available": true,
    "canonical_kinds": ["CanonicalDecision", "CanonicalPrecedent"],
    "document_url_available": true
  },
  "jurimetry": {
    "csv_row_count": 2,
    "courts": ["STJ", "TJSP"],
    "record_kinds": ["decision", "precedent"],
    "store_counts": {
      "total": 2,
      "decisions": 1,
      "precedents": 1
    }
  },
  "developer": {
    "stored_decision_case_number": "0003938-14.2017.8.26.0323",
    "stored_precedent_type": "RR",
    "api_objects": ["NanoJurisClient", "SQLiteStore", "ProviderCapabilities"]
  }
}
```

## Caso 1: advogado usando agente de IA para buscar jurisprudencia

### Jornada simulada

O advogado quer jurisprudencia para embasar uma peca e pede a um agente de IA:

> Busque jurisprudencia sobre homicidio qualificado e organize os resultados.

Fluxo executado:

1. O agente lista fontes com `client.list_sources()`.
2. O agente escolhe uma fonte por capacidades declaradas.
3. O agente executa `client.search(...)`.
4. A resposta e convertida com `search_page_to_canonical(...)`.
5. O resultado e exportado em CSV para revisao humana.
6. Os registros canonicos sao persistidos em `SQLiteStore`.

### O que atende bem

- O agente consegue descobrir fontes e campos antes de consultar.
- O resultado preserva `SourceTrace` e `ExtractionTrace`.
- A decisao vira `CanonicalDecision` e o precedente vira `CanonicalPrecedent`.
- O CSV possui colunas objetivas uteis para triagem: tribunal, processo,
  classe, assunto, relator, orgao julgador, comarca, datas, URL e status.
- O store permite manter uma base local revisavel.

### Lacunas reais

- A biblioteca nao tem um `SearchSession` ou `ResearchProject` para agrupar
  buscas, fontes e exportacoes.
- Saidas completas de `store query`, `store get` e `store records` podem ficar
  grandes quando a fonte publica expõe muitas movimentacoes; use `--compacto`
  para triagem humana.
- Ainda falta um score de completude por resultado para revisao rapida.
- Ainda falta um relatorio persistido de ultimo status live por fonte.

### Mudancas recomendadas

Prioridade alta:

- Manter exemplos reais por publico atualizados com providers live validados.
- Adicionar score de completude por registro.
- Registrar ultimo status live conhecido por fonte no diagnostico.

Prioridade media:

- Adicionar `ResearchRun` com id, consulta, fonte, total, status e timestamps.
- Permitir exportar uma busca salva por id.
- Adicionar logs de falha por fonte.

## Caso 2: pesquisador de jurimetria analisando dados

### Jornada simulada

O pesquisador quer montar uma base de dados para contar resultados por tribunal,
classe e tipo de registro.

Fluxo executado:

1. Busca retorna resultados mistos.
2. `to_csv(page)` gera uma tabela objetiva.
3. `SQLiteStore.save_many(...)` persiste os registros canonicos.
4. `store.count(kind=...)` e `store.list_records(...)` permitem consultas
   simples.

### O que atende bem

- CSV ja oferece um ponto de entrada bom para pandas, Excel e BI.
- SQLite permite persistencia local reprodutivel.
- O schema preserva JSON canonico completo, evitando perda enquanto o modelo
  evolui.
- Indices por `source` e `case_number` cobrem consultas basicas.

### Lacunas reais

- O CSV ainda mistura decisoes e precedentes em uma tabela unica; isso e bom
  para exportacao rapida, mas limitado para analise estatistica fina.
- Falta exportacao canônica JSONL por tipo de registro.
- Falta `store.query(...)` com filtros por tribunal, data, classe, assunto e
  relator.
- Falta schema analitico ou views para jurimetria.
- Falta deduplicacao avancada por benchmark de fonte alem da `canonical_key`
  basica do store.
- Falta benchmark de completude por fonte.

### Mudancas recomendadas

Prioridade alta:

- Adicionar `SQLiteStore.query_records(...)` com filtros estruturados.
- Adicionar exportacao `canonical_jsonl` e CSV por tipo: decisoes, precedentes,
  documentos.
- Adicionar colunas indexaveis extras: `rapporteur`, `subject`,
  `decision_type`, `publication_date`, `precedent_type`.
- Criar `StoreStats` para contagens por fonte, tipo e status.

Prioridade media:

- Criar deduplicacao por chave canonica.
- Expandir CLI para exportar uma busca salva por id.
- Adicionar guias com pandas e DuckDB.

## Caso 3: desenvolvedor criando um sistema com NanoJuris

### Jornada simulada

O desenvolvedor quer usar a biblioteca como backend de um produto ou automacao.

Fluxo executado:

1. Instancia `NanoJurisClient`.
2. Lista capacidades com `list_sources()`.
3. Executa busca.
4. Converte para modelos canonicos.
5. Salva em SQLite.
6. Recupera registros por tipo e id.

### O que atende bem

- API Python e simples.
- `ProviderCapabilities` reduz acoplamento com detalhes internos de cada fonte.
- Modelos dataclass sao faceis de serializar e testar.
- Store local permite prototipos rapidos.
- O projeto ainda nao exige dependencias pesadas.

### Lacunas reais

- Nao existe `PostgresStore` nem contrato de compatibilidade.
- Nao ha camada de jobs, retry persistido ou filas.
- Nao ha API assíncrona.
- Ainda nao ha padrao de plugin externo para novos tribunais.

### Mudancas recomendadas

Prioridade alta:

- Criar exemplo de integracao em app Python.
- Formalizar plugin externo de providers.
- Definir estrategia de jobs/retry para coletas longas.

Prioridade media:

- Planejar `PostgresStore` com `psycopg` opcional.
- Criar interface para providers externos.
- Adicionar callbacks/logging estruturado.

## Decisao: SQLite ou PostgreSQL?

A simulacao confirma a decisao atual:

- SQLite e melhor para o core open source inicial, porque permite uso imediato
  por advogados, pesquisadores e desenvolvedores sem infraestrutura.
- PostgreSQL deve ser backend posterior, quando houver contrato de store mais
  maduro, necessidade multiusuario e MCP/API em producao.

Nao e uma escolha excludente. A estrategia correta e:

1. estabilizar `SQLiteStore` e a interface de store;
2. adicionar filtros e estatisticas;
3. criar `PostgresStore` compatível como extra opcional.

## Backlog resultante

### P0: completar o fluxo real de dados

- `client.search_canonical(...)`: implementado.
- `client.search_and_store(...)`: implementado.
- `SQLiteStore.query_records(...)`: implementado.
- `StoreStats`: implementado.
- exportacao canônica JSONL: implementado.
- CSV separado por tipo de registro: implementado.
- `CanonicalStore` como contrato: implementado.

### P1: agente de IA e MCP

- `nanojuris.mcp` opcional: implementado como `nanojuris.mcp_server`.
- `list_sources`: implementado.
- `source_diagnostics`: implementado.
- `search_jurisprudence`: implementado.
- `get_document`: implementado.
- `export_results`: implementado.
- paginação e limites de resposta: parcialmente implementado.

### P2: fontes e documentos

- refatorar `bnp_pangea` para usar pipeline de aquisicao/parsing;
- refatorar `tjsp_cjsg` para separar fetcher, parser e mapper;
- implementar `CanonicalDocument` para inteiro teor publico;
- iniciar provider STJ.

### P3: escala e producao

- `PostgresStore` opcional;
- jobs e reprocessamento;
- deduplicacao avancada por fonte;
- benchmark de cobertura por fonte;
- guias para pandas, DuckDB e BI.

## Conclusao

A biblioteca ja tem uma fundacao coerente para extracao: providers, capacidades,
modelos canonicos, CSV, pipeline e SQLite. O principal gargalo agora e transformar
essas pecas em fluxos de usuario completos: buscar, canonicalizar, salvar,
consultar, exportar e servir via MCP.

A proxima implementacao deve priorizar o MCP real e a extracao de
`CanonicalDocument` para inteiro teor publico, porque o fluxo nativo de buscar,
canonicalizar, salvar, consultar e exportar ja foi incorporado ao core.
