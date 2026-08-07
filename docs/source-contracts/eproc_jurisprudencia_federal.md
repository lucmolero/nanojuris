# eproc_jurisprudencia_federal

## Identidade
- Fonte oficial: TNU/eproc e TRF6/eproc.
- Categoria: `court_jurisprudence`.
- Familia tecnica: `eproc_jurisprudencia`.
- URL inicial TNU: `https://eproctnu.cjf.jus.br/eproc/externo_controlador.php?acao=jurisprudencia@jurisprudencia/pesquisar`.
- URL inicial TRF6: `https://eproc-jur.trf6.jus.br/eproc/externo_controlador.php?acao=jurisprudencia@jurisprudencia/pesquisar`.
- Status de acesso: publico no probe limpo de 2026-08-07.

## Contrato HTTP
- Rotas:
  - `GET /eproc/externo_controlador.php?acao=jurisprudencia@jurisprudencia/pesquisar`
  - `POST /eproc/externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados`
  - `GET /eproc/externo_controlador.php?acao=jurisprudencia@jurisprudencia/download_inteiro_teor&id_jurisprudencia=<id>` pendente de fixture por tribunal.
- Metodos: `GET` para formulario e inteiro teor; `POST` para resultados.
- Parametros obrigatorios minimos do POST:
  - `txtPesquisa`
  - `rdoCampo`
- Parametros opcionais observados:
  - `hdnExibirPesquisaAvancada`
  - `txtProcesso`
  - `dtDecisaoInicio`
  - `dtDecisaoFim`
  - `dtPublicacaoInicio`
  - `dtPublicacaoFim`
  - `chkAgruparResultados`
  - `selTipoDocumento[]`
  - `selOrigem[]`
- Paginacao: HTML com controles e cards `resultadoItem`; repetir contrato antes de coletar em escala.
- Ordenacao: nao mapeada nesta rodada.
- Filtros: texto, campo de busca, processo, tipo documental, origem e datas.

## Dados retornados
- Campos extraidos: numero CNJ, classe, relator, orgao julgador, datas, decisao/ementa, links.
- Campos canonicos: `CanonicalDecision`.
- Campos opcionais: origem, tipo documental, id de jurisprudencia, URL de inteiro teor.
- Campos instaveis: labels HTML e lista de origens variam por instancia.
- Inteiro teor: link publico esperado pelo padrao eproc; fixture especifica ainda pendente para TNU/TRF6.
- Documentos vinculados: `id_jurisprudencia`.

## Comportamento observado
- Busca com resultado:
  - TNU: `txtPesquisa=aposentadoria`, `rdoCampo=I`, HTTP 200, `resultadoItem`.
  - TRF6: `txtPesquisa=aposentadoria`, `rdoCampo=I`, HTTP 200, `resultadoItem`.
- Busca sem resultado: pendente.
- Erro HTTP esperado: pendente.
- Controle de acesso/captcha: nao observado no fluxo testado.
- Mudanca de layout: risco medio por HTML de sistema.

## Fixtures
- Sucesso: pendente.
- Vazio: pendente.
- Erro: pendente.
- Documento: pendente.

## MCP e agentes
- Quando usar: consultas federais/TNU/TRF6 por tema, ementa, inteiro teor ou numero.
- Quando pular: quando o usuario pedir fonte estadual que nao use eproc ou quando houver sinal de controle de acesso.
- Mensagem segura para o usuario: "A consulta usa jurisprudencia publica do eproc e retorna apenas conteudo acessivel em sessao limpa."
- Riscos: HTML volumoso, mudanca de labels e necessidade de rate limit.

## Proximos passos
- [ ] Parametrizar provider eproc por base URL, tribunal e origens.
- [ ] Criar fixtures sanitizadas de TNU e TRF6.
- [ ] Reusar parser de `trf4_eproc_jurisprudencia`.
- [ ] Validar rota de inteiro teor com `id_jurisprudencia` real de cada fonte.
- [ ] Adicionar testes de sucesso, vazio e acesso restrito.
