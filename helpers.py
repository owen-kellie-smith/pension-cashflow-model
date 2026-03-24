import pandas as pd 
# import numpy as np
# pandas is data-processing library

def read_excel_mortality_table(filepath: str, skip_rows: int = 2, age_col: str = "Age x", qx_col: str = "Durations 0+") -> pd.DataFrame:
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

  return mortality

def formatNum(x: float) -> str:
  """
  Format a number with commas and 2 decimals
  """
  return f"{x:,.2f}"
  #{ number: format }



def survival_function(age_start: float, years: int, mortality_df: pd.DataFrame) -> pd.Series:
    """
    Calculate the survival probability for each year starting from age_start.
    mortality_df must have columns ['age', 'qx'].
    
    Fractional ages are handled by basic linear interpolation of qx.
    """
    # Ensure mortality_df is sorted by age
    mortality_df = mortality_df.sort_values('age').reset_index(drop=True)
#    print("\nmortality_df in survival_function:")
#    print(mortality_df)
    
    surv = []
    prob_survive = 1.0
    ages = []

    for t in range(1, years + 1):
        age = age_start + t - 1
        ages.append(age)
#        print("\nage:")
#        print(age)

        # Find the nearest lower and upper ages in the table
        lower_rows = mortality_df[mortality_df['age'] <= age]
        upper_rows = mortality_df[mortality_df['age'] >= age]
 #       print("\nlower rows:")
 #       print(lower_rows)
 #       print("\nupper_rows:")
 #         print(upper_rows)

        if lower_rows.empty:
            # Age below table: assume certain death
            qx_scalar = 1.0
        elif upper_rows.empty:
            # Age above table: assume certain death
            qx_scalar = 1.0
        else:
            age_low = lower_rows['age'].iloc[-1]
            age_high = upper_rows['age'].iloc[0]
            qx_low = lower_rows['qx'].iloc[-1]
            qx_high = upper_rows['qx'].iloc[0]
    
#            print(f"age_low: {age_low}")
#            print(f"age_high: {age_high}")
#            print(f"qx_low: {qx_low}")
#            print(f"qx_high: {qx_high}")

            if age_high == age_low:
                # Exact integer age
                qx_scalar = qx_low
            else:
                # Linear interpolation
                weight = (age - age_low) / (age_high - age_low)
                qx_scalar = qx_low + weight * (qx_high - qx_low)

#            print(f"qx_scalar: {qx_scalar}")

        # Update cumulative survival
        prob_survive *= (1 - qx_scalar)
        surv.append(prob_survive)

    return pd.Series(surv)
