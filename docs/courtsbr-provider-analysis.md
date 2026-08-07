# CourtsBR Provider Analysis

Analise de `https://github.com/courtsbr` feita em 2026-08-02 para orientar a
expansao da NanoJuris. A organizacao contem pacotes R historicos de scraping
judicial brasileiro. O valor principal para a NanoJuris nao e copiar codigo, mas
aproveitar a inteligencia de fonte: familias tecnicas, payloads, seletores,
campos extraidos e limites reais.

## Repositorios inspecionados

| Repositorio | Escopo | Utilidade para NanoJuris | Cuidado |
| --- | --- | --- | --- |
| `courtsbr/esaj` | e-SAJ: CPOPg, CPOSg, CJPG, CJSG, PDFs de decisoes | mapa de endpoints e parsers para familia e-SAJ | usa quebra de captcha em CPOPg/decisoes; nao copiar esse fluxo |
| `courtsbr/tjsp` | TJSP sobre e-SAJ, com CJSG/CJPG/CPOSg e inteiro teor | confirma payloads e campos TJSP | tambem tenta resolver captcha/audio para PDF |
| `courtsbr/tjdf` | TJDFT primeira instancia e jurisprudencia | candidato forte a provider limpo `tjdf_juris` | precisa fixture e parser Python proprio |
| `courtsbr/stfstj` | STF/STJ jurisprudencia por HTML legado | seletores e campos canonicos de acordaos/monocraticas | rotas STJ/STF testadas hoje retornaram 403 ou sao legadas |
| `courtsbr/stj` | consulta processual STJ com Selenium | pouco aproveitavel como provider limpo | depende de navegador/headless |
| `courtsbr/dje` | download de DJEs estaduais | mapa nacional de diarios oficiais | categoria e `CanonicalDocument`, nao jurisprudencia |
| `courtsbr/djt` | Diario da Justica do Trabalho | publicacoes trabalhistas e parser de PDF/texto | fluxo JSF/ViewState complexo |
| `courtsbr/scraperTJRS` | TJRS diarios e consulta processual | ideias de parser e diario TJRS | usa captcha em consulta processual |
| `courtsbr/JurisMiner` | utilitarios de limpeza/jurimetria | normalizacao de CNJ, TPU, KWIC, limpeza textual | nao e provider de fonte |

## Achado central

`courtsbr` resolve muitos problemas praticos de coleta por tres caminhos:

1. **Payloads e seletores oficiais**: codifica nomes reais de formularios,
   rotas de paginacao e seletores HTML de campos juridicos.
2. **Download em lote com cache local**: baixa HTML/PDF para disco antes de
   parsear, reduzindo perda de coleta e permitindo reprocessamento offline.
3. **Captcha solving em alguns fluxos**: usa OCR/audio/modelos (`tesseract`,
   `captchasaj`, `captchaSajAudio`, `captchaTJRS`) para passar por controles.

Para a NanoJuris, os itens 1 e 2 sao aproveitaveis. O item 3 explica por que o
pacote historico consegue acessar fluxos que hoje bloqueiam `requests`, mas nao
deve ser implementado aqui. A fronteira correta continua sendo: se a fonte exige
captcha, login, token voluvel ou validacao humana, o provider deve diagnosticar e
parar, sem bypass.

## Providers e rotas mais relevantes

### e-SAJ CPOPg/CPOSg

`courtsbr/esaj` mapeia a familia e-SAJ por numero CNJ:

```text
GET /cpopg/search.do
GET /cposg/search.do
```

Parametros importantes para CPOPg:

```text
conversationId=
dadosConsulta.localPesquisa.cdLocal=-1
cbPesquisa=NUMPROC
dadosConsulta.tipoNuProcesso=UNIFICADO
numeroDigitoAnoUnificado=<NNNNNNN-DD.AAAA>
foroNumeroUnificado=<foro>
dadosConsulta.valorConsultaNuUnificado=<CNJ sem mascara no pacote R>
dadosConsulta.valorConsulta=
```

Isso confirma a escolha do provider `tjsp_esaj_cpopg` da NanoJuris. O pacote R
tambem lista outros e-SAJs historicos: TJAL, TJAM, TJBA, TJSC e TJSP. O caminho
recomendado e criar um provider por familia `esaj_cpopg` parametrizado por
tribunal, mas so promover cada tribunal depois de probe limpo sem captcha.

Campos que o parser R extrai e que devem orientar o modelo Python:

- dados basicos do processo;
- partes;
- movimentacoes;
- historico de classes;
- audiencias;
- delegacia/dados policiais quando presentes;
- marcador de processo digital.

### TJSP CJSG

`courtsbr/esaj` e `courtsbr/tjsp` confirmam o endpoint usado pela NanoJuris:

```text
POST /cjsg/resultadoCompleta.do
GET  /cjsg/trocaDePagina.do?tipoDeDecisao=A&pagina=<n>&conversationId=
GET  /cjsg/getArquivo.do?cdAcordao=<id>&cdForo=0
```

Payload observado para busca:

```text
dados.buscaInteiroTeor
dados.pesquisarComSinonimos=N
classesTreeSelection.values
assuntosTreeSelection.values
secoesTreeSelection.values
dados.dtJulgamentoInicio
dados.dtJulgamentoFim
dados.dtRegistroInicio
dados.dtRegistroFim
tipoDecisaoSelecionados=A
dados.ordenarPor=dtPublicacao
```

Campos do parser R equivalentes aos nossos canônicos:

- `id_decision` -> `cdAcordao`/id de decisao;
- `id_lawsuit` -> numero do processo/recurso;
- `class_subject` -> classe/assunto;
- `district` -> comarca;
- `court` -> orgao julgador;
- `date_decision`, `date_publication`, `date_registration`;
- `rapporteur`;
- `summary` e `txt_summary`.

O que isso resolve: valida nossos seletores e mostra a paginacao correta. O que
nao resolve: quando TJSP/CJSG devolve captcha/recaptcha/login, o pacote antigo
recorre a quebra de captcha para PDF; NanoJuris deve manter o diagnostico de
acesso controlado.

### TJSP CJPG

`courtsbr/tjsp` revela uma rota que ainda nao temos:

```text
GET  /cjpg/
POST formulario com dadosConsulta.pesquisaLivre
GET  /cjpg/trocarDePagina.do?pagina=<n>&conversationId=
```

Payload relevante:

```text
dadosConsulta.pesquisaLivre
classeTreeSelection.values
assuntoTreeSelection.values
varasTreeSelection.values
dadosConsulta.dtInicio
dadosConsulta.dtFim
```

Probe limpo em 2026-08-02 abriu `/cjpg/` com HTTP 200. Em nova verificacao, o
formulario limpo expôs `action=/cjpg/pesquisar.do;jsessionid=...`, mas a
submissao POST minima para `dadosConsulta.pesquisaLivre=infanticidio` terminou
em timeout de leitura. Assim, `tjsp_cjpg` continua candidato de pesquisa, mas nao
foi promovido a provider nesta rodada.

### TJDFT Jurisprudencia

Este foi o melhor candidato novo encontrado na analise.

Rota de busca:

```text
GET https://pesquisajuris.tjdft.jus.br/IndexadorAcordaos-web/sistj
```

Primeira chamada limpa testada:

```text
argumentoDePesquisa=infanticidio
visaoId=tjdf.sistj.acordaoeletronico.buscaindexada.apresentacao.VisaoBuscaAcordao
nomeDaPagina=buscaLivre
comando=pesquisar
internet=1
camposSelecionados=ESPELHO
COMMAND=ok
quantidadeDeRegistros=20
tokenDePaginacao=1
```

Resultado observado: HTTP 200, HTML `SISTJWEB`, `count=31` em
`.conteudoComRotulo`.

Segunda chamada de resultados, seguindo o pacote R, retornou 20 ids na primeira
pagina usando o seletor `#id_link_abrir_dados_acordao`, por exemplo:

```text
1917641, 1907747, 1620532, 1150726, 1077582, 897971, 813699, 761853
```

Detalhe limpo de `numeroDoDocumento=1917641` retornou campos canônicos:

```text
Classe do Processo: 07226716720248070000 - ... - Segredo de Justica
Registro do Acordao Numero: 1917641
Data de Julgamento: 04/09/2024
Orgao Julgador: 7 Turma Civel
Relator(a): SANDRA REVES
Data da Intimacao ou Publicacao: 16/09/2024
Ementa: ...
Decisao: CONHECIDO. DESPROVIDO. UNANIME.
Inteiro Teor: Download Inteiro Teor - PJE
```

Classificacao: provider `tjdf_juris` implementado. Ele ataca diretamente a lacuna
de jurisprudencia estadual fora de Sao Paulo e foi reproduzido com HTTP limpo.

### STJ SCON e STF legado

