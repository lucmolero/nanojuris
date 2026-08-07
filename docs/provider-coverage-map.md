# Provider Coverage Map

Este documento mapeia o contexto brasileiro de obtencao publica de dados de
jurisprudencia para orientar a expansao da NanoJuris. Ele nao promete cobertura
total imediata; separa fontes implementadas, fontes prioritarias e familias de
sistemas que exigem pesquisa por tribunal.

Escopo da NanoJuris: extrair dados publicos, normalizar, persistir e expor por
Python, CLI, exporters e MCP. O projeto nao deve contornar captcha, login,
segredo de justica ou controles de acesso.

## Familias de obtencao publica

| Familia | Exemplos | Melhor uso | Complexidade | Observacoes |
| --- | --- | --- | --- | --- |
| APIs publicas/documentadas | DataJud/CNJ, BNP/Pangea, Comunica PJe/DJEN | dados estruturados, cobertura nacional, precedentes e comunicacoes | media | melhor ponto de partida quando endpoints aceitam payloads estaveis |
| Portais de jurisprudencia dos tribunais superiores | STF, STJ, TST, TSE, STM | acordaos, sumulas, repetitivos, repercussao geral | media/alta | cada tribunal tem contratos e filtros proprios |
| Portais HTML legados | TJSP/CJSG, e-SAJ, consultas estaduais | jurisprudencia estadual e inteiro teor quando publico | alta | HTML muda, pode haver captcha/controle de acesso |
| Plataformas processuais | eproc, PJe, Projudi, e-SAJ CPO | consulta processual e documentos publicos pontuais | alta | frequentemente exigem validacao humana ou limitam documentos |
| Diarios oficiais e comunicacoes | DJEN, DJe, DOU, diarios locais | publicacoes, movimentacoes e atos oficiais | media | bom para datasets, menos direto para jurisprudencia consolidada |
| Dados abertos e repositórios institucionais | CNJ, STJ dados abertos, portais gov.br | bases historicas, metadados e estudos | media | requer dicionario de campos e versionamento de datasets |

## Prioridade de implementacao

