# `tjpa_jurisprudencia_bff`

## Identidade

- Fonte oficial: Jurisprudencia publica do TJPA.
- Categoria: `court_jurisprudence`.
- Familia tecnica: `spa_bff_jurisprudencia`.
- URL inicial: `https://jurisprudencia.tjpa.jus.br/`.
- Status de acesso: candidato forte; falta metodo/payload da busca.
- Status no NanoJuris: candidato, ainda sem provider implementado.

## Contrato HTTP

- SPA publica observada:
  - `GET /`
  - `GET /main-6BATNNRR.js`
- Rotas inferidas:
  - `/bff/api/decisoes`
  - `/bff/api/pje/classes`
  - `/bff/api/pje/assuntos`
  - `/bff/api/siglas`
  - `/bff/api/temas-acordao`
- Probe direto:
  - `GET /bff/api/decisoes` retornou HTTP 404.
- Hipotese: metodo ou payload incorreto; precisa HAR.

## Dados retornados

- Campos esperados:
  - decisoes;
  - classes PJe;
  - assuntos PJe;
  - siglas;
  - temas de acordao.
- Campos canonicos esperados: `CanonicalDecision`.
- Inteiro teor: pendente.

## Comportamento observado

- GET do portal: HTTP 200.
- GET simples no endpoint de decisoes: HTTP 404.
- Busca com resultado: nao reproduzida ainda.
- Risco: medio-alto ate descobrir payload.

## Fixtures

- [ ] Bundle publico revisado.
- [ ] HAR de busca real.
- [ ] Payload de `/bff/api/decisoes`.
- [ ] JSON de resultado.
- [ ] JSON vazio.
- [ ] HTTP 404 por metodo incorreto.

## MCP e agentes

- Quando usar: somente depois de provider implementado.
- Quando pular: enquanto o payload de busca nao for conhecido.
- Mensagem segura: "O portal TJPA e oficial e publico, mas a rota final de
  busca ainda precisa ser reproduzida."
- Riscos: tratar 404 de metodo incorreto como fonte quebrada.

## Proximos passos

- [ ] Gravar HAR de busca simples.
- [ ] Identificar metodo, payload e headers minimos.
- [ ] Testar classes/assuntos/siglas como catalogos.
- [ ] Criar parser JSON offline.
