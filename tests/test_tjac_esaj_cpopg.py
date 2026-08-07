from __future__ import annotations

import pytest
import requests

from nanojuris.canonical import search_page_to_canonical
from nanojuris.errors import ParserContractChangedError
from nanojuris.models import JurisprudenceQuery
from nanojuris.providers.tjac_esaj_cpopg import TjacEsajCpopgProvider

PROCESS_NUMBER = "0001970-91.2024.8.01.0001"

PROCESS_HTML = f"""
<html><body>
  <h1 id="numeroProcesso">{PROCESS_NUMBER}</h1>
  <span id="labelSituacaoProcesso">Arquivado</span>
  <div id="classeProcesso">Recurso em Sentido Estrito</div>
  <div id="assuntoProcesso">Homicídio Simples</div>
  <div id="foroProcesso">Foro Rio Branco</div>
  <div id="varaProcesso">1ª Vara do Tribunal do Júri</div>
  <div id="dataHoraDistribuicaoProcesso">Recebido em 25/03/2024 às 21:03</div>
  <div id="numeroControleProcesso">2023/000103</div>
  <div id="areaProcesso">Criminal</div>
  <div class="nomeParteEAdvogado">Recorrente Justiça Pública</div>
  <div class="nomeParteEAdvogado">Recorrido João de Souza</div>
  <table id="tabelaTodasMovimentacoes">
    <tr class="containerMovimentacao">
      <td class="dataMovimentacao">25/03/2024</td>
      <td class="descricaoMovimentacao">Recebido o recurso em sentido estrito</td>
    </tr>
  </table>
</body></html>
"""


class FakeResponse:
    def __init__(
        self,
        text: str,
        status_code: int = 200,
        url: str = "https://esaj.tjac.jus.br/cpopg/show.do",
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


def test_tjac_esaj_cpopg_search_by_case_number_returns_case_document():
    session = FakeSession([FakeResponse(PROCESS_HTML)])
    provider = TjacEsajCpopgProvider(session=session)

    page = provider.search(JurisprudenceQuery(number=PROCESS_NUMBER))

    assert page.source == "tjac_esaj_cpopg"
    assert page.results[0].number == PROCESS_NUMBER
    assert page.results[0].raw["case_class"] == "Recurso em Sentido Estrito"
    assert page.results[0].raw["origin_county"] == "Foro Rio Branco"
    assert page.results[0].raw["last_movement_date"] == "25/03/2024"
    call = session.calls[0]
    assert call["url"] == "https://esaj.tjac.jus.br/cpopg/search.do"
    assert call["kwargs"]["params"]["foroNumeroUnificado"] == "0001"


def test_tjac_esaj_cpopg_get_document_uses_tjac_source_identity():
    provider = TjacEsajCpopgProvider(session=FakeSession([FakeResponse(PROCESS_HTML)]))

    document = provider.get_document(f"tjac-esaj-cpopg-{PROCESS_NUMBER}")

    assert document.id == f"tjac-esaj-cpopg-{PROCESS_NUMBER}"
    assert document.source == "tjac_esaj_cpopg"
    assert document.raw_metadata["case_number"] == PROCESS_NUMBER
    assert document.extraction_trace.parser == "tjac_esaj_cpopg.parse_esaj_cpopg_document"


def test_tjac_esaj_cpopg_canonicalizes_case_lookup_result():
    provider = TjacEsajCpopgProvider(session=FakeSession([FakeResponse(PROCESS_HTML)]))

    records = search_page_to_canonical(provider.search(JurisprudenceQuery(number=PROCESS_NUMBER)))

    assert records[0].source == "tjac_esaj_cpopg"
    assert records[0].court == "TJAC"
    assert records[0].case_number == PROCESS_NUMBER
    assert records[0].case_class == "Recurso em Sentido Estrito"


def test_tjac_esaj_cpopg_rejects_missing_process_number():
    provider = TjacEsajCpopgProvider(session=FakeSession([]))

    with pytest.raises(ParserContractChangedError):
        provider.search(JurisprudenceQuery())


def test_tjac_esaj_cpopg_request_exception_becomes_source_error():
    provider = TjacEsajCpopgProvider(session=FakeSession([requests.RequestException("offline")]))

    with pytest.raises(Exception, match="TJAC/e-SAJ CPOPg request failed"):
        provider.search(JurisprudenceQuery(number=PROCESS_NUMBER))


def test_tjac_esaj_cpopg_capabilities_describe_case_lookup():
    provider = TjacEsajCpopgProvider(session=FakeSession([]))

    capabilities = provider.get_capabilities()

    assert capabilities.source == "tjac_esaj_cpopg"
    assert capabilities.category == "case_lookup"
    assert capabilities.search_modes == ["case_number"]
    assert "GET /cpopg/search.do" in capabilities.endpoints
