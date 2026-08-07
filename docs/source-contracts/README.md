# Dossies De Fonte

Esta pasta reune dossies tecnicos por provider. Cada arquivo deve registrar o
contrato publico observado, lacunas, fixtures e criterios de uso via MCP.

Comece pelos providers de maior impacto:

- `tjdf_juris.md`: fonte madura para demonstracoes e estudos iniciais.
- `tjsp_cjsg.md`: fonte de alto valor, com risco de captcha/controle de acesso.
- `stf_juris.md`: API JSON oficial observada no frontend de jurisprudencia do STF.
- `stf_informativo.md`: planilha publica estruturada do Informativo STF.
- `stj_informativo.md`: HTML publico do Informativo de Jurisprudencia do STJ.
- `stj_scon.md`: fonte superior estrategica, ainda em contrato inicial.
- `bnp_pangea.md`: precedentes qualificados nacionais.
- `trf4_eproc_jurisprudencia.md`: eproc federal com bom potencial de inteiro teor.
- `eproc_jurisprudencia_federal.md`: TNU/TRF2/TRF6 como expansao federal da familia eproc.
- `tjgo_projudi_jurisprudencia.md`: PROJUDI/TJGO com resultado HTML publico e inteiro teor embutido.
- `tjma_jurisconsult.md`: API TJMA parcial para metadados, sumulas/IAC/IRDR; busca principal com captcha.
- `justica_eleitoral_sjur.md`: API SJUR/TSE/TREs parcial para classes e relatorias; busca principal com antirrobo.
- `trt2_pje_jurisprudencia.md`: PJe/TRT2 com opcoes publicas e documentos bloqueados por desafio.
- `tjac_cjsg.md`: CJSG/e-SAJ/TJAC com resultado publico validado por numero.

Use `nanojuris contratos --fonte <provider>` para comparar o dossie com a
matriz viva declarada pelo codigo.
