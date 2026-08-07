from __future__ import annotations

import pytest
import requests

from nanojuris.config import NanoJurisConfig
from nanojuris.errors import AccessControlRequiredError
from nanojuris.models import JurisprudenceQuery, SourceTrace
from nanojuris.providers.tjsp_eproc_jurisprudencia import parse_eproc_jurisprudencia_results
from nanojuris.providers.trf4_eproc_jurisprudencia import Trf4EprocJurisprudenciaProvider

TRF4_HTML = """
<html><body>
  <form id="frmJurisprudenciaPesquisa"></form>
  <div class="card mb-3 resultadoItem" id="resultado41785517964304066196063791796">
    <div class="bg-header-resultado">
      <a class="inteiroTeor"
        data-link="externo_controlador.php?acao=jurisprudencia@jurisprudencia/download_inteiro_teor&amp;id_jurisprudencia=41785517964304066196063791796&amp;termosPesquisados=ZGVzZXJjYW8="
        href="javascript:void(0)">article</a>
      <a class="consultaProcessual"
        data-link="http://www.trf4.jus.br/trf4/processos/acompanhamento/resultado_pesquisa.php?selForma=NU&amp;selOrigem=TRF&amp;txtValor=50378983620254040000"
        href="javascript:void(0)">find_in_page</a>
    </div>
    <div id="41785517964304066196063791796">
      <div class="card-body">
        <div class="resValueTipoJurisprudencia">Despacho/Decisão da Vice-Presidência</div>
        <div class="row">
          <div class="resLabel">PROCESSO</div>
          <div class="resValue">
            <a class="numero-processo" href="http://www.trf4.jus.br/trf4/processos/acompanhamento/resultado_pesquisa.php?selForma=NU&amp;selOrigem=TRF&amp;txtValor=50378983620254040000">5037898-36.2025.4.04.0000/TRF4</a>
            <span>AG - Agravo de Instrumento</span>
          </div>
        </div>
                <div class="row">
                    <div class="resLabel">UF</div><div class="resValue">RS</div>
                </div>
                <div class="row">
                    <div class="resLabel">ÓRGÃO JULGADOR</div>
                    <div class="resValue">VICE-PRESIDÊNCIA</div>
                </div>
                <div class="row">
                    <div class="resLabel">DATA DO JULGAMENTO</div>
                    <div class="resValue">31/07/2026</div>
                </div>
                <div class="row">
                    <div class="resLabel">DATA DA PUBLICAÇÃO</div>
                    <div class="resValue">31/07/2026</div>
                </div>
                <div class="row">
                    <div class="resLabel">RELATOR</div>
                    <div class="resValue">GUSTAVO CHIES CIGNACHI</div>
                </div>
                <div class="row">
                    <div class="resLabel">DECISÃO</div>
                    <div class="resValue limitado">Aplica-se a pena de deserção.</div>
                </div>
      </div>
    </div>
  </div>
</body></html>
"""


class FakeResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code
        self.encoding = "iso-8859-1"
        self.url = "https://jurisprudencia.trf4.jus.br/eproc2trf4/externo_controlador.php"


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


def test_parse_eproc_results_can_stamp_trf4_source_and_court():
    results = parse_eproc_jurisprudencia_results(
        TRF4_HTML,
        trace=SourceTrace(provider="trf4_eproc_jurisprudencia", endpoint="/listar"),
        source_url="https://jurisprudencia.trf4.jus.br/eproc2trf4/externo_controlador.php",
        source="trf4_eproc_jurisprudencia",
        court="TRF4",
        id_prefix="trf4-eproc-jurisprudencia",
        source_label="TRF4/eproc jurisprudence",
    )

    result = results[0]
    assert result.id == "trf4-eproc-jurisprudencia-41785517964304066196063791796"
    assert result.source == "trf4_eproc_jurisprudencia"
    assert result.court == "TRF4"
    assert result.number == "5037898-36.2025.4.04.0000"
    assert result.rapporteur == "GUSTAVO CHIES CIGNACHI"
    assert result.updated_at == "31/07/2026"
    assert result.raw["case_class"] == "AG - Agravo de Instrumento"
    assert result.raw["judging_body"] == "VICE-PRESIDÊNCIA"


def test_provider_search_posts_trf4_payload_and_parses_results():
    session = FakeSession([FakeResponse(TRF4_HTML)])
    provider = Trf4EprocJurisprudenciaProvider(
        NanoJurisConfig(rate_limit_interval=0),
        session=session,
    )

    page = provider.search(
        JurisprudenceQuery(
            text="deserção",
            number="5037898-36.2025.4.04.0000",
            page_size=5,
        )
    )

    assert page.source == "trf4_eproc_jurisprudencia"
    assert page.results[0].court == "TRF4"
    call = session.calls[0]
    assert call["method"] == "POST"
    assert call["url"].endswith(
        "externo_controlador.php?acao=jurisprudencia@jurisprudencia/listar_resultados"
    )
    assert call["kwargs"]["data"]["txtPesquisa"] == "deserção"
    assert call["kwargs"]["data"]["txtProcesso"] == "50378983620254040000"


def test_provider_get_decisions_downloads_trf4_full_text():
    session = FakeSession([FakeResponse("<html>inteiro teor trf4</html>")])
    provider = Trf4EprocJurisprudenciaProvider(
        NanoJurisConfig(rate_limit_interval=0),
        session=session,
    )

    bundle = provider.get_decisions("trf4-eproc-jurisprudencia-41785517964304066196063791796")

    assert bundle.source == "trf4_eproc_jurisprudencia"
    assert bundle.raw["id_jurisprudencia"] == "41785517964304066196063791796"
    assert session.calls[0]["kwargs"]["params"] == {
        "id_jurisprudencia": "41785517964304066196063791796"
    }


def test_provider_get_document_returns_canonical_document():
    session = FakeSession([FakeResponse("<html>inteiro teor trf4</html>")])
    provider = Trf4EprocJurisprudenciaProvider(
        NanoJurisConfig(rate_limit_interval=0),
        session=session,
    )

    document = provider.get_document("trf4-eproc-jurisprudencia-41785517964304066196063791796")

    assert document.source == "trf4_eproc_jurisprudencia"
    assert document.content_type == "text/html"
    assert document.text == "<html>inteiro teor trf4</html>"
    assert document.raw_metadata["id_jurisprudencia"] == "41785517964304066196063791796"


def test_provider_detects_access_control_without_bypass():
    provider = Trf4EprocJurisprudenciaProvider(
        NanoJurisConfig(rate_limit_interval=0),
        session=FakeSession([FakeResponse("<html><div class='g-recaptcha'></div></html>")]),
    )

    with pytest.raises(AccessControlRequiredError):
        provider.search(JurisprudenceQuery(text="teste"))


def test_request_exception_becomes_source_error():
    provider = Trf4EprocJurisprudenciaProvider(
        NanoJurisConfig(rate_limit_interval=0),
        session=FakeSession([requests.RequestException("offline")]),
    )

    with pytest.raises(Exception, match="TRF4/eproc jurisprudence request failed"):
        provider.search(JurisprudenceQuery(text="teste"))


def test_provider_capabilities_describe_trf4_contract():
    capabilities = Trf4EprocJurisprudenciaProvider(
        NanoJurisConfig(rate_limit_interval=0)
    ).get_capabilities()

    assert capabilities.source == "trf4_eproc_jurisprudencia"
    assert capabilities.source_url == "https://jurisprudencia.trf4.jus.br/eproc2trf4"
    assert capabilities.supports_full_text is True
    assert "CanonicalDocument" in capabilities.canonical_records
