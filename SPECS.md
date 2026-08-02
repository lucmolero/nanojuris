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
- `get_catalog()` quando metadados puderem ser normalizados.

Todo resultado deve conter:

- fonte;
- tribunal;
- tipo;
- identificador;
- texto principal disponivel;
- URL ou endpoint publico;
- data/hora de coleta;
- limitacoes conhecidas.

## BNP/Pangea v0.1.x

O provider BNP/Pangea deve cobrir:

- parametros brutos;
- catalogo normalizado de orgaos e especies;
- sugestoes publicas;
- busca paginada;
- agregacoes por orgao e especie;
- decisoes vinculadas quando disponiveis;
- testes sem rede;
- testes live opcionais controlados por `NANOJURIS_RUN_LIVE=1`.

## TJSP/CJSG v0.2.x

O provider TJSP/CJSG deve cobrir:

- formulario publico de consulta completa;
- parser HTML de resultados;
- extracao de `cdAcordao` e `cdForo`;
- URL de inteiro teor publico;
- campos de classe, assunto, relator, comarca, orgao julgador e data;
- fixture HTML sanitizada;
- erro explicito para captcha/controle de acesso;
- nenhum bypass de captcha, login ou acesso restrito.
