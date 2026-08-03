# NanoJuris Specs

NanoJuris e uma biblioteca Python para busca, normalizacao e auditoria de
jurisprudencia publica brasileira.

O foco do projeto e extracao de dados: aquisicao responsavel, parsing,
normalizacao, proveniencia, persistencia e exposicao via CLI/API/MCP. Camadas de
interpretacao juridica, recomendacao de tese ou redacao automatica ficam fora do
core.

## Escopo

- Precedentes qualificados.
- Jurisprudencia publica.
- Acordaos, decisoes monocraticas, sumulas, informativos e teses quando
  disponibilizados publicamente.
- Extracao responsavel, com rastreabilidade e limites.
- Modelos canonicos para decisoes, precedentes e documentos publicos.
- MCP local para agentes de IA consumirem dados auditaveis.

## Fora de escopo

- Bypass de captcha.
- Conteudo protegido por login, segredo de justica ou acesso restrito.
- Parecer juridico automatizado sem revisao humana.
- Scraping agressivo ou coleta massiva sem governanca.
- Interpretacao juridica, classificacao de merito ou recomendacao de argumento
  no pacote core.

## Providers planejados

- `bnp_pangea`: Banco Nacional de Precedentes/Pangea.
- `tjsp_cjsg`: Consulta de Jurisprudencia do Segundo Grau do TJSP.
- `stj_scon`: acordaos publicos do STJ/SCON.
- `stj_precedentes`: repetitivos e precedentes qualificados do STJ.
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

## Contrato premium de extracao

Toda fonte suportada deve declarar:

- capacidades de busca;
- tipos de documento cobertos;
- formatos aceitos;
- status de acesso possiveis;
- campos extraidos;
- fixtures offline sanitizadas;
- teste live opcional;
- limites de uso responsavel.

Todo documento extraido deve preservar:

- hash quando houver conteudo bruto;
- URL ou endpoint publico;
- parser usado;
- versao do parser;
- status de extracao;
- avisos de parcialidade;
- dados brutos necessarios para auditoria.

O pacote deve oferecer exportacao tabular de campos objetivos para uso por
advogados, pesquisadores e pipelines de IA, sem classificar merito juridico.

Cada provider tambem deve declarar `ProviderCapabilities`, permitindo descoberta
por Python, CLI e MCP antes de qualquer consulta externa.

As camadas de aquisicao e parsing devem usar contratos reutilizaveis para
preservar conteudo bruto, hash, status de acesso, `SourceTrace` e
`ExtractionTrace` antes da normalizacao canonica.

O backend de persistencia inicial deve ser SQLite, por acessibilidade e zero
infraestrutura. PostgreSQL deve ser planejado como backend posterior para uso
multiusuario, bases maiores e MCP/API em producao.

As prioridades de produto devem ser validadas por estudos de caso praticos com
advogados, pesquisadores, analistas de dados, desenvolvedores e agentes de IA.

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

## Blueprint de extracao

O plano publico de arquitetura, modelos canonicos, MCP e ordem de implementacao
esta em [docs/elite-extraction-blueprint.md](docs/elite-extraction-blueprint.md).
O contrato de capacidades por fonte esta em [docs/source-capabilities.md](docs/source-capabilities.md).
Os principios de UX por publico estao em [docs/audience-ux.md](docs/audience-ux.md).
