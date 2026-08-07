# Route Mapping Results - 2026-08-07

Rodada inicial de mapeamento de rotas publicas de jurisprudencia, usando sessao
HTTP limpa e sem cookies exportados do navegador. `idpj` foi usado apenas como
um dos termos de smoke test; a bateria recomendada por ramo esta em
[route-mapping-playbook.md](route-mapping-playbook.md).

## Resumo executivo

| Fonte | Rota | Resultado | Decisao |
| --- | --- | --- | --- |
| TST frontend | `GET https://jurisprudencia.tst.jus.br/` | HTTP 200, SPA publica, sem captcha/login | candidato; usar para descobrir contrato |
| TST config | `GET /config.json` | HTTP 200 JSON com `base_url`, URLs de acordao, despacho e processo | promover para contrato |
| TST backend | `POST /rest/pesquisa-textual/1/2` com `{}` | HTTP 200 JSON com `totalRegistros`, `registros`, `agregacoes`, inteiro teor HTML | promover como rota tecnica A; filtro textual ainda pendente |
| TST backend filtrado | mesmo endpoint com `e=idpj` e payload completo observado no frontend | HTTP 400 sem corpo | pendente; reproduzir payload exato para filtros antes de provider completo |
| CJF/TRF1 hub | `GET https://www2.cjf.jus.br/jurisprudencia/trf1` | redireciona para CJF, HTML com sinal de reCAPTCHA | documentar bloqueio/candidato baixo |
| TRF3 | `GET https://web.trf3.jus.br/jurisprudencia/home/index/1` | timeout em 30s/60s no ambiente atual | repetir em outra janela; nao promover ainda |
| TRF5 | `GET https://jurisprudencia.trf5.jus.br/jurisprudencia/pesquisa.wsp` | timeout em 30s/60s no ambiente atual | repetir em outra janela; nao promover ainda |
| TJMG formulario | `GET /jurisprudencia/formEspelhoAcordao.do` | HTTP 200, formulario rico, campos e actions publicas | candidato forte para contrato, mas sem busca direta |
| TJMG palavras | `GET /jurisprudencia/pesquisaPalavrasEspelhoAcordao.do?palavras=idpj` | HTTP 401 com captcha | bloqueado para automacao; nao implementar bypass |
| TJRJ portal | `GET /web/portal-conhecimento/consulta-a-jurisprudencia` | HTTP 200, pagina institucional com links e menu de login | candidato documental, nao provider de resultados |
| TJRJ eJURIS | `GET /EJURIS/ConsultarJurisprudencia.aspx` | HTTP 200 formulario rico com reCAPTCHA | bloquear provider de busca enquanto depender de reCAPTCHA |
| TJPR jurisprudencia | `GET /jurisprudencia/publico/pesquisa.do?actionType=pesquisarRefinado&filtro=true` | HTTP 200, HTML com resultados, ementa, relator, orgao julgador e paginacao | promover para contrato e fixture |
| TJBA frontend | `GET https://jurisprudencia.tjba.jus.br/` | HTTP 200, SPA publica | usar para descobrir contrato |
| TJBA GraphQL | `POST https://jurisprudenciaws.tjba.jus.br/graphql` | HTTP 200 JSON estruturado com `decisoes`, `ementa`, `numeroProcesso`, `relator`, `orgaoJulgador` | promover para provider P0 |
| TJSC/eproc | `GET https://eprocwebcon.tjsc.jus.br/consulta1g/externo_controlador.php?acao=jurisprudencia@jurisprudencia/pesquisar` | HTTP 200, formulario eproc publico, sem captcha/login na pagina inicial | promover para contrato de familia eproc |
| TJSC portal historico | `GET https://busca.tjsc.jus.br/jurisprudencia/#formulario_ancora` | HTTP 200, pagina antiga com aviso de transicao | manter como fonte historica/documental |
| TJSC teses | `GET https://busca.tjsc.jus.br/juris-teses/#/listar` | HTTP 200 SPA curta | investigar API/bundle antes de provider |
| TJRS portal | `GET https://www.tjrs.jus.br/novo/buscas-solr/?aba=jurisprudencia` | HTTP 200, portal publico com iframe de jurisprudencia | usar como entrada documental |
| TJRS iframe | `GET https://www.tjrs.jus.br/buscas/jurisprudencia/` | HTTP 200, app publica com contrato Angular/SOLR | usar para descobrir payload |
| TJRS AJAX/SOLR | `POST https://www.tjrs.jus.br/buscas/jurisprudencia/ajax.php` | HTTP 200, JSON/SOLR com `response.numFound`, `response.docs`, facets e highlighting | promover para provider P0 |
| TNU/eproc | `POST https://eproctnu.cjf.jus.br/eproc/externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados` | HTTP 200, HTML eproc com `resultadoItem`, processo, ementa, relator e inteiro teor | promover como extensao da familia eproc |
| TRF6/eproc | `POST https://eproc-jur.trf6.jus.br/eproc/externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados` | HTTP 200, HTML eproc com resultados reais e bases TRF6/TRU6/Turmas/Varas | promover como extensao da familia eproc |
| TRF2/eproc | `POST https://eproc.trf2.jus.br/eproc/externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados` | HTTP 200, HTML eproc com `resultadoItem`, numero CNJ, ementa/decisao, relator, orgao e inteiro teor | promover como P0 na familia eproc |
| TRF2 legado | `GET https://juris.trf2.jus.br/consulta.php?...` | falha DNS no ambiente atual, apesar de paginas publicas indexadas | nao promover; preferir eproc/TRF2 |
| CJF/TRF1 hub | `GET https://www2.cjf.jus.br/jurisprudencia/trf1/index.xhtml` | redireciona para `jurisprudencia.cjf.jus.br`, hub publico de jurisprudencia unificada/TNU/TRF1/CJF | documentar como entrada, nao provider de resultados |
| TRF1 ementario | `GET https://www.trf1.jus.br/trf1/pesquisa/ementario-de-jurisprudencia` | HTTP 200, catalogo documental paginado com ementarios | manter como rota documental/catalogo |
| TJGO/Projudi | `POST https://projudi.tjgo.jus.br/ConsultaJurisprudencia` | HTTP 200, HTML com mais de 1M resultados, processo, magistrado, orgao, decisao e inteiro teor no proprio card | promover para contrato HTML P0; download separado ainda pendente |
| TJMA/Jurisconsult metadados | `GET https://apijuris.tjma.jus.br/v1/jurisprudencia/lista_relatorios` | HTTP 200 JSON com relatorios e URLs tecnicas de acordaos, monocraticas, sumulas e sentencas | promover contrato parcial/metadados |
| TJMA/Jurisconsult busca | `GET https://apijuris.tjma.jus.br/v1/sg/jurisprudencias/processos?...` sem token | HTTP 400 JSON `captcha_not_provided` | nao automatizar busca principal sem fluxo publico limpo |
| TJAP/Tucujuris | `GET https://tucujuris.tjap.jus.br/tucujuris/pages/consultar-jurisprudencia/consultar-jurisprudencia.html` | Cloudflare/challenge no HTML limpo | bloquear provider enquanto exigir desafio |
| STM | `GET https://jurisprudencia.stm.jus.br/` | HTTP 200, portal publico JMU com sinais juridicos e inteiro teor | manter provider existente e aprofundar contrato |
| TSE/SJUR metadados | `POST https://sjur-pesquisa-api.tse.jus.br/tse/sjur-pesquisa-backend/rest/public/pesquisa/classes` | HTTP 200 JSON com classes eleitorais; endpoint semelhante para relatorias | documentar contrato parcial P1 |
| TREs/SJUR metadados | `POST https://sjur-pesquisa-api.tse.jus.br/tres/sjur-pesquisa-backend/rest/public/pesquisa/classes` | HTTP 200 JSON com classes por TRE; exemplo `TRE-SP` validado | documentar contrato parcial P1 |
| TSE/SJUR busca | `POST /public/pesquisa` | HTTP 200 JSON com mensagem de falha antirrobo, sem resultados | bloquear provider de decisoes ate fluxo limpo |
| TRT2/PJe jurisprudencia | `GET https://pje.trt2.jus.br/jurisprudencia/` e `GET /juris-backend/api/opcoes` | SPA publica e JSON de opcoes; busca/documentos retornam desafio `tokenDesafio`/`imagem` | documentar contrato parcial; nao coletar documentos |
| TRT15/TRT23 PJe | `GET /jurisprudencia/` | HTTP 403 CloudFront/request blocked em sessao limpa | bloquear provider |
| Basis/TRT2 | `GET https://basis.trt2.jus.br/discover?query=teletrabalho` | HTTP 200, repositorio DSpace com boletins, atos e doutrina | rota documental, nao provider de decisoes |
| TJAC/e-SAJ CJSG | `GET https://esaj.tjac.jus.br/cjsg/resultadoSimples.do?...` | HTTP 200 com processo, ementa, relator, orgao, datas e inteiro teor | confirmar fonte forte CJSG |
| TJCE/e-SAJ CJSG | `GET https://esaj.tjce.jus.br/cjsg/consultaSimples.do` | reset/TLS EOF no ambiente atual | repetir antes de promover |
| TJES portal atual | `GET https://sistemas.tjes.jus.br/portaltj/Pesquisa.aspx` | timeout em 45s | inconclusivo; repetir com janela maior |
| TJES ColdFusion antigo | `GET https://aplicativos.tjes.jus.br/sistemaspublicos/consulta_jurisprudencia/det_jurisp.cfm?...` | HTTP 404 no ambiente atual, apesar de resultados antigos indexados | nao promover sem nova rota |
| TJMT jurisprudencia | `GET https://jurisprudencia.tjmt.jus.br/` | HTTP 200 SPA publica; bundle expõe API Hellsgate, metadados e relatorios | candidato forte, contrato de payload/header pendente |
| TJMT API inferida | `GET https://hellsgate-preview.tjmt.jus.br/jurisprudencia/api/consulta/1` | HTTP 401 `No API key found in request` | validar header publico do frontend antes de provider |
| TJPA jurisprudencia | `GET https://jurisprudencia.tjpa.jus.br/` | HTTP 200, portal publico; bundle expõe `/bff/api/decisoes` e metadados PJe | candidato forte, payload pendente |
| TJPA BFF inferido | `GET https://jurisprudencia.tjpa.jus.br/bff/api/decisoes` | HTTP 404 | metodo/payload ainda incorreto |
| TJPB/PJe jurisprudencia | `GET https://pje-jurisprudencia.tjpb.jus.br/` | HTTP 200 com formulario rico, campos juridicos e paginacao; outro cliente recebeu Cloudflare challenge | candidato forte com risco WAF |
| TJPE jurisprudencia | `GET https://portal.tjpe.jus.br/web/jurisprudencia/tjpe-e-turmas-recursais` | HTTP 200, pagina institucional publica com link para Consulta Jurisprudencia Web | entrada documental; endpoint de resultado pendente |
| TJPE sumulas | `GET https://portal.tjpe.jus.br/servicos/consulta/sumulas` | HTTP 200, sumulas e PDFs publicos | candidato de catalogo/precedentes |
| TJPE transparencia decisoes | `GET https://portal.tjpe.jus.br/web/transparencia/decis%C3%B5es` | HTTP 200, orienta DJEN/DJE/PJe e Consulta Jurisprudencia Web | rota documental/orientacao |
| TJPI/JusPI busca | `GET https://jurisprudencia.tjpi.jus.br/jurisprudences/search?q=dano%20moral` | HTTP 200 com resultados reais, CNJ, ementa, relator, orgao e paginacao | promover para fixture/parser HTML |
| TJRO/LIAME | `GET https://liame.tjro.jus.br/` | HTTP 200, portal de precedentes; probe marcou acesso por texto de UI, sem decisoes | candidato de precedentes, nao acordaos |
| TJRR/Juris | `GET https://jurisprudencia.tjrr.jus.br/index.xhtml` | HTTP 200 JSF/PrimeFaces com pesquisa, ementa, acordao, relator e links juridicos | promover para HAR/fixture JSF |
| TJSE jurisprudencia judicial | `GET https://www.tjse.jus.br/portal/consultas/jurisprudencia/judicial` | HTTP 200, pagina oficial de jurisprudencia judicial | entrada forte; rota de resultado pendente |

