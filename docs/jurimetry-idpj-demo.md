# Demo De Jurimetria: IDPJ

Esta demo existe para testar o NanoJuris em uma pergunta juridica comum sem
transformar a biblioteca em opiniao juridica automatica. O foco e extracao:
fontes consultadas, erros, campos retornados, amostra e rastreabilidade.

## Pergunta De Teste

```text
incidente de desconsideracao da personalidade juridica
```

Esse termo e bom para teste porque costuma aparecer em jurisprudencia civel,
empresarial, trabalhista e execucao. Tambem ajuda a revelar falsos positivos,
fontes bloqueadas e diferencas de campos entre tribunais.

## Rodar Pelo SDK

```bash
python examples/idpj_jurimetry_demo.py
```

Com fontes explicitas:

```bash
python examples/idpj_jurimetry_demo.py --sources tjdf_juris,trf4_eproc_jurisprudencia,tjsp_cjsg,stj_scon --page-size 3
```

Para inspecionar o payload completo:

```bash
python examples/idpj_jurimetry_demo.py --raw
```

## Rodar Pelo MCP

Prompt recomendado para um agente:

```text
Use o NanoJuris MCP. Primeiro chame source_contracts. Depois pesquise
"incidente de desconsideracao da personalidade juridica" em tjdf_juris,
trf4_eproc_jurisprudencia, tjsp_cjsg e stj_scon com page_size 3.
Explique searched_sources, skipped_sources, routing_summary e errors. Nao faca
conclusao juridica sem revisar os textos completos.
```

## O Que Medir

- cobertura por fonte;
- total de resultados retornados;
- fontes com captcha, indisponibilidade ou contrato alterado;
- tribunal, orgao julgador, relator e periodo;
- existencia de URL de inteiro teor;
- tamanho da ementa ou resumo;
- falsos positivos aparentes.

## Perguntas Para Revisao Juridica

- A decisao trata mesmo de IDPJ ou apenas menciona o termo?
- O pedido foi deferido, indeferido, nao conhecido ou anulado?
- A decisao discute pressupostos materiais ou apenas questao processual?
- Ha padrao por tribunal, camara, relator, ramo ou periodo?
- Os metadados extraidos bastam ou o inteiro teor precisa ser lido?

## Limites

NanoJuris nao deve inferir tese, probabilidade de exito ou aconselhamento sem
revisao humana. Para estudo serio, salve os resultados, leia o inteiro teor
quando publico e registre filtros, data da coleta, fonte e hash dos documentos.
