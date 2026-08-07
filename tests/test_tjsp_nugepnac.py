from __future__ import annotations

from nanojuris.canonical import search_page_to_canonical
from nanojuris.config import NanoJurisConfig
from nanojuris.models import JurisprudenceQuery, SourceTrace
from nanojuris.providers.tjsp_nugepnac import (
    TjspNugepnacProvider,
    parse_nugepnac_detail,
    parse_nugepnac_list,
)

LIST_HTML = """
<html><body>
  <a href="/NugepNac/Irdr/DetalheTema?codigoNoticia=50879&amp;pagina=1">
    Tema 001 - IRDR - Cobranca - Diferenca - FGC (TRANSITO EM JULGADO)
  </a>
</body></html>
"""

DETAIL_HTML = """
<html><body>
  <article>
    <article>Tema 001 - IRDR - Cobranca - Diferenca - FGC (TRANSITO EM JULGADO)</article>
    <p>Processo Paradigma: IRDR nº 2059683-75.2016.8.26.0000</p>
    <p>Assunto : DIREITO DO CONSUMIDOR - Contratos de Consumo - Bancarios</p>
    <p>Órgão Julgador : Turma Especial - Privado 2</p>
    <p>Relator(a): Desembargador RICARDO PESSOA DE MELLO BELLI</p>
    <p>Data de Admissão: 08/06/2016</p>
    <p>Data de Julgamento do Mérito: 28/03/2017</p>
    <p>Data de Publicação do Acórdão de Mérito : 14/09/2017</p>
    <p>Suspensão: CESSADA - TRANSITO EM JULGADO EM 05/04/2024</p>
    <p>Questão submetida a julgamento: Discussao sobre limite maximo da garantia.</p>
    <p>Tese firmada: Incidente de resolucao de demandas repetitivas. Inadmissibilidade.</p>
    <a href="https://esaj.tjsp.jus.br/cjsg/getArquivo.do?cdAcordao=9531760&amp;cdForo=0">
      Acórdão de Admissibilidade
    </a>
  </article>
</body></html>
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


def test_parse_nugepnac_list_extracts_detail_links():
    links = parse_nugepnac_list(
        LIST_HTML,
        source_url="https://www.tjsp.jus.br/NugepNac/Irdr",
        precedent_type="irdr",
    )

    assert len(links) == 1
    assert links[0].precedent_type == "irdr"
    assert links[0].detail_path == "/NugepNac/Irdr/DetalheTema?codigoNoticia=50879&pagina=1"


def test_parse_nugepnac_detail_maps_precedent_fields():
    result = parse_nugepnac_detail(
        DETAIL_HTML,
        source_url="https://www.tjsp.jus.br/NugepNac/Irdr/DetalheTema?codigoNoticia=50879&pagina=1",
        precedent_type="irdr",
        trace=SourceTrace(provider="tjsp_nugepnac", endpoint="/NugepNac/Irdr"),
    )

    assert result.id == "tjsp-nugepnac-irdr-50879"
    assert result.type == "irdr"
    assert result.number == 1
    assert result.status == "TRANSITO EM JULGADO"
    assert result.paradigm_cases[0].number == "2059683-75.2016.8.26.0000"
    assert result.rapporteur == "Desembargador RICARDO PESSOA DE MELLO BELLI"
    assert result.question == "Discussao sobre limite maximo da garantia."
    assert result.thesis.startswith("Incidente de resolucao")
    assert result.raw["judging_body"] == "Turma Especial - Privado 2"


def test_provider_search_fetches_list_and_detail():
    session = FakeSession(
        [
            FakeResponse(LIST_HTML, "https://www.tjsp.jus.br/NugepNac/Irdr"),
            FakeResponse(
                DETAIL_HTML,
                "https://www.tjsp.jus.br/NugepNac/Irdr/DetalheTema?codigoNoticia=50879&pagina=1",
            ),
        ]
    )
    provider = TjspNugepnacProvider(NanoJurisConfig(rate_limit_interval=0), session=session)

    page = provider.search(JurisprudenceQuery(text="garantia", types=["irdr"], page_size=1))

    assert page.source == "tjsp_nugepnac"
    assert page.results[0].id == "tjsp-nugepnac-irdr-50879"
    assert session.calls[0]["url"].endswith("/NugepNac/Irdr")
    assert "codigoNoticia=50879" in session.calls[1]["url"]


def test_nugepnac_canonicalizes_as_precedent():
    session = FakeSession(
        [
            FakeResponse(LIST_HTML, "https://www.tjsp.jus.br/NugepNac/Irdr"),
            FakeResponse(
                DETAIL_HTML,
                "https://www.tjsp.jus.br/NugepNac/Irdr/DetalheTema?codigoNoticia=50879&pagina=1",
            ),
        ]
    )
    provider = TjspNugepnacProvider(NanoJurisConfig(rate_limit_interval=0), session=session)

    records = search_page_to_canonical(
        provider.search(JurisprudenceQuery(text="garantia", types=["irdr"], page_size=1))
    )

    assert records[0].source == "tjsp_nugepnac"
    assert records[0].precedent_type == "irdr"
    assert records[0].thesis is not None
