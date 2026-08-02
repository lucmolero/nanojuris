"""Runtime configuration for NanoJuris."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class NanoJurisConfig:
    """Configuration shared by clients and providers."""

    timeout: float = 20.0
    user_agent: str = "NanoJuris/0.1 (+https://github.com/lucmolero/nanojuris)"
    bnp_api_url: str = "https://pangeabnp.pdpj.jus.br/api/v1"
    tjsp_cjsg_url: str = "https://esaj.tjsp.jus.br/cjsg"
    rate_limit_interval: float = 0.0
