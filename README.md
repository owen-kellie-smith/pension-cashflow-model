# pension-cashflow-model

![Python Tests](https://github.com/owen-kellie-smith/pension-cashflow-model/actions/workflows/python-tests.yml/badge.svg)

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

## Run the tests

```bash
pytest
```

## Run the model

```bash
python3 model.py -mort "assets/xls/pma92.xls" -age 65
```
to get output like
```
Pension Cashflow Table:
 year cashflow_formatted present_value_formatted
    1           9,877.89                9,590.18
    2           9,739.28                9,180.21
    3           9,582.60                8,769.43
    4           9,406.26                8,357.34
    5           9,208.75                7,943.55
Total          47,814.78               43,840.71
```
where cashflow_formatted are expected amounts paid at the end of each year to survivors age 65 at the start of year 1, and present_value_formatted are the expected amounts discounted at 3% p.a. 


