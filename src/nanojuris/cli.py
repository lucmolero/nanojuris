"""Command line interface for NanoJuris."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from nanojuris import __version__
from nanojuris.client import NanoJurisClient
from nanojuris.exporters import search_page_to_markdown, to_jsonl


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nanojuris",
        description="Busca e normalizacao de jurisprudencia publica brasileira.",
    )
    parser.add_argument("--version", action="version", version=f"nanojuris {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)

    buscar = sub.add_parser("buscar", help="Buscar precedentes ou jurisprudencia publica")
    buscar.add_argument("texto", nargs="?", default="", help="Texto de busca")
    buscar.add_argument("--fonte", default="bnp_pangea", help="Provider de origem")
    buscar.add_argument("--orgaos", default="", help="Siglas separadas por virgula: STF,STJ,TST")
    buscar.add_argument("--tipos", default="", help="Tipos separados por virgula: RG,RR,IAC,IRDR")
    buscar.add_argument("--pagina", type=int, default=1)
    buscar.add_argument("--limite", type=int, default=10)
    buscar.add_argument(
        "--formato",
        choices=["json", "jsonl", "markdown"],
        default="json",
        help="Formato de saida",
    )

    precedente = sub.add_parser("precedente", help="Obter decisoes vinculadas a um precedente")
    precedente.add_argument("id", help="ID do precedente, ex.: stf-rg-615")
    precedente.add_argument("--fonte", default="bnp_pangea")

    parametros = sub.add_parser("parametros", help="Listar parametros publicos do provider")
    parametros.add_argument("--fonte", default="bnp_pangea")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    client = NanoJurisClient()

    try:
        if args.command == "buscar":
            page = client.search(
                args.texto,
                source=args.fonte,
                courts=_split_csv(args.orgaos),
                types=_split_csv(args.tipos),
                page=args.pagina,
                page_size=args.limite,
            )
            print(_format_search(page, args.formato))
            return 0

        if args.command == "precedente":
            bundle = client.get_decisions(args.id, source=args.fonte)
            print(json.dumps(bundle.to_dict(), ensure_ascii=False, indent=2))
            return 0

        if args.command == "parametros":
            params = client.get_parameters(source=args.fonte)
            print(json.dumps(params, ensure_ascii=False, indent=2))
            return 0
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"erro: {exc}", file=sys.stderr)
        return 2

    parser.error("Comando invalido")
    return 2


def _split_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _format_search(page: Any, output_format: str) -> str:
    if output_format == "jsonl":
        return to_jsonl(page)
    if output_format == "markdown":
        return search_page_to_markdown(page)
    return json.dumps(page.to_dict(), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    raise SystemExit(main())
