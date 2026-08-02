"""NanoJuris public API."""

from __future__ import annotations

from nanojuris.client import NanoJurisClient
from nanojuris.config import NanoJurisConfig
from nanojuris.models import (
    DecisionBundle,
    JurisprudenceQuery,
    JurisprudenceResult,
    ParadigmCase,
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
    "SearchPage",
    "SourceTrace",
]

__version__ = "0.1.0"
