from __future__ import annotations

from pathlib import Path

import pytest
import requests

from nanojuris.errors import AccessControlRequiredError, ParserContractChangedError
from nanojuris.models import JurisprudenceQuery, SourceTrace
from nanojuris.providers.tjsp_cjsg import TjspCjsgProvider, parse_cjsg_results

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

    def request(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        if not self.responses:
            raise AssertionError("unexpected request")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def _fixture_html() -> str:
    return (FIXTURES / "tjsp_cjsg_result.html").read_text(encoding="utf-8")


def test_parse_cjsg_results_maps_fixture():
    trace = SourceTrace(provider="tjsp_cjsg", endpoint="/resultadoCompleta.do")

    page = parse_cjsg_results(
        _fixture_html(),
        query=JurisprudenceQuery(text="homicidio", page_size=2),
        trace=trace,
        base_url="https://esaj.tjsp.jus.br/cjsg",
    )

    assert page.source == "tjsp_cjsg"
    assert page.total == 854
    assert page.start == 1
    assert page.end == 2
    assert len(page.results) == 2
    first = page.results[0]
    assert first.id == "tjsp-cjsg-20787558-0"
    assert first.court == "TJSP"
    assert first.type == "acordao"
    assert first.number == "0003938-14.2017.8.26.0323"
    assert first.rapporteur == "Airton Vieira"
    assert first.updated_at == "30/07/2026"
    assert first.raw["classe"] == "Apelacao Criminal"
    assert first.raw["assunto"] == "Homicidio Qualificado"
    assert first.raw["comarca"] == "Lorena"
    assert first.raw["orgao_julgador"] == "3a Camara de Direito Criminal"
    assert first.raw["full_text_url"].endswith("getArquivo.do?cdAcordao=20787558&cdForo=0")


def test_provider_search_posts_cjsg_payload_and_parses_results():
    session = FakeSession([FakeResponse(_fixture_html())])
    provider = TjspCjsgProvider(session=session)

    page = provider.search(
        JurisprudenceQuery(
            text="infanticidio",
            exact_phrase="homicidio",
            number="0003938-14.2017.8.26.0323",
            types=["acordao"],
            updated_from="01/01/2026",
            updated_to="31/12/2026",
            page_size=2,
        )
    )

    assert page.results[0].id == "tjsp-cjsg-20787558-0"
    call = session.calls[0]
    payload = call["kwargs"]["data"]
    assert call["method"] == "POST"
    assert call["url"] == "https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do"
    assert payload["dados.buscaInteiroTeor"] == "infanticidio"
    assert payload["dados.buscaEmenta"] == "homicidio"
    assert payload["dados.nuProcOrigem"] == "0003938-14.2017.8.26.0323"
    assert payload["tipoDecisaoSelecionados"] == ["A"]
    assert payload["dados.dtJulgamentoInicio"] == "01/01/2026"


def test_provider_get_decisions_builds_getarquivo_url():
    session = FakeSession([FakeResponse("<html>inteiro teor publico</html>")])
    provider = TjspCjsgProvider(session=session)

    bundle = provider.get_decisions("tjsp-cjsg-20787558-0")

    assert bundle.precedent_id == "tjsp-cjsg-20787558-0"
    assert bundle.texts[0]["content"] == "<html>inteiro teor publico</html>"
    assert session.calls[0]["method"] == "GET"
    assert session.calls[0]["url"].endswith("getArquivo.do?cdAcordao=20787558&cdForo=0")


def test_provider_detects_access_control_without_bypass():
    session = FakeSession([FakeResponse("<html><div class='g-recaptcha'></div></html>")])
    provider = TjspCjsgProvider(session=session)

    with pytest.raises(AccessControlRequiredError):
        provider.search(JurisprudenceQuery(text="teste"))


def test_parser_detects_missing_result_contract():
    with pytest.raises(ParserContractChangedError):
        parse_cjsg_results(
            "<html><body>sem resultados</body></html>",
            query=JurisprudenceQuery(text="teste"),
            trace=SourceTrace(provider="tjsp_cjsg", endpoint="/resultadoCompleta.do"),
            base_url="https://esaj.tjsp.jus.br/cjsg",
        )


def test_invalid_tjsp_precedent_id_is_rejected():
    provider = TjspCjsgProvider(session=FakeSession([]))

    with pytest.raises(ParserContractChangedError):
        provider.get_decisions("bad-id")


def test_request_exception_becomes_source_error():
    provider = TjspCjsgProvider(session=FakeSession([requests.RequestException("offline")]))

    with pytest.raises(Exception, match="TJSP/CJSG request failed"):
        provider.search(JurisprudenceQuery(text="teste"))
