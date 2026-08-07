# `bnp_pangea`

## Identidade

- Fonte oficial: API publica usada pelo frontend Pangea/Banco Nacional de
  Precedentes.
- Categoria: `qualified_precedents`.
- Familia tecnica: `api_publica_precedentes`.
- Uso preferencial: precedentes qualificados, temas, teses e processos
  paradigma.
- Nivel atual esperado: 4.

## Contrato conhecido

O provider declara `GET /parametros`, `GET /sugestoes`, `POST /precedentes` e
`GET /precedentes/{id}/decisoes`. Retorna precedentes, especie, tribunal,
questao, tese, status, agregacoes e processos paradigma.

## Pontos fortes

- API JSON publica, sem scraping HTML no fluxo principal.
- Catalogo de orgaos e especies.
- Boa fonte para precedentes qualificados e teses nacionais.

## Lacunas a aprofundar

- Mapear rejeicoes HTTP 400 por combinacao de texto, tribunal e especie.
- Documentar payload completo de filtros e agregacoes.
- Cobrir melhor sugestoes/catalogo para consultas curtas.
- Separar claramente precedentes qualificados de jurisprudencia decisoria comum.

## MCP e agentes

Recomendacao: usar quando a pergunta envolver temas, precedentes, teses
qualificadas, repetitivos, repercussao geral, IAC ou IRDR. Para busca livre como
`idpj`, o agente deve preferir fontes de jurisprudencia decisoria antes do BNP.

## Fixtures esperadas

- catalogo de parametros;
- busca com multiplas especies;
- rejeicao HTTP 400;
- decisoes vinculadas a precedente.
