# Audience UX Principles

NanoJuris deve ser uma biblioteca Python direta, acessivel e confiavel para
publicos diferentes que compartilham a mesma necessidade: obter dados publicos de
jurisprudencia brasileira com origem clara, sem interpretacao automatica de
merito juridico.

## Principios gerais

- Toda saida deve deixar claro qual fonte foi consultada.
- Todo erro de acesso deve explicar se a fonte esta indisponivel, bloqueada,
  sujeita a captcha/login ou fora do escopo publico.
- Todo fluxo importante deve existir em Python, CLI e, quando aplicavel, MCP.
- Dados estruturados devem ser exportaveis para CSV, JSONL e Markdown.
- Defaults devem ser conservadores: pagina pequena, timeout, sem live tests por
  padrao e sem coleta agressiva.
- A experiencia deve favorecer revisao humana e auditoria, nao conclusao juridica
  automatica.

## Advogados

Necessidade: localizar jurisprudencia publica, revisar origem e reaproveitar
dados objetivos em pesquisa, memoria ou peca.

UX minima:

- comando CLI simples para buscar e exportar;
- Markdown legivel para revisao;
- URL ou endpoint original quando disponivel;
- mensagem clara quando inteiro teor exigir controle de acesso;
- campos juridicos objetivos como tribunal, classe, assunto, relator, orgao
  julgador, datas e numero do processo.

Exemplo de fluxo:

```bash
nanojuris fontes
nanojuris diagnostico --fonte tjsp_cjsg
nanojuris buscar "dano moral transporte aereo" --fonte tjsp_cjsg --formato markdown
```

## Desenvolvedores

Necessidade: integrar fontes heterogeneas com contratos estaveis e previsiveis.

UX minima:

- API Python tipada;
- dataclasses serializaveis;
- providers isolados;
- erros acionaveis;
- fixtures offline e testes live opt-in;
- guias de provider com ficha tecnica de fonte.

Exemplo de fluxo:

```python
from nanojuris import NanoJurisClient, get_court

client = NanoJurisClient()
print(get_court("TJSP").source_system)
print(client.get_capabilities(source="tjsp_cjsg").to_dict())
```

## Jurimetristas

Necessidade: construir datasets reproduziveis por tribunal, tema, periodo e tipo
de documento.

UX minima:

- CSV e JSONL canonico;
- SQLite local;
- filtros por tribunal, numero, assunto, relator e data;
- `ResearchRun` para repetir e auditar coletas;
- deduplicacao por chave canonica;
- caminho futuro para benchmark de completude por fonte.

Exemplo de fluxo:

```bash
nanojuris buscar "ICMS" --store nanojuris.db --label "ICMS agosto"
nanojuris store query nanojuris.db --tribunal TJSP --limite 50
nanojuris store export nanojuris.db run-... --formato csv
```

## Analistas de dados

Necessidade: auditar, transformar e versionar dados juridicos objetivos em
pipelines de dados.

UX minima:

- hashes de conteudo bruto quando houver documento;
- `SourceTrace` e `ExtractionTrace` preservados;
- exportacao paginada;
- schema canonico completo em JSON;
- campos tabulares estaveis para BI, pandas, DuckDB e warehouses futuros.

## Agentes de IA

Necessidade: usar NanoJuris como ferramenta de dados, sem interpretar merito ou
simular aconselhamento juridico.

UX minima:

- tools MCP pequenas e paginadas;
- `list_sources` e `source_diagnostics` antes da busca;
- limites de pagina para controlar contexto;
- respostas JSON serializaveis;
- status explicito de acesso e extracao;
- nenhum bypass de captcha, login ou segredo de justica.

## Checklist de aceite para novas features

Uma feature nova so deve ser considerada pronta quando responder:

1. O advogado entende de onde veio o dado?
2. O desenvolvedor consegue chamar por API sem ler codigo interno?
3. O jurimetrista consegue exportar e reproduzir o resultado?
4. O analista consegue auditar fonte, hash, status e schema?
5. O agente de IA recebe JSON limitado, rastreavel e sem interpretacao juridica?
6. O comportamento diante de captcha, login ou restricao esta claro e sem bypass?