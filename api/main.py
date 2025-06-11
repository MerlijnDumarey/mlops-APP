from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from tensorflow.keras.models import load_model
import os

app = FastAPI()

MODEL_DIR = "./app/model"
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
        import numpy as np
        from io import BytesIO
        X = np.load(BytesIO(contents))
        prediction = model.predict(X)
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