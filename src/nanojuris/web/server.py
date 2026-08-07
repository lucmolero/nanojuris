"""Command entrypoint for the local NanoJuris Studio server."""

from __future__ import annotations

import argparse
import importlib.util
import os
import webbrowser


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="nanojuris-studio",
        description="Iniciar o NanoJuris Studio local.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument(
        "--ignore-env-proxy",
        action="store_true",
        help="Ignorar HTTP_PROXY/HTTPS_PROXY/ALL_PROXY herdados do ambiente local.",
    )
    args = parser.parse_args(argv)

    if args.ignore_env_proxy:
        os.environ["NANOJURIS_TRUST_ENV"] = "0"

    if importlib.util.find_spec("fastapi") is None:
        raise RuntimeError(
            'NanoJuris Studio requires FastAPI. Install with: pip install "nanojuris[studio]"'
        )

    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError(
            'NanoJuris Studio requires uvicorn. Install with: pip install "nanojuris[studio]"'
        ) from exc

    url = f"http://{args.host}:{args.port}"
    if not args.no_browser:
        webbrowser.open(url)
    proxy_mode = "sem proxy de ambiente" if args.ignore_env_proxy else "com proxy de ambiente"
    print(f"NanoJuris Studio iniciado em {url} ({proxy_mode})")
    uvicorn.run(
        "nanojuris.web.app:create_app",
        host=args.host,
        port=args.port,
        factory=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
