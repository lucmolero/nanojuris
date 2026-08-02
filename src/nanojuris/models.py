"""Typed data contracts for jurisprudence and precedent sources."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    """Return a stable UTC timestamp for source traces."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(slots=True)
class SourceTrace:
    """Technical trace of a public source request."""

    provider: str
    endpoint: str
    retrieved_at: str = field(default_factory=utc_now_iso)
    query: dict[str, Any] = field(default_factory=dict)
    source_url: str | None = None
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ParadigmCase:
    """A process linked to a precedent."""

    number: str
    case_class: str | int | None = None
    url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class JurisprudenceQuery:
    """Unified query object for jurisprudence providers."""

    text: str = ""
    all_words: str = ""
    any_words: str = ""
    without_words: str = ""
    exact_phrase: str = ""
    updated_from: str = ""
    updated_to: str = ""
    include_cancelled: bool = False
    order_by: str = "Text"
    number: str = ""
    courts: list[str] = field(default_factory=list)
    types: list[str] = field(default_factory=list)
    page: int = 1
    page_size: int = 10

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class JurisprudenceResult:
    """A normalized result from a jurisprudence or precedent source."""

    id: str
    source: str
    court: str
    type: str
    number: str | int | None = None
    question: str | None = None
    thesis: str | None = None
    summary: str | None = None
    status: str | None = None
    rapporteur: str | None = None
    updated_at: str | None = None
    paradigm_cases: list[ParadigmCase] = field(default_factory=list)
    highlights: dict[str, str] = field(default_factory=dict)
    source_trace: SourceTrace | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SearchPage:
    """A page of normalized results."""

    source: str
    total: int
    start: int
    end: int
    page: int
    page_size: int
    results: list[JurisprudenceResult]
    aggregations: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    source_trace: SourceTrace | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DecisionBundle:
    """Decision texts linked to a precedent."""

    precedent_id: str
    source: str
    rapporteur: str | None = None
    procedural_follow_url: str | None = None
    texts: list[dict[str, Any]] = field(default_factory=list)
    source_trace: SourceTrace | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ProviderOption:
    """Normalized option exposed by a public provider catalog."""

    code: str
    description: str
    alias: str | None = None
    disabled: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ProviderCatalog:
    """Normalized catalog of courts, precedent species and provider metadata."""

    source: str
    courts: list[ProviderOption] = field(default_factory=list)
    species: list[ProviderOption] = field(default_factory=list)
    species_groups: list[dict[str, Any]] = field(default_factory=list)
    source_trace: SourceTrace | None = None
    raw: dict[str, Any] = field(default_factory=dict, repr=False)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
