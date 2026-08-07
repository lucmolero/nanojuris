"""Source routing helpers for unified jurisprudence searches."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from nanojuris.models import ProviderCapabilities

CNJ_NUMBER_RE = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")

JURISPRUDENCE_CATEGORIES = {
    "administrative_jurisprudence",
    "court_jurisprudence",
    "court_precedents",
    "electoral_jurisprudence",
    "jurisprudence",
    "qualified_precedents",
}

IDENTIFIER_FILTERS = {
    "number",
    "party_name",
    "party_document",
    "lawyer_name",
    "oab",
    "precatory_number",
    "police_document",
    "cda",
}


@dataclass(frozen=True, slots=True)
class SourceSkip:
    """A source that should not be called for the current unified query."""

    source: str
    category: str
    reason: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "source": self.source,
            "category": self.category,
            "reason": self.reason,
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class RoutedSources:
    """Selected sources split into callable and intentionally skipped groups."""

    searched: list[str]
    skipped: list[SourceSkip]


def route_unified_sources(
    *,
    selected_sources: list[str],
    capabilities: dict[str, ProviderCapabilities],
    text: str,
    filters: dict[str, Any],
) -> RoutedSources:
    """Return sources that fit a unified jurisprudence query.

    The router is intentionally conservative: it avoids calls that are known to
    be semantically invalid, but it does not hide source failures for providers
    that are valid candidates for the user's question.
    """

    has_identifier = _has_identifier(text=text, filters=filters)
    searched: list[str] = []
    skipped: list[SourceSkip] = []

    for source in selected_sources:
        capability = capabilities.get(source)
        if capability is None:
            searched.append(source)
            continue

        skip = _skip_reason(capability, has_identifier=has_identifier)
        if skip is None:
            searched.append(source)
        else:
            skipped.append(skip)

    return RoutedSources(searched=searched, skipped=skipped)


def _skip_reason(
    capability: ProviderCapabilities,
    *,
    has_identifier: bool,
) -> SourceSkip | None:
    if not capability.supports_mcp:
        return SourceSkip(
            source=capability.source,
            category=capability.category,
            reason="mcp_not_supported",
            message="A fonte nao declara suporte ao uso via MCP.",
        )

    if capability.category == "case_lookup" and not has_identifier:
        return SourceSkip(
            source=capability.source,
            category=capability.category,
            reason="case_lookup_requires_identifier",
            message=(
                "Consulta processual exige numero CNJ, parte, documento, OAB "
                "ou outro identificador; nao e uma busca textual de jurisprudencia."
            ),
        )
    if capability.category == "case_lookup":
        return None

    if capability.category == "judicial_communications":
        return SourceSkip(
            source=capability.source,
            category=capability.category,
            reason="not_jurisprudence_source",
            message=(
                "A fonte retorna comunicacoes/intimacoes judiciais, nao julgados "
                "de jurisprudencia para estudo jurimetrico."
            ),
        )

    if capability.category not in JURISPRUDENCE_CATEGORIES:
        return SourceSkip(
            source=capability.source,
            category=capability.category,
            reason="category_not_applicable",
            message="A categoria declarada da fonte nao pertence ao escopo de jurisprudencia.",
        )

    return None


def _has_identifier(*, text: str, filters: dict[str, Any]) -> bool:
    if CNJ_NUMBER_RE.search(text):
        return True
    return any(_has_value(filters.get(name)) for name in IDENTIFIER_FILTERS)


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list | tuple | set):
        return bool(value)
    return bool(value)
