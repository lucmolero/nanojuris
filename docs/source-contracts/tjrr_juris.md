# `tjrr_juris`

## Identidade

- Fonte oficial: Jurisprudencia publica do TJRR.
- Categoria: `court_jurisprudence`.
- Familia tecnica: `jsf_primefaces_jurisprudencia`.
- URL inicial: `https://jurisprudencia.tjrr.jus.br/index.xhtml`.
- Status de acesso: candidato forte; GET publico validado.
- Status no NanoJuris: candidato, ainda sem provider implementado.

## Contrato HTTP

- Rotas observadas:
  - `GET /`
  - `GET /index.xhtml`
- Tecnologia observada: JSF/PrimeFaces.
- Parametros conhecidos: formulario publico com termo livre, pesquisa avancada,
  relator, numero SISCOM/PROJUDI, datas, ementa/indexacao e especie.
- Postback: pendente de HAR limpo.
- `javax.faces.ViewState`: deve vir da propria sessao publica; nao pode ser
  reutilizado de navegador pessoal.

## Dados retornados

- Campos esperados:
  - ementa;
  - acordao;
  - relator;
  - orgao;
  - numero;
  - datas;
  - especie;
  - links tematicos.
- Campos canonicos esperados: `CanonicalDecision`.
- Inteiro teor: pendente.

## Comportamento observado

- GET inicial: HTTP 200 com formulario rico.
- Busca com resultado: ainda precisa reproduzir.
- Controle de acesso/captcha: nao observado no GET inicial.
- Risco tecnico: postback JSF pode ser sensivel a campos ocultos e estado da
  sessao.

## Fixtures

- [ ] HTML inicial com `ViewState`.
- [ ] HAR de busca simples.
- [ ] Resultado com ementa/acordao.
- [ ] Busca vazia.
- [ ] Erro de postback/estado expirado.

## MCP e agentes

- Quando usar: somente depois de provider e parser offline.
- Quando pular: enquanto o contrato JSF nao estiver reproduzido.
- Mensagem segura: "A fonte TJRR e publica, mas a busca depende de contrato
  JSF ainda em investigacao."
- Riscos: confundir estado de sessao JSF com token reaproveitavel.

## Proximos passos

- [ ] Gravar HAR de busca simples em navegador limpo.
- [ ] Reproduzir postback com `requests`.
- [ ] Criar parser offline.
- [ ] Documentar parametros obrigatorios.
