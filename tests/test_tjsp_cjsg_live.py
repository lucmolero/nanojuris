from __future__ import annotations

import os

import pytest

from nanojuris import NanoJurisClient
from nanojuris.errors import AccessControlRequiredError

pytestmark = pytest.mark.skipif(
    os.getenv("NANOJURIS_RUN_TJSP_LIVE") != "1",
    reason="Set NANOJURIS_RUN_TJSP_LIVE=1 to query live TJSP/CJSG pages",
)


@pytest.mark.live
def test_live_tjsp_cjsg_search_or_access_control():
    client = NanoJurisClient()

    try:
        page = client.search("infanticidio", source="tjsp_cjsg", types=["acordao"], page_size=1)
    except AccessControlRequiredError as exc:
        assert "captcha" in str(exc).lower() or "access-control" in str(exc).lower()
        return

    assert page.source == "tjsp_cjsg"
    assert page.source_trace is not None
    assert page.results
    assert page.results[0].raw["cd_acordao"]
