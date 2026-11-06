import pandas as pd

# Read the downloaded Parquet file
df = pd.read_parquet("dataset/nyc_311.parquet")

# Convert it into CSV
df.to_csv("dataset/nyc_311.csv", index=False)

# Display dataset information
print("\nDataset converted successfully!")
print("Number of rows and columns:", df.shape)

print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 records:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())