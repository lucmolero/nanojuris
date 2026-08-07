"""Reusable extraction pipeline primitives."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, field
from typing import Any

import requests

from nanojuris.config import NanoJurisConfig
from nanojuris.models import (
    AccessStatus,
    ExtractionStatus,
    ExtractionTrace,
    SourceTrace,
    utc_now_iso,
)


@dataclass(slots=True)
class FetchRequest:
    """HTTP acquisition request for a public source."""

    source: str
    url: str
    endpoint: str
    method: str = "GET"
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    data: dict[str, Any] = field(default_factory=dict)
    json: dict[str, Any] | None = None
    timeout: float | None = None
    query: dict[str, Any] = field(default_factory=dict)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class FetchedContent:
    """Raw content fetched from a public source."""

    source: str
    url: str
    status_code: int
    content: bytes
    content_type: str | None = None
    encoding: str | None = None
    retrieved_at: str = field(default_factory=utc_now_iso)
    access_status: AccessStatus = AccessStatus.PUBLIC
    source_trace: SourceTrace | None = None

    @property
    def text(self) -> str:
        """Decode fetched bytes as text."""

        return self.content.decode(self.encoding or "utf-8", errors="replace")

    @property
    def sha256(self) -> str:
        """Return a stable hash for fetched bytes."""

        return hashlib.sha256(self.content).hexdigest()

    @property
    def byte_size(self) -> int:
        """Return the content size in bytes."""

        return len(self.content)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["content"] = self.text
        payload["sha256"] = self.sha256
        payload["byte_size"] = self.byte_size
        return payload


@dataclass(slots=True)
class ParsedContent:
    """Intermediate parser output before canonical mapping."""

    source: str
    parser: str
    parser_version: str
    records: list[dict[str, Any]] = field(default_factory=list)
    text: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    extraction_trace: ExtractionTrace | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class HttpFetcher:
    """Responsible HTTP fetcher for public extraction sources."""

    def __init__(
        self,
        config: NanoJurisConfig | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.config = config or NanoJurisConfig()
        self.session = session or requests.Session()

    def fetch(self, request: FetchRequest) -> FetchedContent:
        """Fetch raw source content without bypassing access controls."""

        headers = {"User-Agent": self.config.user_agent, **request.headers}
        response = self.session.request(
            request.method,
            request.url,
            headers=headers,
            params=request.params or None,
            data=request.data or None,
            json=request.json,
            timeout=request.timeout or self.config.timeout,
        )
        content = bytes(response.content)
        source_trace = SourceTrace(
            provider=request.source,
            endpoint=request.endpoint,
            query=request.query,
            source_url=request.url,
            limitations=request.limitations,
        )
        return FetchedContent(
            source=request.source,
            url=request.url,
            status_code=response.status_code,
            content=content,
            content_type=response.headers.get("Content-Type"),
            encoding=response.encoding,
            access_status=_status_to_access_status(response.status_code),
            source_trace=source_trace,
        )


def parsed_content(
    *,
    source: str,
    parser: str,
    parser_version: str,
    records: list[dict[str, Any]] | None = None,
    text: str | None = None,
    metadata: dict[str, Any] | None = None,
    status: ExtractionStatus = ExtractionStatus.COMPLETE,
    access_status: AccessStatus = AccessStatus.PUBLIC,
    content_sha256: str | None = None,
    content_bytes: int | None = None,
    warnings: list[str] | None = None,
) -> ParsedContent:
    """Build parser output with an extraction trace."""

    trace = ExtractionTrace(
        parser=parser,
        parser_version=parser_version,
        status=status,
        access_status=access_status,
        content_sha256=content_sha256,
        content_bytes=content_bytes,
        warnings=warnings or [],
        metadata=metadata or {},
    )
    return ParsedContent(
        source=source,
        parser=parser,
        parser_version=parser_version,
        records=records or [],
        text=text,
        metadata=metadata or {},
        extraction_trace=trace,
    )


def _status_to_access_status(status_code: int) -> AccessStatus:
    if status_code == 404:
        return AccessStatus.NOT_FOUND
    if status_code in {401, 403}:
        return AccessStatus.LOGIN_REQUIRED
    if status_code == 429 or status_code >= 500:
        return AccessStatus.SOURCE_UNAVAILABLE
    if 300 <= status_code < 400:
        return AccessStatus.PARTIAL
    return AccessStatus.PUBLIC