| Prioridade | Fonte/familia | Justificativa | Saida esperada |
| --- | --- | --- | --- |
| P0 | BNP/Pangea | ja implementado; precedentes qualificados nacionais | `CanonicalPrecedent`, decisoes vinculadas quando disponiveis |
| P0 | Comunica PJe/DJEN | ja implementado; API publica nacional para comunicacoes judiciais | comunicacoes como `CanonicalDecision` com `type="comunicacao"` |
| P0 | TJDFT/SISTJ | ja implementado; rota limpa validada a partir de inteligencia CourtsBR | acordaos como `CanonicalDecision` e detalhe HTML publico |
| P0 | TJAC/e-SAJ CPOPg | ja implementado; processo publico 1G validado por redirect oficial | `CanonicalDocument` de autos/processo publico |
| P0 | TJMS/CJSG | ja implementado; rota limpa validada a partir de projeto aberto TJMS/e-SAJ | acordaos como `CanonicalDecision` e inteiro teor quando publico |
| P0 | TJSP/CJSG | ja implementado parcialmente; maior tribunal estadual; HTML real validado | `CanonicalDecision`, `CanonicalDocument` quando publico |
| P0 | TJSP/NugepNac | ja implementado; catalogo oficial limpo de IRDR/IAC | `CanonicalPrecedent` com tema, questao e tese |
| P0 | TCE-SP jurisprudencia estatica | ja implementado; sumulas e boletins publicos sem captcha | `CanonicalPrecedent` administrativo |
| P0 | TRE-SP temas selecionados | ja implementado; curadoria tematica eleitoral publica | `CanonicalPrecedent` tematico |
| P0 | TJRS jurisprudencia AJAX/SOLR | rota publica estruturada validada; retorna docs, facets, highlighting e volume total | `CanonicalDecision` via JSON/SOLR |
| P0 | TJBA jurisprudencia GraphQL | rota publica estruturada validada; retorna decisoes, ementa, relator, orgao julgador e numero processual | `CanonicalDecision` via JSON estruturado |
| P0 | TJPR jurisprudencia HTML | rota publica validada com resultado, relator, orgao julgador, ementa e paginacao | `CanonicalDecision` via parser HTML |
| P0 | TJSC/eproc jurisprudencia | formulario publico eproc validado; potencial de reuso por familia tecnica | `CanonicalDecision` e contrato `eproc_jurisprudencia` |
| P0 | TNU/eproc jurisprudencia | POST publico validado em `listar_resultados`; reuso direto da familia eproc | `CanonicalDecision` federal/TNU com inteiro teor publico quando disponivel |
| P0 | TRF6/eproc jurisprudencia | POST publico validado em `listar_resultados`; cobre TRF6, TRU6, Turmas Recursais e Varas Federais | `CanonicalDecision` federal com origens eproc |
| P0 | TJGO/Projudi jurisprudencia | POST publico validado; resultado HTML contem alto volume, processo, orgao, magistrado, decisao e inteiro teor embutido | `CanonicalDecision` via parser HTML Projudi |
| P0 | STJ jurisprudencia/SCON | provider inicial `stj_scon` com parser offline; ficha em [stj-source-profile.md](stj-source-profile.md) | acordaos como `CanonicalDecision`; inteiro teor em fase futura |
| P0 | STF jurisprudencia | provider inicial `stf_juris` via API JSON observada por HAR; WAF/SSL diagnosticados | acordaos como `CanonicalDecision`; inteiro teor como URL ate validar documento sem 403 |
| P1 | TJMA/Jurisconsult metadados e sumulas | API publica limpa para relatorios, tipos, orgaos e links de sumulas/IAC/IRDR; busca principal exige captcha | `CanonicalPrecedent`/catalogo parcial; nao automatizar acordaos sem fluxo limpo |
| P1 | TST jurisprudencia publica | SPA com backend identificado, mas payload exato ainda nao promovido | decisoes trabalhistas apos probe limpo |
| P1 | TSE jurisprudencia publica | backend oficial identificado, mas retorno antirrobo observado | decisoes eleitorais somente se fluxo limpo existir |
| P1 | DataJud/CNJ | cobertura nacional estruturada por processo e classe | metadados nacionais e ponte para jurimetria |
| P2 | TST/TSE/STM | ramos especializados com alta demanda de pesquisa | decisoes e precedentes por ramo |
| P2 | TRFs e TJs via familia de sistema | ampliar cobertura regional com reuso de parsers | providers por sistema antes de providers por tribunal |

## Estrategia por sistema, nao por pagina isolada

A cobertura ampla do Brasil deve priorizar familias tecnicas reutilizaveis:

- `bnp_pangea`: API JSON de precedentes;
- `comunica_pje`: API JSON de comunicacoes judiciais/DJEN;
- `tjdf_juris`: HTML SISTJ/TJDFT para acordaos e bases indexadas;
- `tjac_esaj_cpopg`: e-SAJ CPOPg/TJAC para consulta processual publica;
- `tjms_cjsg`: HTML e-SAJ/CJSG do TJMS;
- `tjsp_cjsg`: HTML ESAJ/CJSG de jurisprudencia;
- `tjsp_nugepnac`: catalogos oficiais TJSP/NugepNac de precedentes;
- `tce_sp_jurisprudencia`: catalogos estaticos TCE-SP de sumulas e boletins;
- `tre_sp_temas`: curadoria tematica publica do TRE-SP;
- `tjrs_solr`: AJAX publico baseado em SOLR para jurisprudencia do TJRS;
- `tjba_graphql`: GraphQL publico de jurisprudencia do TJBA;
- `tjpr_juris`: HTML publico de jurisprudencia do TJPR;
- `eproc_jurisprudencia`: familia eproc para TJSC e tribunais que exponham
  pesquisa publica equivalente, incluindo TNU e TRF6;
- `projudi_jurisprudencia`: HTML publico de jurisprudencia/atos judiciais do
  TJGO quando o POST limpo retornar resultados sem validacao humana;
- `tjma_jurisconsult`: API publica parcial para metadados, filtros e links de
  precedentes/sumulas; busca principal fica bloqueada enquanto exigir captcha;
- `esaj`: familia Softplan/e-SAJ para tribunais que compartilham padroes;
- `eproc`: familia eproc, com pesquisa publica quando disponivel;
- `pje`: familia PJe, normalmente com maior incidencia de controle de acesso;
- `datajud`: API CNJ para dados estruturados nacionais;
- `stj_scon`, `stf_juris`, `tst_jurisprudencia`: providers por tribunal
  superior quando o contrato for proprio.

