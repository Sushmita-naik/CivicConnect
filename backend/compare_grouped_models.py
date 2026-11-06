
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.metrics import accuracy_score, f1_score

df = pd.read_csv("dataset/ps14_mapped.csv")

X = df["description"].str.lower().str.strip()
y = df["category"]
groups = X

cv = StratifiedGroupKFold(
    n_splits=3,
    shuffle=True,
    random_state=42
)

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    ),
    "Multinomial Naive Bayes": MultinomialNB()
}

for name, classifier in models.items():

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2)
        )),
        ("model", classifier)
    ])

    predictions = cross_val_predict(
        pipeline,
        X,
        y,
        groups=groups,
        cv=cv
    )

    print("\nModel:", name)
    print("Accuracy:", round(
        accuracy_score(y, predictions), 4
    ))
    print("Macro F1:", round(
        f1_score(y, predictions, average="macro"), 4
    ))
    print("Weighted F1:", round(
        f1_score(y, predictions, average="weighted"), 4
    ))
