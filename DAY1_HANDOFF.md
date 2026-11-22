# MP023 – Day 1 Handoff Report

**Group ID:** G175  
**Problem ID:** MP023 – Cab Pick-up Time Prediction  
**Assigned member:** Neeraj  
**Handoff recipient:** Ayush  
**Project:** Trustworthy Data Establishment

---

## 1. Day 1 Objective

Establish trustworthy, reproducible training data for the MP023 Cab Pick-up Time Prediction project.

The work includes dataset inventory, data-quality investigation, leakage identification, cleaning implementation, automated testing, and reproducibility documentation.

## 2. Dataset Inventory

| Dataset | Rows | Columns | Date range |
|---|---:|---:|---|
| train.csv | 1,034 | 12 | 2026-01-01 to 2026-06-30 |
| later.csv | 300 | 12 | 2026-07-01 to 2026-08-31 |
| holdout_features.csv | 250 | 10 | 2026-09-01 to 2026-09-30 |

All three raw datasets have zero missing values and zero invalid dates.

The training dataset contains 34 exact duplicate rows.

## 3. Data Access and Integrity

Expected dataset locations:

- `data/raw/train.csv`
- `data/raw/later.csv`
- `data/raw/holdout_features.csv`

The training and later datasets have DVC tracking files:

- `data/raw/train.csv.dvc`
- `data/raw/later.csv.dvc`

**Important:** No shared DVC remote has been configured. The original CSV files must therefore be provided separately through the group's agreed data-sharing method. The DVC pointer files alone do not contain the datasets.

The holdout dataset is locally ignored by Git and must also be supplied separately if the complete audit is to be reproduced.

### Original training dataset SHA-256

`b054947a822e255fa0a005b84fd1a857566f2400bdb941a92567f862368b1fb6`

Verify using:

```powershell
Get-FileHash .\data\raw\train.csv -Algorithm SHA256
```

The calculated hash must match the value above.

## 4. Seven Data-Quality Findings

| Finding | Present | Evidence |
|---|---|---|
| Leakage column | true | `actual_pickup_after_min` |
| Unit mix-up | false | No supported conversion identified |
| Sentinel value | true | `road_closures = -999`, 54 raw occurrences |
| Duplicate rows | true | 34 extra exact duplicate rows |
| Stuck sensor | true | `rain_mm = 18.8`, 2026-02-10 to 2026-03-05 |
| Target typos | true | 10 verified unique records |
| Spelling variants | false | No observed category spelling variants |

### Leakage

`actual_pickup_after_min` represents information unavailable at prediction time. It must not be included as a model feature.

### Target typo correction

Ten individually verified target records were corrected by dividing their target values by 10.

Corrections were restricted to the verified record IDs and validated against the corresponding actual pickup values.

Legitimate high target values were preserved.

### Unit mix-up

No reliable evidence supported a specific unit conversion. No conversion was applied.

## 5. Approved Model Features

The following eight features are approved:

1. `drivers_nearby`
2. `distance_to_driver_km`
3. `hour`
4. `rain_mm`
5. `surge`
6. `road_closures`
7. `car_type`
8. `zone`

**Target:** `pickup_eta_min`

The cleaned dataset also retains `record_id` and `date` for traceability.

The leakage column `actual_pickup_after_min` is excluded.

## 6. Cleaning Implementation

**Module:** `src/mp023/cleaning.py`

**Function signature:**

```python
clean_training_data(raw_df, rules)
```

The function returns:

- A cleaned copy of the input DataFrame.
- A repair summary containing row counts, repair counts, and remaining missing values.

### Cleaning results

| Operation | Count |
|---|---:|
| Original training rows | 1,034 |
| Duplicate rows removed | 34 |
| Sentinel values repaired | 54 |
| Stuck sensor values repaired | 125 |
| Target typos corrected | 10 |
| Category values mapped | 0 |
| Final training rows | 1,000 |

Remaining missing values:

- `rain_mm`: 125
- `road_closures`: 54

These missing values are intentional repairs. No target values were imputed.

### Output files

- Cleaned training data: `data/processed/train_clean.csv`
- Cleaning summary: `reports/cleaning_summary.json`

The raw training dataset is never overwritten.

## 7. Repeatable Audit

**Module:** `src/mp023/data_checks.py`

The audit records:

- Dataset row and column counts.
- Column names.
- Missing values.
- Duplicate rows.
- Numeric statistics.
- Date ranges.
- Category distributions.

Output:

`reports/data_audit.json`

## 8. Reproduction Instructions

From the project root, use the following commands in PowerShell.

### Install the project

```powershell
python -m pip install -e .
```

Install the test and DVC dependencies if needed:

```powershell
python -m pip install pytest dvc
```

### Run the audit

```powershell
python -m mp023.data_checks --config params.yaml
```

### Run the cleaning pipeline

```powershell
python -m mp023.cleaning --config params.yaml
```

### Run automated tests

```powershell
python -m pytest -q
```

### Validate dependencies

```powershell
python -m pip check
```

### Check Git formatting and changes

```powershell
git diff --check
git status --short
```

## 9. Automated Test Results

Test module: `tests/test_cleaning.py`

Four synthetic tests were implemented:

1. Duplicate removal.
2. Sentinel and stuck-sensor repair.
3. Target correction restricted to verified records.
4. Category mapping.

Latest verified result:

```text
4 passed in 1.20s
```

## 10. Reproducibility Requirement for Ayush

Ayush should independently:

1. Obtain the original raw datasets through the agreed group data-sharing method.
2. Verify the training dataset SHA-256.
3. Run the audit script.
4. Run the cleaning pipeline.
5. Verify the cleaned dataset contains 1,000 rows.
6. Verify the eight approved model features.
7. Verify the leakage column is excluded.
8. Run all four automated tests.

The generated cleaned dataset should match the documented repair counts and output structure.

No learned imputation, scaling, or encoding transformations are performed here. Those belong inside the training pipeline and must respect the validation split.

## 11. Final Deliverables

- `params.yaml`
- `pyproject.toml`
- `src/mp023/config.py`
- `src/mp023/data_checks.py`
- `src/mp023/cleaning.py`
- `tests/test_cleaning.py`
- `reports/data_audit.json`
- `reports/findings.yaml`
- `reports/cleaning_summary.json`
- `data/processed/train_clean.csv`
- DVC tracking files for training and later datasets.

## 12. Git Handoff Status

The project changes have been inspected using Git status.

**Commit:** Pending  
**Push:** Pending  
**Pull request:** Pending  
**Ayush review:** Pending

The final handoff is complete only after the intended files are committed and pushed, a pull request is opened, and Ayush independently reproduces the cleaned dataset.

---

**Prepared by:** Neeraj  
**Group:** G175  
**Project:** MP023 – Cab Pick-up Time Prediction  
**Day:** Day 1 – Establish Trustworthy Data