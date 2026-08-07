# `tjsp_cjsg`

## Identidade

- Fonte oficial: pesquisa publica de jurisprudencia CJSG/e-SAJ do TJSP.
- Categoria: `court_jurisprudence`.
- Familia tecnica: `html_esaj_cjsg`.
- Uso preferencial: jurisprudencia estadual paulista quando a fonte publica nao
  exigir controle de acesso.
- Nivel atual esperado: 3.

## Contrato conhecido

O provider cobre busca textual, ementa/resumo, numero CNJ, intervalo de data,
tipo de decisao e inteiro teor quando publico. A fonte pode exigir captcha,
validacao de acesso ou rotas de controle; o NanoJuris deve reportar isso sem
bypass.

## Pontos fortes

- Fonte juridicamente muito relevante.
- Padrao reutilizavel para a familia CJSG/e-SAJ de outros tribunais.
- Suporta documentos publicos quando a rota de inteiro teor esta acessivel.

## Lacunas a aprofundar

- Documentar criterios objetivos de captcha/access-control.
- Separar rotas de pesquisa, detalhe e inteiro teor.
- Criar fixtures por classe, orgao julgador, ementa, documento disponivel e
  documento bloqueado.
- Descrever mensagens seguras para MCP quando houver controle de acesso.

## MCP e agentes

Recomendacao: fonte de alto valor, mas risco operacional alto. O agente deve
tratar `AccessControlRequiredError` como evento esperado e sugerir outra fonte
publica quando a consulta for bloqueada.

## Fixtures esperadas

- resultado CJSG com ementa;
- pagina com captcha/access-control;
- inteiro teor publico;
- zero resultado.
