## Summary

Describe the change and the legal/technical context.

## Checklist

- [ ] Tests were added or updated.
- [ ] Documentation was updated when public behavior changed.
- [ ] No credentials, cookies, tokens or sensitive data were committed.
- [ ] No captcha, login or access-control bypass was introduced.
- [ ] Source trace and limitations remain clear for new providers.

## Validation

```text
python -m pytest --cov
python -m ruff check src tests
python -m mypy src
```
