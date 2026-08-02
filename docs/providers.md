# Providers

## `bnp_pangea`

Provider inicial do NanoJuris.

Endpoints publicos usados:

```text
GET  /parametros
GET  /sugestoes?texto=<termo>
POST /precedentes
GET  /precedentes/{id}/decisoes
```

Campos de filtro:

```text
buscaGeral
todasPalavras
quaisquerPalavras
semPalavras
trechoExato
atualizacaoDesde
atualizacaoAte
cancelados
ordenacao
nr
orgaos
tipos
pagina
tamanhoPagina
```

## Planejados

- `tjsp_cjsg`
- `stj`
- `stf`
- `tse`
- `trf4`
- `tst`
