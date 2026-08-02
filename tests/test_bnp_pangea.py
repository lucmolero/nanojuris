from __future__ import annotations

import pytest
import requests

from nanojuris.config import NanoJurisConfig
from nanojuris.errors import (
    ParserContractChangedError,
    RateLimitDetectedError,
    SourceUnavailableError,
)
from nanojuris.models import JurisprudenceQuery
from nanojuris.providers.bnp_pangea import BnpPangeaProvider


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


def test_search_maps_bnp_response():
    session = FakeSession(
        [
            FakeResponse(
                {
                    "total": 1,
                    "posicao_inicial": 1,
                    "posicao_final": 1,
                    "aggsEspecies": [{"tipo": "RG", "total": 1}],
                    "aggsOrgaos": [{"tipo": "STF", "total": 1}],
                    "resultados": [
                        {
                            "id": "stf-rg-615",
                            "orgao": "STF",
                            "tipo": "RG",
                            "nr": 615,
                            "questao": "Questao publica",
                            "tese": "Tese publica",
                            "situacao": "Vigente",
                            "ultimaAtualizacao": "20/06/2024",
                            "highlight": {"tese": "<mark>Tese</mark> publica"},
                            "processosParadigma": [
                                {
                                    "numero": "680089",
                                    "classe": 1348,
                                    "link": "https://portal.stf.jus.br/processos/detalhe.asp",
                                }
                            ],
                        }
                    ],
                }
            )
        ]
    )
    provider = BnpPangeaProvider(NanoJurisConfig(), session=session)

    page = provider.search(
        JurisprudenceQuery(
            text="ICMS",
            courts=["STF"],
            types=["RG"],
            page=2,
            page_size=5,
        )
    )

    assert page.total == 1
    assert page.start == 1
    assert page.end == 1
    assert page.aggregations["species"][0]["tipo"] == "RG"
    assert page.results[0].id == "stf-rg-615"
    assert page.results[0].court == "STF"
    assert page.results[0].type == "RG"
    assert page.results[0].number == 615
    assert page.results[0].paradigm_cases[0].number == "680089"
    assert page.results[0].source_trace is not None

    call = session.calls[0]
    assert call["method"] == "POST"
    assert call["url"].endswith("/precedentes")
    assert call["kwargs"]["json"]["filtro"]["buscaGeral"] == "ICMS"
    assert call["kwargs"]["json"]["filtro"]["orgaos"] == ["STF"]
    assert call["kwargs"]["json"]["filtro"]["tipos"] == ["RG"]


def test_get_decisions_maps_response():
    session = FakeSession(
        [
            FakeResponse(
                {
                    "relator": "MIN. EXEMPLO",
                    "linkAcompanhamentoProcesssual": "https://example.test/processo",
                    "textos": [{"tipo": "Acordao", "texto": "Conteudo"}],
                }
            )
        ]
    )
    provider = BnpPangeaProvider(session=session)

    bundle = provider.get_decisions("stf-rg-615")

    assert bundle.precedent_id == "stf-rg-615"
    assert bundle.rapporteur == "MIN. EXEMPLO"
    assert bundle.procedural_follow_url == "https://example.test/processo"
    assert bundle.texts[0]["tipo"] == "Acordao"
    assert session.calls[0]["url"].endswith("/precedentes/stf-rg-615/decisoes")


def test_get_parameters_returns_dict():
    session = FakeSession([FakeResponse({"orgaos": [], "especies": []})])
    provider = BnpPangeaProvider(session=session)

    assert provider.get_parameters() == {"orgaos": [], "especies": []}


def test_list_suggestions_maps_response():
    session = FakeSession([FakeResponse(["icms", "icms consumidor final"])])
    provider = BnpPangeaProvider(session=session)

    assert provider.list_suggestions("ic") == ["icms", "icms consumidor final"]
    assert session.calls[0]["kwargs"]["params"] == {"texto": "ic"}


def test_list_suggestions_rejects_invalid_contract():
    session = FakeSession([FakeResponse({"items": []})])
    provider = BnpPangeaProvider(session=session)

    with pytest.raises(ParserContractChangedError):
        provider.list_suggestions("ic")


def test_search_rejects_invalid_contract():
    session = FakeSession([FakeResponse({"total": 1})])
    provider = BnpPangeaProvider(session=session)

    with pytest.raises(ParserContractChangedError):
        provider.search(JurisprudenceQuery(text="ICMS"))


def test_search_rejects_result_without_id():
    session = FakeSession(
        [
            FakeResponse(
                {
                    "total": 1,
                    "posicao_inicial": 1,
                    "posicao_final": 1,
                    "resultados": [{"orgao": "STF", "tipo": "RG"}],
                }
            )
        ]
    )
    provider = BnpPangeaProvider(session=session)

    with pytest.raises(ParserContractChangedError):
        provider.search(JurisprudenceQuery(text="ICMS"))


def test_get_decisions_rejects_invalid_contract():
    session = FakeSession([FakeResponse([])])
    provider = BnpPangeaProvider(session=session)

    with pytest.raises(ParserContractChangedError):
        provider.get_decisions("stf-rg-615")


def test_invalid_json_becomes_parser_error():
    session = FakeSession([FakeResponse(ValueError("bad json"))])
    provider = BnpPangeaProvider(session=session)

    with pytest.raises(ParserContractChangedError):
        provider.get_parameters()


def test_http_429_becomes_rate_limit_error():
    session = FakeSession([FakeResponse({}, status_code=429)])
    provider = BnpPangeaProvider(session=session)

    with pytest.raises(RateLimitDetectedError):
        provider.get_parameters()


def test_http_500_becomes_source_unavailable():
    session = FakeSession([FakeResponse({}, status_code=500)])
    provider = BnpPangeaProvider(session=session)

    with pytest.raises(SourceUnavailableError):
        provider.get_parameters()


def test_http_400_becomes_source_unavailable():
    session = FakeSession([FakeResponse({}, status_code=400)])
    provider = BnpPangeaProvider(session=session)

    with pytest.raises(SourceUnavailableError):
        provider.get_parameters()


def test_request_exception_becomes_source_unavailable():
    provider = BnpPangeaProvider(session=RaisingSession())

    with pytest.raises(SourceUnavailableError):
        provider.get_parameters()