## Achados tecnicos

### TST

Rota de configuracao limpa:

```text
GET https://jurisprudencia.tst.jus.br/config.json
```

Campos observados:

- `base_url`: `https://jurisprudencia-backend2.tst.jus.br`
- `consulta_acordao_url`
- `consulta_despacho_url`
- `consulta_proc_url`
- `consulta_proc_pje_url`

Contrato central observado no bundle publico:

```text
POST {base_url}/rest/pesquisa-textual/{inicio}/{limite}?a=<random>
Content-Type: application/json
```

Payload vazio `{}` retornou JSON real com:

- `tempoGasto`
- `totalRegistros`
- `registros`
- `agregacoes`
- `registro.id`
- `registro.numero`
- `registro.tipo`
- `registro.orgao`
- `registro.nomRelator`
- `registro.numFormatado`
- `registro.dtaPublicacao`
- `registro.txtConteudoDecisao`

Decisao: TST e o alvo mais promissor da rodada. Antes de implementar provider
com busca textual, falta reproduzir o payload filtrado do frontend com uma
bateria trabalhista (`horas extras`, `justa causa`, `equiparacao salarial`).

### TJMG

Formulario publico:

```text
GET https://www5.tjmg.jus.br/jurisprudencia/formEspelhoAcordao.do
```

