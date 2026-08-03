# Use Case Simulation: 2026-08-02

Esta rodada simulou o uso dos providers por publico-alvo com fontes reais quando
viavel e com falhas esperadas quando a fonte exigiu controle de acesso. O objetivo
foi verificar erros, incoerencias de UX e falta de informacao.

## Publicos simulados

| Publico | Fluxo | Resultado |
| --- | --- | --- |
| Advogados | `nanojuris documento "0003938-14.2017.8.26.0323" --fonte tjsp_esaj_cpopg --compacto` | retornou `CanonicalDocument` compacto com classe, assunto, foro, vara, juiz, URL final e trace omitido |
| Advogados | `nanojuris buscar "0003938-14.2017.8.26.0323" --fonte tjsp_esaj_cpopg --formato markdown` | Markdown revisavel com fonte, status e atualizacao |
| Desenvolvedores | `NanoJurisClient().get_document(..., source="tjsp_esaj_cpopg")` | API Python retornou `ExtractionStatus.COMPLETE` |
| Jurimetristas/legal ops | `buscar --store`, `store stats`, `store query --numero ...` | persistencia e filtros funcionaram; `--compacto` foi adicionado para evitar saidas longas |
| Analistas de dados | `buscar "ICMS" --fonte bnp_pangea --formato csv` | CSV canonico retornou precedente `stf-rg-615` com status publico |
| Agentes de IA | `list_sources_tool`, `source_diagnostics_tool`, `get_document_tool` | tools MCP-ready retornaram JSON serializavel e capabilities corretas |
| Mantenedores | `examples/source_route_probe.py` em rota eproc | rota classificada como bloqueada/inconclusiva: texto esperado ausente e sinais de captcha/Cloudflare/Turnstile |

## Status por provider

| Provider | Simulacao | Estado observado |
| --- | --- | --- |
| `bnp_pangea` | busca CSV por `ICMS` em STF/STJ | live OK, retorna precedente publico |
| `tjsp_esaj_cpopg` | documento e busca por numero CNJ | live OK, rota `search.do` -> `show.do` reproduzida com sessao limpa |
| `tjsp_cjsg` | busca live por `infanticidio` | acesso controlado, erro explicito com flags `recaptcha_response_token`, `uuidCaptcha`, rota de captcha e login |
| `stj_scon` | busca live por `homicidio` | acesso controlado, erro explicito sem bypass |
| eproc TJSP | probe de rota compartilhada no navegador | bloqueado/inconclusivo por Cloudflare/Turnstile; nao promovido para provider |

## Problemas encontrados e ajustes feitos

1. Catalogo TJSP listava apenas `tjsp_cjsg`, embora `tjsp_esaj_cpopg` ja esteja
   implementado. Corrigido em `brazil.py` e testes.
2. `documento`, `store query`, `store get` e `store records` podiam despejar
   texto publico muito longo, ruim para triagem humana e agentes. Adicionado
   `--compacto`.
3. Docs antigas ainda diziam que MCP, `get_document`, `CanonicalStore` e fluxo de
   store nao existiam. Atualizadas em `case-studies.md` e
   `use-case-validation-matrix.md`.
4. Quickstart nao mostrava o provider e-SAJ nem o modo compacto. Atualizado.

## Lacunas restantes

- Adicionar exemplos de configuracao de cliente MCP real.
- Registrar ultimo status live conhecido por fonte em diagnostics.
- Criar score de completude por registro/campo.
- Definir plugin externo de providers para expansao nacional sem acoplar tudo ao
  core.