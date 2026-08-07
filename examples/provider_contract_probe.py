"""Print a compact provider contract maturity matrix."""

from __future__ import annotations

from nanojuris import NanoJurisClient, summarize_contracts


def main() -> int:
    client = NanoJurisClient()
    contracts = client.list_source_contracts()
    summary = summarize_contracts(contracts)

    print("NanoJuris provider contract matrix")
    print(f"total_sources={summary['total_sources']}")
    print(f"needs_deepening={', '.join(summary['needs_deepening'])}")
    print()
    print("| source | level | risk | maturity | family |")
    print("| --- | ---: | --- | --- | --- |")
    for contract in contracts:
        print(
            "| "
            f"{contract.source} | "
            f"{contract.contract_level} | "
            f"{contract.risk_level} | "
            f"{contract.maturity} | "
            f"{contract.source_family} |"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
