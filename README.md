# Vatify – Official Python SDK

EU VAT **validation**, **rates**, and **calculation** with one API.

[![PyPI version](https://img.shields.io/pypi/v/vatify.svg)](https://pypi.org/project/vatify/)
[![Python](https://img.shields.io/pypi/pyversions/vatify.svg)](https://pypi.org/project/vatify/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

- Website: https://vatifytax.app  
- Docs: https://vatifytax.app

---

## Install

```bash
pip install vatify
```

## Set your API Key

```bash
export VATIFY_API_KEY="your_api_key"
```

## Quickstart (sync)
```python
from vatify import Vatify

client = Vatify(api_key="YOUR_API_KEY")

# 1) Validate VAT number
res = client.validate_vat("DE123456789")
print(res.valid, res.country_code, res.name)

# 2) Calculate VAT rate (by country, type, date)
calc = client.calculate(country_code="DE", rate_type="standard", supply_date="2025-09-23")
print(calc.rate_percent)

# 3) Get rates for a country
rates = client.rates("DE")
for r in rates:
    print(r.rate_type, r.rate_percent)

client.close()
```

## Quickstart (async)
```python
import asyncio
from vatify import VatifyAsync

async def main():
    client = VatifyAsync(api_key="YOUR_API_KEY")
    res = await client.validate_vat("DE123456789")
    print(res.valid)
    await client.aclose()

asyncio.run(main())
```

## Quickstart (cli)
```bash
vatify validate DE123456789
vatify rates DE
vatify calculate DE standard 2025-09-23
```

## Error Handling
All API/network issues raise `VatifyError` with optional `status_code` and `details`.
```python
from vatify import Vatify, VatifyError

try:
    Vatify(api_key="x").validate_vat("DE123")
except VatifyError as e:
    print("Failed:", e, e.status_code)
```


## Contributing
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"  # (optional if you add dev deps)
pytest -q
```

### Build and upload
```bash
python -m pip install --upgrade build twine
python -m build
twine upload dist/*
```