Esse desenho reduz duplicacao: quando dois tribunais compartilham a mesma
familia tecnica, a NanoJuris deve reaproveitar fetcher, parser e canonical mapper
sempre que o contrato real permitir.

O catalogo publico expõe `source_system` para descoberta por Python, CLI e MCP:

```bash
nanojuris tribunais --sistema esaj_cjsg
```

```python
from nanojuris import list_courts

print([court.code for court in list_courts(source_system="esaj_cjsg")])
```

## Metodologia de pesquisa de fonte

O fluxo operacional detalhado, com score de qualidade e comando `probe-rota`,
esta em [route-mapping-playbook.md](route-mapping-playbook.md).

Antes de implementar um provider, preencher uma ficha tecnica com:

- URL inicial oficial;
- endpoints observados;
- metodo HTTP;
- nomes de parametros de query e formulario, sem valores sensiveis;
- paginacao;
- campos juridicos objetivos disponiveis;
- documentos e formatos retornados;
- sinais de captcha, login, segredo de justica ou bloqueio;
- payload minimo responsavel;
- fixture offline sanitizada;
- teste live opcional e desligado por padrao.

HARs, DevTools e browser network podem ser usados como ferramenta local de
pesquisa, mas nao devem entrar no pacote, nos testes ou em fixtures sem
sanitizacao rigorosa. O artefato publico deve ser a ficha de fonte e o provider
testado, nao o HAR bruto.

## Evidencia ESAJ/TJSP a partir de pesquisa local

Pesquisa local com HAR do portal ESAJ/TJSP de jurisprudencia indicou estas rotas
sanitizadas relevantes:

| Rota | Metodo | Tipo | Campos observados | Classificacao |
| --- | --- | --- | --- | --- |
| `/cjsg/resultadoCompleta.do` | POST | HTML | `dados.buscaInteiroTeor`, `dados.buscaEmenta`, `dados.nuProcOrigem`, `dados.dtJulgamentoInicio`, `dados.dtJulgamentoFim`, `tipoDecisaoSelecionados`, `dados.ordenarPor`, alem de campos de captcha quando exigidos | alta oportunidade com controle de acesso possivel |
| `/cjsg/captchaControleAcesso.do` | POST | JSON | `uuidCaptcha`, `conversationId` | controle de acesso; nao implementar bypass |
| `/sajcas/conteudoIdentificacao` | GET | HTML | `script` | identidade/login; nao usar como rota de extracao |

Conclusao: o provider TJSP/CJSG deve continuar usando payloads de busca
estruturados apenas quando a fonte publica responder sem exigir validacao humana.
Quando a resposta indicar captcha ou outro controle, o comportamento correto e
interromper com erro claro e `AccessStatus.ACCESS_CONTROL_REQUIRED`.

## Matriz de UX por publico

| Publico | Necessidade | UX esperada |
| --- | --- | --- |
| Advogados | localizar decisoes e inteiro teor publico com origem confiavel | comandos simples, Markdown, links/traces e mensagens claras de acesso |
| Desenvolvedores | integrar fontes heterogeneas com contratos estaveis | API Python tipada, erros acionaveis, fixtures e docs de provider |
| Jurimetristas | montar datasets reproduziveis por tribunal, ramo e periodo | CSV/JSONL, SQLite, `ResearchRun`, filtros por tribunal/UF/ramo |
| Analistas de dados | auditar e versionar coletas | hashes, `SourceTrace`, `ExtractionTrace`, deduplicacao e exports paginados |
| Agentes de IA | descobrir fontes, limites e dados sem interpretar merito | MCP com `list_sources`, `list_courts`, busca, store, export e `get_document` |

## Lacunas prioritarias

1. Completar `official_url` e `source_system` no catalogo `CourtInfo`.
2. Aprofundar bases adicionais do `stf_juris`: decisoes, sumulas e informativos.
3. Expandir `stj_scon` para inteiro teor publico quando a fonte responder sem
  controle de acesso.
4. Separar provider por familia de sistema quando houver reaproveitamento real.
5. Criar benchmark de completude por provider e campo canonico.
6. Definir contrato de plugin externo para providers fora do core.
