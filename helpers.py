import pandas as pd 
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
    
    # Drop any rows where age or qx is NaN
    mortality = mortality.dropna(subset=["age", "qx"])

    # Filter out infinite values just in case
    mortality = mortality[mortality["age"].apply(pd.notna) & (mortality["age"] != float('inf'))]

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



def survival_function(age_start: int, years: int, mortality_df: pd.DataFrame) -> pd.Series:
    """
    Calculate the survival probability for each year starting from age_start.
    mortality_df must have columns ['age', 'qx'].
    """
    surv = []
    prob_survive = 1.0
    for t in range(1, years + 1):
        age = age_start + t - 1
        qx_row = mortality_df[mortality_df['age'] == age]
        if not qx_row.empty:
            qx = float(qx_row['qx'])
        else:
            # If age not in table, assume death certain
            qx = 1.0
        prob_survive *= (1 - qx)
        surv.append(prob_survive)
    return pd.Series(surv)




