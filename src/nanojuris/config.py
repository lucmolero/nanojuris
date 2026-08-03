"""Runtime configuration for NanoJuris."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class NanoJurisConfig:
    """Configuration shared by clients and providers."""

    timeout: float = 20.0
    user_agent: str = "NanoJuris/0.1 (+https://github.com/lucmolero/nanojuris)"
    bnp_api_url: str = "https://pangeabnp.pdpj.jus.br/api/v1"
    comunica_pje_url: str = "https://comunicaapi.pje.jus.br"
    stj_url: str = "https://processo.stj.jus.br"
    stj_scon_url: str = "https://scon.stj.jus.br"
    stm_jurisprudencia_url: str = "https://jurisprudencia.stm.jus.br"
    tjdf_juris_url: str = "https://pesquisajuris.tjdft.jus.br"
    trf4_eproc_jurisprudencia_url: str = "https://jurisprudencia.trf4.jus.br/eproc2trf4"
    tjac_cjsg_url: str = "https://esaj.tjac.jus.br/cjsg"
    tjal_cjsg_url: str = "https://www2.tjal.jus.br/cjsg"
    tjam_cjsg_url: str = "https://consultasaj.tjam.jus.br/cjsg"
    tjms_cjsg_url: str = "https://esaj.tjms.jus.br/cjsg"
    tjsp_esaj_url: str = "https://esaj.tjsp.jus.br"
    tjsp_cjsg_url: str = "https://esaj.tjsp.jus.br/cjsg"
    tjsp_eproc_url: str = "https://eproc-consulta.tjsp.jus.br/consulta_1g"
    rate_limit_interval: float = 0.0
