"""Domain exceptions for NanoJuris."""

from __future__ import annotations


class NanoJurisError(Exception):
    """Base exception for all NanoJuris errors."""


class SourceUnavailableError(NanoJurisError):
    """Raised when a public source is unavailable or returns an invalid response."""


class AccessControlRequiredError(NanoJurisError):
    """Raised when a source requires login, captcha or another access control."""


class RateLimitDetectedError(NanoJurisError):
    """Raised when a source signals throttling or excessive usage."""


class ParserContractChangedError(NanoJurisError):
    """Raised when a source response no longer matches the expected contract."""


class UnsupportedProviderError(NanoJurisError):
    """Raised when a provider name is unknown."""
