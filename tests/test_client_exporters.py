from __future__ import annotations

import pytest

from nanojuris.client import NanoJurisClient
from nanojuris.errors import UnsupportedProviderError
from nanojuris.exporters import search_page_to_markdown, to_jsonl
from nanojuris.models import (
    DecisionBundle,
    JurisprudenceQuery,
    JurisprudenceResult,
    ParadigmCase,
    ProviderCatalog,
    ProviderOption,
    SearchPage,
    SourceTrace,
)
from nanojuris.providers.base import JurisprudenceProvider


class FakeProvider:
    name = "fake"

    def __init__(self):
        self.query = None

    def search(self, query: JurisprudenceQuery) -> SearchPage:
        self.query = query
        return SearchPage(
            source="fake",
            total=1,
            start=1,
            end=1,
            page=query.page,
            page_size=query.page_size,
            results=[
                JurisprudenceResult(
                    id="fake-1",
                    source="fake",
                    court="STF",
                    type="RG",
                    number=1,
                    question="Questao",
                    thesis="Tese",
                )
            ],
        )

    def get_decisions(self, precedent_id: str) -> DecisionBundle:
        return DecisionBundle(precedent_id=precedent_id, source="fake")

    def get_parameters(self):
        return {"ok": True}

    def get_catalog(self):
        return ProviderCatalog(
            source="fake",
            courts=[ProviderOption(code="STF", description="Supremo Tribunal Federal")],
            species=[ProviderOption(code="RG", description="Tema de Repercussao Geral")],
        )

    def list_suggestions(self, text):
        return [text, f"{text} sugestao"]


def test_client_builds_query_for_provider():
    provider = FakeProvider()
    client = NanoJurisClient(providers=[provider])

    page = client.search("ICMS", source="fake", courts=["STF"], types=["RG"], page=3, page_size=7)

    assert page.total == 1
    assert provider.query is not None
    assert provider.query.text == "ICMS"
    assert provider.query.courts == ["STF"]
    assert provider.query.types == ["RG"]
    assert provider.query.page == 3
    assert provider.query.page_size == 7


def test_client_delegates_decisions_and_parameters():
    provider = FakeProvider()
    client = NanoJurisClient(providers=[provider])

    assert client.get_decisions("fake-1", source="fake").precedent_id == "fake-1"
    assert client.get_parameters(source="fake") == {"ok": True}
    assert client.get_catalog(source="fake").courts[0].code == "STF"
    assert client.list_suggestions("icms", source="fake") == ["icms", "icms sugestao"]


def test_client_rejects_unknown_provider():
    client = NanoJurisClient(providers=[FakeProvider()])

    with pytest.raises(UnsupportedProviderError):
        client.search("ICMS", source="missing")


def test_exporters_render_results():
    provider = FakeProvider()
    page = provider.search(JurisprudenceQuery(text="ICMS"))

    jsonl = to_jsonl(page)
    markdown = search_page_to_markdown(page)

    assert '"id": "fake-1"' in jsonl
    assert "# Resultados NanoJuris" in markdown
    assert "### Tese" in markdown


def test_markdown_renders_all_optional_sections():
    page = SearchPage(
        source="fake",
        total=1,
        start=1,
        end=1,
        page=1,
        page_size=1,
        results=[
            JurisprudenceResult(
                id="fake-2",
                source="fake",
                court="STJ",
                type="RR",
                number=2,
                question="Questao completa",
                thesis="Tese completa",
                summary="Resumo completo",
                status="Vigente",
                rapporteur="Ministro Exemplo",
                updated_at="01/01/2026",
                paradigm_cases=[
                    ParadigmCase(
                        number="123",
                        case_class="REsp",
                        url="https://example.test",
                    )
                ],
                source_trace=SourceTrace(provider="fake", endpoint="/fake"),
            )
        ],
    )

    rendered = search_page_to_markdown(page)

    assert "Ministro Exemplo" in rendered
    assert "### Resumo" in rendered
    assert "Processos paradigma" in rendered
    assert "Provider: `fake`" in rendered


def test_model_to_dict_methods():
    trace = SourceTrace(provider="fake", endpoint="/fake")
    case = ParadigmCase(number="123")
    result = JurisprudenceResult(id="r1", source="fake", court="STF", type="RG")
    page = SearchPage(source="fake", total=0, start=0, end=0, page=1, page_size=10, results=[])
    bundle = DecisionBundle(precedent_id="r1", source="fake")
    option = ProviderOption(code="STF", description="Supremo Tribunal Federal")
    catalog = ProviderCatalog(source="fake", courts=[option])

    assert trace.to_dict()["provider"] == "fake"
    assert case.to_dict()["number"] == "123"
    assert result.to_dict()["id"] == "r1"
    assert page.to_dict()["source"] == "fake"
    assert bundle.to_dict()["precedent_id"] == "r1"
    assert option.to_dict()["code"] == "STF"
    assert catalog.to_dict()["courts"][0]["code"] == "STF"


def test_base_provider_default_parameters():
    class MinimalProvider(JurisprudenceProvider):
        name = "minimal"

        def search(self, query):
            raise NotImplementedError

        def get_decisions(self, precedent_id):
            raise NotImplementedError

    assert MinimalProvider().get_parameters() == {}
