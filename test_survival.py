from model import survival_function
import pandas as pd
import pytest

def test_survival_basic():
    mortality = pd.DataFrame({
        "age": [65, 66],
        "qx": [0.1, 0.1]
    })

    surv = survival_function(65, 2, mortality)

    s0 = surv.iloc[0]
    assert round(s0,2) == 0.90 # = 1 * (1 - 0.1)

    s1 = surv.iloc[1]
    assert round(s1,2) == 0.81 # = 1  * ( 1 - 0.1) * (1 - 0.1)
    

# -----------------------------
# 1️⃣ survival_function edge cases
# -----------------------------
def test_survival_function_edge_cases():
    # Simple mock mortality table
    mortality = pd.DataFrame({
        "age": [65, 66, 67],
        "qx": [0.01, 0.02, 0.03]
    })

    # Case 1: starting_age beyond table max
    result = survival_function(70, 3, mortality)
    assert all(p == 0.0 for p in result)  # all survival probs should be zero

    # Case 2: n_years = 0
    result = survival_function(65, 0, mortality)
    assert result.empty  # True if Series has 0 elements

