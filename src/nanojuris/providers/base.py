"""Provider contract for jurisprudence sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from nanojuris.models import DecisionBundle, JurisprudenceQuery, ProviderCatalog, SearchPage


class JurisprudenceProvider(ABC):
    """Base class for public jurisprudence providers."""

    name: str

    @abstractmethod
    def search(self, query: JurisprudenceQuery) -> SearchPage:
        """Search the provider and return a normalized page."""

    @abstractmethod
    def get_decisions(self, precedent_id: str) -> DecisionBundle:
        """Return decision texts or metadata linked to a precedent."""

    def get_parameters(self) -> dict[str, Any]:
        """Return provider metadata when available."""

        return {}

    def get_catalog(self) -> ProviderCatalog:
        """Return a normalized provider catalog when available."""

        return ProviderCatalog(source=self.name, raw=self.get_parameters())
