# `tre_sp_temas`

## Identidade

- Fonte oficial: Temas Selecionados do TRE-SP.
- Categoria: `electoral_jurisprudence`.
- Familia tecnica: `catalogo_tematico_eleitoral`.
- URL inicial: `https://www.tre-sp.jus.br/jurisprudencia/temas-selecionados-1`.
- Status de acesso: publico parcial.
- Status no NanoJuris: provider implementado.

## Contrato HTTP

- Rotas conhecidas:
  - `GET /jurisprudencia/temas-selecionados-1`
  - `GET /jurisprudencia/arquivos-da-secao-de-jurisprudencia-sp/temas-selecionados/<slug>`
- Metodos: `GET`.
- Modos de busca: texto e catalogo tematico.
- Paginacao: nao caracterizada como busca geral.

## Dados retornados

- Campos extraidos:
  - tema;
  - resumo;
  - decisoes selecionadas;
  - links de documentos.
- Campos canonicos: `CanonicalPrecedent`.
- Inteiro teor: nao declarado; links podem apontar para sistemas externos.

## Comportamento observado

- Fonte tematica publica.
- Nao e busca geral de acordaos eleitorais.
- Links de inteiro teor dependem de sistemas eleitorais externos.

## Fixtures

- [ ] Indice de temas.
- [ ] Pagina de tema.
- [ ] Tema sem decisoes.
- [ ] Link externo indisponivel.

## MCP e agentes

- Quando usar: curadoria tematica eleitoral paulista.
- Quando pular: estatistica de acordaos eleitorais ou busca nacional.
- Mensagem segura: "Esta fonte e uma curadoria tematica do TRE-SP, nao a base
  completa de jurisprudencia eleitoral."
- Riscos: extrapolar decisoes selecionadas como tendencia estatistica.

## Proximos passos

- [ ] Completar dossie com casos reais publicos.
- [ ] Criar fixtures de indice e detalhe.
- [ ] Documentar relacao com SJUR/TSE quando houver link externo.
