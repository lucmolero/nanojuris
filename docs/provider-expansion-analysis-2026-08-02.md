# Provider Expansion Analysis - 2026-08-02

Este documento consolida a verificacao dos providers existentes e das proximas
expansoes do NanoJuris. A regra operacional permanece: rota so vira contrato de
provider depois de reproducao com sessao HTTP limpa, sem cookies de navegador,
login, captcha solving, HAR privado ou token reaproveitado.

## Resumo executivo

Prioridade imediata:

1. `comunica_pje`: expandir filtros objetivos ja validados, especialmente
   `dataDisponibilizacaoInicio` e `dataDisponibilizacaoFim`.
2. `bnp_pangea`: investigar por que termos criminais como `infanticidio` e
   `homicidio` retornam HTTP 400, enquanto `ICMS` funciona pelo provider.
3. `tjms_cjsg`: aproveitar a rota limpa CJSG para paginacao e filtros
   estruturados reaproveitando o parser generico de `tjsp_cjsg`.
4. `tjdf_juris`: completar paginacao/variantes de busca do SISTJ; a rota limpa
   ja esta implementada e e estrategica para jurisprudencia estadual fora SP.
5. `stj_scon` e `tjsp_cjsg`: manter postura diagnostics-first porque os probes
   limpos mostram controle de acesso/captcha/sessao.
6. Familia e-SAJ CPOPg: extrair base parametrizada depois de validar tribunais
   adicionais com numeros publicos reais.

## Evidencia live desta verificacao

### Comunica PJe/DJEN

Rota base:

```text
GET https://comunicaapi.pje.jus.br/api/v1/comunicacao
```

Resultados observados com sessao limpa:

```text
texto=infanticidio&pagina=0&size=2
  -> HTTP 200, JSON, count=1260, items retornados mesmo com size=2

texto=infanticidio&dataDisponibilizacaoInicio=2026-07-31&dataDisponibilizacaoFim=2026-07-31&pagina=0&size=2
  -> HTTP 200, JSON, count=1, first_date=2026-07-31

texto=infanticidio&data_inicio=2026-07-31&data_fim=2026-07-31&pagina=0&size=2
  -> HTTP 200, mas count=1260; parametros curtos ignorados pela API

/api/v1/comunicacao/tipos
  -> HTTP 422, mensagem de comunicacao nao encontrada

/api/v1/tribunais
  -> HTTP 404
```

Conclusao: filtro por data de disponibilizacao esta validado e deve ser tratado
como contrato implementado. Catalogos REST simples de tipos/tribunais nao foram
confirmados.

### BNP/Pangea

Pelo provider atual:

```text
NanoJurisClient().search('ICMS', source='bnp_pangea', courts=['STF','STJ'], types=['RG','RR'], page_size=1)
  -> OK, total=100, primeiro id stf-rg-615

NanoJurisClient().search('infanticidio', source='bnp_pangea', page_size=1)
  -> SourceUnavailableError, HTTP 400

NanoJurisClient().search('homicidio', source='bnp_pangea', page_size=1)
  -> SourceUnavailableError, HTTP 400
```

Conclusao: o provider esta vivo, mas ha rejeicao especifica de termos criminais.
A expansao correta aqui e diagnosticar contrato/payload e mensagem de erro, nao
adicionar filtros sem evidencia.

Decisao implementada: erros HTTP 4xx do BNP agora preservam um resumo do corpo
da resposta e o payload enviado. No caso `infanticidio`, o smoke live retornou:

```text
SourceUnavailableError
BNP rejected request with HTTP 400; response='Requisição inválida'; payload={...buscaGeral: 'infanticidio'...}
```

### TJDF/SISTJ

Rota limpa validada:

```text
GET https://pesquisajuris.tjdft.jus.br/IndexadorAcordaos-web/sistj?visaoId=...&argumentoDePesquisa=infanticidio&pagina=1
  -> HTTP 200, HTML SISTJWEB, sem captcha/login, sinais de acordao presentes

GET ...&numeroDoDocumento=1917641
  -> HTTP 200, HTML SISTJWEB, sem captcha/login
```

Conclusao: provider P0 ja implementado. Proxima expansao deve focar paginacao,
variantes de base/documento e melhor captura de inteiro teor quando o link publico
estiver exposto.

### TJMS/CJSG

Rota limpa validada:

```text
POST https://esaj.tjms.jus.br/cjsg/resultadoCompleta.do
  dados.buscaInteiroTeor=infanticidio
  -> HTTP 200, HTML CJSG com acordaos, sem captcha/recaptcha/uuidCaptcha
```

O HTML inclui scripts de login do SAJ, mas retornou conteudo de acordaos
parseavel. Isso nao e bloqueio por si so; o bloqueio relevante e captcha/retorno
a formulario sem resultados.

Conclusao: melhor alvo CJSG para expansao live. Implementar paginacao e filtros
estruturados primeiro no parser/payload compartilhado.

