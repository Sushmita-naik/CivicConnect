import pandas as pd

df = pd.read_csv("dataset/nyc_311.csv")

print("Dataset shape:", df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 records:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())

print("\nComplaint categories:")
print(df["complaint_type"].value_counts().head(10))