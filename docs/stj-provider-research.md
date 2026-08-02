# STJ provider research

Status: research-ready, implementation pending.

This note maps official STJ jurisprudence surfaces for a future `stj`
provider. The goal is to avoid coupling NanoJuris to a single fragile page
before the HTML contracts are captured with fixtures and optional live tests.

## Product scope

The STJ Carta de Servicos describes the jurisprudence search as a free,
immediate self-service for public access to collective decisions, individual
monocratic decisions, sumulas, informativo notes and also TFR decisions:

https://cartadeservicos.stj.jus.br/jurisprudencia/pesquisa-de-jurisprudencia-do-stj/

For NanoJuris, the `stj` provider should be split into modules under one
provider family:

```text
stj_scon_acordaos
  Acordaos and inteiro teor from SCON.

stj_scon_decisoes
  Decisoes monocraticas, with STJ search operators.

stj_scon_sumulas
  Sumulas anotadas, canceladas and by branch of law.

stj_scon_informativos
  Informativo de Jurisprudencia notes.

stj_precedentes_qualificados
  Repetitivos, controversias, IACs, SIRDRs and PUILs.

stj_publicacoes
  Jurisprudencia em Teses and PDF/HTML institutional compilations.
```

The first implementation should prefer `stj_scon_acordaos`, because it is the
closest to the current `JurisprudenceResult` model and the most valuable entry
point for lawyers searching case law.

## Source map

### SCON - Acordaos

Official URL:

https://processo.stj.jus.br/SCON/acordaos/

Use case:

- search published STJ acordaos;
- retrieve result metadata;
- retrieve inteiro teor when available;
- preserve the SCON public URL in `SourceTrace`.

Known public fields:

```text
Classe
Numero
Registro
criterio textual
result list
inteiro teor link
```

Implementation notes:

- Capture a HAR from the browser with one simple text query and one process
  number query before writing the parser.
- Prefer fixture-driven parsing from real sanitized HTML.
- Treat JavaScript/session parameters as volatile.
- Parse result pages defensively and keep raw source URLs in the trace.

### SCON - Decisoes monocraticas

Official help URL:

https://processo.stj.jus.br/SCON/decisoes/AjudaDTXT.jsp

Use case:

- search individual decisions published in the electronic journal;
- support STJ operators such as `E`, `OU`, `NAO`, `ADJ`, `PROX`, `MESMO` and
  radical search with `$`;
- support fielded search for process number, publication date and organ.

Contract notes:

```text
.NUM.  numero/classe do processo
.DTPB. data de publicacao in YYYYMMDD
.ORG.  orgao julgador
```

Implementation notes:

- Do not reinterpret STJ query language in NanoJuris v1. Pass the user query
  through and document the official operators.
- Normalize parsed decisions as `type="decisao_monocratica"`.
- Mark availability in docs: STJ states monocratic decisions are available
  from February 1999 onward.

### Precedentes Qualificados

Official URL:

https://processo.stj.jus.br/repetitivos/temas_repetitivos/?pesquisaAvancada=true

Use case:

- search repetitive themes, controversies, IACs, SIRDRs and PUILs;
- retrieve thesis, status, affected cases, judgment/publication dates and
  related links;
- complement the current `bnp_pangea` provider with STJ-native details.

Known public filters:

```text
free text / theme number
precedent type: Repetitivos, Controversias, IACs, SIRDRs, PUILs
theme number range
date range
process
minister
judging organ
origin court
branch of law
status
ordering
synonyms
plurals
```

Implementation notes:

- This should be a separate provider from SCON case-law search because the
  legal object is a qualified precedent, not a regular decision.
- It maps naturally to `question`, `thesis`, `status`, `paradigm_cases` and
  `updated_at`.
- Fixtures must include at least one repetitive theme, one IAC and one
  controversy when available.

### Repetitivos e IACs Anotados

Official help URL:

https://centraldeajuda.stj.jus.br/faq/o-que-sao-os-repetitivos-e-iacs-anotados/

Use case:

- organized index by branch of law, subject and theme;
- links to real-time searches for later acordaos;
- excerpts from ementas linked to the acórdão mirror.

Implementation notes:

- Good second phase after `stj_precedentes_qualificados`.
- Useful for lawyer-facing navigation and documentation examples.
- Should be represented as curated index data, not only free text search.

### Jurisprudencia em Teses, Sumulas Anotadas and Informativos

Official STJ communication page:

https://www.stj.jus.br/sites/portalp/Paginas/Comunicacao/Noticias/2019/Publicacoes-de-Repetitivos-e-IACs-Jurisprudencia-em-Teses-e-Sumulas-Anotadas-tem-novo-formato.aspx

Use case:

- extract thematic thesis publications;
- extract annotated sumulas;
- extract informativo notes and references.

Implementation notes:

- These products may be distributed as HTML pages and compiled PDFs.
- The provider should start by discovering stable links and metadata.
- PDF extraction belongs in a separate parser layer so that agents can read
  text without manual download.

## Recommended provider architecture

```text
src/nanojuris/providers/stj/
  __init__.py
  scon.py
  precedentes.py
  publications.py
  parsers.py
  models.py
```

Public provider names:

```text
stj_scon
stj_precedentes
stj_publicacoes
```

Why not one large provider:

- SCON, Precedentes and publications have different legal objects.
- They will fail in different ways and need separate live tests.
- Lawyers will understand the source better when the provider name describes
  the official surface.

## Implementation plan

1. Capture contracts.

   Save sanitized fixtures for:

   ```text
   tests/fixtures/stj_scon_acordaos_result.html
   tests/fixtures/stj_scon_acordao_detail.html
   tests/fixtures/stj_scon_decisoes_result.html
   tests/fixtures/stj_precedentes_result.html
   tests/fixtures/stj_precedentes_detail.html
   ```

2. Build parser-only tests.

   The first tests should not touch the network. They should assert ids,
   numbers, court, type, summary/thesis, dates, public URLs and source trace.

3. Implement `stj_scon` first.

   Support text search, process number search and inteiro teor retrieval.

4. Add optional live tests.

   Use explicit flags:

   ```powershell
   $env:NANOJURIS_RUN_STJ_LIVE = "1"
   python -m pytest tests/test_stj_live.py
   ```

5. Implement `stj_precedentes`.

   Focus on qualified precedents after the SCON provider is stable.

6. Add docs and examples.

   Include examples for litigation research, thesis validation and precedent
   monitoring.

## Acceptance criteria

- `JurisprudenceResult.source` clearly identifies the STJ source.
- Public URLs are preserved in `SourceTrace`.
- The parser works from sanitized fixtures.
- Network errors, 403/429 and layout misses raise typed NanoJuris errors.
- Optional live tests can pass or explicitly skip/mark source control changes.
- Docs explain official STJ operators without inventing a parallel query
  language.

## Open questions

- Which SCON endpoint shape is most stable after HAR capture?
- Does STJ expose a stable export endpoint for SCON results?
- Are PDF publications text-based, scanned or mixed?
- Should `stj_publicacoes` return `JurisprudenceResult` or a new
  `PublicationResult` model in a later version?
