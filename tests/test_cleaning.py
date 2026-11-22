
import pandas as pd

from mp023.cleaning import clean_training_data


def make_data():
    return pd.DataFrame([
        {
            "record_id": "R00010",
            "date": "2026-02-15",
            "drivers_nearby": 10,
            "distance_to_driver_km": 2.5,
            "hour": 10,
            "rain_mm": 18.8,
            "surge": 1.2,
            "road_closures": -999,
            "car_type": "auto",
            "zone": "Tech Park",
            "actual_pickup_after_min": 20.0,
            "pickup_eta_min": 200.0,
        },
        {
            "record_id": "R99999",
            "date": "2026-04-10",
            "drivers_nearby": 12,
            "distance_to_driver_km": 3.0,
            "hour": 12,
            "rain_mm": 5.0,
            "surge": 1.0,
            "road_closures": 2,
            "car_type": "mini",
            "zone": "Airport",
            "actual_pickup_after_min": 20.0,
            "pickup_eta_min": 200.0,
        },
    ])


def make_rules():
    return {
        "sentinel_value": {
            "present": True,
            "column": "road_closures",
            "value": -999,
        },
        "stuck_sensor": {
            "present": True,
            "column": "rain_mm",
            "start_date": "2026-02-10",
            "end_date": "2026-03-05",
        },
        "target_typos": {"present": True},
        "spelling_variants": {
            "present": True,
            "mappings": {
                "car_type": {"mini": "Mini"}
            },
        },
    }


def test_duplicate_rows_are_removed():
    data = make_data()
    duplicated = pd.concat([data, data.iloc[[0]]], ignore_index=True)

    cleaned, summary = clean_training_data(
        duplicated, make_rules()
    )

    assert len(cleaned) == 2
    assert summary["duplicates_removed"] == 1


def test_sentinel_and_stuck_sensor_are_marked_missing():
    cleaned, summary = clean_training_data(
        make_data(), make_rules()
    )

    affected = cleaned.loc[cleaned["record_id"] == "R00010"].iloc[0]

    assert pd.isna(affected["road_closures"])
    assert pd.isna(affected["rain_mm"])
    assert summary["sentinel_values_repaired"] == 1
    assert summary["stuck_sensor_values_repaired"] == 1


def test_target_correction_only_affects_verified_record():
    cleaned, summary = clean_training_data(
        make_data(), make_rules()
    )

    verified = cleaned.loc[
        cleaned["record_id"] == "R00010", "pickup_eta_min"
    ].iloc[0]

    unverified = cleaned.loc[
        cleaned["record_id"] == "R99999", "pickup_eta_min"
    ].iloc[0]

    assert verified == 20.0
    assert unverified == 200.0
    assert summary["target_typos_repaired"] == 1


def test_category_mapping_is_applied():
    cleaned, summary = clean_training_data(
        make_data(), make_rules()
    )

    mapped = cleaned.loc[
        cleaned["record_id"] == "R99999", "car_type"
    ].iloc[0]

    assert mapped == "Mini"
    assert summary["category_values_mapped"] == 1
