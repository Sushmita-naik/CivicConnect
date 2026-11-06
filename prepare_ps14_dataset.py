
import pandas as pd

df = pd.read_csv("dataset/nyc_311_cleaned.csv")

mapped_records = []

for _, row in df.iterrows():

    complaint = row["complaint_type"]
    descriptor = row["descriptor"]

    category = None

    # 1. Road Damage
    if complaint == "Street Condition":
        category = "Road Damage"

    # 2. Garbage / Waste
    elif complaint == "Illegal Dumping":
        category = "Garbage / Waste"

    elif (
        complaint == "UNSANITARY CONDITION"
        and descriptor == "GARBAGE/RECYCLING STORAGE"
    ):
        category = "Garbage / Waste"

    elif (
        complaint == "Maintenance or Facility"
        and descriptor == "Garbage or Litter"
    ):
        category = "Garbage / Waste"

    elif (
        complaint == "Litter Basket Complaint"
        and descriptor == "Overflowing"
    ):
        category = "Garbage / Waste"

    # 3. Streetlight
    elif complaint == "Street Light Condition":
        category = "Streetlight"

    # 4. Water Leakage
    elif complaint == "WATER LEAK":
        category = "Water Leakage"

    elif (
        complaint == "Water Maintenance"
        and descriptor in [
            "Leak",
            "Fire Hydrant Leaking",
            "Water Main Break"
        ]
    ):
        category = "Water Leakage"

    # 5. Drainage / Sewer Issue
    elif complaint == "Sewer Maintenance":
        category = "Drainage / Sewer Issue"

    if category is not None:

        mapped_records.append({
            "description": descriptor,
            "category": category
        })

# Create the new dataset
mapped_df = pd.DataFrame(mapped_records)

# Save the dataset
mapped_df.to_csv(
    "dataset/ps14_mapped.csv",
    index=False
)

print("PS-14 dataset created successfully!")

print("\nDataset shape:")
print(mapped_df.shape)

print("\nCategory distribution:")
print(mapped_df["category"].value_counts())

print("\nSample records:")
print(mapped_df.head(15).to_string(index=False))
