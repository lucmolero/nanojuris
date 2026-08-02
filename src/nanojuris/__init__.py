"""NanoJuris public API."""

from __future__ import annotations

from nanojuris.client import NanoJurisClient
from nanojuris.config import NanoJurisConfig
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

__all__ = [
    "DecisionBundle",
    "JurisprudenceQuery",
    "JurisprudenceResult",
    "NanoJurisClient",
    "NanoJurisConfig",
    "ParadigmCase",
    "ProviderCatalog",
    "ProviderOption",
    "SearchPage",
    "SourceTrace",
]

__version__ = "0.1.0"
