# External Court Scraper Survey - 2026-08-02

Pesquisa de projetos abertos de scraping judicial brasileiro para orientar a
expansao do NanoJuris. Nenhum scraper foi executado, clonado ou integrado. A
consulta foi limitada a metadados publicos, README e arquivos fonte brutos para
extrair inteligencia de fonte: rotas, familias tecnicas, nomes de campos,
seletores, limites de acesso e riscos.

## Regra de uso

- Usar como mapa de endpoints, payloads, seletores e campos juridicos.
- Nao copiar codigo externo para o core.
- Nao executar scrapers de terceiros.
- Nao adotar fluxo que dependa de login privado, senha, TOTP, storageState,
  captcha manual, captcha solving, stealth browser, proxy residencial ou cookie
  reaproveitado.
- Promover provider apenas depois de probe limpo proprio com `requests`, fixture
  offline e testes.

## Candidatos novos encontrados

| Projeto | Sistema/foco | Achado util | Classificacao NanoJuris |
| --- | --- | --- | --- |
| `leobalieiro/estudos-python-scraper-eproc-tjmg` | eproc consulta publica TJMG | Rota `https://eproc-consulta-publica-1g.tjmg.jus.br/eproc/externo_controlador.php?acao=processo_consulta_publica`; POST por nome da parte; seletores de detalhe `txtNumProcesso`, `txtAutuacao`, `txtSituacao`, `txtOrgaoJulgador`, `txtMagistrado`, `txtClasse`, `fldAssuntos`, `fldPartes`, `fldInformacoesAdicionais`, eventos em `#divInfraAreaProcesso > table` | Forte candidato a probe limpo de consulta publica eproc/TJMG |
| `bborgeswq/eproc-scrapers` | eproc TJRS 1G autenticado | Login eProc com Playwright, campos `username`, password, `#otp`, menu `Prazos`; usa TOTP e credenciais | Nao promover; apenas mapa de limites e telas privadas |
| `bborgeswq/scraper-eproc-last-event` | eproc TJRS login base | `EPROC_BASE_URL=https://eproc1g.tjrs.jus.br/eproc/`, login em `externo_controlador.php?acao=principal`, storageState, 2FA/TOTP | Nao promover; autentica e reutiliza sessao |
| `bborgeswq/eproc_scraper_2.0` | eproc TJRS | Estrutura maior de scraper e documentos, mas requer login/sessao | Apenas pesquisa posterior de campos, sem execucao |
| `GHDaru/esaj-scraper` | e-SAJ SP/SC/BA com Playwright | Bases `https://esaj.tjsp.jus.br`, `https://esaj.tjsc.jus.br`, `https://esaj.tjba.jus.br`; `login_path=/sajcas/login.do`, `consulta_path=/cpopg/open.do`; campos `#numeroDigitoAnoUnificado`, `#foroNumeroUnificado`, `#botaoConsultarProcessos`; seletores `#classeProcesso span`, `#assuntoProcesso span`, `#varaProcesso span`, `#juizProcesso span`, `#tableTodasPartes`, `#tabelaTodasMovimentacoes` | Reforca parametrizacao e-SAJ CPOPg, mas fluxo com login/PDF nao deve ser usado |
| `armentanoc/scraper_TJCE` | e-SAJ TJCE 1G/2G | Rotas `https://esaj.tjce.jus.br/cpopg/show.do` e `https://esaj.tjce.jus.br/cposg5/search.do`; campos `numeroProcesso`, `classeProcesso`, `areaProcesso`, `assuntoProcesso`, `dataHoraDistribuicaoProcesso`, `valorAcaoProcesso`, `tableTodasPartes`, `juizProcesso`, `foroProcesso`, `varaProcesso`, `secaoProcesso`, `orgaoJulgadorProcesso`, `relatorProcesso`, `volumeApensoProcesso`; movimentacoes por `dataMovimentacao`/`descricaoMovimentacao` | Bom candidato a probe limpo de `tjce_esaj_cpopg/cposg` |
| `passoz/ganscraper` | PJe consulta publica multi-tribunal | URLs PJe de TJAP, TJBA, TJCE, TJMA, TJPI, TJRJ; campo `fPP:numProcesso-inputNumeroProcessoDecoration:numProcesso-inputNumeroProcesso`; botao `fPP:searchProcessos`; extrai orgao julgador, classe, autor, advogados/OAB por padroes HTML; detecta login/captcha/Cloudflare | Usar como mapa de endpoints; nao promover sem probe limpo por tribunal |
| `juangalva0/Scraper-PJE` | PJe TRF1 consulta publica | Base `https://pje1g.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam`; campo `fPP:numProcesso-inputNumeroProcessoDecoration:numProcesso-inputNumeroProcesso`; tabela `fPP:processosTable`; link `title='Ver Detalhes'`; movimentacoes em tabela RichFaces, `rich-table-row`, paginacao por `rich-inslider-*` | Candidato a ficha/probe de TRF1 PJe; Selenium/headless nao deve ser adotado |
| `opeclat/api-pje-scraper` | PJe com OAB, login/2FA | API wrapper com `POST /api/scrape/start`, busca por `numeroOAB`, `letraOAB`, `ufOAB`, `otpCode`; sessao em memoria | Nao promover; requer 2FA e sessao autenticada |
| `rppbarbosa/pje_scraper` | DJEN/PJe | Repositorio vazio no momento da consulta | Sem uso atual |
| `joaomarinjr/esaj_scraper`, `rinyakok/eSajScraper` | e-SAJ | Repositorios praticamente vazios/README sem inteligencia tecnica | Baixa utilidade |

