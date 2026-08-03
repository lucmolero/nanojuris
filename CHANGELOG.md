# Changelog

Todas as mudancas relevantes deste projeto serao documentadas aqui.

## 0.1.0 - 2026-08-02

- Fundacao inicial do NanoJuris.
- Provider BNP/Pangea com API publica de precedentes.
- Modelos tipados para precedentes, casos paradigma, decisoes e pagina de busca.
- Cliente Python, CLI, exportadores JSONL/Markdown e testes automatizados.

## Unreleased

- Catalogo normalizado do BNP/Pangea para orgaos e especies.
- Sugestoes publicas de busca expostas no provider, cliente e CLI.
- Fixtures cobrindo RG, RR, IAC, IRDR, SUM e SV.
- Testes live opcionais controlados por `NANOJURIS_RUN_LIVE=1`.
- Provider TJSP/CJSG com parser HTML, fixture sanitizada e deteccao de captcha.
- Providers publicos adicionados para Comunica PJe/DJEN, TJDFT/SISTJ,
	TJAC/TJAL/TJAM/TJMS CJSG, STM/JMU, TJSP/eproc, TJSP/e-SAJ CPOPg,
	TRF4/eproc e STJ/SCON.
- Modelos canonicos, store SQLite, exportacao CSV/JSONL/Markdown, CLI expandida
	e tools MCP locais.
- Fluxo de descoberta documentado para promover somente rotas reproduzidas com
	`requests` limpo, sem login, captcha, cookies ou bypass.
