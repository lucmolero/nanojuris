# NanoJuris Specs

NanoJuris e uma biblioteca Python para busca, normalizacao e auditoria de
jurisprudencia publica brasileira.

## Escopo

- Precedentes qualificados.
- Jurisprudencia publica.
- Acordaos, decisoes monocraticas, sumulas, informativos e teses quando
  disponibilizados publicamente.
- Extracao responsavel, com rastreabilidade e limites.

## Fora de escopo

- Bypass de captcha.
- Conteudo protegido por login, segredo de justica ou acesso restrito.
- Parecer juridico automatizado sem revisao humana.
- Scraping agressivo ou coleta massiva sem governanca.

## Providers planejados

- `bnp_pangea`: Banco Nacional de Precedentes/Pangea.
- `tjsp_cjsg`: Consulta de Jurisprudencia do Segundo Grau do TJSP.
- `stj`: Jurisprudencia e repetitivos do STJ.
- `stf`: Jurisprudencia, repercussao geral e sumulas do STF.
- `tse`: Jurisprudencia eleitoral TSE/TREs.
- `trf4`: Jurisprudencia federal/eproc.
- `tst`: Jurisprudencia trabalhista.

## Contrato minimo

Todo provider deve implementar:

- `search(query)`
- `get_decisions(precedent_id)`
- `get_parameters()` quando a fonte tiver metadados publicos.

Todo resultado deve conter:

- fonte;
- tribunal;
- tipo;
- identificador;
- texto principal disponivel;
- URL ou endpoint publico;
- data/hora de coleta;
- limitacoes conhecidas.
