from __future__ import annotations

from pathlib import Path

import pytest
import requests

from nanojuris.client import NanoJurisClient
from nanojuris.errors import (
    AccessControlRequiredError,
    ParserContractChangedError,
    RateLimitDetectedError,
)
from nanojuris.models import JurisprudenceQuery, SourceTrace
from nanojuris.providers.stj_informativo import (
    StjInformativoProvider,
    parse_stj_informativo_results,
)

FIXTURES = Path(__file__).parent / "fixtures"


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code
        self.encoding = "utf-8"


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append({"url": url, "kwargs": kwargs})
        if not self.responses:
            raise AssertionError("unexpected request")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def _fixture_html() -> str:
    return (FIXTURES / "stj_informativo_infanticidio.html").read_text(encoding="utf-8")


def test_parse_stj_informativo_results_maps_fixture():
    page = parse_stj_informativo_results(
        _fixture_html(),
        query=JurisprudenceQuery(text="infanticídio", page_size=5),
        trace=SourceTrace(provider="stj_informativo", endpoint="GET informativo"),
        base_url="https://processo.stj.jus.br",
    )

    assert page.source == "stj_informativo"
    assert page.total == 1
    first = page.results[0]
    assert first.id == "stj-informativo-507-hc-228-998-mg"
    assert first.court == "STJ"
    assert first.type == "informativo"
    assert first.number == "HC 228.998-MG"
    assert first.rapporteur == "Marco Aurélio Bellizze"
    assert first.updated_at == "23/10/2012"
    assert first.raw["informativo"] == "507"
    assert first.raw["period"] == "18 a 31 de outubro de 2012"
    assert first.raw["orgao_julgador"] == "Quinta Turma"
    assert first.raw["document_url"].endswith("livre=HC+228998")
    assert "não há crime de aborto" in first.summary


def test_parse_stj_informativo_results_filters_by_case_number():
    page = parse_stj_informativo_results(
        _fixture_html(),
        query=JurisprudenceQuery(number="HC 228.998", page_size=5),
        trace=SourceTrace(provider="stj_informativo", endpoint="GET informativo"),
        base_url="https://processo.stj.jus.br",
    )

    assert page.total == 1
    assert page.results[0].number == "HC 228.998-MG"


def test_provider_search_gets_public_informativo_route():
    session = FakeSession([FakeResponse(_fixture_html())])
    provider = StjInformativoProvider(session=session)

    page = provider.search(JurisprudenceQuery(text="infanticidio", page_size=2))

    assert page.results[0].number == "HC 228.998-MG"
    call = session.calls[0]
    assert call["url"] == "https://processo.stj.jus.br/jurisprudencia/externo/informativo/"
    assert call["kwargs"]["params"]["livre"] == "infanticidio"
    assert call["kwargs"]["params"]["b"] == "INFJ"


def test_provider_capabilities_describe_stj_informativo_contract():
    capabilities = StjInformativoProvider(session=FakeSession([])).get_capabilities()

    assert capabilities.source == "stj_informativo"
    assert capabilities.category == "court_jurisprudence"
    assert capabilities.content_formats == ["html"]
    assert capabilities.endpoints == ["GET /jurisprudencia/externo/informativo/"]
    assert "summary" in capabilities.extracted_fields


def test_provider_get_decisions_reports_note_scope():
    bundle = StjInformativoProvider(session=FakeSession([])).get_decisions("stj-informativo-1")

    assert bundle.source == "stj_informativo"
    assert bundle.texts == []
    assert "public note text" in bundle.raw["message"]


def test_client_registers_stj_informativo_by_default():
    client = NanoJurisClient()

    sources = {capability.source for capability in client.list_sources()}
    assert "stj_informativo" in sources


def test_parse_stj_informativo_accepts_empty_result_page():
    html = "<html><body><p>Nenhum item encontrado.</p></body></html>"

    page = parse_stj_informativo_results(
        html,
        query=JurisprudenceQuery(text="sem resultado"),
        trace=SourceTrace(provider="stj_informativo", endpoint="GET informativo"),
        base_url="https://processo.stj.jus.br",
    )

    assert page.total == 0
    assert page.results == []


