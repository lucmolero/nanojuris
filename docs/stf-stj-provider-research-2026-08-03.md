# STF/STJ Provider Research - 2026-08-03

Objetivo: localizar fontes oficiais para providers STF/STJ, com prioridade para
qualidade de dados e acesso a autos/documentos publicos. Regra operacional:
promover apenas rotas reproduziveis com sessao HTTP limpa, sem cookies de
navegador, bypass de captcha, token voluvel ou login.

## Resultado executivo

STJ tem uma fonte oficial de altissima qualidade no Portal de Dados Abertos
CKAN: `https://dadosabertos.web.stj.jus.br/api/3/action/...`. A melhor frente
nao e o SCON live, mas os datasets oficiais em JSON/CSV/ZIP.

STF tem valor juridico maximo, mas as rotas diretas testadas nao ficaram
promoviveis: `portal.stf.jus.br`, `www.stf.jus.br`, `dados.stf.jus.br` e
`transparencia.stf.jus.br` retornaram `403`; `jurisprudencia.stf.jus.br`
retornou `202` com desafio JavaScript/AWS WAF. A cobertura STF mais limpa hoje
continua indireta via `bnp_pangea` para repercussao geral/precedentes, e DataJud
mediante credencial.

## Ranking de candidatos

| Rank | Fonte candidata | Tribunal | Qualidade | Autos/documentos | Decisao |
| --- | --- | --- | --- | --- | --- |
| 1 | STJ Dados Abertos - integras do DJe | STJ | Muito alta | Texto integral de decisoes terminativas e acordaos publicados no DJe; nao sao autos completos do processo | P0 para provider documental/lote |
| 2 | STJ Dados Abertos - espelhos de acordaos | STJ | Muito alta | Metadados ricos de acordaos por orgao julgador, com JSON/ZIP/CSV e dicionario | P0 para provider de jurisprudencia bulk |
| 3 | STJ Dados Abertos - precedentes qualificados | STJ | Muito alta | Temas e processos vinculados; nao autos | P0 para `CanonicalPrecedent` |
| 4 | STJ Dados Abertos - acervo em tramitacao | STJ | Alta | Metadados de processos em tramitacao; nao pecas/autos | P1 para consulta processual bulk |
| 5 | STJ Dados Abertos - atas de distribuicao e pautas futuras | STJ | Alta | Eventos processuais/publicacoes; complementa linha do tempo | P1 como enriquecimento de autos |
| 6 | DataJud API publica STF/STJ | STF/STJ | Alta com credencial | Metadados processuais e movimentos, sem pecas integrais; exige credencial/API key | P1 configuravel por credencial |
| 7 | STJ Precedentes/Informativos HTML | STJ | Media/alta | Paginas oficiais publicas, sem autos completos; conteudo tematico | P2 se CKAN nao cobrir o caso de uso |
| 8 | STJ SCON live | STJ | Alta juridicamente, baixa automatizacao | Jurisprudencia rica, mas probe limpo caiu em verificacao automatica/captcha | Nao promover live; manter parser/ficha |
| 9 | STJ Consulta Processual live | STJ | Alta se acessivel | Autos/processo seriam muito relevantes, mas probe limpo caiu em verificacao automatica | Bloqueado sem bypass |
| 10 | STF via BNP/Pangea | STF | Alta para precedentes | Repercussao geral e precedentes qualificados, sem autos | Ja disponivel indiretamente; manter e documentar |
| 11 | STF jurisprudencia/processos/portal/dados | STF | Alta juridicamente, baixa automatizacao | Potencial alto, mas rotas oficiais testadas retornaram WAF/403/202 | Bloqueado; pesquisar API alternativa |

## Evidencia STJ

Portal CKAN:

```text
GET https://dadosabertos.web.stj.jus.br/api/ -> 200 JSON {"version": 1}
GET https://dadosabertos.web.stj.jus.br/api/3/action/package_search?rows=300 -> 200 JSON
```

Datasets juridicos identificados:

```text
atas-de-distribuicao
precedentes-qualificados
pautas-futuras
acervo-em-tramitacao
integras-de-decisoes-terminativas-e-acordaos-do-diario-da-justica
espelhos-de-acordaos-corte-especial
espelhos-de-acordaos-primeira-secao
espelhos-de-acordaos-segunda-secao
espelhos-de-acordaos-terceira-secao
espelhos-de-acordaos-primeira-turma
espelhos-de-acordaos-segunda-turma
espelhos-de-acordaos-terceira-turma
espelhos-de-acordaos-quarta-turma
espelhos-de-acordaos-quinta-turma
espelhos-de-acordaos-sexta-turma
api-publica-datajud
```

Campos confirmados por dicionarios oficiais:

```text
Espelhos de acordaos:
id, numeroProcesso, numeroRegistro, siglaClasse, descricaoClasse,
nomeOrgaoJulgador, ministroRelator.

Precedentes qualificados:
sequencialPrecedente, tipoPrecedente, numeroPrecedente,
dataPrimeiraAfetacao, dataJulgamento, situacao,
informacoesComplementares.

Acervo em tramitacao:
numeroUnico, data de extracao, numeroRegistro, siglaClasse,
numeroNaClasse, codigoClasseCNJ, processo.

Atas de distribuicao:
numeroUnico, numeroRegistro, forma de distribuicao,
dataHoraDistribuicao, classe e metadados de autuacao.

Integras do DJe:
SeqDocumento, dataPublicacao, tipoDocumento, numeroRegistro,
processo, dataRecebimento, dataDistribuicao.
```

Rotas STJ bloqueadas ou menos prioritarias:

```text
https://scon.stj.jus.br/SCON/ -> 403 com verificacao automatica
https://scon.stj.jus.br/SCON/pesquisar.jsp?livre=ICMS -> 403 com verificacao automatica
https://processo.stj.jus.br/SCON/pesquisar.jsp?livre=ICMS -> 200, mas com captcha/recaptcha/cloudflare
https://processo.stj.jus.br/processo/pesquisa/?aplicacao=processos.ea -> 403 com verificacao automatica
```

## Evidencia STF

Rotas testadas:

```text
https://jurisprudencia.stf.jus.br/pages/search?base=acordaos&queryString=ICMS -> 202, AWS WAF/JavaScript challenge
https://jurisprudencia.stf.jus.br/pages/search?base=decisoes&queryString=ICMS -> 202, AWS WAF/JavaScript challenge
https://jurisprudencia.stf.jus.br/pages/search?base=informativos&queryString=ICMS -> 202, AWS WAF/JavaScript challenge
https://portal.stf.jus.br/jurisprudencia/ -> 403
https://portal.stf.jus.br/processos/ -> 403
https://portal.stf.jus.br/processos/detalhe.asp?incidente=5788952 -> 403
https://portal.stf.jus.br/repercussaogeral/ -> 403
https://portal.stf.jus.br/jurisprudenciaRepercussao/ -> 403
https://dados.stf.jus.br/ -> 403
https://transparencia.stf.jus.br/ -> 403
```

Rodada adicional de jurisprudencia:

```text
URL completa usada por scraper publico:
https://jurisprudencia.stf.jus.br/pages/search?base=acordaos&sinonimo=true&plural=true&page=1&pageSize=250&queryString=ICMS&sort=_score&sortBy=desc
-> 202 text/html, AWS WAF challenge

https://jurisprudencia.stf.jus.br/pages/search?base=decisoes&pesquisa_inteiro_teor=false&sinonimo=true&plural=true&radicais=false&buscaExata=true&page=1&pageSize=10&queryString=ICMS&sort=_score&sortBy=desc
-> 202 text/html, AWS WAF challenge

https://jurisprudencia.stf.jus.br/pages/search?base=informativos&pesquisa_inteiro_teor=false&sinonimo=true&plural=true&radicais=false&buscaExata=true&page=1&pageSize=10&queryString=ICMS&sort=_score&sortBy=desc
-> 202 text/html, AWS WAF challenge

http://www.stf.jus.br/portal/jurisprudencia/listarConsolidada.asp?base=baseAcordaos
-> 403

https://www.stf.jus.br/portal/cms/verTexto.asp?servico=jurisprudenciaSumula
-> 403

https://portal.stf.jus.br/textos/verTexto.asp?servico=informativoSTF
-> 403

https://www.stf.jus.br/arquivo/cms/publicacaoInformativoTema/anexo/Informativo_STF.pdf
-> 403
```