Actions observadas:

```text
GET /jurisprudencia/pesquisaNumeroCNJEspelhoAcordao.do
GET /jurisprudencia/pesquisaPalavrasEspelhoAcordao.do
```

Campo principal:

```text
palavras
```

Teste direto por palavras retornou HTTP 401 com captcha. Decisao: documentar
contrato do formulario, mas nao automatizar busca enquanto a rota de resultado
exigir captcha.

### TJRJ

Rotas oficiais observadas:

```text
GET https://www.tjrj.jus.br/web/portal-conhecimento/consulta-a-jurisprudencia
GET https://www3.tjrj.jus.br/EJURIS/ConsultarJurisprudencia.aspx?Version=1.1.19.1
```

O eJURIS entrega formulario rico, com campos juridicos objetivos, mas inclui
reCAPTCHA. Decisao: nao promover busca automatizada sem fluxo publico limpo.

### TJPR

Rota publica validada:

```text
GET https://portal.tjpr.jus.br/jurisprudencia/publico/pesquisa.do?actionType=pesquisarRefinado&filtro=true
```

Sinais observados:

- HTTP 200 em sessao limpa;
- pagina de resultado com "RESULTADO DA PESQUISA";
- campos juridicos objetivos: relator, orgao julgador, ementa, acordao e
  identificadores processuais;
