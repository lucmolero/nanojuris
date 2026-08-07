"""Provider implementations."""

from nanojuris.providers.base import JurisprudenceProvider
from nanojuris.providers.bnp_pangea import BnpPangeaProvider
from nanojuris.providers.comunica_pje import ComunicaPjeProvider
from nanojuris.providers.eproc_jurisprudencia_federal import (
    FederalEprocJurisprudenciaProvider,
    TnuEprocJurisprudenciaProvider,
    Trf2EprocJurisprudenciaProvider,
    Trf6EprocJurisprudenciaProvider,
)
from nanojuris.providers.stf_juris import StfJurisProvider
from nanojuris.providers.stj_scon import StjSconProvider
from nanojuris.providers.stm_jurisprudencia import StmJurisprudenciaProvider
from nanojuris.providers.tce_sp_jurisprudencia import TceSpJurisprudenciaProvider
from nanojuris.providers.tjac_cjsg import TjacCjsgProvider
from nanojuris.providers.tjac_esaj_cpopg import TjacEsajCpopgProvider
from nanojuris.providers.tjal_cjsg import TjalCjsgProvider
from nanojuris.providers.tjam_cjsg import TjamCjsgProvider
from nanojuris.providers.tjdf_juris import TjdfJurisProvider
from nanojuris.providers.tjgo_projudi_jurisprudencia import TjgoProjudiJurisprudenciaProvider
from nanojuris.providers.tjms_cjsg import TjmsCjsgProvider
from nanojuris.providers.tjsp_cjsg import TjspCjsgProvider
from nanojuris.providers.tjsp_eproc_jurisprudencia import TjspEprocJurisprudenciaProvider
from nanojuris.providers.tjsp_esaj_cpopg import TjspEsajCpopgProvider
from nanojuris.providers.tjsp_nugepnac import TjspNugepnacProvider
from nanojuris.providers.tre_sp_temas import TreSpTemasProvider
from nanojuris.providers.trf4_eproc_jurisprudencia import Trf4EprocJurisprudenciaProvider

__all__ = [
    "BnpPangeaProvider",
    "ComunicaPjeProvider",
    "FederalEprocJurisprudenciaProvider",
    "JurisprudenceProvider",
    "StfJurisProvider",
    "StjSconProvider",
    "StmJurisprudenciaProvider",
    "TceSpJurisprudenciaProvider",
    "TjacCjsgProvider",
    "TjacEsajCpopgProvider",
    "TjdfJurisProvider",
    "TjgoProjudiJurisprudenciaProvider",
    "TjalCjsgProvider",
    "TjamCjsgProvider",
    "TjmsCjsgProvider",
    "TjspCjsgProvider",
    "TjspEprocJurisprudenciaProvider",
    "TjspEsajCpopgProvider",
    "TjspNugepnacProvider",
    "TreSpTemasProvider",
    "TnuEprocJurisprudenciaProvider",
    "Trf2EprocJurisprudenciaProvider",
    "Trf4EprocJurisprudenciaProvider",
    "Trf6EprocJurisprudenciaProvider",
]
