# GitHub Scraper Research

Pesquisa feita em 2026-08-02 para localizar projetos abertos de scraping de
tribunais brasileiros com ideias reaproveitaveis para NanoJuris. O objetivo foi
extrair inteligencia de fonte: endpoints, parametros, seletores, familias de
sistema e sinais de bloqueio. Codigo externo nao deve ser copiado para o core.

## Projetos inspecionados

Levantamento complementar de 2026-08-02, sem executar scrapers externos:
[external-court-scraper-survey-2026-08-02.md](external-court-scraper-survey-2026-08-02.md).

| Projeto | Foco | Achado util | Classificacao |
| --- | --- | --- | --- |
| `mvdiogo/stf-web-scraper` | STF jurisprudencia moderna | URL `https://jurisprudencia.stf.jus.br/pages/search` com bases `acordaos`, `decisoes`, `informativos` e seletores `div.result-container`, `h4.ng-star-inserted`, `span.jud-text` | ficha de fonte; precisa descobrir API por tras do app |
| `kaoyeoshiro/scraper_jurisprudencia_TJ` | TJMS/CJSG e-SAJ | confirma `https://esaj.tjms.jus.br/cjsg`, `POST /resultadoCompleta.do`, paginacao `/trocaDePagina.do`, campos CJSG e seletor `downloadEmenta` | provider `tjms_cjsg` implementado |
| `betogrun/esaj` | e-SAJ CPOPg por OAB/processo | confirma paginacao `cpopg/trocarPagina.do`, parametros `dadosConsulta.localPesquisa.cdLocal`, `cbPesquisa`, `tipoNuProcesso`, `valorConsulta` e parser de links `linkProcesso` | reforca generalizacao e-SAJ CPOPg |
| `armentanoc/scraper_TJCE` | TJCE e-SAJ CPOPg/CPOSg | confirma seletores de consulta processual: `numeroProcesso`, `classeProcesso`, `areaProcesso`, `assuntoProcesso`, `dataHoraDistribuicaoProcesso`, `partes`, movimentacoes | candidato para `esaj_cpopg` parametrizado, depois de probe limpo |
| `passoz/ganscraper` | PJe consulta publica multi-tribunal | lista URLs PJe de TJAP, TJBA, TJCE, TJMA, TJPI, TJRJ e campo `fPP:numProcesso...` | mapa de fonte; alto risco por captcha/login |
| `rppbarbosa/pje_scraper` | DJEN/PJe | repositorio clonado vazio no momento da pesquisa | sem uso atual |
| `leobalieiro/estudos-python-scraper-eproc-tjmg` | eproc/TJMG consulta publica | rota `externo_controlador.php?acao=processo_consulta_publica`, campos `txtNumProcesso`, `txtAutuacao`, `txtSituacao`, `txtOrgaoJulgador`, `txtMagistrado`, `txtClasse`, `fldPartes`, `fldAssuntos` | candidato forte a probe limpo `tjmg_eproc_public` |
| `bborgeswq/eproc-scrapers` e relacionados | eproc/TJRS autenticado | confirma uso de Playwright, login, TOTP, `storageState` e menu privado de prazos | nao promover; apenas mapa de limite autenticado |
| `GHDaru/esaj-scraper` | e-SAJ SP/SC/BA | reforca bases `esaj.tjsp/tjsc/tjba`, campos CNJ `#numeroDigitoAnoUnificado`, `#foroNumeroUnificado` e seletores CPOPg | mapa para parametrizacao e-SAJ; fluxo de login/PDF nao usar |
| `juangalva0/Scraper-PJE` | PJe/TRF1 consulta publica | rota `pje1g.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam`, tabela `fPP:processosTable`, link `Ver Detalhes`, RichFaces para movimentacoes | candidato a ficha/probe PJe/TRF1, sem Selenium |
| `opeclat/api-pje-scraper` | PJe por OAB com 2FA | wrapper API com `numeroOAB`, `letraOAB`, `ufOAB`, `otpCode` e sessao em memoria | nao promover; requer 2FA/autenticacao |

## Probes limpos executados

### TJMS/CJSG

Rota validada com sessao HTTP limpa:

```text
GET  https://esaj.tjms.jus.br/cjsg/consultaCompleta.do
POST https://esaj.tjms.jus.br/cjsg/resultadoCompleta.do
```

Payload minimo reproduzido:

