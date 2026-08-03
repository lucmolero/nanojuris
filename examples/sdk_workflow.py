from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from nanojuris import NanoJurisClient, SQLiteStore
from nanojuris.models import (
    DecisionBundle,
    JurisprudenceQuery,
    JurisprudenceResult,
    ProviderCapabilities,
    SearchPage,
    SourceTrace,
)
from nanojuris.providers.base import JurisprudenceProvider


class OfflineProvider(JurisprudenceProvider):
    name = "offline_demo"

    def search(self, query: JurisprudenceQuery) -> SearchPage:
        return SearchPage(
            source=self.name,
            total=1,
            start=1,
            end=1,
            page=query.page,
            page_size=query.page_size,
            results=[
                JurisprudenceResult(
                    id="offline-demo-1",
                    source=self.name,
                    court="TJSP",
                    type="acordao",
                    number="0003938-14.2017.8.26.0323",
                    summary="Ementa publica demonstrativa para fluxo SDK offline.",
                    source_trace=SourceTrace(
                        provider=self.name,
                        endpoint="offline://jurisprudence/search",
                    ),
                    raw={
                        "classe": "Apelacao Criminal",
                        "assunto": "Homicidio Qualificado",
                        "comarca": "Lorena",
                        "orgao_julgador": "3a Camara de Direito Criminal",
                    },
                )
            ],
        )

    def get_decisions(self, precedent_id: str) -> DecisionBundle:
        return DecisionBundle(precedent_id=precedent_id, source=self.name)

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            source=self.name,
            display_name="Offline Demo Provider",
            source_url="offline://jurisprudence",
            category="demo",
            search_modes=["text"],
            document_types=["acordao"],
            content_formats=["fixture"],
            canonical_records=["CanonicalDecision"],
            extracted_fields=["case_number", "case_class", "subject", "summary"],
            supports_live_tests=False,
            limitations=["Provider demonstrativo sem rede."],
            responsible_use=["Usar apenas para validar fluxo local do SDK."],
        )


def main() -> None:
    with TemporaryDirectory() as temporary_directory:
        output_path = Path(temporary_directory) / "nanojuris_sdk_demo.db"

        client = NanoJurisClient(providers=[OfflineProvider()])
        run = client.search_and_store_run(
            "homicidio qualificado",
            source="offline_demo",
            store=output_path,
            label="Demo SDK offline",
        )

        with SQLiteStore(output_path) as store:
            stats = store.stats().to_dict()
            run_records = store.get_research_run_records(run.id)
            stored = store.query_records(kind="decision", court="TJSP")

        print(
            {
                "run_id": run.id,
                "stored": run.record_count,
                "stats": stats,
                "run_records": len(run_records),
                "first_case_number": stored[0]["case_number"] if stored else None,
            }
        )


if __name__ == "__main__":
    main()
