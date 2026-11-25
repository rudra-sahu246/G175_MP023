
import json
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd

from mlflow.tracking import MlflowClient

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# --------------------------------------------------
# 1. PROJECT CONFIGURATION
# --------------------------------------------------

DATA_PATH = Path("data/processed/train_clean.csv")

TARGET = "pickup_eta_min"

NUMERIC_FEATURES = [
    "drivers_nearby",
    "distance_to_driver_km",
    "hour",
    "rain_mm",
    "surge",
    "road_closures",
]

CATEGORICAL_FEATURES = [
    "car_type",
    "zone",
]

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

RANDOM_STATE = 42

EXPERIMENT_NAME = "MP023_Cab_Pickup_Time"

REGISTERED_MODEL_NAME = "MP023_Cab_Pickup_Time_Model"


# --------------------------------------------------
# 2. LOAD AND VALIDATE DATA
# --------------------------------------------------

def load_data():

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    required_columns = FEATURES + [TARGET, "date"]

    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df["date"] = pd.to_datetime(df["date"], errors="raise")

    df = df.sort_values(
        ["date", "record_id"]
    ).reset_index(drop=True)

    X = df[FEATURES].copy()
    y = pd.to_numeric(df[TARGET], errors="raise")

    return df, X, y


# --------------------------------------------------
# 3. CHRONOLOGICAL TRAIN / VALIDATION SPLIT
# --------------------------------------------------

def chronological_split(df, X, y):

    unique_dates = df["date"].drop_duplicates().sort_values().to_numpy()

    split_index = int(len(unique_dates) * 0.80)

    if split_index <= 0 or split_index >= len(unique_dates):
        raise ValueError("Invalid date-based split.")

    split_date = unique_dates[split_index]

    train_mask = df["date"] < split_date
    valid_mask = df["date"] >= split_date

    X_train = X.loc[train_mask].copy()
    X_valid = X.loc[valid_mask].copy()

    y_train = y.loc[train_mask].copy()
    y_valid = y.loc[valid_mask].copy()

    print("\nCHRONOLOGICAL SPLIT")
    print("-------------------")
    print("Training rows:", len(X_train))
    print("Validation rows:", len(X_valid))
    print("Training end:", df.loc[train_mask, "date"].max())
    print("Validation start:", df.loc[valid_mask, "date"].min())

    assert df.loc[train_mask, "date"].max() < df.loc[valid_mask, "date"].min()

    return X_train, X_valid, y_train, y_valid


# --------------------------------------------------
# 4. PREPROCESSING PIPELINE
# --------------------------------------------------

def create_preprocessor():

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median"))
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            (
                "encoder",
                OneHotEncoder(handle_unknown="ignore")
            ),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_FEATURES
            ),
        ]
    )

    return preprocessor


# --------------------------------------------------
# 5. EVALUATION METRICS
# --------------------------------------------------

def calculate_metrics(y_true, predictions):

    mae = mean_absolute_error(y_true, predictions)

    rmse = np.sqrt(
        mean_squared_error(y_true, predictions)
    )

    r2 = r2_score(y_true, predictions)

    return {
        "mae": float(mae),
        "rmse": float(rmse),
        "r2": float(r2),
    }


# --------------------------------------------------
# 6. RUN ONE EXPERIMENT
# --------------------------------------------------

def run_experiment(
    experiment_name,
    model,
    X_train,
    X_valid,
    y_train,
    y_valid,
    model_params,
):

    pipeline = Pipeline(
        steps=[
            ("preprocessor", create_preprocessor()),
            ("model", model),
        ]
    )

    with mlflow.start_run(run_name=experiment_name) as run:

        pipeline.fit(X_train, y_train)

        predictions = pipeline.predict(X_valid)

        metrics = calculate_metrics(
            y_valid,
            predictions
        )

        mlflow.log_params(model_params)

        mlflow.log_param("random_state", RANDOM_STATE)
        mlflow.log_param("train_rows", len(X_train))
        mlflow.log_param("validation_rows", len(X_valid))
        mlflow.log_param("split_method", "chronological_80_20")
        mlflow.log_param("target", TARGET)

        mlflow.log_metrics(metrics)

        mlflow.set_tag("project", "MP023")
        mlflow.set_tag("owner", "Ayush")
        mlflow.set_tag("experiment_type", experiment_name)

        mlflow.sklearn.log_model(
            sk_model=pipeline,
            name="model",
            serialization_format="cloudpickle",
        )

        print(f"\n{experiment_name}")
        print("-------------------------")
        print(f"MAE:  {metrics['mae']:.4f}")
        print(f"RMSE: {metrics['rmse']:.4f}")
        print(f"R2:   {metrics['r2']:.4f}")

        return {
            "name": experiment_name,
            "run_id": run.info.run_id,
            "metrics": metrics,
            "pipeline": pipeline,
            "params": model_params,
        }


