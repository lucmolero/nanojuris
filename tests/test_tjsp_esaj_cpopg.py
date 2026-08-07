from __future__ import annotations

from pathlib import Path

import pytest
import requests

from nanojuris.canonical import search_page_to_canonical
from nanojuris.errors import AccessControlRequiredError, ParserContractChangedError
from nanojuris.models import JurisprudenceQuery, SourceTrace
from nanojuris.providers.tjsp_esaj_cpopg import (
    TjspEsajCpopgProvider,
    parse_esaj_cpopg_document,
    parse_esaj_cpopg_list,
)

FIXTURES = Path(__file__).parent / "fixtures"
PROCESS_NUMBER = "0003938-14.2017.8.26.0323"


class FakeResponse:
    def __init__(
        self,
        text: str,
        status_code: int = 200,
        url: str = "https://esaj.tjsp.jus.br/cpopg/show.do",
    ):
        self.text = text
        self.status_code = status_code
        self.encoding = "utf-8"
        self.url = url


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
    return (FIXTURES / "tjsp_esaj_cpopg_process.html").read_text(encoding="utf-8")


def _list_fixture_html() -> str:
    return (FIXTURES / "tjsp_esaj_cpopg_list.html").read_text(encoding="utf-8")


def test_parse_esaj_cpopg_document_maps_fixture():
    trace = SourceTrace(
        provider="tjsp_esaj_cpopg",
        endpoint="/cpopg/search.do",
        source_url="https://esaj.tjsp.jus.br/cpopg/show.do",
    )

    document = parse_esaj_cpopg_document(
        _fixture_html(),
        process_number=PROCESS_NUMBER,
        trace=trace,
        source_url=trace.source_url,
    )

    assert document.id == f"tjsp-esaj-cpopg-{PROCESS_NUMBER}"
    assert document.source == "tjsp_esaj_cpopg"
    assert document.document_type == "processo_1g"
    assert document.raw_metadata["case_number"] == PROCESS_NUMBER
    assert document.raw_metadata["case_class"] == "Acao Penal - Procedimento Ordinario"
    assert document.raw_metadata["subject"] == "Homicidio Simples"
    assert document.raw_metadata["origin_county"] == "Foro de Lorena"
    assert document.raw_metadata["court_unit"] == "Vara Criminal"
    assert document.raw_metadata["last_movement_date"] == "09/12/2025"
    assert document.raw_metadata["parties"] == [
        {"role": "Autor", "name": "Justica Publica", "text": "Autor Justica Publica"},
        {
            "role": "Reu",
            "name": "ANDERSON DE AZEVEDO GONCALVES",
            "text": "Reu ANDERSON DE AZEVEDO GONCALVES",
        },
    ]
    assert document.raw_metadata["movements"] == [
        {
            "date": "09/12/2025",
            "description": "Remetidos os Autos para o Tribunal de Justiça",
        }
    ]
    assert document.sha256 is not None


def test_parse_esaj_cpopg_list_maps_public_result_items():
    trace = SourceTrace(
        provider="tjsp_esaj_cpopg",
        endpoint="/cpopg/search.do",
        source_url="https://esaj.tjsp.jus.br/cpopg/search.do",
    )

    results = parse_esaj_cpopg_list(
        _list_fixture_html(),
        trace=trace,
        source_url=trace.source_url,
        page=1,
        page_size=1,
        search_mode="NMPARTE",
        search_value="ANDERSON DE AZEVEDO GONCALVES",
    )

    assert len(results) == 1
    result = results[0]
    assert result.id == "tjsp-esaj-cpopg-0000067-29.2024.8.26.0323"
    assert result.number == "0000067-29.2024.8.26.0323"
    assert result.summary == (
        "0000067-29.2024.8.26.0323 - Exectdo - ANDERSON DE AZEVEDO GONCALVES - "
        "Execução da Pena - Pena Privativa de Liberdade"
    )
    assert result.raw["search_mode"] == "NMPARTE"
    assert result.raw["result_role"] == "Exectdo"
    assert result.raw["received_date"] == "17/01/2024"


