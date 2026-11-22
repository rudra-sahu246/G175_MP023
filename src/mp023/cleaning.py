
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml

from mp023.config import load_config


TARGET_TYPO_IDS = {
    "R00010", "R00354", "R00425", "R00521", "R00552",
    "R00658", "R00751", "R00772", "R00773", "R00887",
}


def clean_training_data(raw_df, rules):
    """Clean a copy of the training data and return repair counts."""
    df = raw_df.copy(deep=True)
    original_rows = len(df)

    required = {
        "record_id", "date", "actual_pickup_after_min",
        "pickup_eta_min", "drivers_nearby",
        "distance_to_driver_km", "hour", "rain_mm",
        "surge", "road_closures", "car_type", "zone",
    }

    missing_columns = required - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    summary = {
        "original_rows": original_rows,
        "duplicates_removed": 0,
        "sentinel_values_repaired": 0,
        "stuck_sensor_values_repaired": 0,
        "target_typos_repaired": 0,
        "category_values_mapped": 0,
    }

    # Remove exact duplicate rows, retaining the first occurrence.
    before = len(df)
    df = df.drop_duplicates(keep="first").copy()
    summary["duplicates_removed"] = before - len(df)

    # Apply only documented category mappings.
    mappings = rules.get("spelling_variants", {}).get("mappings", {})
    for column, mapping in mappings.items():
        if column in df.columns:
            previous = df[column].copy()
            df[column] = df[column].replace(mapping)
            summary["category_values_mapped"] += int(
                (previous != df[column]).sum()
            )

    # Repair the documented sentinel.
    sentinel = rules.get("sentinel_value", {})
    if sentinel.get("present") is True:
        column = sentinel.get("column")
        value = sentinel.get("value")
        if column in df.columns:
            mask = df[column].eq(value)
            summary["sentinel_values_repaired"] = int(mask.sum())
            df.loc[mask, column] = pd.NA

    # Repair the documented stuck sensor interval.
    sensor = rules.get("stuck_sensor", {})
    if sensor.get("present") is True:
        column = sensor.get("column")
        start = sensor.get("start_date")
        end = sensor.get("end_date")

        if column in df.columns and start and end:
            dates = pd.to_datetime(df["date"], errors="coerce")
            mask = (
                dates.between(pd.Timestamp(start), pd.Timestamp(end))
                & df[column].eq(18.8)
            )
            summary["stuck_sensor_values_repaired"] = int(mask.sum())
            df.loc[mask, column] = pd.NA

    # Correct only the individually verified target typo records.
    typo_rule = rules.get("target_typos", {})
    if typo_rule.get("present") is True:
        actual = pd.to_numeric(
            df["actual_pickup_after_min"], errors="coerce"
        )
        target = pd.to_numeric(df["pickup_eta_min"], errors="coerce")

        mask = (
            df["record_id"].isin(TARGET_TYPO_IDS)
            & target.gt(100)
            & actual.gt(0)
            & (target / actual).between(9.5, 10.5)
        )

        summary["target_typos_repaired"] = int(mask.sum())
        df.loc[mask, "pickup_eta_min"] = target.loc[mask] / 10

    # Parse dates and sort records.
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    df = df.sort_values(
        ["date", "record_id"]
    ).reset_index(drop=True)

    summary["final_rows"] = len(df)
    summary["remaining_missing_values"] = {
        column: int(count)
        for column, count in df.isna().sum().items()
        if count > 0
    }

    return df, summary


def main():
    parser = argparse.ArgumentParser(
        description="Clean MP023 training data."
    )
    parser.add_argument("--config", default="params.yaml")
    args = parser.parse_args()

    config = load_config(args.config)

    findings_path = Path("reports/findings.yaml")
    findings = yaml.safe_load(
        findings_path.read_text(encoding="utf-8")
    )

    raw_path = Path(config["data"]["train_path"])
    output_path = Path(config["data"]["processed_train_path"])

    # Calculate SHA-256 from the unchanged raw training file.
    raw_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()

    raw_df = pd.read_csv(raw_path)

    cleaned_df, summary = clean_training_data(
        raw_df,
        findings["data_issues"],
    )

    # Keep traceability fields and approved features.
    # Exclude the post-event leakage column.
    output_columns = (
        ["record_id", "date"]
        + config["features"]
        + [config["target"]["column"]]
    )

    cleaned_df = cleaned_df[output_columns]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(output_path, index=False)

    summary["output_path"] = str(output_path)
    summary["output_columns"] = output_columns
    summary["leakage_column_excluded"] = "actual_pickup_after_min"
    summary["raw_train_sha256"] = raw_hash
    summary["selected_features"] = config["features"]
    summary["target_column"] = config["target"]["column"]

    summary_path = Path("reports/cleaning_summary.json")
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    summary_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2))
    print(f"\nCleaned data saved to: {output_path}")
    print(f"Cleaning summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
