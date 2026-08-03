from __future__ import annotations

import json
from pathlib import Path

import pytest
import requests

from nanojuris.canonical import search_page_to_canonical
from nanojuris.config import NanoJurisConfig
from nanojuris.errors import (
    ParserContractChangedError,
    RateLimitDetectedError,
    SourceUnavailableError,
)
from nanojuris.models import CanonicalDecision, JurisprudenceQuery
from nanojuris.providers.comunica_pje import ComunicaPjeProvider

FIXTURES = Path(__file__).parent / "fixtures"


class FakeResponse:
    def __init__(self, payload, status_code: int = 200):
        self.payload = payload
        self.status_code = status_code

    def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, "kwargs": kwargs})
        if not self.responses:
            raise AssertionError("unexpected request")
        return self.responses.pop(0)


class RaisingSession:
    def request(self, method, url, **kwargs):
        raise requests.RequestException("offline")


def load_fixture(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_search_maps_comunica_pje_response():
    session = FakeSession([FakeResponse(load_fixture("comunica_pje_infanticidio.json"))])
    provider = ComunicaPjeProvider(NanoJurisConfig(rate_limit_interval=0), session=session)

    page = provider.search(
        JurisprudenceQuery(text="infanticídio", courts=["tjsp"], page=1, page_size=1)
    )

    assert page.source == "comunica_pje"
    assert page.total == 1260
    assert page.start == 1
    assert page.end == 1
    assert len(page.results) == 1
    result = page.results[0]
    assert result.id == "comunica-pje-684466035"
    assert result.source == "comunica_pje"
    assert result.court == "TJSP"
    assert result.type == "comunicacao"
    assert result.number == "1500780-26.2025.8.26.0603"
    assert "Infanticídio" in (result.summary or "")
    assert result.updated_at == "2026-07-31"
    assert result.raw["communication_type"] == "Intimação"
    assert result.raw["case_class"] == "INQUÉRITO POLICIAL"
    assert result.raw["origin_county"] == "Foro de Araçatuba - 2ª Vara Criminal"
    assert result.source_trace is not None
    assert result.source_trace.source_url == "https://www.dje.tjsp.jus.br"

    call = session.calls[0]
    assert call["method"] == "GET"
    assert call["url"].endswith("/api/v1/comunicacao")
    assert call["kwargs"]["params"] == {
        "pagina": 0,
        "size": 1,
        "texto": "infanticídio",
        "siglaTribunal": "TJSP",
    }


def test_search_by_number_uses_numero_processo_parameter():
    session = FakeSession([FakeResponse(load_fixture("comunica_pje_infanticidio.json"))])
    provider = ComunicaPjeProvider(NanoJurisConfig(rate_limit_interval=0), session=session)

    provider.search(JurisprudenceQuery(number="1500780-26.2025.8.26.0603", page_size=5))

    assert session.calls[0]["kwargs"]["params"]["numeroProcesso"] == "15007802620258260603"
    assert "numero_processo" not in session.calls[0]["kwargs"]["params"]


def test_search_filters_by_publication_date_range():
    session = FakeSession([FakeResponse(load_fixture("comunica_pje_infanticidio.json"))])
    provider = ComunicaPjeProvider(NanoJurisConfig(rate_limit_interval=0), session=session)

    provider.search(
        JurisprudenceQuery(
            text="infanticidio",
            published_from="2026-07-31",
            published_to="2026-07-31",
            page_size=5,
        )
    )

    params = session.calls[0]["kwargs"]["params"]
    assert params["dataDisponibilizacaoInicio"] == "2026-07-31"
    assert params["dataDisponibilizacaoFim"] == "2026-07-31"


def test_search_page_maps_to_canonical_decision():
    session = FakeSession([FakeResponse(load_fixture("comunica_pje_infanticidio.json"))])
    provider = ComunicaPjeProvider(NanoJurisConfig(rate_limit_interval=0), session=session)

    page = provider.search(JurisprudenceQuery(text="infanticidio", page_size=1))
    records = search_page_to_canonical(page)

    assert len(records) == 1
    record = records[0]
    assert isinstance(record, CanonicalDecision)
    assert record.source == "comunica_pje"
    assert record.court == "TJSP"
    assert record.case_number == "1500780-26.2025.8.26.0603"
    assert record.decision_type == "comunicacao"
    assert record.case_class == "INQUÉRITO POLICIAL"
    assert record.origin_county == "Foro de Araçatuba - 2ª Vara Criminal"
    assert record.publication_date == "2026-07-31"
    assert record.document_url == "https://www.dje.tjsp.jus.br"


def test_get_capabilities_describes_communications_source():
    provider = ComunicaPjeProvider(NanoJurisConfig(rate_limit_interval=0), session=FakeSession([]))

    capabilities = provider.get_capabilities()

    assert capabilities.source == "comunica_pje"
    assert capabilities.category == "judicial_communications"
    assert "case_number" in capabilities.search_modes
    assert "comunicacao" in capabilities.document_types


@pytest.mark.parametrize(
    ("response", "expected_error"),
    [
        (FakeResponse({}, 200), ParserContractChangedError),
        (FakeResponse(ValueError("not json"), 200), ParserContractChangedError),
        (FakeResponse({"items": []}, 429), RateLimitDetectedError),
        (FakeResponse({"items": []}, 500), SourceUnavailableError),
        (FakeResponse({"items": []}, 400), SourceUnavailableError),
    ],
)
def test_search_errors_are_normalized(response, expected_error):
    provider = ComunicaPjeProvider(
        NanoJurisConfig(rate_limit_interval=0), session=FakeSession([response])
    )

    with pytest.raises(expected_error):
        provider.search(JurisprudenceQuery(text="infanticidio"))


def test_request_exception_is_normalized():
    provider = ComunicaPjeProvider(NanoJurisConfig(rate_limit_interval=0), session=RaisingSession())

    with pytest.raises(SourceUnavailableError, match="offline"):
        provider.search(JurisprudenceQuery(text="infanticidio"))
