# Initial Public Release Checklist

Este checklist prepara o NanoJuris para uma versao inicial publica. Ele deve ser
executado antes de tag, changelog final e publicacao do repositorio.

## Principios de release

- O core e extraction-first.
- Dependencias opcionais nao podem quebrar import basico.
- Testes live ficam desligados por padrao.
- Fontes instaveis devem ser documentadas como instaveis.
- Docs devem distinguir implementado, parcial e planejado.
- Nenhum exemplo deve exigir segredo, login ou bypass.

## Gate tecnico local

Executar:

```powershell
git diff --check
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src tests examples
.\.venv\Scripts\python.exe -c "import nanojuris; print(nanojuris.__version__)"
.\.venv\Scripts\python.exe -c "import nanojuris.mcp_tools, nanojuris.mcp_server; print('mcp imports ok')"
.\.venv\Scripts\python.exe examples\sdk_workflow.py
.\.venv\Scripts\python.exe -m pytest tests\test_mcp_tools.py -q
.\.venv\Scripts\python.exe -m pytest tests\test_store.py tests\test_cli.py -q
```

Resultado esperado:

- diff sem problemas de whitespace;
- testes offline passando;
- lint sem erros;
- import do core funcionando;
- import MCP funcionando sem iniciar servidor;
- exemplo SDK executando sem rede.
- tools MCP, incluindo store local, passando em testes offline.
- deduplicacao canonica e CLI de store passando em testes offline.
- buscas salvas por `ResearchRun` passando em SDK, CLI e MCP.
- exportacao de `ResearchRun` passando em CLI e MCP.
- paginacao de `ResearchRun` passando em store, CLI e MCP.
- `get_document` passando em provider, client, CLI e MCP offline.
- catalogo brasileiro de tribunais passando em API, CLI e MCP.

## Gate CLI

Executar:

```powershell
.\.venv\Scripts\python.exe -m nanojuris.cli fontes
.\.venv\Scripts\python.exe -m nanojuris.cli diagnostico --fonte bnp_pangea
.\.venv\Scripts\python.exe -m nanojuris.cli diagnostico --fonte tjsp_cjsg
.\.venv\Scripts\python.exe -m nanojuris.cli store --help
```

Resultado esperado:

- fontes aparecem com `ProviderCapabilities`;
- diagnostico declara limites e uso responsavel;
- TJSP/CJSG informa possibilidade de controle de acesso;
- grupo `store` lista `stats`, `query` e `get`.

## Gate de documentacao

Confirmar que estes documentos existem e estao atualizados:

- [../README.md](../README.md);
- [quickstart.md](quickstart.md);
- [architecture.md](architecture.md);
- [providers.md](providers.md);
- [source-capabilities.md](source-capabilities.md);
- [extraction-pipeline.md](extraction-pipeline.md);
- [storage.md](storage.md);
- [mcp.md](mcp.md);
- [use-case-validation-matrix.md](use-case-validation-matrix.md);
- [provider-development.md](provider-development.md);
- [release-checklist.md](release-checklist.md).

## Gate de escopo juridico

Antes de publicar, revisar:

- README nao promete aconselhamento juridico;
- docs nao falam em tese recomendada ou estrategia processual;
- exemplos mostram extracao e auditoria, nao interpretacao;
- fontes com captcha/login sao tratadas como limite;
- fixtures nao incluem dados sensiveis desnecessarios.

## Gate de empacotamento

Confirmar:

- `pyproject.toml` tem metadata minima;
- `nanojuris` CLI funciona como script;
- `nanojuris-mcp` fica no extra opcional;
- core instala sem MCP;
- `README.md`, `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md` e
  `CODE_OF_CONDUCT.md` existem.

## Gate de status publico

Antes da versao inicial, marcar explicitamente:

- providers implementados;
- providers planejados;
- recursos implementados;
- recursos parciais;
- recursos fora do escopo;
- limitacoes de fontes publicas;
- como rodar live tests opt-in.

## Criterio de pronto para release inicial

A release inicial pode ser publicada quando:

- todos os gates locais passam;
- README aponta para quickstart e uso responsavel;
- matriz de casos de uso tem relatorio atualizado;
- CLI basica funciona;
- store local tem comandos de consulta;
- MCP minimo esta documentado;
- backlog de lacunas esta transparente.
