import pandas as pd

# Load original dataset
df = pd.read_csv("dataset/nyc_311.csv")

# Remove rows with missing complaint descriptions
df = df.dropna(subset=["descriptor"])

# Remove extra spaces
df["descriptor"] = df["descriptor"].str.strip()

# Remove empty descriptions
df = df[df["descriptor"] != ""]

# Save cleaned dataset
df.to_csv("dataset/nyc_311_cleaned.csv", index=False)

print("Cleaning completed!")
print("Original records: 5000")
print("Cleaned records:", len(df))

print("\nCategory distribution:")
print(df["complaint_type"].value_counts())

print("\nSample cleaned records:")
print(df[["descriptor", "complaint_type"]].head(10))