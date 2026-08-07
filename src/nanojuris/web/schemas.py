"""Small request contracts for the local NanoJuris Studio API."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class StudioSearchRequest:
    """Normalized payload accepted by the Studio unified search endpoint."""

    query: str = ""
    sources: list[str] = field(default_factory=list)
    filters: dict[str, Any] = field(default_factory=dict)
    page: int = 1
    page_size: int = 10
    canonical: bool = True

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> StudioSearchRequest:
        filters = payload.get("filters")
        if filters is None:
            filters = {}
        if not isinstance(filters, dict):
            raise ValueError("filters must be an object")
        return cls(
            query=str(payload.get("query") or payload.get("text") or ""),
            sources=_string_list(payload.get("sources")),
            filters=filters,
            page=max(1, int(payload.get("page") or 1)),
            page_size=max(1, min(50, int(payload.get("page_size") or payload.get("limit") or 10))),
            canonical=bool(payload.get("canonical", True)),
        )

    def search_kwargs(self) -> dict[str, Any]:
        kwargs = dict(self.filters)
        if "date_from" in kwargs and "published_from" not in kwargs:
            kwargs["published_from"] = kwargs.pop("date_from")
        if "date_to" in kwargs and "published_to" not in kwargs:
            kwargs["published_to"] = kwargs.pop("date_to")
        return kwargs


def _string_list(value: Any) -> list[str]:
    if value in (None, "", "all"):
        return []
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, list | tuple | set):
        return [str(item).strip() for item in value if str(item).strip()]
    raise ValueError("sources must be a list or comma-separated string")