# --------------------------------------------------
# 7. MAIN TRAINING PIPELINE
# --------------------------------------------------

def main():

    print("\nMP023 MODEL TRAINING PIPELINE")
    print("=============================")

    df, X, y = load_data()

    print("Dataset rows:", len(df))
    print("Features:", FEATURES)
    print("Target:", TARGET)

    X_train, X_valid, y_train, y_valid = chronological_split(
        df, X, y
    )

    # Local MLflow tracking with model registry support
    mlflow.set_tracking_uri("sqlite:///mlflow.db")

    mlflow.set_experiment(EXPERIMENT_NAME)

    results = []

    # Experiment 1: Baseline
    baseline = run_experiment(
        "Baseline_DummyRegressor",
        DummyRegressor(strategy="median"),
        X_train,
        X_valid,
        y_train,
        y_valid,
        {"model_type": "DummyRegressor", "strategy": "median"},
    )

    results.append(baseline)

    # Experiments 2, 3 and 4: Random Forest
    for trees in [100, 200, 300]:

        params = {
            "model_type": "RandomForestRegressor",
            "n_estimators": trees,
            "random_state": RANDOM_STATE,
            "n_jobs": -1,
        }

        result = run_experiment(
            f"RandomForest_{trees}_Trees",
            RandomForestRegressor(
                n_estimators=trees,
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
            X_train,
            X_valid,
            y_train,
            y_valid,
            params,
        )

        results.append(result)

    # --------------------------------------------------
    # 8. COMPARE EXPERIMENTS
    # --------------------------------------------------

    comparison = pd.DataFrame([
        {
            "experiment": r["name"],
            "run_id": r["run_id"],
            "mae": r["metrics"]["mae"],
            "rmse": r["metrics"]["rmse"],
            "r2": r["metrics"]["r2"],
        }
        for r in results
    ])

    comparison = comparison.sort_values("mae")

    Path("reports").mkdir(exist_ok=True)

    comparison.to_csv(
        "reports/model_comparison.csv",
        index=False
    )

    print("\nEXPERIMENT COMPARISON")
    print("=====================")
    print(comparison.to_string(index=False))

    # Select champion among Random Forest experiments.
    rf_results = [
        r for r in results
        if r["params"]["model_type"] == "RandomForestRegressor"
    ]

    best = min(
        rf_results,
        key=lambda r: r["metrics"]["mae"]
    )

    print("\nBEST RANDOM FOREST MODEL")
    print("========================")
    print("Name:", best["name"])
    print("Run ID:", best["run_id"])
    print("Validation MAE:", best["metrics"]["mae"])

    # --------------------------------------------------
    # 9. REGISTER BEST MODEL
    # --------------------------------------------------

    model_uri = f"runs:/{best['run_id']}/model"

    registered = mlflow.register_model(
        model_uri=model_uri,
        name=REGISTERED_MODEL_NAME,
    )

    client = MlflowClient()

    client.set_registered_model_alias(
        name=REGISTERED_MODEL_NAME,
        alias="champion",
        version=registered.version,
    )

    # --------------------------------------------------
    # 10. SAVE MODEL ARTIFACTS
    # --------------------------------------------------

    Path("models").mkdir(exist_ok=True)

    joblib.dump(
        best["pipeline"],
        "models/model.joblib"
    )

    version_path = f"models/v{registered.version}.joblib"

    joblib.dump(
        best["pipeline"],
        version_path
    )

    metadata = {
        "registered_model": REGISTERED_MODEL_NAME,
        "model_version": registered.version,
        "alias": "champion",
        "experiment": best["name"],
        "run_id": best["run_id"],
        "validation_metrics": best["metrics"],
        "parameters": best["params"],
        "features": FEATURES,
        "target": TARGET,
    }

    with open(
        "models/champion_metadata.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(metadata, file, indent=4)

    print("\nMODEL REGISTRATION COMPLETE")
    print("============================")
    print("Registered model:", REGISTERED_MODEL_NAME)
    print("Version:", registered.version)
    print("Alias: champion")
    print("Saved:", "models/model.joblib")
    print("Saved:", version_path)
    print("Saved:", "models/champion_metadata.json")


if __name__ == "__main__":
    main()

