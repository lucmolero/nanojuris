# Route Mapping Playbook

Este playbook orienta a descoberta rapida de rotas publicas viaveis para novos
providers de jurisprudencia. O objetivo nao e raspar qualquer pagina: e encontrar
contratos publicos, auditaveis e juridicamente uteis.

## Principio operacional

Uma rota so deve avancar para provider quando retornar conteudo juridico real em
sessao HTTP limpa, sem cookies exportados do navegador, captcha, login, token
privado, segredo de justica ou contorno de controle de acesso.

O fluxo recomendado e:

1. Encontrar a pagina oficial de jurisprudencia.
2. Fazer uma busca manual simples no navegador.
3. Usar Network/HAR apenas para entender endpoints, metodos e parametros.
4. Reproduzir a rota com `nanojuris probe-rota`.
5. Classificar a rota por score.
6. Criar ficha de contrato em `docs/source-contracts/`.
7. Salvar fixture offline sanitizada.
8. Implementar parser offline.
9. Implementar provider com diagnostics e testes.

## Comando padrao

```bash
nanojuris probe-rota "https://tribunal.exemplo.jus.br/jurisprudencia?q=idpj" \
  --expect "IDPJ" \
  --expect "Ementa"
```

Para rotas POST com formulario:

```bash
nanojuris probe-rota "https://tribunal.exemplo.jus.br/search" \
  --metodo POST \
  --data "q=idpj" \
  --data "pagina=1" \
  --expect "Relator"
```

Para API JSON:

```bash
nanojuris probe-rota "https://api.tribunal.exemplo.jus.br/jurisprudencia" \
  --metodo POST \
  --json "{\"q\":\"idpj\",\"page\":1}" \
  --expect "ementa"
```

`--json` aceita objeto ou array JSON. Para endpoints de metadados que recebem
lista de tribunais, por exemplo, o payload pode ser:

```json
["TSE"]
```

Em PowerShell ou payloads maiores, prefira arquivo JSON para evitar problemas de
escape e preservar aspas internas:

```bash
nanojuris probe-rota "https://api.tribunal.exemplo.jus.br/jurisprudencia" \
  --metodo POST \
  --json-file payload.json \
  --expect "totalRegistros"
```

## Bateria de termos

`idpj` e apenas um smoke test civil/empresarial. O mapeamento serio deve usar
uma bateria por ramo, porque algumas fontes ranqueiam melhor ou validam payloads
com termos mais naturais ao acervo.

| Ramo/fonte | Termos iniciais |
| --- | --- |
| TJs estaduais | `dano moral`, `plano de saude`, `inventario`, `idpj`, `execucao fiscal` |
| TST/TRTs | `horas extras`, `justa causa`, `equiparacao salarial`, `adicional de insalubridade` |
| TRFs/TNU | `aposentadoria`, `beneficio previdenciario`, `execucao fiscal`, `mandado de seguranca` |
| STJ/STF | `repetitivo`, `repercussao geral`, `icms`, `habeas corpus`, `recurso especial` |
| TSE/TREs | `abuso de poder`, `propaganda eleitoral`, `registro de candidatura` |
| STM/JMU | `desercao`, `insubmissao`, `habeas corpus` |

## Interpretacao do score

O probe retorna `route_status`, `score`, `quality_grade`, sinais juridicos,
sinais de acesso e uma recomendacao.

| Grade | Significado | Acao |
| --- | --- | --- |
| A | Rota forte, com conteudo juridico e bons sinais tecnicos | criar contrato e fixture |
| B | Rota promissora, mas precisa aprofundar paginacao/campos | pesquisar mais antes do provider |
| C | Rota fraca ou incompleta | registrar, mas nao priorizar |
| D | Bloqueada, indisponivel ou sem valor juridico suficiente | descartar ou revisitar depois |

Status principais:

- `live_valid`: rota retornou conteudo juridico real sem bloqueio.
- `candidate`: resposta limpa, mas ainda sem evidencia juridica suficiente.
- `access_control_or_login`: ha captcha, login, antirrobo, sessao ou WAF.
- `not_found`: rota candidata nao existe no formato testado.
- `source_unavailable`: fonte indisponivel, recusada ou com erro HTTP/rede.

## Sinais de rota boa

Priorizar rotas que retornem:

- JSON, XML ou HTML sem estado fragil;
- numero CNJ, classe, assunto, relator, orgao julgador e datas;
- ementa, tese, sumula, tema, precedente ou decisao;
- paginacao clara;
- link publico de inteiro teor;
- comportamento repetivel com `requests` limpo.

## Sinais de bloqueio

Nao promover rotas que dependam de:

- captcha, reCAPTCHA, Turnstile ou antirrobo;
- login, CAS, SSO ou area autenticada;
- cookies de navegador ou token extraido de HAR;
- segredo de justica;
- rota que apenas ecoa formulario sem resultado juridico.

## Priorizacao nacional

Ordem recomendada para mapear proximas rotas:

| Prioridade | Alvo | Motivo |
| --- | --- | --- |
| P0 | TST | alto valor pratico e lacuna nacional trabalhista |
| P0 | TRF1, TRF3, TRF5, TRF6 | completa Justica Federal junto com TRF4 |
| P0 | TJMG, TJRJ, TJRS, TJPR, TJSC | grandes acervos estaduais |
| P1 | TSE | jurisprudencia eleitoral nacional |
| P1 | TJBA, TJPE, TJGO, TJCE | volume estadual e relevancia regional |
| P1 | TREs principais | cobertura eleitoral regional |
| P2 | TJs restantes | completude nacional |
| P2 | TNU/CJF e CNJ | uniformizacao e decisao administrativa |

## Checklist de promocao

Antes de abrir PR de provider:

- `probe-rota` mostra `live_valid` ou uma justificativa tecnica clara;
- contrato documenta endpoint, metodo, payload, paginacao e campos;
- fixture offline contem conteudo publico e sanitizado;
- parser offline cobre resultado vazio, resultado valido e mudanca de contrato;
- provider declara capabilities e responsible use;
- testes nao dependem de rede por padrao;
- teste live opcional fica marcado com `pytest.mark.live`;
- mensagens de erro separam indisponibilidade, captcha/login e parser quebrado.
