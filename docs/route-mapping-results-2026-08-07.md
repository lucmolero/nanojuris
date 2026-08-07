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

## Proximos probes recomendados

1. TJRS: criar contrato AJAX/SOLR, fixture JSON sanitizada e parser offline.
2. TJBA: criar contrato em `docs/source-contracts/`, fixture GraphQL sanitizada
   e parser offline.
3. TJPR: criar contrato da rota HTML, fixture de resultado e parser offline.
4. TJSC: documentar contrato eproc, descobrir payload de busca e validar
   paginacao.
5. TST: reproduzir filtro textual com payload salvo em `--json-file` usando
   termos trabalhistas (`horas extras`, `justa causa`, `equiparacao salarial`).
6. TRF3/TRF5: repetir com janela maior e pagina alternativa oficial.
7. TJMG/TJRJ: manter documentados como formulacoes ricas, mas bloquear provider
   enquanto resultado depender de captcha/reCAPTCHA.

## Ranking de implementacao

| Rank | Fonte | Motivo |
| --- | --- | --- |
| 1 | TJRS AJAX/SOLR | JSON estruturado, facets ricas, alto volume e rota publica rapida |
| 2 | TJBA GraphQL | contrato estruturado, campos canonicos diretos, resposta limpa |
| 3 | TJPR HTML | alto volume, resultado publico e sinais juridicos completos |
| 4 | TJSC/eproc | fonte publica forte e potencial de provider por familia tecnica |
| 5 | TST backend | JSON rico, mas filtro textual ainda precisa ser estabilizado |
| 6 | TJMG/TJRJ | formularios ricos, mas busca direta bloqueada por captcha/reCAPTCHA |
