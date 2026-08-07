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

Rotas declaradas:

```text
POST /resultadoCompleta.do
GET /getArquivo.do?cdAcordao=<id>&cdForo=<foro>
```

Payload principal da busca:

```text
dados.buscaInteiroTeor=<texto livre>
dados.buscaEmenta=<trecho exato quando informado>
dados.nuProcOrigem=<numero CNJ quando informado>
dados.dtJulgamentoInicio=<data inicial>
dados.dtJulgamentoFim=<data final>
tipoDecisaoSelecionados=<A|M|H>
dados.ordenarPor=dtPublicacao
```

Mapeamento de tipo decisorio:

| Entrada | Codigo enviado |
| --- | --- |
| `A`, `acordao` | `A` |
| `M`, `monocratica` | `M` |
| `H`, `homologacao` | `H` |

Campos extraidos:

- numero do processo;
- tipo decisorio;
- classe/assunto;
- comarca;
- orgao julgador;
- relator;
- data de registro/publicacao;
- ementa/resumo;
- `cd_acordao`;
- `cd_foro`;
- URL publica de inteiro teor quando disponivel.

## Diagnostico de acesso

O provider classifica sinais do HTML sem resolver nenhum controle:

| Sinal | Campo tecnico |
| --- | --- |
| Container de resultado | `has_result_container` |
| Links de ementa/arquivo | `has_download_links` |
| Formulario de busca retornado | `has_search_form` |
| Campo reCAPTCHA | `has_recaptcha_field` |
| Campo uuidCaptcha | `has_uuid_captcha_field` |
| Widget reCAPTCHA | `has_recaptcha_widget` |
| Rota de controle de acesso | `has_access_control_route` |
| Script de login/SAJ | `has_login_script` |

Se houver sinais de captcha/controle sem container de resultado, o provider
levanta `AccessControlRequiredError`.

## Estados de resposta

| Estado | Como o provider deve tratar |
| --- | --- |
| Resultado publico | Retornar `SearchPage` com metadados e URL de inteiro teor. |
| Zero resultado | Retornar pagina vazia quando a fonte indicar resultado sem itens. |
| Captcha/controle | Levantar `AccessControlRequiredError` com flags diagnosticas. |
| HTTP 429 | Levantar `RateLimitDetectedError`. |
| HTTP 5xx | Levantar `SourceUnavailableError`. |
| HTML com total mas sem itens | Levantar `ParserContractChangedError`. |

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
- pagina de zero resultado;
- inteiro teor publico;

## Proximos passos

- [x] Criar fixture especifica para `diagnose_cjsg_access`.
- [x] Criar fixture de zero resultado.
- [ ] Criar fixture de inteiro teor publico com hash e tamanho.
- [ ] Documentar variacoes de `classe/assunto` por area.
- [ ] Promover dossie da familia CJSG/e-SAJ para ser reutilizado por TJAC,
  TJAL, TJAM e TJMS.
