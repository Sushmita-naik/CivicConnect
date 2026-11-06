
import pandas as pd
import joblib

from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Find project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load all mapped records
df = pd.read_csv(BASE_DIR / "dataset" / "ps14_mapped.csv")

X = df["description"].str.lower().str.strip()
y = df["category"]

# Create final candidate pipeline
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2)
    )),
    ("model", LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    ))
])

# Train using all 383 mapped records
pipeline.fit(X, y)

# Save separately
model_path = BASE_DIR / "backend" / "complaint_pipeline_383.pkl"

joblib.dump(pipeline, model_path)

print("Final model candidate trained!")
print("Training records:", len(X))
print("Unique descriptions:", X.nunique())
print("Categories:", list(pipeline.classes_))
print("Saved at:", model_path)
