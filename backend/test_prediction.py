import joblib

pipeline = joblib.load("backend/complaint_pipeline.pkl")

test_complaints = [
    "Pothole on the main road",
    "Street light is not working",
    "Garbage is overflowing",
    "Water is leaking from the pipe",
    "Drainage is blocked",
    "Road surface is damaged"
]

for complaint in test_complaints:

    prediction = pipeline.predict([complaint])[0]

    print("Complaint:", complaint)
    print("Predicted Category:", prediction)
    print("-" * 50)