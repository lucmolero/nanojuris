# `tjpb_pje_jurisprudencia`

## Identidade

- Fonte oficial: Banco de Jurisprudencia PJe do TJPB.
- Categoria: `court_jurisprudence`.
- Familia tecnica: `pje_jurisprudencia_estadual`.
- URL inicial: `https://pje-jurisprudencia.tjpb.jus.br/`.
- Status de acesso: candidato forte com risco WAF/Cloudflare.
- Status no NanoJuris: candidato, ainda sem provider implementado.

## Contrato HTTP

- Rota observada:
  - `GET /`
- Sinais do formulario:
  - ementa;
  - inteiro teor;
  - numero do processo;
  - classe;
  - orgao julgador;
  - relator;
  - data;
  - origem de documento.
- Metodo/payload de busca: pendente de HAR.
- Paginacao: indicada pela UI, ainda nao reproduzida.

## Dados retornados

- Campos esperados:
  - numero do processo;
  - classe;
  - orgao julgador;
  - relator;
  - data;
  - ementa;
  - inteiro teor ou link.
- Campos canonicos esperados: `CanonicalDecision`.
- Inteiro teor: pendente.

## Comportamento observado

- Probe `requests` com User-Agent NanoJuris: HTTP 200 e formulario publico.
- `Invoke-WebRequest`/PowerShell: Cloudflare managed challenge.
- Busca com resultado: ainda precisa fixture.
- Risco: alto enquanto o desafio variar por cliente.

## Fixtures

- [ ] HTML inicial sem desafio.
- [ ] HAR de busca real.
- [ ] Resultado com ementa.
- [ ] Busca vazia.
- [ ] Resposta Cloudflare/challenge para diagnostico.

## MCP e agentes

- Quando usar: somente depois de chamada reproduzivel sem desafio.
- Quando pular: se o ambiente receber Cloudflare, captcha ou desafio.
- Mensagem segura: "A fonte TJPB/PJe mostra formulario publico, mas o acesso
  automatizado deve respeitar eventuais desafios sem bypass."
- Riscos: variacao de WAF por cliente/ambiente.

## Proximos passos

- [ ] Gravar HAR de busca simples.
- [ ] Confirmar se a busca reproduz por `requests`.
- [ ] Criar fixture de desafio para erro seguro.
- [ ] Implementar somente se houver fluxo publico estavel.
