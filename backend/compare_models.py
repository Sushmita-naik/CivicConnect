
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, f1_score

# Load cleaned dataset
df = pd.read_csv("dataset/nyc_311_cleaned.csv")

# Keep categories with at least 20 records
counts = df["complaint_type"].value_counts()
valid_categories = counts[counts >= 20].index
df = df[df["complaint_type"].isin(valid_categories)]

X = df["descriptor"]
y = df["complaint_type"]

# Same split for both models
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Define models
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Multinomial Naive Bayes": MultinomialNB()
}

results = []

for name, classifier in models.items():

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2)
        )),
        ("model", classifier)
    ])

    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)
    macro_f1 = f1_score(
        y_test, predictions, average="macro"
    )

    results.append({
        "Model": name,
        "Accuracy": accuracy,
        "Macro F1": macro_f1
    })

    print("\nModel:", name)
    print("Accuracy:", round(accuracy, 4))
    print("Macro F1:", round(macro_f1, 4))

    # Save Logistic Regression pipeline
    if name == "Logistic Regression":
        joblib.dump(
            pipeline,
            "backend/complaint_pipeline.pkl"
        )

    # Save Naive Bayes pipeline
    else:
        joblib.dump(
            pipeline,
            "backend/naive_bayes_pipeline.pkl"
        )

# Display comparison
result_df = pd.DataFrame(results)

print("\nMODEL COMPARISON")
print(result_df.to_string(index=False))
