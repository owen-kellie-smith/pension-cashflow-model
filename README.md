# pension-cashflow-model

![Python Tests](https://github.com/owen-kellie-smith/pension-cashflow-model/actions/workflows/ci.yml/badge.svg)

A simple actuarial-style model written in Python.

---

Features:
- models pension cashflows
- reads mortality rates from a standard spreadsheet (.xls)
- calculates discounted liabilities

# Getting started
## Use a virtual environment venv

```bash
python3 -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

## Run the model

```bash
python3 model.py
```

## Run the tests

```bash
pytest
```

