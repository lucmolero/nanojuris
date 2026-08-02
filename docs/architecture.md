# Architecture

NanoJuris e organizado em camadas.

```text
providers
  Conectores para fontes publicas.

models
  Contratos tipados e estaveis.

client
  Fachada de alto nivel.

exporters
  JSONL, Markdown e outros formatos.

cli
  Interface de linha de comando.
```

## Provider contract

Todo provider deve implementar:

```python
search(query)
get_decisions(precedent_id)
get_parameters()
```

## Modelo unificado

O modelo principal e `JurisprudenceResult`:

```text
id
source
court
type
number
question
thesis
summary
status
rapporteur
updated_at
paradigm_cases
source_trace
```

## Rastreabilidade

`SourceTrace` preserva:

- provider;
- endpoint;
- query;
- data de coleta;
- URL publica;
- limitacoes.

Isso permite auditoria por advogados, pesquisadores e sistemas corporativos.
