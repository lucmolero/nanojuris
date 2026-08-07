"""Probe a public source route before implementing a NanoJuris provider.

This script intentionally uses a clean requests session. Do not pass browser
cookies, captcha tokens, HAR secrets or authenticated headers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from typing import Any

import requests
from bs4 import BeautifulSoup

DEFAULT_USER_AGENT = "NanoJuris/route-probe (+https://github.com/lucmolero/nanojuris)"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Probe a public route with a clean HTTP session before provider work."
    )
    parser.add_argument("url", help="Absolute public URL to test")
    parser.add_argument(
        "--expect",
        action="append",
        default=[],
        help="Text that must appear in the response body. Can be repeated.",
    )
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)
    args = parser.parse_args()

    payload = probe_route(
        args.url,
        expected_texts=args.expect,
        timeout=args.timeout,
        user_agent=args.user_agent,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 2


def probe_route(
    url: str,
    *,
    expected_texts: list[str],
    timeout: float,
    user_agent: str,
) -> dict[str, Any]:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": user_agent,
        }
    )
    try:
        response = session.get(url, timeout=timeout, allow_redirects=True)
    except requests.RequestException as exc:
        return {
            "ok": False,
            "url": url,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "expected_texts": {item: False for item in expected_texts},
            "access_signals": {},
        }
    text = response.text or ""
    lowered = text.lower()
    soup = BeautifulSoup(text, "html.parser")
    visible = _normalize_spaces(soup.get_text(" ", strip=True))
    expected = {item: item in text or item in visible for item in expected_texts}
    access_signals = {
        "captcha": "captcha" in lowered,
        "cloudflare": "cloudflare" in lowered,
        "turnstile": "turnstile" in lowered,
        "recaptcha": "recaptcha" in lowered or "g-recaptcha" in lowered,
        "login": "login" in lowered or "sajcas" in lowered or "entrar no sistema" in lowered,
    }
    access_blocked = any(access_signals.values())
    content_sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
    title = soup.title.get_text(strip=True) if soup.title else ""
    ok = response.status_code < 400 and all(expected.values()) and not access_blocked

    return {
        "ok": ok,
        "status_code": response.status_code,
        "url": url,
        "final_url": response.url,
        "title": title,
        "content_bytes": len(response.content),
        "content_sha256": content_sha256,
        "expected_texts": expected,
        "access_signals": access_signals,
        "route_status": "access_control_or_login" if access_blocked else "candidate",
        "visible_sample": visible[:1000],
    }


def _normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


if __name__ == "__main__":
    raise SystemExit(main())
