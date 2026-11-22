
import argparse
import json
from pathlib import Path

import pandas as pd

from mp023.config import load_config


def audit_dataset(file_path):
    """Generate a repeatable inventory and quality audit."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)

    numeric_columns = df.select_dtypes(include="number").columns

    audit = {
        "file": str(path),
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "column_names": df.columns.tolist(),
        "missing_values": {
            column: int(count)
            for column, count in df.isna().sum().items()
        },
        "duplicate_rows": int(df.duplicated().sum()),
        "numeric_statistics": df[numeric_columns].describe().to_dict(),
        "date_range": None,
        "categories": {},
    }

    if "date" in df.columns:
        dates = pd.to_datetime(df["date"], errors="coerce")
        valid_dates = dates.dropna()

        if not valid_dates.empty:
            audit["date_range"] = {
                "start": str(valid_dates.min().date()),
                "end": str(valid_dates.max().date()),
                "invalid_dates": int(dates.isna().sum()),
            }

    for column in ["car_type", "zone"]:
        if column in df.columns:
            audit["categories"][column] = {
                str(key): int(value)
                for key, value in df[column].value_counts(
                    dropna=False
                ).items()
            }

    return audit


def main():
    parser = argparse.ArgumentParser(
        description="Audit MP023 datasets."
    )
    parser.add_argument("--config", default="params.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    paths = config["data"]

    datasets = {
        "train.csv": paths["train_path"],
        "later.csv": paths["later_path"],
        "holdout_features.csv": paths["holdout_path"],
    }

    report = {
        name: audit_dataset(path)
        for name, path in datasets.items()
    }

    output_path = Path("reports/data_audit.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8",
    )

    for name, result in report.items():
        print(
            f"{name}: {result['rows']} rows, "
            f"{result['columns']} columns, "
            f"{result['duplicate_rows']} duplicates"
        )

    print(f"\nAudit report saved to: {output_path}")


if __name__ == "__main__":
    main()
