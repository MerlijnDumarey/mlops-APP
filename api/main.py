from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

MODEL_SERVER_URL = "http://model-server:8501/v1/models/model:predict"

class PredictRequest(BaseModel):
    data: list  

@app.post("/predict")
def predict(request: PredictRequest):
    payload = {
        "instances": [request.data]
    }
    try:
        response = requests.post(MODEL_SERVER_URL, json=payload)
        response.raise_for_status()
        prediction = response.json()["predictions"][0]
        return {"prediction": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")