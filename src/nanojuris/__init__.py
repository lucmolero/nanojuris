"""NanoJuris public API."""

from __future__ import annotations

from nanojuris.brazil import (
    COURTS,
    CourtBranch,
    CourtInfo,
    ImplementationStatus,
    SourceSystem,
    get_court,
    list_courts,
    normalize_court_code,
)
from nanojuris.canonical import (
    result_to_canonical_decision,
    result_to_canonical_precedent,
    search_page_to_canonical,
)
from nanojuris.client import NanoJurisClient
from nanojuris.config import NanoJurisConfig
from nanojuris.extraction import FetchedContent, FetchRequest, HttpFetcher, ParsedContent
from nanojuris.models import (
    AccessStatus,
    CanonicalDecision,
    CanonicalDocument,
    CanonicalPrecedent,
    DecisionBundle,
    ExtractionStatus,
    ExtractionTrace,
    JurisprudenceQuery,
    JurisprudenceResult,
    ParadigmCase,
    ProviderCapabilities,
    ProviderCatalog,
    ProviderOption,
    SearchPage,
    SourceTrace,
)
from nanojuris.store import CanonicalStore, ResearchRun, SQLiteStore, StoreStats

__all__ = [
    "AccessStatus",
    "CanonicalDecision",
    "CanonicalDocument",
    "CanonicalPrecedent",
    "CanonicalStore",
    "COURTS",
    "CourtBranch",
    "CourtInfo",
    "DecisionBundle",
    "ExtractionStatus",
    "ExtractionTrace",
    "FetchedContent",
    "FetchRequest",
    "HttpFetcher",
    "ImplementationStatus",
    "get_court",
    "JurisprudenceQuery",
    "JurisprudenceResult",
    "list_courts",
    "NanoJurisClient",
    "NanoJurisConfig",
    "normalize_court_code",
    "ParadigmCase",
    "ParsedContent",
    "ProviderCapabilities",
    "ProviderCatalog",
    "ProviderOption",
    "ResearchRun",
    "result_to_canonical_decision",
    "result_to_canonical_precedent",
    "SearchPage",
    "search_page_to_canonical",
    "SourceTrace",
    "SourceSystem",
    "SQLiteStore",
    "StoreStats",
]

__version__ = "0.1.0"
