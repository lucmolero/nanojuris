# Source Contracts

NanoJuris trata cada provider como um contrato tecnico auditavel. O objetivo nao
e apenas "fazer a busca funcionar", mas saber com clareza:

- quais rotas publicas sustentam a extracao;
- quais parametros sao aceitos;
- quais campos sao estaveis;
- quais respostas representam sucesso, vazio, bloqueio ou erro;
- quais fontes sao adequadas para agentes de IA;
- quais lacunas ainda impedem uso profissional em escala.

## Uso rapido

Via CLI:

```bash
nanojuris contratos
nanojuris contratos --fonte tjdf_juris
nanojuris contratos --resumo
```

Via Python:

```python
from nanojuris import NanoJurisClient

client = NanoJurisClient()

for contract in client.list_source_contracts():
    print(contract.source, contract.contract_level, contract.risk_level)
    print(contract.gaps)
```

Via MCP, use a tool `source_contracts` para agentes inspecionarem maturidade,
lacunas e proximos passos antes de consultar fontes reais.

## Niveis de maturidade

| Nivel | Label | Criterio pratico |
| --- | --- | --- |
| 1 | `busca_basica` | Provider inicial ou contrato ainda pouco conhecido. |
| 2 | `parser_com_fixtures` | Parser coberto por fixtures representativas. |
| 3 | `contrato_http_documentado` | Rotas, parametros, erros e limites com dossie tecnico. |
| 4 | `campos_canonicos_estaveis` | Campos canonicos, traces e documentos testados. |
| 5 | `erros_e_vazios_mapeados` | Sucesso, vazio, bloqueio e falhas sao separados. |
| 6 | `pronto_para_agentes` | Fonte pronta para fluxos MCP/IA com roteamento e limites claros. |

## Metodo de aprofundamento

Para cada provider superficial, siga este fluxo:

1. Abra a fonte oficial em navegador limpo.
2. Grave um HAR com uma busca publica simples.
3. Identifique rotas, metodos, parametros e payloads.
4. Reproduza a chamada com `requests` usando headers minimos.
5. Salve fixtures publicas para sucesso, vazio e erro esperado.
6. Documente campos obrigatorios, opcionais e ausentes.
7. Adicione testes de parser, erro, vazio e acesso restrito.
8. Atualize `ProviderCapabilities`.
9. Atualize ou crie o dossie em `docs/source-contracts/`.
10. Rode `nanojuris contratos --fonte <provider>` e ataque as lacunas restantes.

## O que nao fazer

- Nao contornar captcha, login, segredo de justica ou controle de acesso.
- Nao usar cookies pessoais ou sessoes autenticadas como contrato publico.
- Nao misturar comunicacoes judiciais, consulta processual e jurisprudencia
  decisoria como se fossem a mesma coisa.
- Nao tratar zero resultado como erro sem evidencias.
- Nao tratar controle de acesso esperado como quebra de parser.

## Template de dossie

Cada dossie especifico deve seguir esta estrutura:

```text
# <provider>

## Identidade
- Fonte oficial:
- Categoria:
- Familia tecnica:
- URL inicial:
- Status de acesso:

## Contrato HTTP
- Rotas:
- Metodos:
- Parametros obrigatorios:
- Parametros opcionais:
- Paginacao:
- Ordenacao:
- Filtros:

## Dados retornados
- Campos extraidos:
- Campos canonicos:
- Campos opcionais:
- Campos instaveis:
- Inteiro teor:
- Documentos vinculados:

## Comportamento observado
- Busca com resultado:
- Busca sem resultado:
- Erro HTTP esperado:
- Controle de acesso/captcha:
- Mudanca de layout:

## Fixtures
- Sucesso:
- Vazio:
- Erro:
- Documento:

## MCP e agentes
- Quando usar:
- Quando pular:
- Mensagem segura para o usuario:
- Riscos:

## Proximos passos
- [ ] ...
```

## Prioridade atual

Use `needs_deepening` do resumo como fila tecnica. Em geral, priorize:

1. Fontes com alto valor juridico e risco alto, como `tjsp_cjsg` e `stj_scon`.
2. Fontes boas para demonstracao e jurimetria, como `tjdf_juris` e `trf4_eproc_jurisprudencia`.
3. Familias reutilizaveis, como CJSG/e-SAJ e eproc.
4. Fontes especializadas, como NUGEP-NAC, TCE-SP, TRE-SP e Comunica PJe.
