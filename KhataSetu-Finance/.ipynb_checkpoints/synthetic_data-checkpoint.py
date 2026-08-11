import pandas as pd
import numpy as np

def generate_data(num_records=100):
    """Generate synthetic borrower data for testing."""
    np.random.seed(42)
    data = {
        "Borrower_ID": range(1, num_records + 1),
        "Age": np.random.randint(21, 60, num_records),
        "Loan_Amount": np.random.randint(50000, 500000, num_records),
        "Credit_Score": np.random.randint(300, 850, num_records),
        "Region": np.random.choice(["Urban", "Semi-Urban", "Rural"], num_records)
    }
    df = pd.DataFrame(data)
    return df