## eproc - parametros e seletores aproveitaveis

### TJMG consulta publica

Rota observada no projeto `leobalieiro/estudos-python-scraper-eproc-tjmg`:

```text
GET/POST https://eproc-consulta-publica-1g.tjmg.jus.br/eproc/externo_controlador.php?acao=processo_consulta_publica
```

Payload de busca por parte observado:

```text
hdnInfraTipoPagina=1
txtNumProcesso=
txtNumChave=
txtNumChaveDocumento=
txtStrParte=<nome>
chkFonetica=S
txtStrOAB=
rdoTipo=CPF
txtCpfCnpj=
hdnInfraSelecoes=Infra
```

Campos/seletores do detalhe:

```text
span#txtNumProcesso
span#txtAutuacao
span#txtSituacao
span#txtOrgaoJulgador
span#txtMagistrado
span#txtClasse
fieldset#fldAssuntos
fieldset#fldPartes
fieldset#fldInformacoesAdicionais
#divInfraAreaProcesso > table
```

Campos resultantes sugeridos para um futuro `tjmg_eproc_public`:

```text
case_number
autuation_date
status
judging_body
magistrate
case_class
subjects
parties_and_representatives
additional_information
events
```

Criterio antes de implementar: reproduzir a rota com `requests` limpo usando
numero/nome publico e confirmar ausencia de captcha/login.

### TJRS eproc autenticado

Projetos `bborgeswq/eproc-scrapers`, `scraper-eproc-last-event` e
`eproc_scraper_2.0` mostram um fluxo de eproc TJRS que depende de:

```text
EPROC_BASE_URL=https://eproc1g.tjrs.jus.br/eproc/
EPROC_USER
EPROC_PASS
EPROC_TOTP_SECRET
storageState.json
Playwright/Chromium
```

Conclusao: estes projetos ajudam a entender campos e navegacao de tela privada,
mas nao sao base para provider publico do NanoJuris. Podem orientar apenas um
futuro diagnostico de limites do eproc, nunca coleta autenticada.

## e-SAJ - parametros e seletores aproveitaveis

Projetos analisados reforcam a familia CPOPg/CPOSg:

```text
/cpopg/open.do
/cpopg/search.do
/cpopg/show.do
/cposg5/search.do
/sajcas/login.do
```

Campos CNJ usados no formulario:

```text
#numeroDigitoAnoUnificado
#foroNumeroUnificado
#botaoConsultarProcessos
```

Seletores de detalhe recorrentes:

```text
#numeroProcesso
#classeProcesso
#areaProcesso
#assuntoProcesso
#dataHoraDistribuicaoProcesso
#valorAcaoProcesso
#tableTodasPartes
#tablePartesPrincipais
#tabelaTodasMovimentacoes
#tabelaUltimasMovimentacoes
#foroProcesso
#varaProcesso
#juizProcesso
#secaoProcesso
#orgaoJulgadorProcesso
#relatorProcesso
#volumeApensoProcesso
.dataMovimentacao
.descricaoMovimentacao
```

Tribunais candidatos:

