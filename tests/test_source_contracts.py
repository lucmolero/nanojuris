from __future__ import annotations

from nanojuris.client import NanoJurisClient
from nanojuris.models import ProviderCapabilities
from nanojuris.source_contracts import (
    assess_source_contract,
    contracts_payload,
    summarize_contracts,
)


def test_assess_source_contract_uses_declared_capabilities_and_overrides():
    capability = ProviderCapabilities(
        source="tjdf_juris",
        display_name="TJDFT Juris",
        source_url="https://example.test",
        category="court_jurisprudence",
        search_modes=["text", "date_range"],
        canonical_records=["CanonicalDecision"],
        extracted_fields=["summary", "rapporteur"],
        endpoints=["GET /search"],
        supports_full_text=True,
        supports_live_tests=True,
        limitations=["HTML publico"],
        responsible_use=["Usar page_size pequeno"],
    )

    assessment = assess_source_contract(capability)

    assert assessment.source == "tjdf_juris"
    assert assessment.contract_level == 5
    assert assessment.maturity == "maduro"
    assert assessment.source_family == "html_jurisprudencia_tribunal"
    assert assessment.risk_level == "baixo"
    assert "summary" in assessment.evidence["extracted_fields"]


def test_assess_source_contract_infers_gap_for_shallow_unknown_source():
    capability = ProviderCapabilities(
        source="unknown",
        display_name="Fonte Nova",
        source_url="https://example.test",
        category="court_jurisprudence",
    )

    assessment = assess_source_contract(capability)

    assert assessment.contract_level == 1
    assert assessment.maturity == "inicial"
    assert assessment.risk_level == "alto"
    assert assessment.gaps[0] == "Documentar contrato HTTP completo com parametros e respostas."


def test_summarize_contracts_lists_sources_that_need_deepening():
    mature = assess_source_contract(
        ProviderCapabilities(
            source="tjdf_juris",
            display_name="TJDFT Juris",
            source_url="https://example.test",
            category="court_jurisprudence",
        )
    )
    shallow = assess_source_contract(
        ProviderCapabilities(
            source="new_source",
            display_name="Fonte Nova",
            source_url="https://example.test",
            category="court_jurisprudence",
        )
    )

    summary = summarize_contracts([mature, shallow])

    assert summary["total_sources"] == 2
    assert "new_source" in summary["needs_deepening"]
    assert "tjdf_juris" in summary["ready_for_agents"]


def test_contracts_payload_can_filter_one_source():
    capabilities = [
        ProviderCapabilities(
            source="tjdf_juris",
            display_name="TJDFT Juris",
            source_url="https://example.test",
            category="court_jurisprudence",
        ),
        ProviderCapabilities(
            source="new_source",
            display_name="Fonte Nova",
            source_url="https://example.test",
            category="court_jurisprudence",
        ),
    ]

    payload = contracts_payload(capabilities, source="tjdf_juris")

    assert payload["summary"]["total_sources"] == 1
    assert payload["contracts"][0]["source"] == "tjdf_juris"


def test_client_exposes_source_contract_inventory():
    class FakeProvider:
        name = "fake"

        def get_capabilities(self):
            return ProviderCapabilities(
                source="fake",
                display_name="Fonte Fake",
                source_url="https://example.test",
                category="court_jurisprudence",
            )

    client = NanoJurisClient(providers=[FakeProvider()])

    assert client.get_source_contract(source="fake").source == "fake"
    assert [contract.source for contract in client.list_source_contracts()] == ["fake"]