- paginacao e volume total de registros;
- ausencia de captcha/login no teste inicial.

Decisao: TJPR deve entrar no proximo ciclo de implementacao como provider HTML
P0. O primeiro passo tecnico e salvar fixture publica representativa com uma busca multi-area
(`dano moral`, `plano de saude`, `execucao fiscal`) e criar parser offline antes
do fetcher live.

### TJBA

Frontend publico:

```text
GET https://jurisprudencia.tjba.jus.br/
```

Backend observado no bundle publico:

```text
POST https://jurisprudenciaws.tjba.jus.br/graphql
Content-Type: application/json
```

Consulta GraphQL observada:

```graphql
query filter($decisaoFilter: DecisaoFilter!, $pageNumber: Int!, $itemsPerPage: Int!) {
  filter(
    decisaoFilter: $decisaoFilter
    pageNumber: $pageNumber
    itemsPerPage: $itemsPerPage
  ) {
    decisoes {
      dataPublicacao
      relator { id nome }
      orgaoJulgador { id nome }
      classe { id descricao }
      conteudo
      tipoDecisao
      ementa
      hash
      numeroProcesso
    }
    relatores { key value }
    orgaos { key value }
    classes { key value }
    pageCount
    itemCount
  }
}
```

Campos de filtro observados:

- `assunto`
- `numeroRecurso`
- `relator`
- `orgao`
- `classe`
- `segundoGrau`
- `turmasRecursais`
- `tipoAcordaos`
- `tipoDecisoesMonocraticas`
- `publicacoesDe`
- `publicacoesAte`
- `dataInicial`
- `dataFinal`
- `ordenadoPor`
- `orgaos`
- `relatores`
- `classes`

Teste com `assunto="dano moral"` retornou JSON juridico real com `decisoes`,
`numeroProcesso`, `ementa`, relator, orgao julgador, classe e conteudo. Decisao:
TJBA e a melhor rota nova da rodada para provider estruturado, porque entrega
GraphQL sem captcha/login e com campos canonicos diretos.

### TJSC

Pagina oficial:

```text
GET https://www.tjsc.jus.br/web/tjsc/pesquisa-jurisprudencia
```

Rota final validada por redirecionamento oficial:

```text
GET https://eprocwebcon.tjsc.jus.br/consulta1g/externo_controlador.php?acao=jurisprudencia@jurisprudencia/pesquisar
```

Sinais observados:

- HTTP 200 em sessao limpa;
- pagina de jurisprudencia eproc;
- filtros por base/origem, tipo, ementa, inteiro teor, caput, classe e periodo;
- ausencia de captcha/login no formulario inicial;
- bom potencial de reuso com familia `eproc`.

Tambem foi localizada a rota historica:

```text
GET https://busca.tjsc.jus.br/jurisprudencia/#formulario_ancora
```

Ela informa transicao para a plataforma integrada ao eproc. Decisao: priorizar
o eproc como provider principal e manter a rota antiga apenas como referencia
historica ou fallback documental.

### TJRS

Entrada publica no portal:

```text
GET https://www.tjrs.jus.br/novo/buscas-solr/?aba=jurisprudencia
```

