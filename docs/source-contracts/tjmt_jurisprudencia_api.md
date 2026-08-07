# `tjmt_jurisprudencia_api`

## Identidade

- Fonte oficial: Jurisprudencia publica do TJMT.
- Categoria: `court_jurisprudence`.
- Familia tecnica: `spa_api_jurisprudencia`.
- URL inicial: `https://jurisprudencia.tjmt.jus.br/`.
- Status de acesso: candidato forte, dependente de contrato de API/header.
- Status no NanoJuris: candidato, ainda sem provider implementado.

## Contrato HTTP

- SPA publica observada:
  - `GET /`
  - `GET /main.4fbae9a9bb684a741e57.bundle.js`
- Rotas inferidas do bundle:
  - `https://hellsgate-preview.tjmt.jus.br/jurisprudencia/api/consulta/<tipoConsulta>`
  - `/jurisprudencia/api/termo/<termo>`
  - `/jurisprudencia/api/consulta/relator?Quantidade=1000`
  - `/jurisprudencia/api/consulta/orgao-julgador?Quantidade=100`
  - `/jurisprudencia/api/consulta/classe?Quantidade=100`
  - `/jurisprudencia/VisualizaRelatorio/RetornaDocumentoAcordao`
- Probe direto em `/api/consulta/1`: HTTP 401 `No API key found in request`.
- Header/chave: existe indicio de header publico emitido pelo frontend; precisa
  validar antes de qualquer provider.

## Dados retornados

- Campos esperados:
  - acordao;
  - relator;
  - orgao julgador;
  - classe;
  - termo;
  - documento/acordao em relatorio.
- Campos canonicos esperados: `CanonicalDecision`.
- Inteiro teor: possivel por rota de relatorio, ainda nao validado.

## Comportamento observado

- GET do portal: HTTP 200.
- API sem header: HTTP 401.
- Busca com resultado: nao reproduzida ainda.
- Risco: alto ate confirmar se o header faz parte do contrato publico do
  frontend.

## Fixtures

- [ ] Bundle publico revisado com rotas relevantes.
- [ ] HAR de busca real.
- [ ] JSON de resultado.
- [ ] JSON vazio.
- [ ] Erro 401 sem header.

## MCP e agentes

- Quando usar: somente depois de confirmar payload/header publico.
- Quando pular: enquanto a API direta retornar 401.
- Mensagem segura: "O portal TJMT e publico, mas o contrato de API ainda nao
  foi estabilizado."
- Riscos: promover header de frontend sem validar natureza publica e
  reproduzivel.

## Proximos passos

- [ ] Capturar HAR de busca simples.
- [ ] Identificar headers minimos enviados pelo frontend.
- [ ] Validar endpoint de metadados.
- [ ] Validar endpoint de busca e documento.
