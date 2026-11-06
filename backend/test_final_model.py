
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

model = joblib.load(
    BASE_DIR / "complaint_pipeline_383.pkl"
)

test_complaints = [
    "There is a large pothole on the main road",
    "Garbage is overflowing near the bus stop",
    "Street light is not working",
    "Water is leaking from the pipeline",
    "The drainage is blocked",
    "The sewer is overflowing",
    "A manhole cover is missing",
    "Several street lights are not working",
    "There is a water main break",
    "The road surface is badly damaged"
]

print("\nFINAL MODEL PREDICTIONS\n")

for complaint in test_complaints:

    prediction = model.predict([complaint])[0]

    probabilities = model.predict_proba([complaint])[0]

    confidence = max(probabilities) * 100

    print("Complaint:", complaint)
    print("Predicted Category:", prediction)
    print("Confidence:", round(confidence, 2), "%")
    print("-" * 55)
