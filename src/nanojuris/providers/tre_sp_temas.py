"""TRE-SP public selected jurisprudence themes provider."""

from __future__ import annotations

import re
import time
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag

from nanojuris.config import NanoJurisConfig
from nanojuris.errors import (
    ParserContractChangedError,
    RateLimitDetectedError,
    SourceUnavailableError,
)
from nanojuris.models import (
    AccessStatus,
    DecisionBundle,
    JurisprudenceQuery,
    JurisprudenceResult,
    ProviderCapabilities,
    SearchPage,
    SourceTrace,
)
from nanojuris.providers.base import JurisprudenceProvider


class TreSpTemasProvider(JurisprudenceProvider):
    """Provider for TRE-SP public selected jurisprudence theme pages."""

    name = "tre_sp_temas"

    def __init__(
        self,
        config: NanoJurisConfig | None = None,
        session: requests.Session | None = None,
    ) -> None:
        self.config = config or NanoJurisConfig()
        self.session = session or requests.Session()
        self._last_request = 0.0

    def search(self, query: JurisprudenceQuery) -> SearchPage:
        index_html, index_url = self._request_text("GET", "/jurisprudencia/temas-selecionados-1")
        trace = SourceTrace(
            provider=self.name,
            endpoint="/jurisprudencia/temas-selecionados-1",
            query=query.to_dict(),
            source_url=index_url,
            limitations=[
                "Fonte tematica publica do TRE-SP validada com sessao HTTP limpa.",
                "A pagina de pesquisa de jurisprudencia pode conter mecanismos "
                "antirobo; este provider usa paginas estaticas.",
            ],
        )
        themes = parse_tre_sp_theme_links(index_html, source_url=index_url)
        normalized_query = _normalize_text(query.text or query.exact_phrase)
        results: list[JurisprudenceResult] = []
        for theme in themes:
            if normalized_query and normalized_query not in _normalize_text(theme.title):
                detail_html, detail_url = self._request_text("GET", theme.path)
                detail_text = BeautifulSoup(detail_html, "html.parser").get_text(" ", strip=True)
                if normalized_query not in _normalize_text(f"{theme.title} {detail_text}"):
                    continue
                results.append(
                    parse_tre_sp_theme_detail(detail_html, source_url=detail_url, trace=trace)
                )
            else:
                detail_html, detail_url = self._request_text("GET", theme.path)
                results.append(
                    parse_tre_sp_theme_detail(detail_html, source_url=detail_url, trace=trace)
                )
            if len(results) >= query.page * query.page_size:
                break

        start_index = (query.page - 1) * query.page_size
        limited = results[start_index : start_index + query.page_size]
        start = start_index + 1 if limited else 0
        return SearchPage(
            source=self.name,
            total=len(results),
            start=start,
            end=start + len(limited) - 1 if limited else 0,
            page=query.page,
            page_size=query.page_size,
            results=limited,
            source_trace=trace,
        )

    def get_decisions(self, precedent_id: str) -> DecisionBundle:
        path = _path_from_id(precedent_id)
        html, source_url = self._request_text("GET", path)
        trace = SourceTrace(
            provider=self.name,
            endpoint=path,
            query={"precedent_id": precedent_id},
            source_url=source_url,
            limitations=["Pagina tematica publica do TRE-SP."],
        )
        return DecisionBundle(
            precedent_id=precedent_id,
            source=self.name,
            texts=[{"content": html, "content_type": "text/html"}],
            source_trace=trace,
            raw={"path": path},
        )

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            source=self.name,
            display_name="TRE-SP Temas Selecionados",
            source_url=self.config.tre_sp_url.rstrip("/") + "/jurisprudencia/temas-selecionados-1",
            category="electoral_jurisprudence",
            search_modes=["text", "thematic_catalog"],
            document_types=["tema_selecionado"],
            content_formats=["html"],
            canonical_records=["CanonicalPrecedent"],
            extracted_fields=[
                "theme",
                "summary",
                "selected_decisions",
                "document_links",
            ],
            access_statuses=[
                AccessStatus.PUBLIC,
                AccessStatus.PARTIAL,
                AccessStatus.SOURCE_UNAVAILABLE,
            ],
            endpoints=[
                "GET /jurisprudencia/temas-selecionados-1",
                "GET /jurisprudencia/arquivos-da-secao-de-jurisprudencia-sp/"
                "temas-selecionados/<slug>",
            ],
            supports_full_text=False,
            supports_catalog=True,
            supports_suggestions=False,
            supports_live_tests=True,
            limitations=[
                "Fonte tematica, nao uma busca geral de acordaos.",
                "Links de inteiro teor podem apontar para sistemas eleitorais externos.",
            ],
            responsible_use=[
                "Usar como curadoria tematica eleitoral paulista.",
                "Preservar URL da pagina tematica e links de decisoes selecionadas.",
            ],
        )

    def _request_text(self, method: str, path: str, **kwargs: Any) -> tuple[str, str]:
        self._respect_rate_limit()
        url = urljoin(self.config.tre_sp_url.rstrip("/") + "/", path.lstrip("/"))
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": self.config.user_agent,
        }
        try:
            response = self.session.request(
                method,
                url,
                headers=headers,
                timeout=self.config.timeout,
                allow_redirects=True,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise SourceUnavailableError(f"TRE-SP temas request failed: {exc}") from exc

        response.encoding = response.encoding or response.apparent_encoding or "utf-8"
        if response.status_code == 429:
            raise RateLimitDetectedError("TRE-SP temas returned HTTP 429")
        if response.status_code >= 500:
            raise SourceUnavailableError(f"TRE-SP temas returned HTTP {response.status_code}")
        if response.status_code >= 400:
            raise SourceUnavailableError(
                f"TRE-SP temas rejected request with HTTP {response.status_code}"
            )
        return response.text, getattr(response, "url", url)

    def _respect_rate_limit(self) -> None:
        interval = self.config.rate_limit_interval
        if interval <= 0:
            return
        elapsed = time.monotonic() - self._last_request
        if elapsed < interval:
            time.sleep(interval - elapsed)
        self._last_request = time.monotonic()


class _ThemeLink:
    def __init__(self, *, title: str, path: str) -> None:
        self.title = title
        self.path = path


def parse_tre_sp_theme_links(html: str, *, source_url: str) -> list[_ThemeLink]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[_ThemeLink] = []
    for node in soup.find_all("a", href=True):
        href = str(node.get("href") or "")
        if "/temas-selecionados/" not in href:
            continue
        title = _clean_text(node.get_text(" ", strip=True))
        if not title:
            continue
        links.append(_ThemeLink(title=title, path=_relative_url_path(urljoin(source_url, href))))
    if not links:
        raise ParserContractChangedError("TRE-SP selected theme links not found")
    return links


def parse_tre_sp_theme_detail(
    html: str,
    *,
    source_url: str,
    trace: SourceTrace,
) -> JurisprudenceResult:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main") or soup.find("article") or soup.body
    if not isinstance(main, Tag):
        raise ParserContractChangedError("TRE-SP theme content not found")
    text = _clean_text(main.get_text(" ", strip=True))
    title = _extract_title(soup, text)
    slug = _slug_from_url(source_url)
    links = _document_links(main, source_url)
    summary = _extract_summary(text, title)
    result_trace = SourceTrace(
        provider=trace.provider,
        endpoint="/jurisprudencia/temas-selecionados-1",
        query={"theme": slug},
        source_url=source_url,
        limitations=trace.limitations,
    )
    return JurisprudenceResult(
        id=f"tre-sp-tema-{slug}",
        source="tre_sp_temas",
        court="TRE-SP",
        type="tema_selecionado",
        summary=summary or title,
        question=title,
        thesis=summary,
        source_trace=result_trace,
        raw={"title": title, "document_links": links, "source_url": source_url},
    )


def _path_from_id(precedent_id: str) -> str:
    prefix = "tre-sp-tema-"
    if not precedent_id.startswith(prefix):
        raise ParserContractChangedError("TRE-SP theme id must start with tre-sp-tema-")
    slug = precedent_id.removeprefix(prefix)
    return f"/jurisprudencia/arquivos-da-secao-de-jurisprudencia-sp/temas-selecionados/{slug}"


def _extract_title(soup: BeautifulSoup, fallback_text: str) -> str:
    for selector in ["h1", "h2", "h3", "title"]:
        node = soup.select_one(selector)
        if node:
            title = _clean_text(node.get_text(" ", strip=True))
            if title:
                return title.replace("— Tribunal Regional Eleitoral de São Paulo", "").strip()
    return fallback_text[:120]


def _extract_summary(text: str, title: str) -> str | None:
    cleaned = text.replace(title, "", 1).strip()
    if not cleaned:
        return None
    return cleaned[:2000]


def _document_links(node: Tag, source_url: str) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    for item in node.find_all("a", href=True):
        label = _clean_text(item.get_text(" ", strip=True))
        href = str(item.get("href") or "")
        if not label:
            continue
        links.append({"label": label, "url": urljoin(source_url, href)})
    return links


def _slug_from_url(url: str) -> str:
    slug = urlparse(url).path.rstrip("/").split("/")[-1]
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", slug).strip("-") or "tema"


def _relative_url_path(url: str) -> str:
    parsed = urlparse(url)
    return parsed.path + (f"?{parsed.query}" if parsed.query else "")


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _normalize_text(value: object) -> str:
    normalized = _clean_text(str(value or "")).casefold()
    replacements = {
        "á": "a",
        "à": "a",
        "â": "a",
        "ã": "a",
        "é": "e",
        "ê": "e",
        "í": "i",
        "ó": "o",
        "ô": "o",
        "õ": "o",
        "ú": "u",
        "ç": "c",
    }
    for original, replacement in replacements.items():
        normalized = normalized.replace(original, replacement)
    return normalized
