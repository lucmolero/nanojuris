# `stj_scon`

## Identidade

- Fonte oficial: pesquisa publica de acordaos STJ/SCON.
- Categoria: `court_jurisprudence`.
- Familia tecnica: `html_jurisprudencia_superior`.
- Uso preferencial: acordaos do STJ quando a pagina publica responder sem
  validacao de acesso.
- Nivel atual esperado: 2.

## Contrato conhecido

O provider atual envia `POST /SCON/pesquisar.jsp` para a base de acordaos. O
escopo v1 cobre lista de resultados e parser offline por fixture HTML
sanitizada. O inteiro teor ainda nao foi promovido como contrato estavel.

Payload declarado pelo provider:

```text
b=ACOR
O=JT
livre=<texto livre do usuario>
num_processo=<numero quando informado>
```

Campos extraidos quando o HTML segue o contrato esperado:

- numero do processo;
- numero de registro;
- classe/tipo decisorio;
- relator;
- orgao julgador;
- data de julgamento;
- data de publicacao;
- ementa/resumo;
- URL oficial do documento quando houver link no resultado.

## Estados de resposta

| Estado | Como o provider deve tratar |
| --- | --- |
| Resultado publico | Retornar `SearchPage` com `CanonicalDecision` derivavel. |
| Zero resultado | Retornar `SearchPage` vazia quando o HTML indicar ausencia de resultado. |
| Captcha/controle de acesso | Levantar `AccessControlRequiredError`. |
| HTTP 429 | Levantar `RateLimitDetectedError`. |
| HTTP 5xx | Levantar `SourceUnavailableError`. |
| HTML sem container esperado | Levantar `ParserContractChangedError`. |

## Pontos fortes

- Fonte institucional de alto valor para jurisprudencia superior.
- Parser ja preserva `SourceTrace` e campos objetivos.
- O provider evita reinterpretar operadores oficiais do STJ.

## Lacunas a aprofundar

- Mapear fluxo publico SCON com HAR limpo e parametros minimos.
- Separar acordaos, monocraticas, sumulas e informativos como superficies
  tecnicas diferentes.
- Adicionar fixtures de acesso controlado e busca vazia.
- Validar URL publica de inteiro teor antes de promover `get_document`.
- Documentar operadores oficiais com exemplos seguros.

## MCP e agentes

Recomendacao: fonte estrategica, mas ainda inicial. O agente deve:

- consultar `source_contracts("stj_scon")` antes da busca;
- avisar que a fonte pode exigir validacao de acesso;
- usar `page_size` pequeno;
- preservar operadores STJ fornecidos pelo usuario sem "traduzir" juridicamente;
- sugerir fontes alternativas quando receber `AccessControlRequiredError`.

## Fixtures esperadas

- `tests/fixtures/stj_scon_acordaos_result.html` implementada;
- `tests/fixtures/stj_scon_access_control.html` implementada;
- `tests/fixtures/stj_scon_empty.html` implementada;
- futura fixture de inteiro teor publico, somente se a URL responder sem
  bypass.

## Proximos passos

- [ ] Capturar HAR publico limpo de busca simples.
- [ ] Reduzir headers ao minimo necessario.
- [ ] Documentar parametros obrigatorios/opcionais em detalhe.
- [x] Adicionar fixtures de acesso controlado e vazio.
- [ ] Reavaliar nivel de contrato para 3 quando o dossie HTTP estiver completo.
