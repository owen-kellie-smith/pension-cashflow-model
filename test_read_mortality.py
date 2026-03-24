import pandas as pd
import pytest
from io import BytesIO
from helpers import read_excel_mortality_table

def test_read_excel_mortality_table():
    # Create sample data
    data = {
        "Age x": [0, 1, 2, 3],
        "Durations 0+": [0.005, 0.001, 0.0015, 0.002],
        "ExtraCol": ["a", "b", "c", "d"]  # should be ignored
    }
    df = pd.DataFrame(data)

    # Write the DataFrame to a BytesIO Excel object
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False)
    excel_file.seek(0)  # Reset pointer to the beginning

    # Call the function with the in-memory "file"
    result = read_excel_mortality_table(excel_file, skip_rows=0)

    # Expected DataFrame
    expected = pd.DataFrame({
        "age": [0, 1, 2, 3],
        "qx": [0.005, 0.001, 0.0015, 0.002]
    })

    # Check that the result matches expected
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)
