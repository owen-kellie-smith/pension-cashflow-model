# pension-cashflow-model

![Python Tests](https://github.com/owen-kellie-smith/pension-cashflow-model/actions/workflows/python-tests.yml/badge.svg)
[![codecov](https://codecov.io/gh/owen-kellie-smith/pension-cashflow-model/graph/badge.svg?token=WXTCICVPA0)](https://codecov.io/gh/owen-kellie-smith/pension-cashflow-model)

A simple actuarial-style model written in Python.

---

Features:
- models pension cashflows
- reads mortality rates from a standard spreadsheet (.xls)
- reads model points from a model point file
- calculates discounted liabilities
- aggregates results over various indices

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
and expect all tests to pass.

## Run the test coverage

```bash
pytest --cov=./ --cov-report=html
```
and see in `htmlcov/index.html` that test coverage (i.e. code run through some test) is close to the amount shown on the badge at the top of this README.


## Run the model for a single record specified in the command line

```bash
python3 model.py -mort "assets/xls/pma92.xls" -age 65 -benefit 10000 -n10 -r 0.03
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
    6           8,988.65                7,527.85
    7           8,744.72                7,110.26
    8           8,475.98                6,691.02
    9           8,181.75                6,270.63
   10           7,861.81                5,849.92
Total          90,067.69               77,290.40
```
where cashflow_formatted are expected amounts of 10,000 paid at the end of each year to survivors age 65 at the start of year 1, and present_value_formatted are the expected amounts discounted at 3% p.a. 

## Run the model for multiple records defined in a model point file

Aggregate over all indices (i.e. over all projection years and all records) to get a single sum:
```bash
python3 run_model.py -mp assets/csv/MPF.csv -a assets/xls -n 10 -r 0.03 -agg sum
```
to get output like
```
     benefit_pp     cashflow  present_value
All    500000.0  452801.3762    388434.6276
```
The total benefit_pp of 500,000 comes from the fact that in the model point file benefit_pa happens to be 10,000 for each of 5 records.  
5 records * 10,000 / year (per record) * 10 projected years = 500,000.  

Aggregate over records only (i.e. separate results by projection year)
```bash
python3 run_model.py -mp assets/csv/MPF.csv -a assets/xls -n 10 -r 0.03 -agg sum_year
```
to get output like
```
      benefit_pp      cashflow  present_value
year                                         
1        50000.0  49416.800000   47977.475728
2        50000.0  48756.050944   45957.254165
3        50000.0  48010.369319   43936.289045
4        50000.0  47172.368719   41912.038626
5        50000.0  46234.888304   39882.620796
6        50000.0  45191.209607   37846.926586
7        50000.0  44035.349616   35804.768972
8        50000.0  42762.395085   33757.029561
9        50000.0  41368.854291   31705.782127
10       50000.0  39853.090316   29654.441994
```
In this case the benefit_pp of 50,000 per year is simply 5 records * 10,000 / year (per record) = 50,000 per year.  