O portal renderiza um iframe publico:

```text
GET https://www.tjrs.jus.br/buscas/jurisprudencia/?q_palavra_chave=dano%20moral&aba=jurisprudencia&q=dano%20moral&site=ementario
```

O iframe carrega uma aplicacao Angular que chama:

```text
POST https://www.tjrs.jus.br/buscas/jurisprudencia/ajax.php
Content-Type: application/x-www-form-urlencoded
```

Payload minimo validado:

```text
action=consultas_solr_ajax
metodo=buscar_resultados
parametros=aba=jurisprudencia&realizando_pesquisa=1&pagina_atual=1&q_palavra_chave=dano+moral&conteudo_busca=ementa_completa
```

Resposta observada:

- JSON/SOLR retornado como `text/html; charset=iso-8859-1`;
- `responseHeader.params`;
- `response.numFound`;
- `response.docs`;
- facets por `orgao_julgador`, `origem`, `relator_redator`,
  `ano_julgamento`, `nome_classe_cnj`, `nome_assunto_cnj`,
  `nome_tribunal`, `tipo_processo`, `mes_ano_publicacao` e
  `data_publicacao`;
- highlighting para ementa/inteiro teor;
- links de processo e documento montados no frontend.

Decisao: TJRS deve ser promovido a P0 junto de TJBA. Ele combina contrato
estruturado, alto volume, facets juridicas e resposta rapida. O parser deve
normalizar JSON com charset legado e preservar facets em `raw_metadata`.

### TNU e TRF6/eproc

Rotas publicas validadas na mesma familia tecnica do eproc:

```text
GET  https://eproctnu.cjf.jus.br/eproc/externo_controlador.php?acao=jurisprudencia@jurisprudencia/pesquisar
POST https://eproctnu.cjf.jus.br/eproc/externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados

GET  https://eproc-jur.trf6.jus.br/eproc/externo_controlador.php?acao=jurisprudencia@jurisprudencia/pesquisar
POST https://eproc-jur.trf6.jus.br/eproc/externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados
```

Payload minimo validado:

```text
txtPesquisa=aposentadoria
rdoCampo=I
hdnExibirPesquisaAvancada=
chkAgruparResultados=on
```

Sinais observados:

- HTTP 200 em sessao limpa;
- formulario publico sem captcha/login no fluxo testado;
- `resultadoItem` nos resultados;
- numero CNJ, classe, relator, orgao, ementa/decisao e links de inteiro teor;
- TNU com origem unica `TNU`;
- TRF6 com origens `TRF6`, `TRU6`, Turmas Recursais e Varas Federais.

Decisao: TNU, TRF2 e TRF6 devem entrar como P0 por reuso do parser/fetcher eproc ja
existente. O proximo passo tecnico e parametrizar o provider eproc por
instancia, preservando `source`, `court`, base URL, origens disponiveis e tipos
documentais.

### TRF2/eproc e CJF/TRF1

Rota publica TRF2/eproc validada:

```text
GET  https://eproc.trf2.jus.br/eproc/externo_controlador.php?acao=jurisprudencia@jurisprudencia/pesquisar
POST https://eproc.trf2.jus.br/eproc/externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados
```

Payload minimo validado:

```text
txtPesquisa=aposentadoria
rdoCampo=I
hdnExibirPesquisaAvancada=
chkAgruparResultados=on
```

Sinais observados:

- HTTP 200 em sessao limpa;
- formulario publico "Jurisprudencia Justica Federal da 2a Regiao";
- origens `TRF2`, `TRU2` e Turmas Recursais;
- tipos documentais `Acordao`, `Decisao monocratica`, `Sumula`,
  `Despacho/Decisao da Vice-Presidencia` e `Sentenca`;
- resultados com `resultadoItem`, numero CNJ, relator, orgao, ementa/decisao e
  link de inteiro teor;
- ausencia de captcha/login no fluxo testado.

A rota legada `juris.trf2.jus.br` falhou DNS no ambiente atual. Como o eproc
TRF2 respondeu com conteudo juridico completo, a decisao tecnica e promover
TRF2 pela familia `eproc_jurisprudencia` e manter o legado apenas como nota de
pesquisa.

Tambem foram testadas entradas CJF/TRF1:

```text
GET https://www2.cjf.jus.br/jurisprudencia/trf1/index.xhtml
GET https://www.trf1.jus.br/trf1/pesquisa/ementario-de-jurisprudencia
```

