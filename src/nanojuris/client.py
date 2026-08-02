"""High-level client for NanoJuris."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from nanojuris.config import NanoJurisConfig
from nanojuris.errors import UnsupportedProviderError
from nanojuris.models import DecisionBundle, JurisprudenceQuery, SearchPage
from nanojuris.providers.base import JurisprudenceProvider
from nanojuris.providers.bnp_pangea import BnpPangeaProvider


class NanoJurisClient:
    """Facade over public jurisprudence providers."""

    def __init__(
        self,
        config: NanoJurisConfig | None = None,
        providers: Iterable[JurisprudenceProvider] | None = None,
    ) -> None:
        self.config = config or NanoJurisConfig()
        provider_list = (
            list(providers) if providers is not None else [BnpPangeaProvider(self.config)]
        )
        self.providers = {provider.name: provider for provider in provider_list}

    def search(
        self,
        text: str = "",
        *,
        source: str = "bnp_pangea",
        courts: list[str] | None = None,
        types: list[str] | None = None,
        page: int = 1,
        page_size: int = 10,
        **filters: Any,
    ) -> SearchPage:
        """Search one provider and return a normalized page."""

        query = JurisprudenceQuery(
            text=text,
            courts=courts or [],
            types=types or [],
            page=page,
            page_size=page_size,
            all_words=str(filters.get("all_words") or ""),
            any_words=str(filters.get("any_words") or ""),
            without_words=str(filters.get("without_words") or ""),
            exact_phrase=str(filters.get("exact_phrase") or ""),
            updated_from=str(filters.get("updated_from") or ""),
            updated_to=str(filters.get("updated_to") or ""),
            include_cancelled=bool(filters.get("include_cancelled") or False),
            order_by=str(filters.get("order_by") or "Text"),
            number=str(filters.get("number") or ""),
        )
        return self._provider(source).search(query)

    def get_decisions(self, precedent_id: str, *, source: str = "bnp_pangea") -> DecisionBundle:
        """Return decisions linked to a precedent."""

        return self._provider(source).get_decisions(precedent_id)

    def get_parameters(self, *, source: str = "bnp_pangea") -> dict[str, Any]:
        """Return provider metadata."""

        return self._provider(source).get_parameters()

    def _provider(self, source: str) -> JurisprudenceProvider:
        try:
            return self.providers[source]
        except KeyError as exc:
            available = ", ".join(sorted(self.providers))
            raise UnsupportedProviderError(
                f"Provider {source!r} is not registered. Available: {available}"
            ) from exc
