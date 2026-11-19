# G175 / MP023 — Cab pick-up time prediction

Team repository: https://github.com/rudra-sahu246/G175_MP023

SCSE3040 MLOps mini project: predict `pickup_eta_min` for cab bookings in Lucknow. Evaluate regression predictions using mean absolute error (MAE), in minutes.

## Start here

1. Read [PROBLEM.md](PROBLEM.md) and [STUDENT_HANDBOOK.md](STUDENT_HANDBOOK.md).
2. Read the [four-day overview and acceptance checklists](FOUR_DAY_PLAN.md).
3. Follow the [detailed day-by-day implementation guide](DAY_BY_DAY_GUIDE.md), containing 47 sequential tasks, commands, expected outputs, and handoff checks.

## Four-day ownership

| Day | Owner | Responsibility |
| --- | --- | --- |
| 1 | Neeraj | Repository/data setup, seven data checks, cleaning, DVC |
| 2 | Ayush | Model pipeline, experiments, MLflow tracking, registered v1 |
| 3 | Aanya | FastAPI, request validation, tests, logging, CI, Docker, Kubernetes |
| 4 | Rudra | PSI drift, group MAE, retraining, champion selection, holdout predictions, final verification |

Everyone commits their own implementation and understands the whole pipeline. Repository ownership does not change the daily work split. This repository currently contains planning documents and starter materials; model training, service implementation, and measured results remain team tasks.

## Original datasets

The release tagged **`starter-data`** contains `original-data.zip`, holding byte-preserved copies of the three supplied CSVs. Download it from [the starter-data release](https://github.com/rudra-sahu246/G175_MP023/releases/tag/starter-data) and extract its CSVs into `data/raw/`.

The training and later CSVs are deliberately excluded from Git history, as the handbook requires. On Day 1, Neeraj must initialize DVC and generate real `.dvc` tracking files for those originals. No DVC remote has been configured yet. `holdout_features.csv` is already included under `data/raw/`.

Verify dataset SHA-256 values against [reports/original_data_sha256.json](reports/original_data_sha256.json). Never save the originals through Excel or overwrite them during cleaning.

## Starter files

- `reports/findings.yaml`: untouched findings template; fill it with actual code-generated evidence.
- `GROUP.md`: original assigned roster.
- Assignment instructions and both work plans at the repository root.

The requested working split has four members. The supplied official roster lists five, including Paridhi. Confirm official membership with faculty before finalizing the README roster or submitting; preserve the supplied group document.

## Submission

The handbook states a deadline of **29 November 2026, 11:59 PM**. Every official member must submit the same final repository URL separately and describe their genuine contribution. Confirm the exact submission process in the course email.

Only this repository should become the final shared submission if the team agrees to use it; ensure all members use the same link rather than splitting work between the earlier repository and this one.
