from fastapi import FastAPI, Body
from typing import Any # For generic type hint
import joblib # Or pickle, tensorflow, etc.
import os
from pydantic import BaseModel # For PredictionOutput

app = FastAPI()

MODEL_PATH = "/app/model_artifact" # Matches the COPY instruction in Dockerfile
model = None

@app.on_event("startup")
def load_model_on_startup():
    global model
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            print(f"Model loaded successfully from {MODEL_PATH}")
        except Exception as e:
            print(f"Error loading model from {MODEL_PATH}: {e}")
            model = None
    else:
        print(f"Error: Model file not found at {MODEL_PATH}")

class PredictionOutput(BaseModel): # Output can still be structured
    prediction: Any # Or be more specific if you know the output structure

@app.post("/predict", response_model=PredictionOutput)
async def predict(payload: Any = Body(...)): # Accepts any valid JSON body
    if model is None:
        # Ensure the error response matches the PredictionOutput structure
        return {"prediction": "Model not loaded or failed to load"}

    try:
        print(f"Received payload for prediction: {payload}") # this will still need converting and preprocessing

        prediction_result = model.predict(payload) # Adapt 'payload' as needed for your model
        # --- END ADAPTATION ---

        if hasattr(prediction_result, 'tolist'):
            processed_result = prediction_result.tolist()
        else:
            processed_result = prediction_result
        
        return {"prediction": processed_result}

    except Exception as e:
        print(f"Error during prediction: {e}")
        return {"prediction": f"Error during prediction: {str(e)}"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": model is not None}

@app.get("/ready")
async def readiness_check():
    if model is None:
        return {"status": "model_not_ready"}
    return {"status": "ready"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) # Port 8080 as defined for model-server