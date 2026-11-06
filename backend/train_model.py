
import pandas as pd
import joblib

from pathlib import Path
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Load cleaned PS-14 dataset
df = pd.read_csv("dataset/ps14_clean.csv")

X = df["description"]
y = df["category"]

# Create ML pipeline
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

# Evaluate using Leave-One-Out cross-validation
loo = LeaveOneOut()

predictions = cross_val_predict(
    pipeline,
    X,
    y,
    cv=loo
)

print("\nMODEL EVALUATION")
print("Accuracy:", round(accuracy_score(y, predictions), 4))

print("\nClassification Report:")
print(classification_report(
    y,
    predictions,
    zero_division=0
))

# Train final model on all available examples
pipeline.fit(X, y)

# Save model
model_path = Path(__file__).resolve().parent / "complaint_pipeline.pkl"
joblib.dump(pipeline, model_path)

print("\nModel trained and saved successfully!")
