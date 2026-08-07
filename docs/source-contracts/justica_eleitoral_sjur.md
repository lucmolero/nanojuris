# justica_eleitoral_sjur

## Identidade
- Fonte oficial: SJUR/TSE e agregador SJUR/TREs.
- Categoria: `court_jurisprudence`.
- Familia tecnica: `justica_eleitoral_sjur`.
- URL inicial TSE: `https://jurisprudencia.tse.jus.br/`.
- URL inicial TREs: `https://jurisprudencia-tres.tse.jus.br/`.
- Status de acesso: metadados publicos validados; busca principal bloqueada por antirrobo no probe limpo de 2026-08-07.

## Contrato HTTP
- Host API observado: `https://sjur-pesquisa-api.tse.jus.br/{tribunal}/sjur-pesquisa-backend/rest/public/pesquisa`.
- Valores observados de `{tribunal}`:
  - `tse`;
  - `tres`.
- Rotas auxiliares observadas:
  - `POST /classes`
  - `POST /relatorias`
  - `POST /eleicoes`
  - `POST /normas`
  - `POST /download/`
  - `POST /pesquisaTokenValidado`
  - `POST /livre`
  - `POST /simples`
  - `POST /rede`
- Payload de metadados TSE:

```json
["TSE"]
```

- Payload de metadados TRE-SP:

```json
["TRE-SP"]
```

## Dados retornados
- `POST /classes`: classes processuais eleitorais, como `RESPE`, `AI`, `REspEl` e `AREspEl`.
- `POST /relatorias`: lista de relatores.
- Campos canonicos possiveis: catalogo auxiliar de filtros, nao `CanonicalDecision` nesta fase.
- Busca de decisoes: pendente; `POST /public/pesquisa` retornou mensagem de falha antirrobo com lista vazia.

## Comportamento observado
- Metadados TSE: HTTP 200, JSON publico.
- Metadados TRE-SP: HTTP 200, JSON publico.
- Busca principal com payload minimalista: HTTP 200, JSON com `mensagem` de falha antirrobo, `content=[]`, `totalRegistros=0`.
- Rotas `/livre` e `/rede` nao foram promovidas: retornaram 404 ou nao apresentaram contrato suficiente no payload testado.

## Decisao
- Promover apenas como contrato parcial P1.
- Nao implementar provider de decisoes enquanto a rota exigir antirrobo, token ou validacao humana.
- Usar o contrato atual para descoberta de filtros eleitorais e para orientar pesquisa futura com HAR/DevTools.

## MCP e agentes
- Quando usar: explicar quais filtros/classes eleitorais a fonte declara publicamente.
- Quando pular: perguntas que exigem acordaos, ementas ou inteiro teor do TSE/TREs.
- Mensagem segura para o usuario: "A API publica expõe metadados eleitorais, mas a busca de decisoes retornou controle antirrobo em sessao limpa."

## Proximos passos
- [ ] Coletar HAR sanitizado de uma busca manual autorizada para entender payload exato.
- [ ] Verificar se existe endpoint documentado de busca sem token.
- [ ] Criar fixture de `classes` e `relatorias`.
- [ ] Adicionar testes de diagnostico para `anti_robot`.
