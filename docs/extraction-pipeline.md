# Extraction Pipeline

NanoJuris separa a extracao em contratos reutilizaveis para que cada fonte
nacional possa evoluir sem duplicar regras de aquisicao, parsing, traces e
normalizacao.

Essa camada e objetiva: ela captura conteudo, metadados e campos estruturados.
Ela nao interpreta merito juridico.

## Camadas

```text
FetchRequest
  Descreve uma requisicao publica: fonte, URL, endpoint, metodo, payload e
  limitacoes conhecidas.

HttpFetcher
  Executa a aquisicao responsavel usando timeout, user-agent e sessao HTTP.

FetchedContent
  Preserva bytes brutos, texto decodificado, hash, tamanho, status de acesso e
  SourceTrace.

ParsedContent
  Representa o resultado intermediario do parser antes do modelo canonico.

CanonicalDecision / CanonicalPrecedent / CanonicalDocument
  Normalizam a saida para advogados, pesquisadores, analistas e agentes de IA.
```

## Uso basico

```python
from nanojuris import FetchRequest, HttpFetcher

fetcher = HttpFetcher()
content = fetcher.fetch(
    FetchRequest(
        source="example",
        url="https://example.test/jurisprudencia",
        endpoint="/jurisprudencia",
        query={"text": "icms"},
    )
)

print(content.access_status)
print(content.sha256)
print(content.source_trace.to_dict() if content.source_trace else None)
```

## Resultado de parser

```python
from nanojuris.extraction import parsed_content
from nanojuris.models import AccessStatus, ExtractionStatus

parsed = parsed_content(
    source="example",
    parser="example.html_parser",
    parser_version="1",
    records=[{"case_number": "0000000-00.0000.0.00.0000"}],
    status=ExtractionStatus.COMPLETE,
    access_status=AccessStatus.PUBLIC,
)
```

## Status de acesso

O `HttpFetcher` mapeia status HTTP para `AccessStatus` de forma conservadora:

- `200..299`: `public`
- `300..399`: `partial`
- `401` ou `403`: `login_required`
- `404`: `not_found`
- `429` ou `5xx`: `source_unavailable`

Providers especificos ainda podem refinar esse status quando detectarem captcha,
pagina de validacao ou outro controle de acesso.

## Regra de engenharia

Novos providers devem preferir esta ordem:

1. declarar `ProviderCapabilities`;
2. adquirir conteudo com `FetchRequest`/`HttpFetcher` ou fetcher especializado;
3. emitir `FetchedContent`;
4. transformar em `ParsedContent`;
5. mapear para modelos canonicos;
6. preservar traces em todas as etapas.
