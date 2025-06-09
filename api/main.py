from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
import requests
import os # For environment variables

app = FastAPI()

MODEL_SERVER_INTERNAL_URL = os.getenv("MODEL_SERVER_URL", "http://model-server-service:80/predict")


class ApiPredictRequest(BaseModel):
    data: Any 

class ApiPredictResponse(BaseModel):
   
    prediction_result: Any


@app.post("/predict", response_model=ApiPredictResponse)
async def api_predict(request: ApiPredictRequest):
    payload_to_model_server = request.data

    try:
        print(f"Sending payload to model server: {payload_to_model_server}")
        response = requests.post(MODEL_SERVER_INTERNAL_URL, json=payload_to_model_server)
        response.raise_for_status() 
        
        model_server_response_json = response.json()
        
        prediction_from_model = model_server_response_json.get("prediction")

        return {"prediction_result": prediction_from_model}

    except requests.exceptions.RequestException as e:
        print(f"Error calling model server: {e}")
        raise HTTPException(status_code=503, detail=f"Model service unavailable or returned an error: {e}")
    except Exception as e:
        print(f"Unexpected error during prediction call: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed due to an internal error: {e}")
    

@app.get("/health")
def health():
    return {"status": "ok"}