Subdominios candidatos:

```text
api-jurisprudencia.stf.jus.br -> DNS_FAIL
jurisprudencia-api.stf.jus.br -> DNS_FAIL
jurisprudencia-backend.stf.jus.br -> DNS_FAIL
jurisprudencia-backend2.stf.jus.br -> DNS_FAIL
pesquisa-jurisprudencia.stf.jus.br -> DNS_FAIL
search-jurisprudencia.stf.jus.br -> DNS_FAIL
busca-jurisprudencia.stf.jus.br -> DNS_FAIL
jurisprudencia.stf.jus.br -> resolve, mas responde AWS WAF challenge
```

Fontes externas/espelhadas testadas:

```text
dados.gov.br HTML para termos STF/Supremo Tribunal Federal/repercussao geral -> 200 HTML de app, sem dataset parseavel no probe limpo
dados.gov.br API /dados/api/publico/conjuntos-dados?... -> 401
LexML busca STF/repercussao/sumula -> 200 HTML com verificacao de seguranca do Senado
```

Cobertura STF indireta confirmada:

```text
NanoJurisClient().search('ICMS', source='bnp_pangea', courts=['STF'], types=['RG'], page_size=3)
-> total=65; primeiros IDs: stf-rg-615, stf-rg-1331, stf-rg-456
```

DNS/API:

```text
dadosabertos.stf.jus.br -> nao resolveu DNS no probe local
api.stf.jus.br -> nao resolveu DNS no probe local
dados.stf.jus.br -> resolve, mas retorna 403 para raiz, api, swagger e openapi
```

DataJud:

```text
POST https://api-publica.datajud.cnj.jus.br/api_publica_stj/_search -> 401 missing authentication credentials
POST https://api-publica.datajud.cnj.jus.br/api_publica_stf/_search -> 401 missing authentication credentials
```

## Leitura para autos completos

Nenhuma rota STF/STJ testada entregou autos completos publicos em sessao HTTP
limpa. O melhor substituto responsavel hoje e montar um dossie processual STJ a
partir de fontes abertas: acervo em tramitacao, atas de distribuicao, pautas,
integras do DJe e precedentes. Isso nao substitui pecas integrais de autos, mas
oferece linha do tempo, metadados, decisoes e textos publicados.

Para STF/STJ, DataJud pode complementar metadados e movimentos mediante API key,
mas tambem nao fornece pecas integrais. Consulta processual live e jurisprudencia
live devem permanecer bloqueadas se exigirem verificacao automatica/captcha.

## Proxima implementacao recomendada

1. `stj_dados_abertos_jurisprudencia`: listar datasets `espelhos-de-acordaos-*`,
   escolher recursos JSON/ZIP por data, normalizar para `CanonicalDecision`.
2. `stj_dados_abertos_integras_dje`: ingerir metadados + ZIP/TXT de decisoes e
   acordaos publicados no DJe como `CanonicalDocument`.
3. `stj_dados_abertos_precedentes`: converter `Temas.csv` e `Processos.csv` para
   `CanonicalPrecedent`.
4. `stj_dados_abertos_processos`: criar dossie processual a partir de acervo,
   distribuicao e pautas, declarando explicitamente que nao sao autos completos.
5. `datajud`: provider opcional com credencial configurada para STF/STJ e demais
   tribunais.
6. `stf_bnp_repercussao_geral`: documentar/embrulhar a cobertura STF ja
   disponivel via `bnp_pangea` quando o usuario pedir precedentes STF.
7. `stf_jurisprudencia`: manter em discovery ate surgir API publica limpa sem
   WAF/captcha/token voluvel.