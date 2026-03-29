# Standard library
import argparse
import os
import sys
import math

# Third-party libraries
import pandas as pd 
import numpy as np

# Local application imports
from helpers import read_excel_mortality_table, formatNum, copy_all_output_to_log, between

# ------------------------------------------------
# Argument parsing
# ------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(description="Calculate and display pension cashflow table.")
    parser.add_argument("-mort", "--mortality_file", required=True, help="Path to mortality Excel file")
    parser.add_argument("-age", "--starting_age", type=between(0,199), required=True, help="Starting age")
    parser.add_argument("-benefit", "--base_benefit", type=between(0,math.inf), default=10000, help="Base annual benefit per person")
    parser.add_argument("-n", "--n_years", type=between(0,1000,int), default=5, help="Number of years to project")
    parser.add_argument("-r", "--discount_rate", type=between(-0.2,0.3), default=0.03, help="Discount rate (e.g., 0.03 for 3pc)")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")    
    parser.add_argument("-l", "--log_file", help="Optional log file for output")
    return parser.parse_args()

def survival_function(age_start: float, years: int, mortality_df: pd.DataFrame, debug = False) -> pd.Series:
    """
    Vectorized survival probability calculation with correct edge handling.
    """

    required_cols = {"age", "qx"}
    if not required_cols.issubset(mortality_df.columns):
        raise ValueError("Mortality table must contain columns: age, qx")

    # Extract numpy arrays
    ages = mortality_df["age"].to_numpy()
    qx = mortality_df["qx"].to_numpy()

    # Target ages
    target_ages = age_start + np.arange(years) #np.arange(years) = [0, 1, ..., years-2, years -1]

    # NEW: np.interp with explicit bounds handling
    # values below min(ages) -> 0.0 (no death)
    # values above max(ages) -> 1.0 (certain death)
    qx_interp = np.interp(target_ages, ages, qx, left=0.0, right=1.0)

    survival = np.cumprod(1 - qx_interp)
    if debug:
        print("\n age_start:", age_start)
        print("\n target_ages:", target_ages)
        print("\n qx_interp:", qx_interp)
        print("\n survival:", survival)
        print("\n pd.Series(survival):")
        print(pd.Series(survival))
    return pd.Series(survival)


def calculate_pension_cashflows(
    mortality_file: str = None,
    mortality_df: pd.DataFrame = None,
    starting_age: float = 65,
    base_benefit: float = 10000,
    n_years: int = 5,
    discount_rate: float = 0.03,
    debug: bool = False
) -> pd.DataFrame:
  # Read mortality table using function defined in helpers.py
  """
  Either provide mortality_file (str) OR mortality_df (DataFrame). 
  mortality_df takes priority if given.
  """
  if mortality_df is None:
      if mortality_file is None:
          raise ValueError("Either mortality_file or mortality_df must be provided.")
      mortality_df = read_excel_mortality_table(mortality_file, debug=debug)
  years = np.arange(1, n_years + 1)
  data = pd.DataFrame({
    "year": years,
    "benefit_pp": base_benefit
  })
  # DataFrame is like an Excel sheet i.e. a table. Each item is a column where (key,item) = (column label, Series).

  # -----------------------------
  # Mortality-weighted cashflows 
  # -----------------------------
  data["survival_prob"] = survival_function(starting_age, n_years, mortality_df, debug=debug)
  data["cashflow"] = data["benefit_pp"] * data["survival_prob"]

  # -----------------------------
  # Discounted cashflows
  # -----------------------------
  data["discount_factor"] = (1 + discount_rate) ** (-data["year"]) 
  # adds to data the transformed column discount_factor with formula in terms of existing column labels.
  data["present_value"] = data["cashflow"] * data["discount_factor"]

  # Add running total columns
  data["running_total_cashflow"] = data["cashflow"].cumsum()
  data["running_total_present_value"] = data["present_value"].cumsum()

  # -----------------------------
  # Totals
  # -----------------------------
  # Sum numeric columns
  total_row = data[["benefit_pp","cashflow", "present_value"]].sum()

  # Add label for non-numeric column
  total_row["year"] = "Total"

  # Append as a new row
  data = pd.concat([data, pd.DataFrame([total_row])], ignore_index=True, axis=0)
  # axis = 0 (redundant since 0 is default) means add a row

  # -----------------------------
  # Optional: formatted columns for display
  # -----------------------------
  data["benefit_pp_formatted"] = data["benefit_pp"].map(formatNum)
  data["cashflow_formatted"] = data["cashflow"].map(formatNum)
  data["present_value_formatted"] = data["present_value"].map(formatNum)
  return data

def print_pension_table(df: pd.DataFrame):
  # -----------------------------
  # Print output
  # -----------------------------
  #print("\nData Frame (entire):")
  #print(data)
  #print("\n")
  print("\nPension Cashflow Table:")
  print(df[["year", "benefit_pp_formatted", "cashflow_formatted", "present_value_formatted"]].to_string(index=False))
  # index = False: leave out the 0,1,2,... row count


# -----------------------------
# CLI main function
# -----------------------------
def main_cli():
    
    args = parse_args()

    if not( args.log_file is None):
        with open(args.log_file, "w") as f:
            full_path = os.path.abspath(__file__)
            f.write(full_path)
            f.write("\nCommand used:\n")
            f.write(" ".join(sys.argv) + "\n\n")
        copy_all_output_to_log(args.log_file)

    df = calculate_pension_cashflows(
        mortality_file=args.mortality_file,
        starting_age=args.starting_age,
        base_benefit=args.base_benefit,
        n_years=args.n_years,
        discount_rate=args.discount_rate,
        debug=args.debug,
    )

    print_pension_table(df)

# Keep the original behavior
if __name__ == "__main__":
    main_cli()
