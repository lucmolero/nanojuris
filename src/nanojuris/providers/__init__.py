"""Provider implementations."""

from nanojuris.providers.base import JurisprudenceProvider
from nanojuris.providers.bnp_pangea import BnpPangeaProvider

__all__ = ["BnpPangeaProvider", "JurisprudenceProvider"]
