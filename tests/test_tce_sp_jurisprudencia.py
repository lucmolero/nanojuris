from __future__ import annotations

from nanojuris.canonical import search_page_to_canonical
from nanojuris.config import NanoJurisConfig
from nanojuris.models import JurisprudenceQuery, SourceTrace
from nanojuris.providers.tce_sp_jurisprudencia import (
    TceSpJurisprudenciaProvider,
    parse_tce_sp_boletins,
    parse_tce_sp_sumulas,
)

SUMULAS_HTML = """
<html><body><article>
  REPERTÓRIO DE SÚMULAS
  SÚMULA Nº 1 - Não é lícita a concessão de subvenção personalíssima.
  (Veja histórico e fundamento)
  <table><tr><td>HISTÓRICO</td><td>Aprovada pela Resolução nº 79/1971</td></tr></table>
  SÚMULA Nº 2 - É inconstitucional a aplicação de auxílios em culto religioso.
  (Veja histórico e fundamento)
  <table><tr><td>FUNDAMENTO</td><td>TC-001142-65</td></tr></table>
</article></body></html>
"""

BOLETINS_HTML = """
<html><body><article>
  <a href="/boletim-de-jurisprudencia/publicacoes/boletim-jurisprudencia-edicao-53-marco2026">
    Novo Boletim de Jurisprudência - Edição N.º 53 - Março/2026
  </a>
  <a href="/publicacoes/boletim-jurisprudencia-edicao-52-fevereiro2026">
    Boletim de Jurisprudência - Edição N.º 52 - Fevereiro/2026
  </a>
</article></body></html>
"""


class FakeResponse:
    def __init__(self, text: str, url: str, status_code: int = 200):
        self.text = text
        self.url = url
        self.status_code = status_code
        self.encoding = "utf-8"
        self.apparent_encoding = "utf-8"


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        if not self.responses:
            raise AssertionError("unexpected request")
        return self.responses.pop(0)


def test_parse_tce_sp_sumulas_extracts_statements():
    results = parse_tce_sp_sumulas(
        SUMULAS_HTML,
        source_url="https://www.tce.sp.gov.br/boletim-de-jurisprudencia/sumulas",
        trace=SourceTrace(provider="tce_sp_jurisprudencia", endpoint="/sumulas"),
    )

    assert len(results) == 2
    assert results[0].id == "tce-sp-sumula-1"
    assert results[0].type == "sumula"
    assert results[0].thesis == "Não é lícita a concessão de subvenção personalíssima."
    assert "Resolução" in (results[0].raw["history"] or "")


def test_parse_tce_sp_boletins_extracts_publication_links():
    results = parse_tce_sp_boletins(
        BOLETINS_HTML,
        source_url="https://www.tce.sp.gov.br/boletim-de-jurisprudencia/publicacoes",
        trace=SourceTrace(provider="tce_sp_jurisprudencia", endpoint="/publicacoes"),
    )

    assert len(results) == 2
    assert results[0].id == "tce-sp-boletim-53"
    assert results[0].number == 53
    assert results[0].raw["document_url"].endswith("edicao-53-marco2026")


def test_provider_search_filters_catalog_results():
    session = FakeSession(
        [
            FakeResponse(
                SUMULAS_HTML, "https://www.tce.sp.gov.br/boletim-de-jurisprudencia/sumulas"
            ),
            FakeResponse(
                BOLETINS_HTML, "https://www.tce.sp.gov.br/boletim-de-jurisprudencia/publicacoes"
            ),
        ]
    )
    provider = TceSpJurisprudenciaProvider(NanoJurisConfig(rate_limit_interval=0), session=session)

    page = provider.search(JurisprudenceQuery(text="religioso", page_size=5))

    assert page.source == "tce_sp_jurisprudencia"
    assert len(page.results) == 1
    assert page.results[0].id == "tce-sp-sumula-2"


def test_tce_sp_canonicalizes_as_precedent():
    session = FakeSession(
        [FakeResponse(SUMULAS_HTML, "https://www.tce.sp.gov.br/boletim-de-jurisprudencia/sumulas")]
    )
    provider = TceSpJurisprudenciaProvider(NanoJurisConfig(rate_limit_interval=0), session=session)

    records = search_page_to_canonical(provider.search(JurisprudenceQuery(types=["sumula"])))

    assert records[0].source == "tce_sp_jurisprudencia"
    assert records[0].precedent_type == "sumula"
    assert records[0].thesis is not None
