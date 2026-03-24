import pandas as pd
from model import calculate_pension_cashflows, print_pension_table
from unittest.mock import patch, MagicMock

def test_calculate_pension_cashflows_with_df():
    # Create a mock mortality table
    mock_mortality = pd.DataFrame({
        "age": list(range(100)),
        "qx": [0.01] * 100  # flat 1% mortality for simplicity
    })

    # Call function with a DataFrame instead of a file
    df = calculate_pension_cashflows(
        mortality_df=mock_mortality,
        starting_age=65,
        base_benefit=10000,
        n_years=5,
        discount_rate=0.03
    )

    # Basic structural checks
    assert df.shape[0] == 6  # 5 years + totals row
    assert "cashflow" in df.columns
    assert "present_value" in df.columns
    assert df.iloc[-1]["year"] == "Total"

    # Cashflow values are positive
    assert df["cashflow"].iloc[:-1].sum() > 0

    # Present value is less than cashflow due to discounting at positive interest rate
    assert all(df["present_value"].iloc[:-1] <= df["cashflow"].iloc[:-1])
    
# -----------------------------
# 2️⃣ calculate_pension_cashflows edge cases
# -----------------------------
def test_calculate_pension_cashflows_edge_cases():
    # Mock mortality table
    mortality = pd.DataFrame({
        "age": [65, 66, 67],
        "qx": [0.01, 0.02, 0.03]
    })

    # n_years = 0
    df = calculate_pension_cashflows(
        mortality_df=mortality,
        starting_age=65,
        base_benefit=10000,
        n_years=0
    )
    assert df.shape[0] == 1  # only totals row
    assert df.iloc[0]["year"] == "Total"

    # starting_age beyond table
    df = calculate_pension_cashflows(
        mortality_df=mortality,
        starting_age=70,
        base_benefit=10000,
        n_years=3
    )
    # survival_prob and cashflow should be zero
    assert (df["survival_prob"].iloc[:-1] == 0).all()
    assert (df["cashflow"].iloc[:-1] == 0).all()
    
# -----------------------------
# 3️⃣ print_pension_table coverage
# -----------------------------
def test_print_pension_table_output(capsys):
    df = pd.DataFrame({
        "year": [1, 2, "Total"],
        "cashflow_formatted": ["100", "100", "200"],
        "present_value_formatted": ["90", "85", "175"]
    })

    print_pension_table(df)
    captured = capsys.readouterr()
    # Ensure key content is in output
    assert "Pension Cashflow Table" in captured.out
    assert "100" in captured.out
    assert "200" in captured.out


# test_model_cli.py
import pytest
from unittest.mock import patch
import model

def test_main_cli(monkeypatch):
    # Fake command-line arguments
    test_args = [
        "prog",
        "-mort", "fake_mort.xlsx",
        "-age", "30",
        "-benefit", "1000",
        "-n", "10",
        "-r", "0.05"
    ]
    monkeypatch.setattr("sys.argv", test_args)

    # Mock calculate_pension_cashflows and print_pension_table
    mock_df = "mocked_dataframe"
    with patch("model.calculate_pension_cashflows", return_value=mock_df) as mock_calc, \
         patch("model.print_pension_table") as mock_print:
        # Call the CLI function
        model.main_cli()

        # Check that calculate_pension_cashflows was called correctly
        mock_calc.assert_called_once_with(
            mortality_file="fake_mort.xlsx",
            starting_age=30.0,
            base_benefit=1000.0,
            n_years=10,
            discount_rate=0.05
        )

        # Check that print_pension_table was called with the mock DataFrame
        mock_print.assert_called_once_with(mock_df)
