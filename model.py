import pandas as pd 
# pandas is data-processing library

discount_rate = 0.03

data = pd.DataFrame({
    "year": [1,2,3,4,5],
    "cashflow": [10000,10000,10000,10000,10000]
}) 
# DataFrame is like an Excel sheet i.e. a table. Each item is a column where (key,item) = (column label, Series).
# Replace the hard-coded DataFrame with: pd.read_excel("your_file.xlsx") for real data


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
def formatNum(x: float) -> str:
    """
    Format a number with commas and 2 decimals
    """
    return f"{x:,.2f}"
    #{ number: format }

data["cashflow_formatted"] = data["cashflow"].apply(formatNum)
data["present_value_formatted"] = data["present_value"].apply(formatNum)

# -----------------------------
# Print output
# -----------------------------
print("\nData Frame (entire):")
print(data)
print("\n")

print("\nPension Cashflow Table:")
print(data[["year", "cashflow_formatted", "present_value_formatted"]].to_string(index=False))
# index = False: leave out the 0,1,2,... row count





