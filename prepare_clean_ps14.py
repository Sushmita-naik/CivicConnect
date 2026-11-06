
import pandas as pd

df = pd.read_csv("dataset/ps14_mapped.csv")

print("Original records:", len(df))

# Remove exact repeated description-category pairs
df = df.drop_duplicates(
    subset=["description", "category"]
).copy()

# Normalize text
df["description"] = (
    df["description"]
    .str.strip()
    .str.lower()
)

# Check whether the same description has multiple categories
conflicts = df.groupby("description")["category"].nunique()

conflicting_descriptions = conflicts[conflicts > 1]

print("\nConflicting descriptions:")
print(conflicting_descriptions)

# Save the clean dataset
df.to_csv(
    "dataset/ps14_clean.csv",
    index=False
)

print("\nClean dataset records:", len(df))
print("\nCategory distribution:")
print(df["category"].value_counts())

print("\nClean dataset saved!")
