
import pandas as pd

df = pd.read_csv("dataset/nyc_311_cleaned.csv")

target_categories = [
    "Illegal Dumping",
    "UNSANITARY CONDITION",
    "Litter Basket Complaint",
    "Litter Basket Request",
    "Maintenance or Facility",
    "Street Condition",
    "Street Light Condition",
    "Water Maintenance",
    "WATER LEAK",
    "Sewer Maintenance",
    "Root/Sewer/Sidewalk Condition"
]

for category in target_categories:

    subset = df[df["complaint_type"] == category]

    print("\n" + "=" * 55)
    print("CATEGORY:", category)
    print("TOTAL RECORDS:", len(subset))

    if len(subset) > 0:
        print("\nDESCRIPTORS:")
        print(subset["descriptor"].value_counts().head(20).to_string())
    else:
        print("No records found")