Tentativa rejeitada nesta rodada: mapear `published_from/published_to` para
`dados.dtPublicacaoInicio/Fim`. Mesmo a faixa ampla `01/01/1900` a `31/12/2099`
zerou a busca `infanticidio`, enquanto a mesma busca sem data retornou 22
resultados. Portanto, esse filtro nao foi promovido no provider.

### TJSP/CJSG

Rota testada:

```text
POST https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do
  dados.buscaInteiroTeor=infanticidio
  -> HTTP 200, mas com captcha, recaptcha, uuidCaptcha, sajcas/login e verificacao
```

Conclusao: manter provider com diagnostico e parser offline/fixture. Nao prometer
coleta live sem controle de acesso.

### STJ/SCON

Rota testada:

```text
GET https://processo.stj.jus.br/SCON/pesquisar.jsp?livre=infanticidio
  -> redirect/final em /SCON/, HTML grande com sinais de captcha, recaptcha,
     Cloudflare/verificacao e login
```

Conclusao: manter ficha tecnica e parser offline; live depende de API publica ou
contrato institucional. `get_decisions()` pode ser preparado com fixture, mas nao
deve assumir acesso limpo.

## Matriz por provider

| Provider | Estado atual | Melhor expansao | Evidencia | Risco |
| --- | --- | --- | --- | --- |
| `comunica_pje` | API JSON publica | Data de disponibilizacao; depois tipos se endpoint real for descoberto | Data range validado com count=1 | Baixo |
| `bnp_pangea` | API publica viva para termos comuns | Diagnostico HTTP 400 criminal; contrato atual do frontend | `ICMS` OK, criminais HTTP 400 | Medio |
| `tjms_cjsg` | CJSG live limpo | Paginacao, filtros de relator/comarca/classe/assunto/publicacao | POST limpo com acordaos | Medio |
| `tjdf_juris` | SISTJ live limpo | Paginacao completa e variantes de documento/base | Search/detalhe HTTP 200 | Medio |
| `tjsp_esaj_cpopg` | CPOPg expandido | Classe base e-SAJ parametrizada; mais modos por probe real | NUMPROC/NMPARTE/NUMOAB validados | Medio |
| `tjsp_cjsg` | Parser e diagnostico | Offline + diagnostics; filtros so se rota limpa voltar | Captcha/recaptcha/uuidCaptcha | Alto |
| `stj_scon` | Parser offline/ficha | Contato/API publica; get_document com fixture | Controle/Cloudflare/recaptcha | Alto |

## Backlog de implementacao recomendado

### P0 - Aplicar agora

- `comunica_pje`: `published_from` e `published_to` mapeando para
  `dataDisponibilizacaoInicio` e `dataDisponibilizacaoFim`.
- Documentar que `data_inicio/data_fim` nao filtram a API observada.
- Testar CLI/Python com termo + data.

### P1 - Proxima rodada curta

- `bnp_pangea`: continuar a descoberta do contrato que rejeita termos criminais;
  o diagnostico especifico de HTTP 400 com corpo e payload ja foi implementado.
- `tjms_cjsg`: implementar paginacao por `trocaDePagina.do` se o
  `conversationId` limpo estiver presente; adicionar fixture multipagina.
- `tjdf_juris`: garantir que `page > 1` usa pagina real do SISTJ e nao apenas
  corta a primeira pagina localmente.

### P2 - Expansao estrutural

- Extrair uma base `EsajCpopgProvider` parametrizada por tribunal/base_url.
- Criar allowlist de tribunais e-SAJ aprovados somente apos probe limpo com
  numero publico real.
- Padronizar filtros estruturados CJSG em `JurisprudenceQuery` ou em `filters`
  tipado, antes de expor relator/comarca/classe/assunto no CLI.

### P3 - Bloqueados ou institucionais

- `stj_scon`: continuar com parser offline e contato institucional para API ou
  acesso responsavel.
- `tjsp_cjsg`: manter deteccao de controle de acesso e evitar qualquer fluxo de
  captcha/login.
- DataJud/CNJ: requer credencial; nao tratar como fonte anonima.

## Criterios de aceite para expansao

Uma expansao so deve entrar no provider quando cumprir estes pontos:

1. Probe limpo reproduzido com status e conteudo juridico objetivo.
2. Fixture offline minima salva em `tests/fixtures`.
3. Parser testado sem rede.
4. Capabilities atualizadas com campos e limitacoes.
5. Teste live opt-in quando a rota for estavel.
6. Documentacao em `docs/providers.md` e `docs/source-discovery.md`.

## Decisao desta rodada

Implementado nesta rodada: `comunica_pje` passou a aceitar filtro de data de
publicacao/disponibilizacao por `published_from` e `published_to`, integrado ao
SDK e CLI como `--publicacao-de` e `--publicacao-ate`. O BNP tambem passou a
emitir diagnostico rico em HTTP 4xx para apoiar a descoberta de contrato. A
promocao de data de publicacao em CJSG foi testada e descartada por enquanto por
falhar no smoke limpo do TJMS.
