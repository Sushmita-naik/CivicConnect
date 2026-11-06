import pandas as pd

df = pd.read_csv("dataset/ps14_mapped.csv")

print("DATASET SHAPE:", df.shape)

print("\nCATEGORY DISTRIBUTION:")
print(df["category"].value_counts())

print("\nMISSING VALUES:")
print(df.isnull().sum())

print("\nDUPLICATE RECORDS:")
print(df.duplicated().sum())

print("\nSAMPLE RECORDS:")
print(df.sample(min(15, len(df)), random_state=42).to_string(index=False))