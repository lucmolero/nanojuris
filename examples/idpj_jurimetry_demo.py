"""Demonstrate an IDPJ jurimetry-oriented search with NanoJuris.

The script is intentionally descriptive: it helps maintainers and AI agents
check routing, source failures and extracted fields before any legal analysis.
It may call public sources, so run it with small page sizes and respect access
controls reported by providers.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, is_dataclass
from typing import Any

from nanojuris import NanoJurisClient

DEFAULT_QUERY = "incidente de desconsideracao da personalidade juridica"
DEFAULT_SOURCES = ["tjdf_juris", "trf4_eproc_jurisprudencia", "tjsp_cjsg", "stj_scon"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a small NanoJuris IDPJ study for routing and provider diagnostics."
    )
    parser.add_argument("--query", default=DEFAULT_QUERY)
    parser.add_argument("--sources", default=",".join(DEFAULT_SOURCES))
    parser.add_argument("--page-size", type=int, default=3)
    parser.add_argument("--raw", action="store_true", help="Print the complete JSON payload")
    args = parser.parse_args()

    client = NanoJurisClient()
    payload = client.search_many(
        args.query,
        sources=[source.strip() for source in args.sources.split(",") if source.strip()],
        page_size=args.page_size,
        canonical=True,
    )
    jsonable = _to_jsonable(payload)
    if args.raw:
        print(json.dumps(jsonable, ensure_ascii=False, indent=2))
        return 0
    print(json.dumps(_briefing(jsonable), ensure_ascii=False, indent=2))
    return 0


def _briefing(payload: dict[str, Any]) -> dict[str, Any]:
    results = list(payload.get("results") or [])
    return {
        "study": "IDPJ jurimetry smoke demo",
        "searched_sources": payload.get("searched_sources", []),
        "skipped_sources": payload.get("skipped_sources", []),
        "errors": payload.get("errors", []),
        "routing_summary": payload.get("routing_summary", []),
        "total_returned": payload.get("total_returned", 0),
        "sample": [
            {
                "id": item.get("id"),
                "source": item.get("source"),
                "court": item.get("court"),
                "case_number": item.get("case_number"),
                "decision_type": item.get("decision_type"),
                "subject": item.get("subject"),
                "rapporteur": item.get("rapporteur"),
                "publication_date": item.get("publication_date"),
                "document_url": item.get("document_url"),
                "summary_chars": len(item.get("summary") or ""),
            }
            for item in results[:5]
        ],
        "questions_for_legal_review": [
            "A amostra distingue deferimento, indeferimento e conhecimento do IDPJ?",
            "Ha tribunal, camara, relator ou periodo com concentracao relevante?",
            "Os resultados retornados sao realmente sobre IDPJ ou ha falsos positivos?",
            "Alguma fonte falhou por captcha, contrato alterado ou indisponibilidade?",
        ],
    }


def _to_jsonable(value: object) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return _to_jsonable(asdict(value))
    if isinstance(value, dict):
        return {str(key): _to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


if __name__ == "__main__":
    raise SystemExit(main())
