# Elite Extraction Blueprint

NanoJuris deve ser uma biblioteca open source premium para extracao,
normalizacao e unificacao de fontes brasileiras de jurisprudencia. O projeto
nao deve interpretar o merito juridico, recomendar teses ou substituir revisao
humana. A camada de valor e extrair dados confiaveis, rastreaveis e consumiveis
por advogados, pesquisadores juridicos e agentes de IA via MCP.

## Principio de produto

O usuario deve conseguir fazer tres coisas com seguranca:

- buscar jurisprudencia em fontes nacionais relevantes;
- obter dados estruturados e auditaveis;
- reutilizar os dados em planilhas, bases locais, pipelines e agentes de IA.

Toda funcionalidade deve preservar:

- fonte original;
- endpoint ou URL publica;
- payload de consulta quando aplicavel;
- data/hora de coleta;
- status de acesso;
- limitacoes conhecidas;
- versao do parser usado.

## Criterios tecnicos de excelencia

Toda evolucao do NanoJuris deve preservar estes criterios publicos:

- arquitetura modular entre providers, fetchers, parsers, modelos canonicos,
  stores, exporters, CLI e MCP;
- modelos tipados e estaveis para uso por Python, automacoes e agentes;
- extracao objetiva de dados, sem interpretacao juridica ou recomendacao;
- rastreabilidade por `SourceTrace` e `ExtractionTrace` sempre que houver coleta
  ou parsing;
- fixtures publicas representativas e testes offline para cada provider;
- testes live apenas opt-in;
- deteccao explicita de captcha, login, segredo de justica e controle de acesso,
  sem bypass;
- documentacao honesta sobre fontes implementadas, parciais e planejadas;
- UX pratica para advogados, desenvolvedores, jurimetristas, analistas de dados
  e agentes de IA.

## Arquitetura alvo

```text
sources
  APIs, HTML publico, PDF publico e catalogos oficiais.

fetchers
  Aquisicao responsavel de conteudo bruto com retries, timeout, rate limit e
  status de acesso.

parsers
  Conversao de HTML/PDF/JSON em documentos intermediarios.

extractors
  Extracao objetiva de campos juridicos e tecnicos.

canonical models
  Decisoes, documentos, precedentes, sumulas, informativos e traces.

stores
  Persistencia local e analitica.

exports
  JSON, JSONL, CSV, Markdown e formatos analiticos.

mcp
  Ferramentas locais para agentes de IA consultarem dados e fontes.
```

## Modelos canonicos a criar

### `CanonicalDecision`

Campos minimos:

- `id`
- `source`
- `court`
- `case_number`
- `registry_number`
- `decision_type`
- `case_class`
- `subject`
- `rapporteur`
- `judging_body`
- `origin_county`
- `judgment_date`
- `publication_date`
- `summary`
- `full_text`
- `document_url`
- `source_trace`
- `extraction_trace`
- `raw`

### `CanonicalPrecedent`

Campos minimos:

- `id`
- `source`
- `court`
- `precedent_type`
- `number`
- `status`
- `question`
- `thesis`
- `affected_cases`
- `paradigm_cases`
- `updated_at`
- `source_trace`
- `extraction_trace`
- `raw`

### `CanonicalDocument`

Campos minimos:

- `id`
- `source`
- `document_type`
- `content_type`
- `title`
- `text`
- `url`
- `sha256`
- `byte_size`
- `retrieved_at`
- `access_status`
- `source_trace`
- `extraction_trace`
- `raw_metadata`

## Status padronizados

### `AccessStatus`

- `public`
- `partial`
- `access_control_required`
- `login_required`
- `secret_or_restricted`
- `not_found`
- `source_unavailable`

### `ExtractionStatus`

- `complete`
- `partial`
- `empty`
- `parser_contract_changed`
- `unsupported_format`
- `failed`

## Fontes nacionais prioritarias

### Prioridade 0

- BNP/Pangea: precedentes qualificados e catalogo nacional.
- TJSP/CJSG: acordaos e inteiro teor publico quando disponivel.
- STJ/SCON: jurisprudencia, repetitivos e sumulas.
- STF: jurisprudencia, repercussao geral e sumulas.

### Prioridade 1

- TST: jurisprudencia trabalhista e informativos.
- TSE: jurisprudencia eleitoral e TREs quando viavel.
- TRF4/eproc: jurisprudencia federal com eproc.
- TRF1, TRF2, TRF3, TRF5 e TRF6.

### Prioridade 2

- TJs estaduais com portais publicos estaveis.
- Diarios oficiais apenas quando usados como fonte auxiliar de publicacao.
- DataJud e DJEN como fontes complementares, nao substitutas de jurisprudencia.

## MCP minimo

O pacote opcional `nanojuris[mcp]` deve entregar um servidor local com tools
deterministicas:

- `list_sources`: lista providers e capacidades.
- `search_jurisprudence`: busca paginada com filtros estruturados.
- `get_decision`: recupera decisao por identificador canonico.
- `get_document`: recupera documento/texto quando publicamente disponivel.
- `export_results`: exporta resultados em formatos suportados.
- `source_diagnostics`: explica disponibilidade, status e limites da fonte.

Todas as respostas MCP devem ser JSON serializavel, paginadas quando necessario
e acompanhadas de traces.

## Ordem de implementacao

1. Criar modelos canonicos e traces de extracao. Implementado.
2. Adicionar exportacao CSV orientada a dados juridicos objetivos. Implementado.
3. Implementar diagnostico de fontes e capacidades. Implementado no contrato base.
4. Criar contratos reutilizaveis de aquisicao e parsing. Implementado.
5. Separar aquisicao, parsing e normalizacao nos providers existentes.
6. Criar store SQLite local. Implementado como backend acessivel inicial.
7. Planejar `PostgresStore` para uso multiusuario e producao.
8. Evoluir TJSP/CJSG para extracao de inteiro teor publico com status claro.
9. Implementar STJ como primeiro provider novo completo.
10. Criar servidor MCP local com tools minimas.
11. Adicionar benchmarks de cobertura por fonte.
12. Expandir para STF, TST, TSE, TRFs e TJs.

## Definicao de pronto

Uma fonte so deve ser considerada suportada quando entregar:

- provider documentado;
- fixtures offline publicas representativas;
- teste unitario de parser;
- teste de contrato do modelo canonico;
- teste live opcional;
- status de acesso explicito;
- traces completos;
- exemplo Python;
- exemplo CLI;
- cobertura no MCP quando aplicavel.
