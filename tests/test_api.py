from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.main import app


VALID = {
    "drivers_nearby": 5,
    "distance_to_driver_km": 2.5,
    "hour": 18,
    "rain_mm": 0,
    "surge": 1.2,
    "road_closures": 0,
    "car_type": "sedan",
    "zone": "Airport",
}


@pytest.mark.parametrize("changes", [
    {"distance_to_driver_km": 15.01},
    {"rain_mm": -0.1},
])
def test_invalid_request_never_calls_model(changes):
    with TestClient(app) as client:
        spy = Mock()
        app.state.model = spy

        response = client.post("/predict", json=VALID | changes)

        assert response.status_code == 422
        spy.predict.assert_not_called()

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


@pytest.mark.parametrize("changes", [
    {},
    {"distance_to_driver_km": 15, "rain_mm": 0},
])
def test_valid_prediction(changes):
    import math

    with TestClient(app) as client:
        response = client.post("/predict", json=VALID | changes)
        assert response.status_code == 200
        prediction = response.json()["prediction"]
        assert isinstance(prediction, (int, float))
        assert math.isfinite(prediction)

@pytest.mark.parametrize("case", ["missing", "extra"])
def test_invalid_request_shape(case):
    payload = VALID.copy()
    if case == "missing":
        del payload["hour"]
    else:
        payload["actual_pickup_after_min"] = 10

    with TestClient(app) as client:
        spy = Mock()
        app.state.model = spy
        response = client.post("/predict", json=payload)

        assert response.status_code == 422
        spy.predict.assert_not_called()

def test_success_writes_one_json_event(capsys):
    import json
    import math
    import sys
    from datetime import datetime, timedelta

    from app.main import prediction_logger

    import logging

    handlers = [
        h for h in prediction_logger.handlers
        if type(h) is logging.StreamHandler
    ]
    assert len(handlers) == 1
    handler = handlers[0]
    original_stream = handler.setStream(sys.stdout)

    try:
        with TestClient(app) as client:
            capsys.readouterr()
            response = client.post("/predict", json=VALID)
            captured = capsys.readouterr()
    finally:
        handler.setStream(original_stream)

    assert response.status_code == 200
    lines = [line for line in captured.out.splitlines() if line.strip()]
    assert len(lines) == 1

    event = json.loads(lines[0])
    assert set(event) == {"timestamp", "event", "prediction", "elapsed_ms"}
    assert event["event"] == "prediction_success"
    assert event["prediction"] == response.json()["prediction"]
    assert math.isfinite(event["elapsed_ms"])
    assert event["elapsed_ms"] >= 0
    assert datetime.fromisoformat(event["timestamp"]).utcoffset() == timedelta(0)