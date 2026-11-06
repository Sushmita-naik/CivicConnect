
import joblib

pipeline = joblib.load("backend/complaint_pipeline.pkl")

test_complaints = [
    "Garbage is scattered near the bus stand",
    "Garbage is overflowing from the dustbin",
    "There is a pothole on the main road",
    "Street light is not working",
    "Water is leaking from the pipeline",
    "Drainage water is overflowing"
]

vectorizer = pipeline.named_steps["tfidf"]

model = pipeline.named_steps["model"]

for complaint in test_complaints:

    transformed = vectorizer.transform([complaint])

    probabilities = model.predict_proba(transformed)[0]

    top_indices = probabilities.argsort()[-3:][::-1]

    print("\nComplaint:", complaint)

    print("Recognized features:", transformed.nnz)

    print("Top 3 predictions:")

    for index in top_indices:
        print(
            model.classes_[index],
            ":", round(probabilities[index] * 100, 2), "%"
        )
