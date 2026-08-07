# Uso Com Agentes De IA

NanoJuris pode ser usado por agentes locais compativeis com MCP para consultar
jurisprudencia publica brasileira com rastreabilidade. O servidor MCP roda no
ambiente do usuario e nao contorna captcha, login, segredo de justica ou
controle de acesso.

## Instalacao recomendada

Para uso local com pacote publicado:

```bash
uvx --from "nanojuris[mcp]" nanojuris-mcp
```

Para desenvolvimento a partir do repositorio:

```bash
pip install -e ".[mcp]"
nanojuris-mcp
```

Para validar a biblioteca sem MCP:

```bash
nanojuris fontes
nanojuris contratos --resumo
nanojuris contratos --fonte tjdf_juris
```

## Configuracao MCP local

Use o comando do servidor como transporte `stdio` no cliente MCP:

```json
{
  "mcpServers": {
    "nanojuris": {
      "command": "uvx",
      "args": ["--from", "nanojuris[mcp]", "nanojuris-mcp"]
    }
  }
}
```

Em ambiente de desenvolvimento local:

```json
{
  "mcpServers": {
    "nanojuris": {
      "command": "nanojuris-mcp"
    }
  }
}
```

## Ordem recomendada para o agente

Antes de consultar fontes reais, o agente deve:

1. Chamar `list_sources`.
2. Chamar `source_contracts`.
3. Escolher fontes com maturidade adequada para a pergunta.
4. Chamar `search_unified` ou `search_jurisprudence`.
5. Interpretar separadamente `searched_sources`, `skipped_sources` e `errors`.
6. Usar `get_document` ou `get_decisions` apenas quando a fonte suportar
   documento publico sem bypass.

## Perguntas naturais recomendadas

Exemplos seguros:

```text
Liste as fontes de jurisprudencia maduras para agentes.
```

```text
Busque jurisprudencia sobre IDPJ e explique quais fontes foram consultadas,
puladas ou falharam.
```

```text
Consulte source_contracts para stj_scon e diga se a fonte esta pronta para
pesquisa ampla.
```

```text
Pesquise "incidente de desconsideracao da personalidade juridica" nas fontes
mais adequadas e traga os metadados principais.
```

## Como interpretar a busca unificada

`search_unified` retorna tres grupos importantes:

| Campo | Significado |
| --- | --- |
| `searched_sources` | Fontes realmente chamadas. |
| `skipped_sources` | Fontes puladas porque nao se aplicavam a pergunta. |
| `routing_summary` | Explicacao pronta para o usuario sobre consultar, pular ou falhar. |
| `errors` | Fontes chamadas que falharam por erro real, acesso ou contrato. |

Isso evita falso diagnostico. Uma consulta textual como `idpj` nao deve chamar
fontes `case_lookup` sem numero CNJ, parte, OAB ou documento. Do mesmo modo,
uma fonte de comunicacoes judiciais nao deve ser usada como jurisprudencia
decisoria.

## Fontes boas para demonstracao

Segundo a matriz atual de contratos, as fontes mais maduras para agentes sao:

- `tjdf_juris`;
- `trf4_eproc_jurisprudencia`.

Fontes estrategicas, mas que exigem mais cuidado:

- `stj_scon`;
- `tjsp_cjsg`.

## Troubleshooting

| Sinal | Interpretacao |
| --- | --- |
| `AccessControlRequiredError` | A fonte exigiu captcha/login/validacao; nao tentar bypass. |
| `ParserContractChangedError` | O HTML mudou ou a fixture nao cobre aquele formato. |
| `SourceUnavailableError` | A fonte retornou erro HTTP ou falha de rede. |
| fonte em `skipped_sources` | A fonte nao era adequada para a pergunta. |
| `total_returned=0` sem erro | A busca executou, mas nao encontrou resultados. |

## Prompt unico para instalacao assistida

Um usuario pode pedir ao agente:

```text
Instale e configure o NanoJuris MCP localmente usando uvx. Depois rode
list_sources, source_contracts --resumo e uma busca de teste por "idpj".
Nao contorne captcha, login ou controle de acesso; apenas reporte o status das
fontes.
```

## Responsabilidade

NanoJuris extrai dados publicos e auditaveis. Ele nao substitui revisao juridica
profissional, nao interpreta merito automaticamente e nao deve ser usado para
acessar conteudo restrito.