```text
TJSP: ja implementado em `tjsp_esaj_cpopg`
TJCE: bom candidato por `armentanoc/scraper_TJCE`, precisa probe limpo
TJSC: citado por `GHDaru/esaj-scraper`, precisa probe limpo
TJBA: citado por `GHDaru/esaj-scraper`, precisa probe limpo
```

Limite: qualquer fluxo que entre em `/sajcas/login.do`, CPF/senha, certificado ou
PDF restrito deve ser classificado como login/controle de acesso.

## PJe - endpoints e limites

### Multi-tribunal estadual

URLs observadas em `passoz/ganscraper`:

```text
TJAP: https://pje.tjap.jus.br/pje/ConsultaPublica/listView.seam
TJBA: https://consultapublicapje.tjba.jus.br/pje/ConsultaPublica/listView.seam
TJCE: https://pje.tjce.jus.br/pje/ConsultaPublica/listView.seam
TJMA: https://pje.tjma.jus.br/pje/ConsultaPublica/listView.seam
TJPI: https://pje.tjpi.jus.br/pje/ConsultaPublica/listView.seam
TJRJ: https://tjrj.pje.jus.br/pje/ConsultaPublica/listView.seam
```

Campo principal:

```text
fPP:numProcesso-inputNumeroProcessoDecoration:numProcesso-inputNumeroProcesso
```

Botao/tabela:

```text
fPP:searchProcessos
input[value="Pesquisar"]
```

Campos extraidos por heuristica:

```text
orgao_julgador
classe_judicial
autor
advogados
oabs
advogado_oab
```

O proprio projeto espera Cloudflare, captcha manual e login. Portanto, para
NanoJuris, estes endpoints devem virar primeiro um diagnostico `pje_public_query`
que classifique `public`, `captcha`, `login`, `not_found`, `source_unavailable`,
sem tentar resolver captcha.

### TRF1 PJe

Projeto `juangalva0/Scraper-PJE` aponta:

```text
https://pje1g.trf1.jus.br/consultapublica/ConsultaPublica/listView.seam
```

Seletores/controles:

```text
#fPP\:numProcesso-inputNumeroProcessoDecoration\:numProcesso-inputNumeroProcesso
#fPP\:processosTable
a[title="Ver Detalhes"]
//div[contains(text(), 'Dados do Processo')]
//a[contains(text(), 'Movimentações')]
//table[contains(@class, 'rich-table')]
.rich-table-row
.rich-inslider-inc-horizontal.rich-inslider-arrow
.rich-inslider-right-num
.rich-inslider-field
```

Utilidade: candidato a ficha de fonte PJe/TRF1, principalmente para parser
offline de HTML publico. Precisa probe limpo porque o projeto usa Selenium.

## Priorizacao para NanoJuris

### P0 - Probes limpos imediatos

1. `tjmg_eproc_public`: testar consulta publica eproc/TJMG por nome ou CNJ com
   `requests`, buscando os campos `txtNumProcesso`, `fldPartes`, `txtClasse`.
2. `tjce_esaj_cpopg`: testar `cpopg/search.do`/`show.do` com numero publico real
   e os seletores e-SAJ padrao.
3. `trf1_pje_public`: testar `ConsultaPublica/listView.seam` com CNJ publico,
   classificando captcha/login se aparecer.

### P1 - Parametrizacao

1. Extrair uma classe base `EsajCpopgProvider` depois de validar TJCE/TJSC/TJBA
   individualmente.
2. Criar um diagnostico `PjePublicQueryProbe` que apenas classifica acesso e
   extrai HTML publico quando disponivel.
3. Criar uma ficha tecnica `eproc_public_profile` separando consulta publica de
   eproc autenticado.

### P2 - Nao promover como provider publico

1. eproc TJRS autenticado com TOTP/storageState.
2. PJe por OAB com 2FA.
3. e-SAJ com CPF/senha/certificado/PDF restrito.
4. Qualquer fluxo que dependa de captcha manual, stealth browser ou proxy.

## Proxima acao recomendada

Rodar apenas probes proprios, nao scrapers externos:

```text
examples/source_route_probe.py <url publica TJMG eproc> --expect txtNumProcesso
examples/source_route_probe.py <url publica TJCE cpopg> --expect numeroProcesso
examples/source_route_probe.py <url publica TRF1 PJe> --expect fPP:processosTable
```

Se o probe limpo passar, criar fixture HTML minima antes de qualquer provider.
