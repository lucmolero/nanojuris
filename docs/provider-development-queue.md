# Provider Development Queue

Este documento organiza a fila de novos providers do NanoJuris. Ele separa
fontes ja implementadas, candidatos prontos para fixture/parser e rotas que
dependem de investigacao adicional.

Regra de produto: nenhum provider deve ser implementado antes de existir um
dossie em `docs/source-contracts/` com contrato publico observado, limites,
fixtures esperadas e decisao de uso via MCP.

## Status

| Status | Significado | Pode virar codigo? |
| --- | --- | --- |
| `implemented` | Provider existe em `src/nanojuris/providers` e tem dossie proprio. | ja existe |
| `candidate_ready` | Rota publica retornou conteudo juridico valido em sessao limpa. | sim, apos fixture |
| `candidate_needs_har` | Portal oficial existe, mas falta payload/postback/header publico. | nao ainda |
| `documental` | Conteudo publico util, mas nao e busca decisoria geral. | somente catalogo |
| `blocked_or_inconclusive` | Timeout, desafio, captcha, 404 ou contrato insuficiente. | nao |

## Fila Recomendada

| Ordem | Fonte | Status | Dossie | Proximo passo |
| --- | --- | --- | --- | --- |
| 1 | TJPI/JusPI | `implemented` | [tjpi_juspi.md](source-contracts/tjpi_juspi.md) | monitorar live opt-in e ampliar filtros catalogados |
| 2 | TJGO/Projudi | `implemented` | [tjgo_projudi_jurisprudencia.md](source-contracts/tjgo_projudi_jurisprudencia.md) | validar paginacao live opt-in e numero de processo |
| 3 | TNU/TRF2/TRF6 eproc federal | `implemented` | [eproc_jurisprudencia_federal.md](source-contracts/eproc_jurisprudencia_federal.md) | validar inteiro teor live por instancia e ampliar filtros |
| 4 | TJRR/Juris JSF | `candidate_needs_har` | [tjrr_juris.md](source-contracts/tjrr_juris.md) | HAR de busca simples e postback JSF |
| 5 | TJMT/Jurisprudencia API | `candidate_needs_har` | [tjmt_jurisprudencia_api.md](source-contracts/tjmt_jurisprudencia_api.md) | validar header/payload publico do frontend |
| 6 | TJPA/Jurisprudencia BFF | `candidate_needs_har` | [tjpa_jurisprudencia_bff.md](source-contracts/tjpa_jurisprudencia_bff.md) | capturar payload de `/bff/api/decisoes` |
| 7 | TJPB/PJe Jurisprudencia | `candidate_needs_har` | [tjpb_pje_jurisprudencia.md](source-contracts/tjpb_pje_jurisprudencia.md) | confirmar busca sem desafio Cloudflare |
| 8 | TJPE Sumulas | `documental` | ainda sem ficha propria | avaliar provider de catalogo/sumulas |
| 9 | TJSE Jurisprudencia Judicial | `candidate_needs_har` | ainda sem ficha propria | localizar endpoint final de busca |
| 10 | TJRO/LIAME | `documental` | ainda sem ficha propria | tratar como precedentes/catalogo |
| 11 | TJES | `blocked_or_inconclusive` | ainda sem ficha propria | repetir probe com timeout maior |

## Checklist De Entrada Para Implementar

Antes de criar `src/nanojuris/providers/<provider>.py`:

- [ ] A fonte e oficial ou institucionalmente confiavel.
- [ ] A rota publica foi reproduzida sem cookie pessoal, login, captcha ou
  desafio.
- [ ] Existe HTML/JSON real com conteudo juridico valido.
- [ ] Existe fixture real de sucesso representativa do contrato observado.
- [ ] Existe fixture de vazio ou erro esperado.
- [ ] O dossie define campos canonicos e lacunas.
- [ ] O dossie define quando o MCP deve usar ou pular a fonte.
- [ ] O provider declara `ProviderCapabilities`.
- [ ] O parser funciona offline antes do teste live.

## Ordem De Desenvolvimento Recomendada

1. **TJRR/Juris JSF**: alto potencial, mas exige entender `ViewState` e
   postback PrimeFaces sem usar sessao privada.
2. **TJPA/TJMT APIs**: alto potencial tecnico; precisam confirmar payloads e
   headers publicos emitidos pelo proprio frontend.
3. **TJPB/PJe**: so avancar se o desafio Cloudflare nao aparecer no fluxo
   publico reproduzivel.
4. **Documentais**: TJPE, TJSE e TJRO podem virar providers de catalogo antes
   de virarem jurisprudencia decisoria.

## Regra Para Promover Status

- `candidate_ready -> implemented`: fixture, parser, provider, testes e
  `ProviderCapabilities`.
- `candidate_needs_har -> candidate_ready`: HAR limpo e chamada reproduzida por
  `requests` com headers minimos.
- `documental -> candidate_ready`: rota de resultados decisorios localizada.
- `blocked_or_inconclusive -> candidate_needs_har`: portal responde e mostra
  formulario/fluxo publico reproduzivel.
