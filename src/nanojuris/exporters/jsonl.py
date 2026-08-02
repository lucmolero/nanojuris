"""JSON Lines exporter."""

from __future__ import annotations

import json

from nanojuris.models import JurisprudenceResult, SearchPage


def to_jsonl(page_or_results: SearchPage | list[JurisprudenceResult]) -> str:
    """Serialize a search page or result list as JSON Lines."""

    results = (
        page_or_results.results if isinstance(page_or_results, SearchPage) else page_or_results
    )
    return "\n".join(
        json.dumps(result.to_dict(), ensure_ascii=False, sort_keys=True) for result in results
    )
