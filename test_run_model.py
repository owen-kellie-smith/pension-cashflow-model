# test_run_model.py
import pytest
import pandas as pd
import os
from unittest.mock import patch, MagicMock
import run_model


# ------------------------------------------------
# Test parse_args
# ------------------------------------------------
def test_parse_args(monkeypatch):
    test_args = [
        "prog",
        "-mp", "model_points_monkey.csv",
        "-a", "assets_monkey",
        "-n", "10",
        "-r", "0.03",
        "-agg", "sum",
        "-o", "output_monkey.csv"
    ]
    monkeypatch.setattr("sys.argv", test_args)
    # without monkeypatch the next line run_model.parse_args() would use arguments for e.g. pytest
    args = run_model.parse_args()
    assert args.model_point_file == "model_points_monkey.csv"
    assert args.assets_folder == "assets_monkey"
    assert args.projection_years == 10
    assert args.interest_rate == 0.03
    assert args.aggregation_type == "sum"
    assert args.output_file == "output_monkey.csv"


# ------------------------------------------------
# Test read_model_points
# ------------------------------------------------
def test_read_model_points(tmp_path):
    # Create a temporary CSV
    csv_file = tmp_path / "mp.csv"
    df = pd.DataFrame({"age_at_vdate": [30.0], "benefit_pa": [1000.0], "mortality": ["mort.csv"]})
    df.to_csv(csv_file, index=False)

    result = run_model.read_model_points(str(csv_file))
    pd.testing.assert_frame_equal(result, df)

def test_read_model_points_file_not_found():
    with pytest.raises(FileNotFoundError):
        run_model.read_model_points("nonexistent.csv")


# ------------------------------------------------
# Test run_model_point
# ------------------------------------------------
@patch("run_model.read_excel_mortality_table")
@patch("run_model.calculate_pension_cashflows")
def test_run_model_point(mock_calc, mock_read_mort, tmp_path):
    # Decorators are applied from the bottom up, but 
    # the mock arguments are passed into the test function from left to right 
    # corresponding to the decorators from the bottom up.
    # so mock_calc becomes the replacement for run_model.calculate_pension_cashflows and
    # and mock_read_mort becomes the replacement for run_model.read_excel_mortality_table

    # Setup mock return
    mock_df = pd.DataFrame({"year": [1, 2], "benefit_pp": [100, 200], "cashflow": [100, 200], "present_value": [95, 180]})
    mockmort_df = pd.DataFrame({"Age": [61, 62], "qx": [0.01, 0.02]})
    mock_calc.return_value = mock_df
    mock_read_mort.return_value = mockmort_df

    # Create fake mortality file
    mortality_file = tmp_path / "mort.csv"
    mortality_file.write_text("dummy")

    row = {"age_at_vdate": 30, "benefit_pa": 1000, "mortality": "mort.csv"}
    df = run_model.run_model_point(row, str(tmp_path), 10, 0.03)

    pd.testing.assert_frame_equal(df, mock_df)
    mock_calc.assert_called_once_with(
        mortality_df=mockmort_df,
        starting_age=30,
        base_benefit=1000,
        n_years=10,
        discount_rate=0.03
    )

def test_run_model_point_mortality_file_not_found():
    row = {"age_at_vdate": 30, "benefit_pa": 1000, "mortality": "missing.csv"}
    with pytest.raises(FileNotFoundError):
        run_model.run_model_point(row, "nonexistent_folder", 10, 0.03)


# ------------------------------------------------
# Test run_all_model_points
# ------------------------------------------------
@patch("run_model.run_model_point")
def test_run_all_model_points(mock_run):
    mock_run.return_value = pd.DataFrame({"year": [1], "benefit_pp": [100], "cashflow": [100], "present_value": [95]})
    mp_df = pd.DataFrame([
        {"age_at_vdate": 30, "benefit_pa": 1000, "mortality": "mort1.csv"},
        {"age_at_vdate": 40, "benefit_pa": 2000, "mortality": "mort2.csv"}
    ])
    args = MagicMock()
    args.assets_folder = "assets"
    args.projection_years = 10
    args.interest_rate = 0.03

    results = run_model.run_all_model_points(mp_df, args)
    assert len(results) == 2
    for df in results:
        assert "year" in df.columns
    assert mock_run.call_count == 2


# ------------------------------------------------
# Test aggregate_results
# ------------------------------------------------
def test_aggregate_results():
    df1 = pd.DataFrame({"year": [1, 2, "Total"], "benefit_pp": [100, 200, 300],
                        "cashflow": [100, 200, 300], "present_value": [90, 180, 270]})
    df2 = pd.DataFrame({"year": [1, 2, "Total"], "benefit_pp": [50, 75, 125],
                        "cashflow": [50, 75, 125], "present_value": [45, 70, 115]})

    results = [df1, df2]

    # year_record
    agg = run_model.aggregate_results(results, "year_record")
    assert ("year", "record") == agg.index.names

    # sum_year
    agg = run_model.aggregate_results(results, "sum_year")
    assert agg.loc[1, "benefit_pp"] == 150 # = 100 (df1) + 50 (df2)
    assert agg.loc[2, "cashflow"] == 275 # = 200 (df1) + 75 (df2)

    # sum_record
    agg = run_model.aggregate_results(results, "sum_record")
    assert agg.loc[1, "benefit_pp"] == 300 # = 100 + 200
    assert agg.loc[2, "present_value"] == 115 # = 45 + 70

    # sum
    agg = run_model.aggregate_results(results, "sum")
    assert agg["benefit_pp"]["All"] == 425 # 100 + 200 + 50 + 75  =  300 + 125

    # invalid aggregation_type
    with pytest.raises(ValueError):
        run_model.aggregate_results(results, "invalid")


# ------------------------------------------------
# Test write_output
# ------------------------------------------------
def test_write_output(tmp_path, capfd):
    df = pd.DataFrame({"a": [1, 2]})
    file_path = tmp_path / "out.csv"

    # Normal write
    run_model.write_output(df, str(file_path))
    assert file_path.exists()

    # Overwrite warning
    run_model.write_output(df, str(file_path))
    captured = capfd.readouterr()
    assert "already exists and will be overwritten" in captured.out



import subprocess
import sys

def test_model_runs_without_error_as_in_README_1():
    """
    Test that running model.py with given arguments completes successfully.
    """
    cmd = [
        sys.executable,  # ensures we use the same Python interpreter
        "run_model.py",
        "-mp", "assets/csv/MPF.csv",
        "-a", "assets/xls",
        "-n", "10", 
        "-r", "0.03",
        "-agg", "sum",
        "-o", "out_sum.csv"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    
    # Debug output in case of failure
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    
    assert result.returncode == 0, "model.py did not run successfully"

def test_model_runs_without_error_as_in_README_2():
    """
    Test that running model.py with given arguments completes successfully.
    """
    cmd = [
        sys.executable,  # ensures we use the same Python interpreter
        "run_model.py",
        "-mp", "assets/csv/MPF.csv",
        "-a", "assets/xls",
        "-n", "10", 
        "-r", "0.03",
        "-agg", "sum_year",
        "-o", "out_sum_year.csv"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    
    # Debug output in case of failure
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    
    assert result.returncode == 0, "model.py did not run successfully"
