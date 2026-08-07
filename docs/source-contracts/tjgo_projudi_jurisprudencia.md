# tjgo_projudi_jurisprudencia

## Identidade
- Fonte oficial: PROJUDI/TJGO - Consulta de Jurisprudencia.
- Categoria: `court_jurisprudence`.
- Familia tecnica: `projudi_jurisprudencia`.
- URL inicial: `https://projudi.tjgo.jus.br/ConsultaJurisprudencia`.
- Status de acesso: busca publica validada em sessao limpa em 2026-08-07.

## Contrato HTTP
- Rotas:
  - `GET /ConsultaJurisprudencia`
  - `POST /ConsultaJurisprudencia`
  - `POST /ConsultaJurisprudencia?PaginaAtual=1&Id_Arquivo=<id>&g-recaptcha-response=` pendente; voltou ao formulario no teste sem token.
- Metodos: `GET` para formulario; `POST` para resultados.
- Parametros obrigatorios minimos do POST validado:
  - `PaginaAtual=2`
  - `PosicaoPaginaAtual=0`
  - `Texto=<termo>`
  - `Id_Instancia=0`
  - `Id_Area=0`
  - `Id_ServentiaSubTipo=0`
  - `Localizar=Consultar`
- Parametros opcionais:
  - `Viewstate`
  - `Id_Serventia`
  - `Id_Usuario`
  - `Id_ArquivoTipo`
  - `ProcessoNumero`
  - `DataInicial`
  - `DataFinal`
  - `g-recaptcha-response`
- Paginacao: pendente; resultado indica volume total, mas o contrato de troca de pagina deve ser validado.
- Ordenacao: nao mapeada.
- Filtros: texto, instancia, area, orgao/materia, serventia, magistrado, tipo de ato, processo e datas.

## Dados retornados
- Campos extraidos: numero CNJ, classe, partes, magistrado/relator, orgao/unidade, data/hora, decisao e trechos destacados.
- Campos canonicos: `CanonicalDecision`.
- Campos opcionais: id de arquivo, quantidade de ocorrencias no inteiro teor, unidade judicial.
- Campos instaveis: estrutura HTML de cards e textos longos sem separadores claros.
- Inteiro teor: presente no proprio HTML de resultado no probe com `dano moral`.
- Documentos vinculados: botao `Baixar Inteiro teor` com `Id_Arquivo`, mas download separado ainda nao confirmado.

## Comportamento observado
- Busca com resultado: `Texto=dano moral`, HTTP 200, `1357643 resultados encontrados`, processo, decisao e `Baixar Inteiro teor`.
- Busca sem resultado: pendente.
- Erro HTTP esperado: pendente.
- Controle de acesso/captcha: scripts globais aparecem no HTML, mas nao bloquearam o resultado testado; o diagnostico deve diferenciar asset global de desafio real.
- Mudanca de layout: risco alto por HTML de sistema processual.

## Fixtures
- Sucesso: pendente.
- Vazio: pendente.
- Erro: pendente.
- Documento: pendente.

## MCP e agentes
- Quando usar: consultas amplas de atos/jurisprudencia TJGO por termo ou processo.
- Quando pular: quando o fluxo passar a exigir captcha, token obrigatorio ou sessao autenticada.
- Mensagem segura para o usuario: "A busca retorna conteudo publico do PROJUDI/TJGO; o inteiro teor foi extraido do resultado HTML quando disponivel."
- Riscos: resultados muito grandes, documentos pessoais em decisoes publicas, HTML volumoso e necessidade de sanitizacao em fixtures.

## Proximos passos
- [ ] Criar fixture sanitizada com 2 a 3 cards.
- [ ] Implementar parser offline antes do fetcher.
- [ ] Validar busca vazia e paginacao.
- [ ] Testar `ProcessoNumero` com numero publico.
- [ ] Manter download por `Id_Arquivo` como pendente ate contrato limpo.
