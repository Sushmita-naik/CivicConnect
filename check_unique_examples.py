
import pandas as pd

df = pd.read_csv("dataset/ps14_mapped.csv")

unique_df = df.drop_duplicates(
    subset=["description", "category"]
)

print("TOTAL RECORDS:", len(df))
print("UNIQUE RECORDS:", len(unique_df))

print("\nUNIQUE EXAMPLES PER CATEGORY:")

for category, group in unique_df.groupby("category"):

    print("\nCATEGORY:", category)
    print("Unique examples:", len(group))

    print(group["description"].tolist())

# Save unique records separately
unique_df.to_csv(
    "dataset/ps14_unique.csv",
    index=False
)

print("\nUnique dataset saved successfully!")
