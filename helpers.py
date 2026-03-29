import pandas as pd 
import os
import sys
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
      pd.set_option('display.max_rows', None)
      print(f"\n {filepath} mortality:\n {mortality}")

  return mortality

def formatNum(x: float) -> str:
  """
  Format a number with commas and 2 decimals
  """
  return f"{x:,.2f}"
  #{ number: format }


def copy_all_output_to_log(filename):
    class Tee:
        def __init__(self, filename):
            self.file = open(filename, "a")
            self.stdout = sys.stdout

        def write(self, data):
            self.stdout.write(data)   # print to terminal
            self.file.write(data)     # write to log file

        def flush(self):
            self.stdout.flush()
            self.file.flush()

    sys.stdout = Tee(filename)

def initialize_log_file(log_file, calling_file):
    if not( log_file is None):
        with open(log_file, "w") as f:
            f.write(calling_file)
            f.write("\nCommand used:\n")
            f.write(" ".join(sys.argv) + "\n\n")
        copy_all_output_to_log(log_file)

# ------------------------------------------------
# Main
# ------------------------------------------------
def main():

    full_path = os.path.abspath(__file__)
    print(full_path)
    print("is called by other script(s).\n")

# ------------------------------------------------
# Only run if CLI calls .py directly
# ------------------------------------------------
if __name__ == "__main__":
    main()
