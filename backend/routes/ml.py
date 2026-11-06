
from pathlib import Path

import joblib
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


# Load the existing trained model
MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "complaint_pipeline_383.pkl"
)

pipeline = joblib.load(MODEL_PATH)


# Create ML router
router = APIRouter(
    prefix="/api/ml",
    tags=["Machine Learning"]
)


# Input received from frontend
class PredictionRequest(BaseModel):
    title: str = ""
    description: str = Field(min_length=5, max_length=2000)


# Predict complaint category
@router.post("/predict")
def predict_category(request: PredictionRequest):

    # Combine title and description
    text = (
        request.title.strip() + " " +
        request.description.strip()
    ).strip()

    try:
        category = pipeline.predict([text])[0]

        probabilities = pipeline.predict_proba([text])[0]
        confidence = float(max(probabilities))

        return {
            "category": category,
            "confidence": confidence
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="ML prediction failed"
        )
