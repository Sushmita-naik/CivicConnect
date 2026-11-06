import pandas as pd

df = pd.read_csv("dataset/nyc_311_cleaned.csv")

print("DATASET SHAPE:", df.shape)

print("\n1. CATEGORY DISTRIBUTION")
print(df["complaint_type"].value_counts().head(30))

print("\n2. MOST COMMON DESCRIPTORS")
print(df["descriptor"].value_counts().head(30))

print("\n3. UNIQUE DESCRIPTORS")
print("Total unique descriptors:", df["descriptor"].nunique())

print("\n4. DUPLICATE RECORDS")
print("Duplicate rows:", df.duplicated().sum())

print("\n5. GARBAGE-RELATED RECORDS")
mask = (
    df["complaint_type"].str.contains(
        "garbage|sanitation|waste|litter",
        case=False,
        na=False
    )
    | df["descriptor"].str.contains(
        "garbage|sanitation|waste|litter",
        case=False,
        na=False
    )
)

print(df.loc[mask, ["descriptor", "complaint_type"]].head(30))