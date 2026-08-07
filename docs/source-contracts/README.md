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

Use `nanojuris contratos --fonte <provider>` para comparar o dossie com a
matriz viva declarada pelo codigo.
