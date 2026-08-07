# Dossies De Fonte

Esta pasta reune dossies tecnicos por provider e por fonte candidata. Cada
arquivo registra contrato publico observado, lacunas, fixtures e criterios de
uso via MCP.

Regra de manutencao: todo provider implementado em `src/nanojuris/providers`
deve possuir dossie proprio com o mesmo nome. Fontes ainda nao implementadas
devem ficar marcadas como `candidato` para nao serem confundidas com provider
pronto.

Use `nanojuris contratos --fonte <provider>` para comparar o dossie com a
matriz viva declarada pelo codigo.

## Providers Implementados

| Provider | Categoria | Dossie |
| --- | --- | --- |
| `bnp_pangea` | precedentes qualificados | [bnp_pangea.md](bnp_pangea.md) |
| `comunica_pje` | comunicacoes judiciais | [comunica_pje.md](comunica_pje.md) |
| `tnu_eproc_jurisprudencia` | jurisprudencia eproc federal | [eproc_jurisprudencia_federal.md](eproc_jurisprudencia_federal.md) |
| `stf_informativo` | jurisprudencia curada | [stf_informativo.md](stf_informativo.md) |
| `stf_juris` | jurisprudencia superior | [stf_juris.md](stf_juris.md) |
| `stj_informativo` | jurisprudencia curada | [stj_informativo.md](stj_informativo.md) |
| `stj_scon` | jurisprudencia superior | [stj_scon.md](stj_scon.md) |
| `stm_jurisprudencia` | jurisprudencia judicial | [stm_jurisprudencia.md](stm_jurisprudencia.md) |
| `tce_sp_jurisprudencia` | jurisprudencia administrativa | [tce_sp_jurisprudencia.md](tce_sp_jurisprudencia.md) |
| `tjac_cjsg` | jurisprudencia CJSG/e-SAJ | [tjac_cjsg.md](tjac_cjsg.md) |
| `tjac_esaj_cpopg` | consulta processual | [tjac_esaj_cpopg.md](tjac_esaj_cpopg.md) |
| `tjal_cjsg` | jurisprudencia CJSG/e-SAJ | [tjal_cjsg.md](tjal_cjsg.md) |
| `tjam_cjsg` | jurisprudencia CJSG/e-SAJ | [tjam_cjsg.md](tjam_cjsg.md) |
| `tjdf_juris` | jurisprudencia judicial | [tjdf_juris.md](tjdf_juris.md) |
| `tjgo_projudi_jurisprudencia` | jurisprudencia judicial | [tjgo_projudi_jurisprudencia.md](tjgo_projudi_jurisprudencia.md) |
| `tjms_cjsg` | jurisprudencia CJSG/e-SAJ | [tjms_cjsg.md](tjms_cjsg.md) |
| `tjpi_juspi` | jurisprudencia judicial | [tjpi_juspi.md](tjpi_juspi.md) |
| `tjsp_cjsg` | jurisprudencia CJSG/e-SAJ | [tjsp_cjsg.md](tjsp_cjsg.md) |
| `tjsp_eproc_jurisprudencia` | jurisprudencia eproc | [tjsp_eproc_jurisprudencia.md](tjsp_eproc_jurisprudencia.md) |
| `tjsp_esaj_cpopg` | consulta processual | [tjsp_esaj_cpopg.md](tjsp_esaj_cpopg.md) |
| `tjsp_nugepnac` | precedentes locais | [tjsp_nugepnac.md](tjsp_nugepnac.md) |
| `tre_sp_temas` | jurisprudencia eleitoral tematica | [tre_sp_temas.md](tre_sp_temas.md) |
| `trf2_eproc_jurisprudencia` | jurisprudencia eproc federal | [eproc_jurisprudencia_federal.md](eproc_jurisprudencia_federal.md) |
| `trf4_eproc_jurisprudencia` | jurisprudencia eproc federal | [trf4_eproc_jurisprudencia.md](trf4_eproc_jurisprudencia.md) |
| `trf6_eproc_jurisprudencia` | jurisprudencia eproc federal | [eproc_jurisprudencia_federal.md](eproc_jurisprudencia_federal.md) |

## Contratos De Pesquisa E Expansao

| Fonte | Status | Dossie |
| --- | --- | --- |
| Justica Eleitoral SJUR/TSE/TREs | contrato parcial | [justica_eleitoral_sjur.md](justica_eleitoral_sjur.md) |
| TJMA JurisConsult | contrato parcial | [tjma_jurisconsult.md](tjma_jurisconsult.md) |
| TRT2 PJe Jurisprudencia | bloqueio/desafio documentado | [trt2_pje_jurisprudencia.md](trt2_pje_jurisprudencia.md) |
| TJRR/Juris JSF | candidato precisa HAR | [tjrr_juris.md](tjrr_juris.md) |
| TJMT Jurisprudencia API | candidato precisa header/payload | [tjmt_jurisprudencia_api.md](tjmt_jurisprudencia_api.md) |
| TJPA Jurisprudencia BFF | candidato precisa payload | [tjpa_jurisprudencia_bff.md](tjpa_jurisprudencia_bff.md) |
| TJPB PJe Jurisprudencia | candidato com risco WAF | [tjpb_pje_jurisprudencia.md](tjpb_pje_jurisprudencia.md) |

## Fila De Desenvolvimento

A ordem de implementacao dos proximos providers fica em
[provider-development-queue.md](../provider-development-queue.md).