`courtsbr/stfstj` mostra rotas historicas:

```text
STJ /SCON/jurisprudencia/toc.jsp?b=ACOR
STJ /SCON/decisoes/toc.jsp?b=DTXT
STF /portal/jurisprudencia/listarConsolidada.asp?base=baseAcordaos
STF /portal/jurisprudencia/listarConsolidada.asp?base=baseMonocraticas
```

Probes limpos atuais:

| Rota | Resultado |
| --- | --- |
| STJ `/SCON/jurisprudencia/toc.jsp` | HTTP 403, verificacao JavaScript/cookies |
| STJ `/SCON/decisoes/toc.jsp` | HTTP 403, verificacao JavaScript/cookies |
| STF `listarConsolidada.asp` | HTTP 403 Forbidden |

Conclusao: sao uteis para parsers offline e para ficha tecnica historica, mas
nao devem virar provider live ate surgir rota atual reproduzivel sem bloqueio.

### Diarios oficiais: DJE/DJT

`courtsbr/dje` e `courtsbr/djt` mostram uma frente que conversa com o provider
`comunica_pje`, mas em nivel de documento bruto:

- `dje`: downloads de PDFs de diarios estaduais por data/caderno;
- `djt`: consulta ao DEJT com JSF/ViewState e download de PDFs;
- parsers de texto removem cabecalho/rodape e localizam processos/contextos.

Isso resolve a lacuna de publicacoes oficiais em massa. O modelo correto na
NanoJuris e `CanonicalDocument`/`judicial_publications`, nao
`CanonicalDecision`, salvo quando um parser extrai uma decisao especifica.

### JurisMiner

`JurisMiner` nao e provider, mas oferece ideias de camada utilitaria:

- pontuacao/limpeza de CNJ;
- consulta/uso de TPU/CNJ;
- KWIC e busca fuzzy;
- agrupamento de datas e tempo de movimentacao;
- leitura/limpeza de PDFs e textos juridicos.

Isso pertence a uma futura camada `nanojurs.text` ou `nanojurs.jurimetrics`, nao
ao core dos providers.

## Como isso resolve problemas da NanoJuris

| Problema nosso | Como `courtsbr` ajuda | Decisao recomendada |
| --- | --- | --- |
| Descobrir rotas validas sem tentativa cega | Repos trazem endpoint, payload e seletor historico | transformar em fichas de fonte e probes limpos |
| e-SAJ CPOPg por varios tribunais | `get_lwst_data()` lista dominios e parametros por TJ | generalizar `tjsp_esaj_cpopg` para familia `esaj_cpopg` com allowlist validada |
| TJSP/CJSG parser | `parse_cjsg` confirma seletores e campos | usar como checklist de completude do parser Python |
| Falta de jurisprudencia estadual fora de SP | `tjdft` tem rota limpa com resultados atuais | implementar `tjdf_juris` primeiro |
| STJ/STF bloqueados | `stfstj` mostra rotas e campos, mas probes atuais falham | manter como parser offline/fixture; nao prometer live |
| Publicacoes e diarios | `dje`/`djt` mapeiam downloads e cadernos | criar familia `judicial_publications` separada de jurisprudencia |
| Limpeza/jurimetria | `JurisMiner` concentra utilitarios comuns | reaproveitar ideias, nao misturar com provider |

## Prioridade sugerida

1. **Implementar `tjdf_juris`**: rota limpa, campos ricos, alto ganho de
   cobertura estadual.
2. **Adicionar probe/subprovider `tjsp_cjpg`**: sentencas/julgados de primeiro
   grau no TJSP, se a submissao limpa funcionar.
3. **Generalizar e-SAJ CPOPg**: transformar `tjsp_esaj_cpopg` em base reutilizavel
   para TJAL/TJAM/TJBA/TJSC/TJSP, com promocao tribunal a tribunal.
4. **Melhorar parser TJSP/CJSG**: comparar cobertura com `parse_cjsg` e preencher
   lacunas de datas/campos.
5. **Criar familia `judicial_publications`**: Comunica PJe, DJE e DJT como fontes
   de publicacoes/documentos.

## Fronteira de compliance

Nao copiar fluxos de captcha solving, OCR de captcha, audio captcha ou Selenium
usado para passar por validacao humana. O uso adequado de `courtsbr` dentro da
NanoJuris e como inteligencia de fonte, fixture offline publica representativa e mapa de
contratos historicos. Providers live so devem nascer depois de reproducao com
sessao HTTP limpa.