O primeiro redireciona para um hub de jurisprudencia unificada/TNU/TRF1/CJF. O
segundo retorna ementario documental paginado. Decisao: documentar como rotas de
entrada/catalogo, mas nao implementar como provider de decisoes ate localizar
endpoint de resultado limpo.

### TJGO/Projudi

Entrada oficial observada em fontes publicas:

```text
GET https://projudi.tjgo.jus.br/ConsultaJurisprudencia
```

Contrato de busca validado:

```text
POST https://projudi.tjgo.jus.br/ConsultaJurisprudencia
Content-Type: application/x-www-form-urlencoded

PaginaAtual=2
PosicaoPaginaAtual=0
Viewstate=
Texto=dano moral
Id_Instancia=0
Id_Area=0
Id_ServentiaSubTipo=0
Id_Serventia=
Id_Usuario=
Id_ArquivoTipo=
ProcessoNumero=
DataInicial=
DataFinal=
g-recaptcha-response=
Localizar=Consultar
```

Resultado observado:

- HTTP 200 em sessao limpa;
- `1357643 resultados encontrados para o filtro da pesquisa` no teste com
  `dano moral`;
- resultados com numero CNJ, classe, magistrado/relator, unidade/orgao, data de
  julgamento e texto da decisao;
- texto integral aparece no proprio HTML de resultado;
- botao `Baixar Inteiro teor` referencia `Id_Arquivo`, mas o probe separado de
  download sem token voltou ao formulario.

Decisao: TJGO deve ser promovido como provider HTML P0 com extracao inicial a
partir dos cards de resultado. A rota de download deve ficar pendente ate haver
contrato limpo sem token/captcha. O diagnostico `probe-rota` foi ajustado para
nao classificar como bloqueio uma pagina que contem scripts globais de
Cloudflare/Turnstile mas entrega resultados juridicos reais.

### TJMA/Jurisconsult

Frontend publico:

```text
GET https://jurisconsult.tjma.jus.br/#/sg-jurisprudence-list
```

Host API observado no bundle publico:

```text
https://apijuris.tjma.jus.br/v1
```

Endpoints auxiliares validados:

```text
GET /jurisprudencia/lista_relatorios
GET /jurisprudencia/lista_todos_tipos_pesquisa?tipoRelatorio=1
GET /jurisprudencia/lista_todos_camaras?tipoRelatorio=1
GET /jurisprudencia/links_pesquisa_sumulas
```

`/jurisprudencia/lista_relatorios` retornou relatorios e rotas tecnicas:

- `/sg/jurisprudencias/processos` para acordaos;
- `/jurisprudencia/processos/pesquisa_acordaos_tr`;
- `/jurisprudencia/processos/pesquisa_monocraticas`;
- `/jurisprudencia/processos/pesquisa_monocraticas_tr`;
- `/jurisprudencia/links_pesquisa_sumulas`;
- `/jurisprudencia/processos/sentencas_pg`;
- `/jurisprudencia/processos/sentencas_je`.

Teste da busca principal sem token:

```text
GET /sg/jurisprudencias/processos?chave=dano%20moral&tipoPesquisa=1&dtaInicio=2020-01-01&dtaFim=2026-08-07&tokenG=&keyId=
```

Resultado: HTTP 400 JSON `{"error":"captcha_not_provided"}`.

Decisao: promover apenas o contrato parcial de metadados e links de sumulas/IAC/
IRDR. Nao implementar busca de acordaos/sentencas enquanto depender de captcha.

### TSE e TREs/SJUR

Frontends publicos:

```text
GET https://jurisprudencia.tse.jus.br/
GET https://jurisprudencia-tres.tse.jus.br/
```

O bundle publico revelou o host tecnico:

```text
https://sjur-pesquisa-api.tse.jus.br/{tribunal}/sjur-pesquisa-backend/rest/public/pesquisa
```

O placeholder `{tribunal}` foi observado como:

- `tse` para jurisprudencia do TSE;
- `tres` para o agregador dos TREs.

Endpoints auxiliares observados:

```text
POST /classes
POST /relatorias
POST /eleicoes
POST /normas
POST /download/
POST /pesquisaTokenValidado
POST /livre
POST /simples
POST /rede
```

Payloads de metadados validados:

```json
["TSE"]
```

```json
["TRE-SP"]
```

Sinais observados:

- `POST /classes` e `POST /relatorias` retornam JSON publico com classes e
  relatores;
- exemplos de classes: `RESPE`, `AI`, `REspEl`, `AREspEl`;
- a busca principal `POST /public/pesquisa` respondeu com mensagem de falha
  antirrobo e `content=[]`;
- a rota `/livre` testada com payload simples retornou 404 no ambiente atual.

