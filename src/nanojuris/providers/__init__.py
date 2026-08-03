"""Provider implementations."""

from nanojuris.providers.base import JurisprudenceProvider
from nanojuris.providers.bnp_pangea import BnpPangeaProvider
from nanojuris.providers.comunica_pje import ComunicaPjeProvider
from nanojuris.providers.stj_scon import StjSconProvider
from nanojuris.providers.stm_jurisprudencia import StmJurisprudenciaProvider
from nanojuris.providers.tjac_cjsg import TjacCjsgProvider
from nanojuris.providers.tjal_cjsg import TjalCjsgProvider
from nanojuris.providers.tjam_cjsg import TjamCjsgProvider
from nanojuris.providers.tjdf_juris import TjdfJurisProvider
from nanojuris.providers.tjms_cjsg import TjmsCjsgProvider
from nanojuris.providers.tjsp_cjsg import TjspCjsgProvider
from nanojuris.providers.tjsp_eproc_jurisprudencia import TjspEprocJurisprudenciaProvider
from nanojuris.providers.tjsp_esaj_cpopg import TjspEsajCpopgProvider
from nanojuris.providers.trf4_eproc_jurisprudencia import Trf4EprocJurisprudenciaProvider

__all__ = [
	"BnpPangeaProvider",
	"ComunicaPjeProvider",
	"JurisprudenceProvider",
	"StjSconProvider",
	"StmJurisprudenciaProvider",
	"TjacCjsgProvider",
	"TjdfJurisProvider",
	"TjalCjsgProvider",
	"TjamCjsgProvider",
	"TjmsCjsgProvider",
	"TjspCjsgProvider",
	"TjspEprocJurisprudenciaProvider",
	"TjspEsajCpopgProvider",
	"Trf4EprocJurisprudenciaProvider",
]
