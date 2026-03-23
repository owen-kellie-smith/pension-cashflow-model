from helpers import survival_function
import pandas as pd

def test_survival_basic():
    mortality = pd.DataFrame({
        "age": [65, 66],
        "qx": [0.1, 0.1]
    })

    surv = survival_function(65, 2, mortality)

    s0 = surv.iloc[0]
    assert round(s0,2) == 0.90

    s1 = surv.iloc[1]
    assert round(s1,2) == 0.81
    