```text
conversationId=
paginaConsulta=1
dados.ordenarPor=dtPublicacao
dados.pesquisarComSinonimos=S
dados.buscaInteiroTeor=infanticidio
dados.origensSelecionadas=T
tipoDecisaoSelecionados=A
pbSubmit=Pesquisar
```

Resultado observado: HTTP 200, sem captcha, com marcadores CJSG e `22`
resultados parseados pelo parser CJSG existente. Primeiro item observado:
processo `0000008-16.2011.8.12.0055`, classe `Recurso em Sentido Estrito`,
assunto `Crimes contra a vida`, orgao `2a Camara Criminal`, relator
`Des. Romero Osme Dias Lopes`, publicacao `12/09/2011`.

Decisao: promover para provider `tjms_cjsg`, parametrizando o parser CJSG para
nao carimbar tudo como `TJSP/tjsp_cjsg`.

### STF jurisprudencia moderna

Projeto analisado usa:

```text
https://jurisprudencia.stf.jus.br/pages/search?base=acordaos&queryString=<termo>
```

Probe com `requests` limpo encontrou falha local de certificado. Probe apenas de
pesquisa, com verificacao SSL desativada, retornou HTTP `202` sem corpo.

Atualizacao: HAR posterior revelou a API JSON oficial do frontend em
`POST /api/search/search`. A decisao atual e promover provider inicial
`stf_juris` com parser por fixture e diagnostico explicito de WAF/SSL, sem
prometer acesso live estavel nem inteiro teor enquanto o portal retornar 403 em
sessao limpa.

### PJe consulta publica

URLs observadas no projeto PJe:

```text
https://consultapublicapje.tjba.jus.br/pje/ConsultaPublica/listView.seam
https://pje.tjma.jus.br/pje/ConsultaPublica/listView.seam
https://tjrj.pje.jus.br/pje/ConsultaPublica/listView.seam
```

Probes limpos retornaram formularios PJe, mas com sinais de captcha em TJBA,
TJMA e TJRJ; TJCE redirecionou para pagina de login; TJAP/TJPI retornaram 404
nas URLs testadas.

Decisao: manter como mapa de endpoints, nao como provider. NanoJuris pode criar
um diagnostico `pje_public_query` no futuro, mas nao deve esperar resolucao manual
ou automatica de captcha.

### e-SAJ CPOPg/CPOSg

Projetos Ruby/Python confirmam seletores e parametros ja usados pelo provider
`tjsp_esaj_cpopg`, e indicam oportunidade de familia parametrizada:

```text
/cpopg/search.do
/cpopg/show.do
/cpopg/trocarPagina.do
/cposg/search.do
```

Campos de interesse:

```text
numeroProcesso
classeProcesso
areaProcesso
assuntoProcesso
dataHoraDistribuicaoProcesso
valorAcaoProcesso
tableTodasPartes
tabelaTodasMovimentacoes
foroProcesso
varaProcesso
juizProcesso
orgaoJulgadorProcesso
relatorProcesso
```

Decisao: proximo passo recomendado e criar um provider de familia
`esaj_cpopg`, mas so habilitar cada tribunal apos probe limpo com numero publico
real e sem captcha.

## Priorizacao resultante

| Prioridade | Provider/ficha | Motivo |
| --- | --- | --- |
| P0 implementado | `tjms_cjsg` | rota limpa validada e parser CJSG reutilizavel |
| P1 | `esaj_cpopg` parametrizado | varios projetos confirmam padrao, mas cada tribunal precisa probe |
| P0 implementado | `stf_juris` | API JSON descoberta por HAR; provider funciona por fixture e reporta WAF/SSL |
| P2 | `pje_public_query` diagnostico | muitos tribunais, mas captcha/login frequentes |
| P2 | `tjce_esaj_cpopg` | seletores confirmados, precisa validacao limpa com caso publico |

## Regras de reaproveitamento

- Usar projetos externos como mapa de rotas, payloads, seletores e edge cases.
- Nao copiar codigo para o core sem revisao, simplificacao e testes proprios.
- Nao adotar fluxos que dependem de captcha solving, browser stealth, login,
  cookie de usuario, token reaproveitado ou intervencao manual.
- Promover provider apenas quando a rota for reproduzida por sessao HTTP limpa ou
  quando o browser for usado somente para pesquisa de API publica reproduzivel.