def test_provider_search_builds_esaj_query_and_returns_result():
    session = FakeSession([FakeResponse(_fixture_html())])
    provider = TjspEsajCpopgProvider(session=session)

    page = provider.search(JurisprudenceQuery(number=PROCESS_NUMBER))

    assert page.source == "tjsp_esaj_cpopg"
    assert page.total == 1
    assert page.results[0].number == PROCESS_NUMBER
    assert page.results[0].type == "processo"
    assert page.results[0].raw["case_class"] == "Acao Penal - Procedimento Ordinario"
    call = session.calls[0]
    assert call["method"] == "GET"
    assert call["url"] == "https://esaj.tjsp.jus.br/cpopg/search.do"
    params = call["kwargs"]["params"]
    assert params["cbPesquisa"] == "NUMPROC"
    assert params["numeroDigitoAnoUnificado"] == "0003938-14.2017"
    assert params["foroNumeroUnificado"] == "0323"
    assert params["dadosConsulta.valorConsultaNuUnificado"] == PROCESS_NUMBER


def test_provider_search_by_party_name_returns_process_list():
    session = FakeSession([FakeResponse(_list_fixture_html())])
    provider = TjspEsajCpopgProvider(session=session)

    page = provider.search(
        JurisprudenceQuery(party_name="ANDERSON DE AZEVEDO GONCALVES", page_size=2)
    )

    assert page.source == "tjsp_esaj_cpopg"
    assert page.total == 2
    assert page.results[0].number == "0000067-29.2024.8.26.0323"
    assert page.results[1].number == PROCESS_NUMBER
    params = session.calls[0]["kwargs"]["params"]
    assert params["cbPesquisa"] == "NMPARTE"
    assert params["dadosConsulta.valorConsulta"] == "ANDERSON DE AZEVEDO GONCALVES"


def test_provider_prefers_explicit_filter_over_text_fallback():
    session = FakeSession([FakeResponse(_list_fixture_html())])
    provider = TjspEsajCpopgProvider(session=session)

    provider.search(JurisprudenceQuery(text="ignorar como parte", oab="123456", page_size=2))

    params = session.calls[0]["kwargs"]["params"]
    assert params["cbPesquisa"] == "NUMOAB"
    assert params["dadosConsulta.valorConsulta"] == "123456"


def test_provider_get_document_accepts_id_with_embedded_process_number():
    session = FakeSession([FakeResponse(_fixture_html())])
    provider = TjspEsajCpopgProvider(session=session)

    document = provider.get_document(f"tjsp-esaj-cpopg-{PROCESS_NUMBER}")

    assert document.raw_metadata["case_number"] == PROCESS_NUMBER


def test_esaj_search_page_canonicalizes_as_decision_like_record():
    session = FakeSession([FakeResponse(_fixture_html())])
    provider = TjspEsajCpopgProvider(session=session)

    records = search_page_to_canonical(provider.search(JurisprudenceQuery(number=PROCESS_NUMBER)))

    assert len(records) == 1
    assert records[0].source == "tjsp_esaj_cpopg"
    assert records[0].court == "TJSP"
    assert records[0].case_number == PROCESS_NUMBER
    assert records[0].case_class == "Acao Penal - Procedimento Ordinario"
    assert records[0].subject == "Homicidio Simples"


def test_provider_detects_access_control_without_bypass():
    session = FakeSession([FakeResponse("<html>Cloudflare Turnstile captcha</html>")])
    provider = TjspEsajCpopgProvider(session=session)

    with pytest.raises(AccessControlRequiredError):
        provider.search(JurisprudenceQuery(number=PROCESS_NUMBER))


def test_provider_rejects_missing_process_number():
    provider = TjspEsajCpopgProvider(session=FakeSession([]))

    with pytest.raises(ParserContractChangedError):
        provider.search(JurisprudenceQuery())


def test_request_exception_becomes_source_error():
    provider = TjspEsajCpopgProvider(session=FakeSession([requests.RequestException("offline")]))

    with pytest.raises(Exception, match="TJSP/e-SAJ CPOPg request failed"):
        provider.search(JurisprudenceQuery(number=PROCESS_NUMBER))


def test_provider_capabilities_describe_case_lookup():
    provider = TjspEsajCpopgProvider(session=FakeSession([]))

    capabilities = provider.get_capabilities()

    assert capabilities.source == "tjsp_esaj_cpopg"
    assert capabilities.category == "case_lookup"
    assert "case_number" in capabilities.search_modes
    assert "party_name" in capabilities.search_modes
    assert "oab" in capabilities.search_modes
    assert "GET /cpopg/search.do" in capabilities.endpoints
