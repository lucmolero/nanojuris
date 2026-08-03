# Source Capabilities

NanoJuris declara capacidades por fonte para que advogados, pesquisadores,
pipelines e agentes de IA saibam exatamente o que cada provider cobre antes de
executar consultas.

Essa camada e deliberadamente objetiva: ela descreve busca, formatos, campos,
status de acesso e limites. Ela nao interpreta merito juridico.

Para priorizacao nacional por familia de sistema e tribunal, veja
[provider-coverage-map.md](provider-coverage-map.md).

## Por que existe

Um projeto nacional e escalavel precisa responder perguntas operacionais sem
exigir leitura do codigo:

- Quais fontes estao registradas?
- Quais tribunais brasileiros existem no catalogo da lib?
- Que tipo de documento cada fonte retorna?
- Quais campos sao extraidos?
- Ha inteiro teor publico?
- O provider implementa `get_document` sem depender de bypass?
- A fonte pode exigir captcha ou login?
- Que endpoint ou rota publica sustenta a extracao?
- A fonte e adequada para CLI, lote ou MCP?

## Uso via Python

```python
from nanojuris import NanoJurisClient

client = NanoJurisClient()

for source in client.list_sources():
    print(source.source, source.display_name)
    print(source.document_types)
    print(source.extracted_fields)
```

Detalhar uma fonte:

```python
capabilities = client.get_capabilities(source="tjsp_cjsg")
print(capabilities.to_dict())
```

Listar tribunais brasileiros conhecidos por ramo, UF, familia tecnica ou status
de provider:

```python
from nanojuris import list_courts

for court in list_courts(branch="state", state="SP"):
    print(court.code, court.name, court.provider_status)
```

## Uso via CLI

Listar todas as fontes:

```bash
nanojuris fontes
nanojuris tribunais --implementados
```

Detalhar uma fonte:

```bash
nanojuris fontes --fonte tjsp_cjsg
```

Diagnostico de capacidades e limites:

```bash
nanojuris diagnostico --fonte bnp_pangea
```

## Campos declarados

Cada provider retorna um `ProviderCapabilities` com:

- `source`: identificador interno do provider;
- `display_name`: nome legivel da fonte;
- `source_url`: URL base publica;
- `category`: categoria da fonte;
- `search_modes`: modos de busca suportados;
- `document_types`: tipos de documento cobertos;
- `content_formats`: formatos de origem;
- `canonical_records`: modelos canonicos gerados;
- `extracted_fields`: campos objetivos extraidos;
- `access_statuses`: status de acesso possiveis;
- `endpoints`: endpoints ou rotas publicas usadas;
- `supports_full_text`: se ha tentativa de obter inteiro teor publico;
- `supports_catalog`: se a fonte expoe catalogo/parametros;
- `supports_suggestions`: se a fonte expoe sugestoes;
- `supports_live_tests`: se ha teste live opcional;
- `supports_mcp`: se a fonte deve ser exposta no MCP;
- `limitations`: limitacoes tecnicas conhecidas;
- `responsible_use`: cuidados de uso responsavel.

## Fontes atuais

### `bnp_pangea`

Categoria: precedentes qualificados.

Cobertura objetiva:

- texto, tribunal, especie, numero e periodo;
- precedentes, teses, questoes, status e processos paradigma;
- catalogo publico de orgaos e especies;
- sugestoes quando o endpoint publico estiver disponivel.

### `comunica_pje`

Categoria: comunicacoes judiciais publicas.

Cobertura objetiva:

- busca textual em comunicacoes do Comunica PJe/DJEN;
- filtro por tribunal via `siglaTribunal`;
- busca por numero de processo via `numeroProcesso` sem mascara;
- filtro por data de disponibilizacao via `dataDisponibilizacaoInicio` e
    `dataDisponibilizacaoFim`;
- tipo de comunicacao/documento, orgao, classe, texto, data de disponibilizacao,
  numero do processo e link publico;
- canonicalizacao como `CanonicalDecision` por compatibilidade operacional,
  preservando `type="comunicacao"` para diferenciar de acordaos.

