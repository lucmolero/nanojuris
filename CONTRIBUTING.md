# Contributing

Obrigado por considerar contribuir com o NanoJuris.

## Principios

- Prefira APIs oficiais ou fluxos publicos documentaveis.
- Nao implemente bypass de captcha, login, segredo de justica ou bloqueios.
- Todo provider deve ter testes com fixtures sem rede.
- Toda resposta externa deve preservar rastreabilidade da fonte.
- Mudancas de parser precisam incluir fixture representativa.

## Ambiente

```bash
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m pytest
```

## Checklist

- [ ] Testes adicionados ou atualizados.
- [ ] Documentacao atualizada quando houver API publica nova.
- [ ] Sem credenciais, tokens, cookies ou dados sensiveis em fixtures.
- [ ] Sem automacao para contornar controles de acesso.
