"""FastAPI application factory for NanoJuris Studio."""

from __future__ import annotations

from importlib import resources
from pathlib import Path
from typing import Any

from nanojuris import __version__
from nanojuris.client import NanoJurisClient
from nanojuris.web.schemas import StudioSearchRequest
from nanojuris.web.studio import studio_search, studio_sources_payload


def create_app(client: NanoJurisClient | None = None) -> Any:
    """Create the optional FastAPI app used by ``nanojuris studio``."""

    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import FileResponse
        from fastapi.staticfiles import StaticFiles
    except ImportError as exc:  # pragma: no cover - exercised without importing FastAPI.
        raise RuntimeError(
            "NanoJuris Studio requires optional dependencies. "
            'Install with: pip install "nanojuris[studio]"'
        ) from exc

    active_client = client or NanoJurisClient()
    app = FastAPI(
        title="NanoJuris Studio",
        version=__version__,
        description="Local unified jurisprudence search UI for NanoJuris.",
    )
    static_dir = _static_dir()

    @app.get("/api/health")
    def health() -> dict[str, Any]:
        return {
            "ok": True,
            "name": "NanoJuris Studio",
            "version": __version__,
            "providers": len(active_client.providers),
        }

    @app.get("/api/sources")
    def sources() -> dict[str, Any]:
        return studio_sources_payload(active_client)

    @app.get("/api/sources/{source}")
    def source_detail(source: str) -> dict[str, Any]:
        try:
            capability = active_client.get_capabilities(source=source).to_dict()
            contract = active_client.get_source_contract(source=source).to_dict()
        except Exception as exc:  # noqa: BLE001 - API boundary
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {"capability": capability, "contract": contract}

    @app.post("/api/search")
    def search(payload: dict[str, Any]) -> dict[str, Any]:
        try:
            request = StudioSearchRequest.from_payload(payload)
            return studio_search(active_client, request)
        except Exception as exc:  # noqa: BLE001 - API boundary
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/api/documents/{source}/{document_id:path}")
    def document(source: str, document_id: str) -> dict[str, Any]:
        try:
            return active_client.get_document(document_id, source=source).to_dict()
        except Exception as exc:  # noqa: BLE001 - API boundary
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> FileResponse:
        return FileResponse(static_dir / "assets" / "favicon.svg", media_type="image/svg+xml")

    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")
    return app


def _static_dir() -> Path:
    return Path(str(resources.files("nanojuris.web.static")))
