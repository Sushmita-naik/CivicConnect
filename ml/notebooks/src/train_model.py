import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Load cleaned dataset
df = pd.read_csv("dataset/nyc_311_cleaned.csv")

# Remove categories having fewer than 20 records
counts = df["complaint_type"].value_counts()
valid_categories = counts[counts >= 20].index

df = df[df["complaint_type"].isin(valid_categories)].copy()

# Input and target
X = df["descriptor"]
y = df["complaint_type"]

# Convert text into numerical features
vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2)
)

X_vectorized = vectorizer.fit_transform(X)

# Split training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Train Logistic Regression
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Evaluate model
predictions = model.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("Model training completed!")
print("Number of categories:", len(valid_categories))
print("Training records:", X_train.shape[0])
print("Testing records:", X_test.shape[0])
print("Accuracy:", accuracy)

print("\nClassification Report:")
print(classification_report(y_test, predictions))

# Save model and vectorizer
joblib.dump(model, "backend/complaint_model.pkl")
joblib.dump(vectorizer, "backend/tfidf_vectorizer.pkl")

print("\nModel and vectorizer saved successfully!")