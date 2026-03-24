import pandas as pd 
import argparse
# pandas is data-processing library
from helpers import read_excel_mortality_table, formatNum, survival_function

def calculate_pension_cashflows(
    mortality_file: str = None,
    mortality_df: pd.DataFrame = None,
    starting_age: float = 65,
    base_benefit: float = 10000,
    n_years: int = 5,
    discount_rate: float = 0.03
) -> pd.DataFrame:
  # Read mortality table using function defined in helpers.py
  """
  Either provide mortality_file (str) OR mortality_df (DataFrame). 
  mortality_df takes priority if given.
  """
  if mortality_df is None:
      if mortality_file is None:
          raise ValueError("Either mortality_file or mortality_df must be provided.")
      mortality_df = read_excel_mortality_table(mortality_file)
  data = pd.DataFrame({
    "year": list(range(1, n_years + 1)),
    "benefit_pp": [base_benefit] * n_years
  })
  # DataFrame is like an Excel sheet i.e. a table. Each item is a column where (key,item) = (column label, Series).

  # -----------------------------
  # Mortality-weighted cashflows 
  # -----------------------------
  data["survival_prob"] = survival_function(starting_age, n_years, mortality_df)
  data["cashflow"] = data["benefit_pp"] * data["survival_prob"]

  # -----------------------------
  # Discounted cashflows
  # -----------------------------
  data["discount_factor"] = 1 / ((1 + discount_rate) ** data["year"]) 
  # adds to data the transformed column discount_factor with formula in terms of existing column labels.
  data["present_value"] = data["cashflow"] * data["discount_factor"]

  # Add running total columns
  data["running_total_cashflow"] = data["cashflow"].cumsum()
  data["running_total_present_value"] = data["present_value"].cumsum()

  # -----------------------------
  # Totals
  # -----------------------------
  # Sum numeric columns
  total_row = data[["cashflow", "present_value"]].sum()

  # Add label for non-numeric column
  total_row["year"] = "Total"

  # Append as a new row
  data = pd.concat([data, pd.DataFrame([total_row])], ignore_index=True, axis=0)
  # axis = 0 (redundant since 0 is default) means add a row

  # -----------------------------
  # Optional: formatted columns for display
  # -----------------------------
  data["cashflow_formatted"] = data["cashflow"].apply(formatNum)
  data["present_value_formatted"] = data["present_value"].apply(formatNum)
  return data

def print_pension_table(df: pd.DataFrame):
  # -----------------------------
  # Print output
  # -----------------------------
  #print("\nData Frame (entire):")
  #print(data)
  #print("\n")
  print("\nPension Cashflow Table:")
  print(df[["year", "cashflow_formatted", "present_value_formatted"]].to_string(index=False))
  # index = False: leave out the 0,1,2,... row count


# -----------------------------
# CLI main function
# -----------------------------
def main_cli():
    parser = argparse.ArgumentParser(description="Calculate and display pension cashflow table.")
    parser.add_argument("-mort", "--mortality_file", required=True, help="Path to mortality Excel file")
    parser.add_argument("-age", "--starting_age", type=float, required=True, help="Starting age")
    parser.add_argument("-benefit", "--base_benefit", type=float, default=10000, help="Base annual benefit per person")
    parser.add_argument("-n", "--n_years", type=int, default=5, help="Number of years to project")
    parser.add_argument("-r", "--discount_rate", type=float, default=0.03, help="Discount rate (e.g., 0.03 for 3%)")
    
    args = parser.parse_args()

    df = calculate_pension_cashflows(
        mortality_file=args.mortality_file,
        starting_age=args.starting_age,
        base_benefit=args.base_benefit,
        n_years=args.n_years,
        discount_rate=args.discount_rate
    )

    print_pension_table(df)

# Keep the original behavior
if __name__ == "__main__":
    main_cli()