Decisao: contrato parcial P1 para metadados eleitorais publicos. Nao promover
provider de decisoes enquanto a busca principal depender de token/antirrobo ou
validacao humana.

### TRT2/PJe jurisprudencia e Basis

Frontend publico TRT2:

```text
GET https://pje.trt2.jus.br/jurisprudencia/
```

Endpoints observados no bundle:

```text
GET  /juris-backend/api/opcoes
POST /juris-backend/api/filtros
POST /juris-backend/api/documentos
GET  /juris-backend/api/token
```

Sinais observados:

- `GET /opcoes` retorna JSON publico com regional, versao, URL de consulta PJe
  e configuracao de captcha;
- `POST /filtros` com payload incompleto retorna erro de parametros;
- `POST /documentos` retorna `tokenDesafio` e `imagem` em vez de documentos no
  fluxo limpo;
- `GET /token` retornou HTTP 200 sem conteudo util no probe.

Decisao: documentar contrato parcial e bloquear provider de documentos enquanto
o fluxo exigir desafio por imagem/token. O diagnostico `probe-rota` deve marcar
esse retorno como `access_control_or_login`, nao como rota valida.

Rota documental relacionada:

```text
GET https://basis.trt2.jus.br/discover?query=teletrabalho
```

O Basis/TRT2 e um repositorio DSpace publico com boletins, atos normativos,
doutrina e materiais correlatos. Pode virar provider documental ou de boletins,
mas nao deve ser confundido com busca de decisoes completas.

### TJAC/e-SAJ CJSG e TJCE

TJAC/CJSG validado:

```text
GET https://esaj.tjac.jus.br/cjsg/consultaCompleta.do
GET https://esaj.tjac.jus.br/cjsg/resultadoSimples.do?conversationId=&nuProcOrigem=0700309-51.2015.8.01.0001&nuRegistro=
```

Sinais observados:

- HTTP 200 em sessao limpa;
- formulario CJSG completo;
- resultado com numero CNJ, ementa, relator, orgao julgador, data de julgamento
  e publicacao;
- link/conteudo de inteiro teor publico.

Decisao: fonte forte da familia e-SAJ/CJSG. Como ja existem providers CJSG no
codigo, TJAC deve ser usado para endurecer a abstracao por familia e fixtures
reais.

TJCE/CJSG:

```text
GET https://esaj.tjce.jus.br/cjsg/consultaSimples.do
```

O ambiente atual recebeu `ConnectionResetError`/TLS EOF. Decisao: nao promover
ate haver probe limpo; repetir com janela diferente e confirmar se e bloqueio
regional, instabilidade ou requisito TLS especifico.

### STM

Rota validada:

```text
GET https://jurisprudencia.stm.jus.br/
```

Sinais observados:

- HTTP 200 em sessao limpa;
- pagina oficial JMU/STM com sinais de jurisprudencia, inteiro teor e pesquisa;
- provider `stm_jurisprudencia` ja existe no codigo.

Decisao: manter como fonte especializada relevante. O proximo passo e comparar
o contrato documentado com o provider existente e adicionar fixture publica
representativa se ainda faltar.

### TJAP/Tucujuris

Rotas testadas:

```text
GET https://services.tjap.jus.br/pages/consultar-jurisprudencia/consultar-jurisprudencia.html
GET https://tucujuris.tjap.jus.br/tucujuris/pages/consultar-jurisprudencia/consultar-jurisprudencia.html
```

Resultado observado:

- `services.tjap.jus.br` nao resolveu DNS no ambiente atual;
- `tucujuris.tjap.jus.br` respondeu desafio Cloudflare/JavaScript em sessao
  limpa.

Decisao: documentar bloqueio e nao implementar provider TJAP ate localizar rota
publica estavel sem desafio.

### Rodada estadual complementar: TJES, TJMT, TJPA, TJPB, TJPE, TJPI, TJRO,
TJRR e TJSE

A rodada complementar esta detalhada em
[state-court-route-mapping-2026-08-07.md](state-court-route-mapping-2026-08-07.md).
Ela retirou esses estados da zona de "sem candidato claro" e separou tres
grupos:

- candidatos de provider decisorio: TJPI, TJRR, TJMT, TJPA e TJPB;
- candidatos documentais/precedentes: TJPE, TJSE e TJRO;
- inconclusivo: TJES.

