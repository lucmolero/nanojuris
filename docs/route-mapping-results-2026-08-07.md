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
| TJGO/Projudi | `POST https://projudi.tjgo.jus.br/ConsultaJurisprudencia` | HTTP 200, HTML com mais de 1M resultados, processo, magistrado, orgao, decisao e inteiro teor no proprio card | promover para contrato HTML P0; download separado ainda pendente |
| TJMA/Jurisconsult metadados | `GET https://apijuris.tjma.jus.br/v1/jurisprudencia/lista_relatorios` | HTTP 200 JSON com relatorios e URLs tecnicas de acordaos, monocraticas, sumulas e sentencas | promover contrato parcial/metadados |
| TJMA/Jurisconsult busca | `GET https://apijuris.tjma.jus.br/v1/sg/jurisprudencias/processos?...` sem token | HTTP 400 JSON `captcha_not_provided` | nao automatizar busca principal sem fluxo publico limpo |
| TJAP/Tucujuris | `GET https://tucujuris.tjap.jus.br/tucujuris/pages/consultar-jurisprudencia/consultar-jurisprudencia.html` | Cloudflare/challenge no HTML limpo | bloquear provider enquanto exigir desafio |

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
P0. O primeiro passo tecnico e salvar fixture sanitizada com uma busca multi-area
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

Decisao: TNU e TRF6 devem entrar como P0 por reuso do parser/fetcher eproc ja
existente. O proximo passo tecnico e parametrizar o provider eproc por
instancia, preservando `source`, `court`, base URL, origens disponiveis e tipos
documentais.

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

## Proximos probes recomendados

1. Parametrizar familia eproc para TNU e TRF6, reaproveitando parser ja testado
   em TRF4/TJSP.
2. TJGO: criar contrato Projudi, fixture HTML sanitizada e parser offline de
   cards com inteiro teor embutido.
3. TJRS: criar contrato AJAX/SOLR, fixture JSON sanitizada e parser offline.
4. TJBA: criar contrato em `docs/source-contracts/`, fixture GraphQL sanitizada
   e parser offline.
5. TJPR: criar contrato da rota HTML, fixture de resultado e parser offline.
6. TJSC: documentar contrato eproc, descobrir payload de busca e validar
   paginacao.
7. TJMA: documentar contrato parcial de metadados e manter busca principal
   bloqueada enquanto exigir captcha.
8. TST: reproduzir filtro textual com payload salvo em `--json-file` usando
   termos trabalhistas (`horas extras`, `justa causa`, `equiparacao salarial`).
9. TRF3/TRF5: repetir com janela maior e pagina alternativa oficial.
10. TJMG/TJRJ/TJAP: manter documentados como formulacoes ricas ou bloqueadas, mas bloquear provider
   enquanto resultado depender de captcha/reCAPTCHA.

## Ranking de implementacao

| Rank | Fonte | Motivo |
| --- | --- | --- |
| 1 | TNU/TRF6 eproc | alto valor federal, rota limpa e reuso imediato do parser eproc |
| 2 | TJGO/Projudi | alto volume, resultado publico e inteiro teor embutido nos cards |
| 3 | TJRS AJAX/SOLR | JSON estruturado, facets ricas, alto volume e rota publica rapida |
| 4 | TJBA GraphQL | contrato estruturado, campos canonicos diretos, resposta limpa |
| 5 | TJPR HTML | alto volume, resultado publico e sinais juridicos completos |
| 6 | TJSC/eproc | fonte publica forte e potencial de provider por familia tecnica |
| 7 | TST backend | JSON rico, mas filtro textual ainda precisa ser estabilizado |
| 8 | TJMA metadados/sumulas | API limpa parcial; busca principal exige captcha |
| 9 | TJMG/TJRJ/TJAP | formularios ricos ou portais conhecidos, mas busca direta bloqueada por captcha/reCAPTCHA/Cloudflare |
