from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_every_provider_has_source_contract_dossier() -> None:
    provider_dir = ROOT / "src" / "nanojuris" / "providers"
    docs_dir = ROOT / "docs" / "source-contracts"

    providers = {
        path.stem for path in provider_dir.glob("*.py") if path.stem not in {"__init__", "base"}
    }
    dossiers = {path.stem for path in docs_dir.glob("*.md")}

    assert sorted(providers - dossiers) == []


def test_provider_development_queue_links_existing_candidate_dossiers() -> None:
    queue_path = ROOT / "docs" / "provider-development-queue.md"
    docs_dir = ROOT / "docs" / "source-contracts"

    expected_candidates = {
        "tjpi_juspi",
        "tjrr_juris",
        "tjmt_jurisprudencia_api",
        "tjpa_jurisprudencia_bff",
        "tjpb_pje_jurisprudencia",
    }

    queue = queue_path.read_text(encoding="utf-8")
    existing_dossiers = {path.stem for path in docs_dir.glob("*.md")}

    assert expected_candidates <= existing_dossiers
    for candidate in sorted(expected_candidates):
        assert f"source-contracts/{candidate}.md" in queue