O achado mais maduro e o TJPI/JusPI, porque a URL de busca server-side retornou
resultado real com CNJ, ementa, relator, orgao, tipo e paginacao. TJRR tambem e
forte, mas exige reproducao cuidadosa de JSF/PrimeFaces. TJMT e TJPA sao bons
alvos de API moderna, porem dependem de HAR/payload: o TJMT respondeu 401 sem a
chave/header publico usado pelo frontend, e o TJPA respondeu 404 em GET simples
para `/bff/api/decisoes`.

## Proximos probes recomendados

1. Validar inteiro teor live da familia eproc federal para TNU, TRF2 e TRF6,
   agora que os providers de busca ja reaproveitam o parser testado em TRF4/TJSP.
2. TJGO: criar contrato Projudi, fixture HTML publica representativa e parser offline de
   cards com inteiro teor embutido.
3. TJRS: criar contrato AJAX/SOLR, fixture JSON publica representativa e parser offline.
4. TJBA: criar contrato em `docs/source-contracts/`, fixture GraphQL publica representativa
   e parser offline.
5. TJPR: criar contrato da rota HTML, fixture de resultado e parser offline.
6. TJSC/TRF2: documentar contrato eproc, descobrir payload de busca e validar
   paginacao.
7. TSE/TREs: manter metadados em contrato parcial e nao promover busca enquanto
   houver antirrobo/token.
8. TRT2/PJe: documentar desafio `tokenDesafio`/`imagem` e bloquear automacao de
   documentos.
9. TJMA: documentar contrato parcial de metadados e manter busca principal
   bloqueada enquanto exigir captcha.
10. TST: reproduzir filtro textual com payload salvo em `--json-file` usando
   termos trabalhistas (`horas extras`, `justa causa`, `equiparacao salarial`).
11. TJPI: criar fixture HTML publica representativa com `q=dano moral`, `q=idpj` e pagina 2.
12. TJRR: gravar HAR de busca simples e reproduzir JSF/PrimeFaces sem cookies
   privados.
13. TJMT/TJPA: capturar payloads publicos dos frontends e validar APIs BFF/REST.
14. TJPB: repetir busca real e registrar se Cloudflare/WAF aparece em sessao
   limpa.
15. TJPE/TJSE/TJRO: aprofundar como catalogos/entradas e localizar endpoint de
   resultado quando existir.
16. TJES: repetir `Pesquisa.aspx` com janela maior.
17. TRF1/TRF3/TRF5: repetir com janela maior e pagina alternativa oficial.
18. TJMG/TJRJ/TJAP/TJCE/TRT15/TRT23: manter documentados como formulacoes ricas ou bloqueadas, mas bloquear provider
   enquanto resultado depender de captcha/reCAPTCHA/Cloudflare/reset.

## Ranking de implementacao

| Rank | Fonte | Motivo |
| --- | --- | --- |
| 1 | TNU/TRF2/TRF6 eproc | alto valor federal, rota limpa e reuso imediato do parser eproc |
| 2 | TJGO/Projudi | alto volume, resultado publico e inteiro teor embutido nos cards |
| 3 | TJRS AJAX/SOLR | JSON estruturado, facets ricas, alto volume e rota publica rapida |
| 4 | TJBA GraphQL | contrato estruturado, campos canonicos diretos, resposta limpa |
| 5 | TJPR HTML | alto volume, resultado publico e sinais juridicos completos |
| 6 | TJSC/eproc | fonte publica forte e potencial de provider por familia tecnica |
| 7 | TJAC/CJSG | rota CJSG validada e util para endurecer familia e-SAJ |
| 8 | TJPI/JusPI | busca HTML limpa com resultados reais e paginacao |
| 9 | TJRR/Juris JSF | pagina rica, sem bloqueio no GET, bom acervo estadual |
| 10 | TJMT/TJPA APIs modernas | bundles revelam contratos promissores; falta payload |
| 11 | TJPB/PJe jurisprudencia | UI rica, mas precisa estabilizar risco WAF |
| 12 | TST backend | JSON rico, mas filtro textual ainda precisa ser estabilizado |
| 13 | TSE/TREs metadados | contrato oficial util para filtros, mas busca principal bloqueada |
| 14 | TRT2 metadados/opcoes | contrato parcial util para diagnostico PJe, mas documentos exigem desafio |
| 15 | TJPE/TJSE/TJRO documentais | entradas uteis para sumulas, precedentes e orientacao, mas ainda sem busca decisoria limpa |
| 16 | TJMA metadados/sumulas | API limpa parcial; busca principal exige captcha |
| 17 | TJES/TJMG/TJRJ/TJAP/TJCE/TRT15/TRT23 | inconclusivos, formularios ricos ou portais conhecidos, mas busca direta bloqueada/instavel |