Estado atual: provider implementado com fixture offline e busca live reproduzida
em sessao limpa para `infanticidio`, `TJSP`, `STJ`, numero de processo e filtro
por data de disponibilizacao.

### `tjdf_juris`

Categoria: jurisprudencia de tribunal.

Cobertura objetiva:

- busca textual no TJDFT/SISTJ por HTML publico;
- fluxo em duas etapas: pagina de contagem, pagina de resultados e detalhe por
    `numeroDoDocumento`;
- acordao, numero CNJ, numero de registro, relator, orgao julgador, data de
    julgamento, data de publicacao/intimacao, ementa e resultado do julgamento;
- canonicalizacao para `CanonicalDecision` e detalhe HTML via `get_document`;
- rota validada em sessao HTTP limpa, sem captcha ou login no fluxo testado.

Estado atual: provider implementado com fixture offline e rota live reproduzida
para `infanticidio` durante a descoberta baseada nos scripts CourtsBR.

### `tjms_cjsg`

Categoria: jurisprudencia de tribunal.

Cobertura objetiva:

- busca textual no TJMS/CJSG por HTML publico;
- reaproveitamento do contrato CJSG/e-SAJ ja usado em `tjsp_cjsg`;
- acordao, numero do processo, classe, assunto, comarca, relator, orgao julgador,
    data de julgamento/publicacao, ementa e URL de inteiro teor;
- canonicalizacao para `CanonicalDecision`;
- rota validada em sessao HTTP limpa para `infanticidio`, com 22 resultados
    observados.

Estado atual: provider implementado com fixture offline reaproveitando o contrato
CJSG e smoke live reproduzido durante pesquisa de projetos abertos no GitHub.

### `tjsp_cjsg`

Categoria: jurisprudencia de tribunal.

Cobertura objetiva:

- busca por inteiro teor, ementa, numero e periodo;
- acordaos, monocraticas e homologacoes quando retornados pela fonte;
- classe, assunto, relator, comarca, orgao julgador, data e URL de inteiro teor;
- diagnostico de retorno ao formulario, campos `recaptcha_response_token`,
  `uuidCaptcha`, rota `captchaControleAcesso`, scripts de login e containers de
  resultado;
- deteccao de captcha/controle de acesso sem bypass.

### `tjsp_esaj_cpopg`

Categoria: consulta processual publica.

Cobertura objetiva:

- consulta de processo de primeiro grau por numero CNJ;
- busca de lista por nome da parte (`NMPARTE`) e OAB (`NUMOAB`) reproduzida com
    sessao HTTP limpa;
- modos de formulario mapeados para documento da parte (`DOCPARTE`), advogado
    (`NMADVOGADO`), precatoria (`PRECATORIA`), documento de delegacia (`DOCDELEG`)
    e CDA (`NUMCDA`), sujeitos a variacao de acesso da fonte;
- redirect oficial `search.do` para `show.do` quando a fonte encontra o caso;
- classe, assunto, foro, vara, juiz, distribuicao, controle, area, partes e
        movimentacoes em texto publico;
- partes e movimentacoes estruturadas quando o HTML publico contem seletores
    estaveis;
- resultados de lista com numero CNJ, papel, nome da parte, classe, assunto,
    data de recebimento, vara e URL publica;
- normalizacao para `CanonicalDocument` e resumo em `JurisprudenceResult`;
- deteccao de captcha, multiplas consultas simultaneas e controle de acesso sem
    bypass.

Estado atual: provider expandido para detalhe por numero CNJ e listas CPOPg.
Smoke live reproduzido para `NMPARTE` com 4 resultados e `NUMOAB` com 2
resultados durante a descoberta.

### `stj_scon`

Categoria: jurisprudencia de tribunal superior.

Cobertura objetiva inicial:

- acordaos publicos do STJ/SCON por HTML;
- classe processual, numero, registro, relator, orgao julgador, datas, ementa e
    URL de documento quando disponivel;
- parser offline com fixture sanitizada;
- canonicalizacao para `CanonicalDecision`;
- deteccao de captcha/controle de acesso sem bypass.

Estado atual: implementacao inicial. A busca live deve ser tratada como opt-in e
validada por fixture antes de expandir inteiro teor.