def test_parse_stj_informativo_filters_to_empty_page():
    page = parse_stj_informativo_results(
        _fixture_html(),
        query=JurisprudenceQuery(text="tributario inexistente", page_size=5),
        trace=SourceTrace(provider="stj_informativo", endpoint="GET informativo"),
        base_url="https://processo.stj.jus.br",
    )

    assert page.total == 0
    assert page.start == 0
    assert page.results == []


def test_parse_stj_informativo_maps_live_like_title_fallback():
    html = """
    <html><body>
      <p>Notas encontradas: 1</p>
      <div class="clsInformativoBlocoItem">
        <div class="clsInformativoTextoBlocoTitulo">
          Informativo nº 507 Período: 18 a 31 de outubro de 2012.
        </div>
        QUINTA TURMA
        Informativo de Jurisprudência n. 507 - 18 a 31 de outubro de 2012.
        DIREITO PENAL. CRIME DE ABORTO. INÍCIO DO TRABALHO DE PARTO.
        HOMICÍDIO OU INFANTICÍDIO. Compartilhe:
        Iniciado o trabalho de parto, não há crime de aborto.
        <a href="/jurisprudencia/externo/informativo/?livre=@CNOT=013685">nota</a>
        HC 228.998-MG, Rel. Min. Marco Aurélio Bellizze, julgado em 23/10/2012.
      </div>
    </body></html>
    """

    page = parse_stj_informativo_results(
        html,
        query=JurisprudenceQuery(text="infanticidio", page_size=5),
        trace=SourceTrace(provider="stj_informativo", endpoint="GET informativo"),
        base_url="https://processo.stj.jus.br",
    )

    first = page.results[0]
    assert first.raw["title"].startswith("DIREITO PENAL. CRIME DE ABORTO")
    assert first.raw["document_url"].endswith("livre=@CNOT=013685")


def test_provider_detects_access_control_without_bypass():
    provider = StjInformativoProvider(
        session=FakeSession([FakeResponse("<html><div id='challenge-error-text'></div></html>")])
    )

    with pytest.raises(AccessControlRequiredError):
        provider.search(JurisprudenceQuery(text="teste"))


def test_provider_detects_access_control_with_forbidden_status():
    provider = StjInformativoProvider(
        session=FakeSession([FakeResponse("<html>captcha</html>", status_code=403)])
    )

    with pytest.raises(AccessControlRequiredError):
        provider.search(JurisprudenceQuery(text="teste"))


def test_provider_reports_rate_limit_and_http_errors():
    provider = StjInformativoProvider(session=FakeSession([FakeResponse("", status_code=429)]))
    with pytest.raises(RateLimitDetectedError):
        provider.search(JurisprudenceQuery(text="teste"))

    provider = StjInformativoProvider(session=FakeSession([FakeResponse("", status_code=503)]))
    with pytest.raises(Exception, match="HTTP 503"):
        provider.search(JurisprudenceQuery(text="teste"))

    provider = StjInformativoProvider(session=FakeSession([FakeResponse("", status_code=404)]))
    with pytest.raises(Exception, match="HTTP 404"):
        provider.search(JurisprudenceQuery(text="teste"))


def test_parser_detects_missing_contract():
    with pytest.raises(ParserContractChangedError):
        parse_stj_informativo_results(
            "<html><body>sem contrato conhecido</body></html>",
            query=JurisprudenceQuery(text="teste"),
            trace=SourceTrace(provider="stj_informativo", endpoint="GET informativo"),
            base_url="https://processo.stj.jus.br",
        )


def test_request_exception_becomes_source_error():
    provider = StjInformativoProvider(session=FakeSession([requests.RequestException("offline")]))

    with pytest.raises(Exception, match="request failed"):
        provider.search(JurisprudenceQuery(text="teste"))
