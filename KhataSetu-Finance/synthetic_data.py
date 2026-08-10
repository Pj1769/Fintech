
def save_synthetic_data(df, filename="synthetic_borrowers.csv"):
    import os
    os.makedirs("data", exist_ok=True)
    path = os.path.join("data", filename)
    df.to_csv(path, index=False)
    print(f"Saved synthetic dataset to {path}")

def save_synthetic_data(df, filename="synthetic_borrowers.csv"):
    import os
    os.makedirs("data", exist_ok=True)
    path = os.path.join("data", filename)
    df.to_csv(path, index=False)
    print(f"Saved synthetic dataset to {path}")
