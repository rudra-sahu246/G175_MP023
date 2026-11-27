from contextlib import asynccontextmanager
from pathlib import Path
import logging
import math
import json
import sys
import time
from datetime import datetime, timezone
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "model.joblib"
logger = logging.getLogger(__name__)

prediction_logger = logging.getLogger("mp023.predictions")
prediction_logger.setLevel(logging.INFO)
prediction_logger.propagate = False

if not prediction_logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    prediction_logger.addHandler(handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load(MODEL_PATH)
    yield
    app.state.model = None


app = FastAPI(lifespan=lifespan)


class BookingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    drivers_nearby: int
    distance_to_driver_km: float = Field(..., le=15)
    hour: int
    rain_mm: float = Field(..., ge=0)
    surge: float
    road_closures: int
    car_type: str
    zone: str


class PredictionResponse(BaseModel):
    prediction: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(booking: BookingRequest, request: Request):
    started = time.perf_counter()

    try:
        features = pd.DataFrame([booking.model_dump()])
        value = float(request.app.state.model.predict(features)[0])
        if not math.isfinite(value):
            raise ValueError("Model returned a non-finite prediction")
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction failed") from exc

    response = PredictionResponse(prediction=value)

    prediction_logger.info(json.dumps({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "prediction_success",
        "prediction": value,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
    }, allow_nan=False))

    return response
