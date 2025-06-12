from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from tensorflow.keras.models import load_model
import h5py
import numpy as np
from io import BytesIO
from utils import (
    h5_to_dataframe,
    flag_joint_missingness,
    impute_missingness,
    dataframe_to_h5
)
import os

app = FastAPI()

MODEL_DIR = "./model"
MODEL_FILE = None
model = None

# Find the first .h5 file in the model directory
for fname in os.listdir(MODEL_DIR):
    if fname.endswith(".h5"):
        MODEL_FILE = os.path.join(MODEL_DIR, fname)
        break

if MODEL_FILE:

    model = load_model(MODEL_FILE)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not available."
        )
    try:
        contents = await file.read()

        file_bytes_io = BytesIO(contents)

        with h5py.File(file_bytes_io, 'r') as f:
            X = f['data'][:]

        df = h5_to_dataframe(X)
        df_missing_flagged = flag_joint_missingness(df, target_cols=df.columns)
        df_imputed = impute_missingness(df_missing_flagged)

        X_cleaned = dataframe_to_h5(df_imputed)
        X_reshaped = X_cleaned.reshape((-1, 15, 4, 25, 1))



        prediction = model.predict(X_reshaped)
        if hasattr(prediction, "tolist"):
            prediction = prediction.tolist()
        return JSONResponse(content={"prediction": prediction})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "model_file": MODEL_FILE if model is not None else None
    }
