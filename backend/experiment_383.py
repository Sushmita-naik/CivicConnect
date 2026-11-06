
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.metrics import accuracy_score, classification_report

# Load all 383 mapped records
df = pd.read_csv("dataset/ps14_mapped.csv")

X = df["description"].str.lower().str.strip()
y = df["category"]

# Group identical descriptions together
groups = X

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

# Group-aware cross-validation
cv = StratifiedGroupKFold(
    n_splits=3,
    shuffle=True,
    random_state=42
)

# Predict each record without putting its
# description group in the training fold
predictions = cross_val_predict(
    pipeline,
    X,
    y,
    groups=groups,
    cv=cv
)

print("\n383-RECORD MODEL EVALUATION")

print(
    "Accuracy:",
    round(accuracy_score(y, predictions), 4)
)

print("\nClassification Report:")

print(classification_report(
    y,
    predictions,
    zero_division=0
))
