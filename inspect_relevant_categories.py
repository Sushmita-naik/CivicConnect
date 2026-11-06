
import pandas as pd

df = pd.read_csv("dataset/nyc_311_cleaned.csv")

keywords = [
    "street",
    "road",
    "pothole",
    "garbage",
    "waste",
    "litter",
    "dump",
    "sanitary",
    "water",
    "leak",
    "drain",
    "sewer",
    "light"
]

categories = df["complaint_type"].value_counts()

for keyword in keywords:

    matching = categories[
        categories.index.str.contains(
            keyword,
            case=False,
            regex=False
        )
    ]

    print(f"\n--- {keyword.upper()} ---")

    if matching.empty:
        print("No matching categories found")
    else:
        print(matching.to_string())
