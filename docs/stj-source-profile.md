# STJ Source Profile

Status: ficha tecnica publica pronta para implementacao inicial do provider.

Objetivo: orientar o primeiro provider STJ da NanoJuris com foco em
jurisprudencia publica, rastreabilidade e UX direta para advogados,
desenvolvedores, jurimetristas, analistas de dados e agentes de IA.

## Fonte oficial

Tribunal: Superior Tribunal de Justica.

Catalogo NanoJuris: `STJ`, `branch="superior"`,
`source_system="portal_proprio"`.

URLs oficiais de pesquisa:

- portal institucional: https://www.stj.jus.br/sites/portalp/Inicio
- pesquisa de acordaos SCON: https://processo.stj.jus.br/SCON/acordaos/
- ajuda de decisoes monocraticas SCON:
  https://processo.stj.jus.br/SCON/decisoes/AjudaDTXT.jsp
- precedentes qualificados:
  https://processo.stj.jus.br/repetitivos/temas_repetitivos/?pesquisaAvancada=true

## Provider inicial recomendado

Nome publico recomendado: `stj_scon`.

Escopo v1:

- pesquisar acordaos publicados no SCON;
- extrair metadados objetivos de resultados;
- preservar URL oficial de resultado e inteiro teor quando disponivel;
- mapear resultados para `JurisprudenceResult` e `CanonicalDecision`;
- declarar limites e formatos em `ProviderCapabilities`;
- manter testes offline por fixture HTML publica representativa.

Fora do escopo v1:

- interpretar tese juridica;
- reescrever operadores oficiais do STJ;
- consultar area restrita;
- contornar captcha, login, sessao expirada ou qualquer controle de acesso;
- coletar em massa sem governanca.

## Superficies STJ futuras

| Superficie | Provider futuro | Objeto principal | Modelo canonico |
| --- | --- | --- | --- |
| SCON acordaos | `stj_scon` | acordaos e inteiro teor publico | `CanonicalDecision`, `CanonicalDocument` |
| SCON decisoes monocraticas | `stj_scon_decisoes` | decisoes individuais publicadas | `CanonicalDecision` |
| Precedentes qualificados | `stj_precedentes` | repetitivos, controversias, IACs, SIRDRs, PUILs | `CanonicalPrecedent` |
| Sumulas e informativos | `stj_publicacoes` | sumulas, informativos e publicacoes tematicas | `CanonicalPrecedent` ou documento publico |

## Campos objetivos esperados

Campos minimos para a primeira fixture:

- classe processual;
- numero do processo ou registro;
- orgao julgador quando disponivel;
- relator quando disponivel;
- data de julgamento ou publicacao quando disponivel;
- ementa ou resumo publico;
- URL oficial do resultado;
- URL de inteiro teor quando disponivel;
- raw metadata publico revisado para auditoria.

Campos derivados permitidos:

- `canonical_key`;
- `SourceTrace.provider="stj_scon"`;
- `ExtractionTrace.parser="stj_scon_html"`;
- status de acesso e extracao.

## Parametros e operadores

O STJ possui linguagem propria em algumas superficies. A v1 deve passar a busca
do usuario para a fonte sem reinterpretar operadores oficiais.

Operadores e campos documentados na pesquisa tecnica existente incluem:

- operadores textuais como `E`, `OU`, `NAO`, `ADJ`, `PROX` e `MESMO`;
- radical de busca com `$`;
- campos como `.NUM.`, `.DTPB.` e `.ORG.` em decisoes monocraticas.

A documentacao do provider deve explicar que esses operadores pertencem ao STJ,
nao a uma linguagem proprietaria da NanoJuris.

## Acesso e riscos

Status esperado:

- `AccessStatus.PUBLIC` quando a pagina responder com resultados publicos;
- `AccessStatus.ACCESS_CONTROL_REQUIRED` se houver captcha, validacao humana,
  sessao obrigatoria ou bloqueio de acesso;
- erro claro para indisponibilidade ou mudanca de contrato HTML.

Riscos conhecidos:

- HTML e fluxos de pesquisa podem mudar;
- parametros de sessao/JavaScript podem ser volateis;
- paginas podem retornar erro ou tela intermediaria;
- inteiro teor pode estar indisponivel para parte dos resultados.

## Fixtures e testes obrigatorios

Antes de implementar busca live, criar fixtures publicas representativas:

```text
tests/fixtures/stj_scon_acordaos_result.html
tests/fixtures/stj_scon_acordao_detail.html
tests/fixtures/stj_scon_access_control.html
```

Testes minimos:

- parser de lista de acordaos;
- parser de detalhe/inteiro teor publico quando disponivel;
- deteccao de acesso controlado;
- `get_capabilities` do provider;
- mapeamento para `CanonicalDecision`;
- live test opt-in controlado por `NANOJURIS_RUN_STJ_LIVE=1`.

## UX esperada por publico

| Publico | Resultado minimo |
| --- | --- |
| Advogados | busca por termo, resultado em Markdown e URL oficial para revisao |
| Desenvolvedores | provider isolado, fixtures e erros acionaveis |
| Jurimetristas | CSV/JSONL com tribunal, classe, numero, relator, orgao e datas |
| Analistas de dados | traces, raw metadata e hash quando houver documento |
| Agentes de IA | capabilities, diagnostico de fonte, busca paginada e status de acesso |

## Ordem de implementacao

1. Capturar fixture HTML publica representativa de uma busca simples no SCON acordaos.
2. Criar parser puro `parse_stj_scon_results(html)`.
3. Criar `StjSconProvider.get_capabilities()`.
4. Criar busca usando `HttpFetcher` e timeout conservador.
5. Mapear resultado para `JurisprudenceResult` com `SourceTrace`.
6. Adicionar canonicalizacao para `CanonicalDecision`.
7. Expor em `NanoJurisClient`, CLI, MCP e docs.
8. Adicionar live test opt-in.