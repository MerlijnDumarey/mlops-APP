from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tensorflow as tf
import h5py
import numpy as np
import os

app = FastAPI()

ASSET_DIR = "api/assets"
MODEL_PATH = os.path.join(ASSET_DIR, "model", "cyclical_convlstm_modelV9.h5")
DATASET_PATH = os.path.join(ASSET_DIR, "dataset", "test_data_cleaned.h5")

model = None

class PredictRequest(BaseModel):
    record_id: str

@app.on_event("startup")
def load_assets():
    global model
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        raise RuntimeError(f"Failed to load model: {e}")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/records")
def list_records():
    try:
        with h5py.File(DATASET_PATH, "r") as f:
            record_ids = list(f.keys())
        return {"record_ids": record_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list records: {e}")

@app.post("/predict")
def predict(request: PredictRequest):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    try:
        with h5py.File(DATASET_PATH, "r") as f:
            if request.record_id not in f:
                raise HTTPException(status_code=404, detail="Record not found")
            data = np.array(f[request.record_id])
        # Adjust shape as needed for your model
        prediction = model.predict(np.expand_dims(data, axis=0))
        return {"prediction": prediction.tolist()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)