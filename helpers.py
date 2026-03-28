import pandas as pd 
import numpy as np
# pandas is data-processing library

def read_excel_mortality_table(filepath: str, skip_rows: int = 2, age_col: str = "Age x", qx_col: str = "Durations 0+", debug: bool=False ) -> pd.DataFrame:
  """
  Reads an Excel mortality table and returns a standardized DataFrame with columns ['age', 'qx'].

  Args:
  filepath: Path to the Excel file (.xls or .xlsx)
  skip_rows: Number of rows to skip at the top (default 2)
  age_col: Name of the age column in the Excel sheet
  qx_col: Name of the mortality probability column in the Excel sheet

  Returns:
  DataFrame with columns ['age', 'qx'], age=int, qx=float
  """
  mortality = pd.read_excel(filepath, skiprows=skip_rows)

  # Rename columns
  mortality = mortality.rename(columns={age_col: "age", qx_col: "qx"})

  # Keep only 'age' and 'qx'
  mortality = mortality[['age', 'qx']]

  # Drop any rows where age or qx is NaN
  mortality = mortality.dropna(subset=["age", "qx"])

  # Filter out infinite values just in case
  filtered = mortality["age"].apply(pd.notna) & (mortality["age"] != float('inf'))
  mortality = mortality[filtered]

  # Transform (possibly changing nothing) to expected data types
  mortality["age"] = mortality["age"].astype(int)
  mortality["qx"] = mortality["qx"].astype(float)
  if debug:
      print(f"\n {filepath} mortality:\n {mortality}")

  return mortality

def formatNum(x: float) -> str:
  """
  Format a number with commas and 2 decimals
  """
  return f"{x:,.2f}"
  #{ number: format }


def survival_function(age_start: float, years: int, mortality_df: pd.DataFrame, debug = False) -> pd.Series:
    """
    Vectorized survival probability calculation with correct edge handling.
    """

    # Extract numpy arrays
    ages = mortality_df["age"].values
    qx = mortality_df["qx"].values

    # Target ages
    target_ages = age_start + np.arange(years) #np.arange(years) = [0, 1, ..., years-2, years -1]

    # NEW: np.interp with explicit bounds handling
    # values below min(ages) -> 0.0 (no death)
    # values above max(ages) -> 1.0 (certain death)
    qx_interp = np.interp(target_ages, ages, qx, left=0.0, right=1.0)

    survival = np.cumprod(1 - qx_interp)
    if (debug):
        print("\n age_start:", age_start)
        print("\n survival:", survival)
        print("\n pd.Series(survival)", pd.Series(survival))
    return pd.Series(survival)

