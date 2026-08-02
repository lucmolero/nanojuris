# Quickstart

## Instale para desenvolvimento

```bash
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

## Busque precedentes

```python
from nanojuris import NanoJurisClient

client = NanoJurisClient()
page = client.search(
    "ICMS consumidor final",
    courts=["STF", "STJ"],
    types=["RG", "RR"],
    page_size=5,
)

print(page.total)
print(page.results[0].to_dict())
```

## Use a CLI

```bash
nanojuris buscar "ICMS consumidor final" --orgaos STF,STJ --tipos RG,RR --limite 5
```

## Consulte decisoes vinculadas

```bash
nanojuris precedente stf-rg-615
```

## Liste catalogo BNP/Pangea

```bash
nanojuris parametros --catalogo
```

## Consulte sugestoes publicas

```bash
nanojuris sugestoes "icms"
```
