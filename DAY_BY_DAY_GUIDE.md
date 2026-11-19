# MP023 — Detailed four-day implementation guide

Repository: https://github.com/rudra-sahu246/G175_MP023

Read this together with `PROBLEM.md`, `STUDENT_HANDBOOK.md`, and `FOUR_DAY_PLAN.md`. The assignment documents control the assessed requirements. This guide makes the team's implementation sequence explicit.

| Day | Person | Outcome |
| --- | --- | --- |
| 1 | Neeraj | Original data preserved, seven issues investigated, cleaning reproducible |
| 2 | Ayush | Three or more tracked experiments, registered v1, portable prediction pipeline |
| 3 | Aanya | Validated API, tests, green CI, Docker and Kubernetes files |
| 4 | Rudra | Drift report, v2 comparison, champion decision, holdout predictions, final verification |

## How to follow this guide

Every numbered task has an action and a completion condition. Finish tasks in order. A later task must not cover up an unresolved earlier problem. The owner writes the implementation and commits their work; the next owner reproduces the handoff before building on it.

Commands use PowerShell and run from the Git repository root unless stated otherwise. Replace text inside `<...>` with your actual value before executing. The package/module commands below are **interfaces the team must implement**, not scripts already present in the starter folder. This document does not claim any results or completed experiments.

Use a simple editable Python package named `mp023` under `src/mp023`. Neeraj creates a minimal `pyproject.toml` with setuptools package discovery under `src`; each machine installs it using `python -m pip install -e . --no-deps`. This makes `python -m mp023...`, pytest, API imports, and Docker imports consistent. `pyproject.toml` is an additional team convenience; it does not replace pinned `requirements.txt`.

Agree to implement these command interfaces, each accepting `--config params.yaml`:

```powershell
python -m mp023.data_checks --config params.yaml
python -m mp023.cleaning --config params.yaml
python -m mp023.training --config params.yaml
python -m mp023.monitoring --config params.yaml
python -m mp023.retraining --config params.yaml
python -m mp023.predict_holdout --config params.yaml
```

Use Python's `argparse` for these small command interfaces. Each module should expose reusable functions and call its command entry point only under `if __name__ == "__main__"`. Importing a module must not train a model, modify findings, or start a server.

## Before Day 1 — brief setup by everyone

1. **Aanya gives repository access.** In the GitHub repository settings, invite Neeraj, Ayush, and Rudra as collaborators. Each person accepts their invitation. This access setup does not change Aanya's Day 3 implementation slot.
2. **Confirm the official roster.** The supplied `GROUP.md` includes Paridhi as a fifth member. The requested work plan has four people. Confirm the official roster with faculty; preserve the supplied document and ensure every official member gets appropriate contribution/submission arrangements.
3. **Share the original assignment zip.** Every developer needs the original CSVs; Git/DVC pointer files alone will not provide them. Do not distribute a spreadsheet-resaved copy.
4. **Install Git and Python 3.12.** Check `git --version` and `py -3.12 --version`. Aanya should also arrange Docker Desktop before Day 3 if she will build the image locally.
5. **Agree the four working days and a daily handoff time.** Reserve approximately 6–8 focused hours per owner, with extra time if a dependency or tool installation fails. These are working estimates, not a guarantee.
6. **Use genuine Git identities.** Each person uses their own GitHub account and a verified email or their account's GitHub no-reply email. Never configure another teammate's identity to make their commits.

---

## Day 1 — Neeraj: establish trustworthy data

### Day 1.1 — Clone and create your branch

Run these from a parent directory where you want the checkout, not inside the starter folder:

```powershell
git clone https://github.com/rudra-sahu246/G175_MP023.git
Set-Location G175_MP023
git switch -c day1-data-neeraj
git config user.name "<Neeraj's GitHub name>"
git config user.email "<Neeraj's verified GitHub email>"
git status
```

**Check:** the branch is `day1-data-neeraj`, the remote is the shared repository (`git remote -v`), and the identity belongs to Neeraj. Read all assignment instructions before editing anything.

### Day 1.2 — Create the environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
```

If PowerShell activation is blocked by local policy, call `.\.venv\Scripts\python.exe` explicitly for subsequent Python commands rather than changing machine-wide policy.

Install the Day 1 libraries: pandas, NumPy, PyYAML, DVC, pytest, and setuptools as needed for editable packaging. Choose compatible released versions, then record the actual versions used as exact `package==version` entries in `requirements.txt`. Do not put placeholder versions in that file. Later owners add their own exact dependencies and verify installation together. Use a clean environment if recording installed versions so unrelated global packages do not enter the project requirements.

**Check:** the virtual-environment interpreter imports the installed libraries, and `python -m pip check` reports no broken dependencies.

### Day 1.3 — Create directories and preserve the original files

Create these directories if absent:

```text
src/mp023/
tests/
data/raw/
data/processed/
reports/
models/
predictions/
app/
k8s/
.github/workflows/
```

Copy the supplied `PROBLEM.md`, `STUDENT_HANDBOOK.md`, and `GROUP.md` into the repository root. Copy the supplied findings template to `reports/findings.yaml`. Copy the three original CSVs into `data/raw/` using filesystem copying, not an application that parses and saves them.

Calculate SHA-256 for both the source and copied training file with `Get-FileHash -Algorithm SHA256 -LiteralPath <path>`. The hashes must agree. Save the hash and original row/column information in a small provenance report such as `reports/data_provenance.json`. Prefer computing the report through code so it can be recreated.

**Check:** all three filenames are correct, source/copy training hashes match, and the original CSVs have never been edited in place.

### Day 1.4 — Establish packaging and configuration

1. Create `src/mp023/__init__.py`.
2. Create minimal setuptools-based `pyproject.toml`: specify a project name/version, Python 3.12 compatibility, build backend, and package discovery inside `src`.
3. Create `src/mp023/config.py` with a configuration loader using `yaml.safe_load` and basic checks for missing required keys. Resolve paths relative to the repository/configuration location consistently, not an author's personal absolute path.
4. Create `params.yaml` with these agreed settings. These are example team conventions; keep code and configuration consistent:

```yaml
paths:
  train_raw: data/raw/train.csv
  later_raw: data/raw/later.csv
  holdout: data/raw/holdout_features.csv
  train_clean: data/processed/train_clean.csv
  findings: reports/findings.yaml
  model: models/model.joblib
features:
  numeric:
    - drivers_nearby
    - distance_to_driver_km
    - hour
    - rain_mm
    - surge
    - road_closures
  categorical:
    - car_type
    - zone
target: pickup_eta_min
training:
  seed: 42
  validation_fraction: 0.20
tracking:
  uri: sqlite:///mlflow.db
  experiment_name: mp023-pickup-eta
  registered_model_name: mp023-pickup-eta
monitoring:
  psi_bins: 10
  later_train_fraction: 0.70
  required_relative_improvement: 0.10
```

5. Install the package with `python -m pip install -e . --no-deps`.
6. Verify the package imports and that your code actually reads the YAML settings. Merely creating `params.yaml` does not meet the configuration requirement.

**Check:** imports work from the repository root and every path in the configuration has a clear owner/meaning. Ayush will add model settings tomorrow.

### Day 1.5 — Initialize DVC before staging data

```powershell
dvc init
dvc add data/raw/train.csv data/raw/later.csv
dvc status
```

Review the generated `.dvc` pointer files and ignore rules. Add `.venv/`, Python caches, `.pytest_cache/`, editable-install metadata, generated processed data, and disposable MLflow artifact directories to `.gitignore` as appropriate. **Do not ignore `mlflow.db`, `models/model.joblib`, or the final predictions.**

Choose one working data-access method:

- Configure a DVC remote accessible to all four members and test upload/download; keep private credentials out of Git.
- Or document that teammates must copy the original zip's CSVs into `data/raw/` and confirm the expected hash. This is sufficient for handoff when no shared DVC remote is available; do not claim `dvc pull` works without a remote and uploaded objects.

**Check:** `git status --short` proposes pointer/config files, not raw training/later CSV contents. `git check-ignore data/raw/train.csv data/raw/later.csv` confirms those files are ignored.

### Day 1.6 — Produce an initial data inventory

In `data_checks.py`, load training data without modifying it. Record:

1. Actual row count, column names, inferred types, and date range.
2. Missing-value count per column.
3. Numeric minimum, selected quantiles, median, mean, and maximum.
4. Full category frequencies for text features, showing whitespace visibly where useful.
5. Repeated `record_id` count separately from exact full-row duplicates.
6. Column differences between train, later, and holdout. Reading later's schema and clean category spellings is allowed here; do not use it for model selection.

Write the inspection output to `reports/data_audit.json` or a readable report, and document which source rows support each suspected issue. Do not infer exact counts from the assignment's approximate row descriptions.

**Check:** running the checks command twice produces the same findings and never changes the raw file hash.

### Day 1.7 — Check leakage

1. List every candidate feature and ask whether it is known at booking time.
2. Investigate `actual_pickup_after_min`: examine its relationship to `pickup_eta_min`, and its absence from holdout/service inputs.
3. Use correlation or numerical differences as supporting evidence; availability at prediction time is the decisive criterion.
4. Record the evidence and fill `data_issues.leaking_column` with the observed answer.
5. Establish the explicit eight-feature whitelist from `PROBLEM.md`. Every downstream training/inference entry point must use it.

**Check:** post-event columns and the target are absent from the training feature matrix, even if they remain in an audit dataframe.

### Day 1.8 — Check unit mix-up

1. Group numeric summaries by `zone`; inspect distance and other plausible unit-bearing columns.
2. Identify whether one zone's values occupy an implausible scale.
3. Test plausible exact conversions supported by the unit definition, such as metres/km. A ratio of sample means is evidence, not an exact conversion factor.
4. Identify the exact affected rows/group and check the corrected range.
5. Record `column`, `group_value`, and `factor` where `wrong = correct × factor`, or mark absent if evidence does not support this issue.

**Check:** any division/multiplication is applied only to affected original training rows. Clean later and holdout data must not undergo the historical conversion again.

### Day 1.9 — Check sentinel values

1. Inspect frequencies of suspicious numeric values such as `-1`, `-999`, `999`, and `9999`, plus other impossible repeated values actually present.
2. Use the feature's meaning and range to distinguish missing-value codes from valid readings. Zero rain and zero road closures can be valid.
3. Count affected rows using the declared original-row or deduplicated-row convention.
4. Record the actual column, value, and count.
5. Replace a supported feature sentinel with missingness in cleaned data, leaving learned imputation to the modeling pipeline.

**Check:** the sentinel disappears from the cleaned affected feature; legitimate zeros remain unchanged.

### Day 1.10 — Check exact duplicates

1. Compute full-row duplicate count with `df.duplicated().sum()`.
2. Inspect examples to verify they are exact duplicate records.
3. Record the number of extra copies, not the number of all rows participating in duplicate groups.
4. Remove extra copies deterministically, retaining the first occurrence.
5. Investigate repeated IDs with conflicting content separately; do not treat every repeated ID as an exact duplicate.

**Check:** cleaned data has no remaining full-row duplicates; the drop count agrees with the report.

### Day 1.11 — Check stuck sensor intervals

1. Parse `date` and sort stably.
2. For each numeric feature, examine daily counts, distinct values, and runs of identical readings. A run in sorted rows is only a candidate: multiple rows can occur on one date.
3. Confirm whether all relevant rows share an implausibly fixed reading through a sustained observed date interval.
4. Record the first and last affected observed dates and column, with supporting row/date counts. Do not invent readings for missing calendar days.
5. Choose and explain an appropriate feature repair, such as marking the identified readings missing for pipeline imputation. Do not replace a broken feature with the target.

**Check:** the interval boundaries are justified by code, and legitimate repeated categorical/count values are not automatically declared a sensor failure.

### Day 1.12 — Check target typos

1. Sort `pickup_eta_min`; inspect the largest values, quantiles, and gaps.
2. Identify whether a small separated group plausibly has an extra zero.
3. Validate the hypothesis using domain scale and available audit evidence; do not classify every large target as a typo.
4. Count affected rows and record the evidence-based detection rule.
5. Divide supported typo targets by 10 in the training-cleaning step. Preserve valid high targets.

**Check:** target repair is reproducible from original data and is never applied blindly to clean later targets or holdout predictions.

### Day 1.13 — Check spelling variants

1. Inspect `car_type` and `zone` frequencies with exact string representations.
2. Compare variants with the clean levels in later data and the problem's descriptions.
3. Build an explicit canonical mapping for observed variants; stripping whitespace/case may help, but punctuation or abbreviations may require explicit handling.
4. Record the affected column and number of genuine categories as `true_levels`.
5. Keep public outputs consistent with the required zone labels: `Airport`, `Old City`, `Tech Park`.

**Check:** mapped spellings represent the same categories, no legitimate category is merged accidentally, and group-report labels match the template.

### Day 1.14 — Assemble the cleaning function and report

Implement a function such as `clean_training_data(raw_df, rules)` that returns a cleaned copy plus a repair summary. Write `data/processed/train_clean.csv` without overwriting the original.

Use a documented order: inspect raw data; remove exact duplicates; canonicalize categories; repair affected historical units; mark supported sentinels/stuck readings missing; repair supported target typos; parse dates and validate the result. If inspection shows a different order is necessary, document why and keep raw-row counts for reporting.

Do not learn a median, scaling transform, or encoder on the full cleaned dataset here: learned feature preprocessing belongs inside Ayush's training pipeline and must respect the validation split. If a missing target is found, document its handling explicitly; do not impute supervised target values casually.

Record original and final row counts, counts repaired per operation, remaining missingness, selected features, and the unchanged raw hash. Fill all seven `present` flags as actual YAML booleans. For absent issues, leave their detail fields null as the template requires. Preserve all unrelated findings keys.

### Day 1.15 — Add focused tests and hand over

Create synthetic-data tests for the repairs you implement: for example, duplicate removal retaining a unique row, a known category mapping, and correction restricted to affected rows. Tests should verify meaningful edge cases rather than merely asserting that functions exist.

Run:

```powershell
python -m mp023.data_checks --config params.yaml
python -m mp023.cleaning --config params.yaml
python -m pytest -q
python -m pip check
git diff --check
git status --short
```

Review every staged path; stage intended files explicitly. Commit and push your branch, open a pull request through GitHub, and have Ayush review before merging. Preserve author attribution when merging.

**Day 1 handoff package:** reproducible commands, raw hash, access instructions for data, audit report, seven findings, cleaned-data path and counts, cleaning function signature, feature whitelist, test results, and commit/PR link. Ayush should recreate cleaned data himself. Day 1 is complete only when that works.

---

## Day 2 — Ayush: build and register v1

### Day 2.1 — Start from accepted Day 1 work

Clone the repository if needed; otherwise verify your working tree is clean, then:

```powershell
git switch main
git pull --ff-only origin main
git switch -c day2-model-ayush
```

Create/activate your own Python 3.12 environment, install `requirements.txt`, and install the editable project. Obtain raw CSVs using the agreed data-access method. Recalculate the original training SHA-256 and compare it with Neeraj's record. Run checks, cleaning, and tests.

**Stop condition:** if the hash or cleaning counts disagree, resolve this with Neeraj before training. Do not generate replacement findings to hide the disagreement.

### Day 2.2 — Install and pin modeling dependencies

Add compatible versions of scikit-learn, MLflow, and joblib, plus any chosen estimator dependency. Keep the model simple; a good sklearn tree ensemble is a reasonable starting point. Verify that your versions install on Python 3.12 and serialize/load successfully. Run `python -m pip check` after installing the complete requirements.

Record the final runtime versions because Aanya's service and Rudra's retraining must load the serialized pipeline using compatible libraries.

### Day 2.3 — Define the v1 validation split

1. Load cleaned training data and parse dates.
2. Sort by date reproducibly and use approximately the first 80% for fitting and last 20% for validation. Where practical, choose a date boundary so the same day is not split across partitions; document the actual counts.
3. Select only the eight whitelisted input columns as `X`; use `pickup_eta_min` as `y`.
4. Assert that training and validation record selections are separate and target values are finite.
5. Save split date/count metadata in a training report. Do not use later or holdout rows for this selection.

**Check:** all model candidates use identical validation rows and no preprocessing component has been fitted on validation inputs yet.

### Day 2.4 — Implement a preprocessing-plus-model factory

Implement a reusable function such as `build_pipeline(model_settings)` returning an unfitted sklearn `Pipeline`:

1. Numeric branch selects the six numeric features and imputes missing values using training-partition statistics.
2. Categorical branch selects `car_type` and `zone`, handles missingness if needed, and encodes categories with a documented unknown-category policy.
3. A `ColumnTransformer` combines the branches.
4. The final estimator performs regression.

Choose encoding output compatible with the estimator: some estimators accept sparse encoded features and others require dense inputs. Validate that choice in your own environment. Use deterministic random seeds where supported.

Historical repairs are already done on original training data; the pipeline handles normal feature preparation at prediction time. Do not make inference apply a training-only target/unit repair.

**Check:** fitting this object on training inputs and calling `predict` on validation inputs returns one finite numeric value per row. The serialized object must work on raw valid booking-feature values.

### Day 2.5 — Establish a baseline and three model settings

Calculate a simple baseline such as predicting the training target median. Use it to confirm the learned models provide a sensible improvement, but do not invent an assignment MAE threshold.

Try at least three defined estimator configurations. One manageable approach is three settings of the same tree ensemble with different depth/leaf-size choices. Put their exact settings in configuration or a clear experiment table before comparing results. Avoid changing the validation rows between settings.

For every candidate: build a fresh pipeline, fit only on the training partition, predict validation, compute MAE, record elapsed fit time if useful, and save the actual result. Do not repeatedly inspect later data to choose a winner.

### Day 2.6 — Track every experiment in MLflow

Set the tracking URI to `sqlite:///mlflow.db` and the configured experiment name. For each run:

1. Calculate `data_sha256` from the original raw file bytes, not cleaned CSV serialization.
2. Log the hash as parameter `data_sha256`.
3. Log estimator settings, seed, feature set, split information, and cleaning/report version if useful.
4. Log validation MAE with a name such as `mae_validation`.
5. Log the candidate pipeline/artifacts as needed and capture the run ID.
6. End the run cleanly before starting the next.

**Check:** at least three completed runs exist, each has the original hash and an MAE metric. Do not register all candidates: experiment runs and registered model versions are different things.

### Day 2.7 — Select, refit, and register v1

1. Choose the configuration with the lowest validation MAE, applying a documented simple tie-break such as lower complexity.
2. Build a fresh pipeline with that setting and fit it on all cleaned original training rows.
3. Log a final v1 run if useful; preserve the selection-validation MAE and identify the split/candidate it came from rather than presenting a full-fit training score as validation.
4. Log the final fitted pipeline as an MLflow model, with a booking-feature input example/signature where supported.
5. Register this final v1 under the agreed registered model name; verify it becomes version **1**.
6. Assign alias `champion` to version 1.
7. Export the same fitted object to `models/model.joblib` and preserve `models/v1.joblib` for Rudra's future comparison.
8. Save a small `models/champion_metadata.json` containing registered name, version, run ID, original data hash, runtime versions, and serving-artifact SHA-256. This is a team consistency aid, not a required marker file.

If the installed MLflow version rejects serialization with an untrusted-types error, follow the handbook's `serialization_format="cloudpickle"` guidance for the relevant model logging call. Check the installed API before applying version-specific options.

**Check:** the registered version references the final fitted model, not an earlier validation-only candidate. The model serving artifact and metadata refer to this same model.

### Day 2.8 — Make the handoff portable

MLflow's SQLite database records metadata; model artifacts can live elsewhere. Aanya/Rudra need actual artifacts as well as the database.

1. Keep `models/v1.joblib` and `models/model.joblib` available in the repository as required/appropriate.
2. Arrange a shared MLflow artifact location or document and test an artifact-transfer procedure that makes registered model URIs resolvable on another machine.
3. Do not assume a URI referencing your personal `C:\Users\...` folder works on another computer.
4. Have Aanya load the registry version or its verified associated artifact from her checkout. If working offline with an exported artifact, check its metadata against the registry version; do not claim an inaccessible registry URI was tested.
5. Close active writes before committing `mlflow.db`. Do not let two people independently modify and merge this binary database.

### Day 2.9 — Fill tracking findings and verify predictions

Fill the four original tracking fields from the actual final v1 run and registry:

- `experiment_name`: configured experiment actually used.
- `best_run_id`: final registered v1's run ID, with selection information documented.
- `registered_model_name`: exact registry name.
- `champion_version`: current version 1.

Use this valid input for a loading smoke test; its expected prediction must come from your model:

```json
{"drivers_nearby": 5, "distance_to_driver_km": 2.5, "hour": 18, "rain_mm": 0, "surge": 1.2, "road_closures": 0, "car_type": "sedan", "zone": "Airport"}
```

Verify a fresh process can load `model.joblib`, construct a one-row dataframe with the eight names, and produce a finite prediction without original CSVs or a running tracking server. Add a focused pipeline test using synthetic data if needed; record load/runtime checks in the report.

### Day 2.10 — Document, commit, and hand over

Document environment installation, training command, split method, three actual candidate MAEs, chosen settings, registry/run/version IDs, serialization route, and sample prediction procedure. Update pinned requirements and configuration.

Run tests, `python -m pip check`, and `git diff --check`. Review staged changes, commit under Ayush's identity, push, and request Aanya's handoff review. Do not rerun registration just to demonstrate it after version 1 exists; inspection and loading are sufficient. Document how training avoids accidental duplicate registrations on rerun.

**Day 2 handoff package:** pipeline factory, v1 artifacts, artifact-transfer instructions, MLflow database, registry/run IDs, exact versions, eight-feature sample, command outputs, candidate comparison report, and merged commit. Aanya must demonstrate a fresh-process load before accepting.

---

## Day 3 — Aanya: make the prediction service reliable

### Day 3.1 — Reproduce and inspect the model handoff

Pull accepted Day 2 work into a new `day3-service-aanya` branch. Set up Python 3.12 and install requirements plus the editable package. Run tests and the standalone model-loading check. Add and pin FastAPI, uvicorn, Pydantic, and httpx as needed for TestClient compatibility.

**Check:** you can predict without the original data. The API must depend on the exported champion pipeline, not on training execution during startup.

### Day 3.2 — Define the API contract

Create `app/__init__.py` and `app/main.py`. The request model has exactly these required fields:

| Field | Suggested Python type | Required rule |
| --- | --- | --- |
| `drivers_nearby` | int | Required |
| `distance_to_driver_km` | float | `Field(..., le=15)` |
| `hour` | int | Required |
| `rain_mm` | float | `Field(..., ge=0)` |
| `surge` | float | Required |
| `road_closures` | int | Required |
| `car_type` | str | Required |
| `zone` | str | Required |

Configure the Pydantic model to forbid additional fields. If adding other domain constraints, document them and verify they accept valid assignment inputs; the two mandatory rules above must be in the schema itself. Do not require metadata, target, or post-event columns.

Choose a simple documented response such as `{"prediction": <float>}`. A response model can make its shape clear.

### Day 3.3 — Implement model lifecycle and endpoints

1. Load `models/model.joblib` once during application startup/lifespan rather than on every request.
2. Resolve the artifact path consistently; fail startup clearly if the artifact is missing/corrupt rather than silently substituting a dummy prediction.
3. Store the loaded pipeline in application state or an explicit dependency that tests can replace.
4. Implement `/health` to return `{"status": "ok"}` when the application is ready. Additional version metadata is optional.
5. For `/predict`, use the validated request to build a dataframe with the exact eight feature names, call the pipeline, and turn the one-element result into a JSON-compatible float.
6. Verify the output is finite and handle genuine prediction failures through a clear error path.
7. Avoid any training, data cleaning of historical targets, or registry modification during API requests.

**Check:** `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000` starts successfully from the repository root. The selected champion can change tomorrow without changing endpoint code.

### Day 3.4 — Add JSON logging to stdout

Use Python's `logging` module and a JSON formatter with `StreamHandler(sys.stdout)`. Emit a single prediction-event JSON object for every successful prediction. Useful fields include timestamp, event name, model version if known, prediction, and elapsed time. Avoid personal information and unnecessary full request dumps.

Configure handlers once so repeated application/test creation does not multiply logs. Uvicorn may have its own access logs; verify the application's prediction-event line is valid JSON and not printed multiple times.

**Check:** send one valid request, copy its prediction-event line, and parse it with a JSON parser. Invalid schema requests should not create a successful-prediction event.

### Day 3.5 — Write meaningful API tests

Create `tests/test_api.py` using `TestClient`; use its context manager when testing application lifespan. Use synthetic request data. Tests must not read raw CSVs or need a live MLflow server.

Implement these cases:

1. Health returns 200 and body contains `status == "ok"`.
2. Valid eight-field request returns 200 and a finite numeric `prediction`.
3. Distance 15.01 returns 422.
4. Rainfall -0.1 returns 422.
5. Distance exactly 15 and rainfall exactly 0 are accepted.
6. Missing required field returns 422.
7. An extra field such as `actual_pickup_after_min` returns 422.
8. For both mandatory validation failures, a model spy/stub confirms `predict` was never called. This verifies rejection happens before inference.

Use a dependency/stub for focused schema tests and at least one smoke check with the committed real model. Avoid exact floating-point prediction assertions tied to one trained artifact; Rudra may legitimately replace the champion.

**Check:** at least three collected pytest tests exist overall, including TestClient usage; the broader cases above provide stronger coverage than the minimum. `python -m pytest -q` passes without raw data.

### Day 3.6 — Write and verify GitHub Actions

Create `.github/workflows/ci.yml` as plain YAML text. Because the handbook explicitly requires it, put literal `on:` as the first top-level key and configure `push`; optional pull-request triggering may be added. Do not write the workflow using a YAML 1.1 serializer that changes `on` to `true`.

Define a job on a supported GitHub-hosted runner that:

1. Checks out the repository.
2. Sets up Python 3.12.
3. Installs `requirements.txt`.
4. Installs the project with `python -m pip install -e . --no-deps`.
5. Runs `python -m pytest -q`.

Use supported official action versions verified when implementing. A Linux runner is useful for catching case-sensitive imports and platform-specific path assumptions. The job must not depend on your local files, raw CSVs, Docker Desktop, or an existing MLflow service.

Push and inspect the actual Actions job log. If red, read the first meaningful failure, fix it, and rerun by pushing a correction. Record the successful run URL and commit SHA. A workflow file without a real green run does not satisfy this handoff.

### Day 3.7 — Write the Dockerfile and ignore rules

Build the image in this order:

1. Base image `python:3.12-slim`.
2. Set a working directory such as `/app`.
3. Copy `requirements.txt`.
4. Install pinned dependencies.
5. Copy package metadata, source, API, configuration/metadata needed at runtime, and model artifacts.
6. Install the local package with dependencies already installed.
7. `EXPOSE 8000`.
8. Exec-form command starting uvicorn with `app.main:app --host 0.0.0.0 --port 8000`.

Create `.dockerignore` excluding `.git`, `.venv`, caches, raw/processed datasets, unnecessary MLflow artifacts/database, and other development files the service does not need. Verify that `models/model.joblib`, package source, and `pyproject.toml` remain in the build context.

With Docker available:

```powershell
docker build -t mp023-api:1.0 .
docker run --rm -d --name mp023-smoke -p 8000:8000 mp023-api:1.0
```

Stop any local uvicorn process first if port 8000 is occupied. Wait for successful startup before the requests in the next task.

### Day 3.8 — Smoke-test HTTP behavior

These PowerShell commands exercise either the running container or local API:

```powershell
Invoke-RestMethod -Uri http://localhost:8000/health
$sampleBooking = @{
    drivers_nearby = 5
    distance_to_driver_km = 2.5
    hour = 18
    rain_mm = 0
    surge = 1.2
    road_closures = 0
    car_type = "sedan"
    zone = "Airport"
}
$sampleBody = $sampleBooking | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://localhost:8000/predict -ContentType "application/json" -Body $sampleBody
```

Then repeat with distance above 15 and negative rain, verifying HTTP 422. PowerShell may throw on non-success status; inspect the exception/status or rely on the automated status assertions. Inspect `docker logs mp023-smoke` for startup and JSON prediction events; stop the test container with `docker stop mp023-smoke` when done.

**Check:** note whether the API was tested locally, inside Docker, or both. If Docker could not be run, report that limitation accurately instead of marking the build as verified.

### Day 3.9 — Write Kubernetes YAML

For `k8s/deployment.yaml`:

1. Use `apps/v1`, kind `Deployment`, metadata name `mp023-api`.
2. Set `replicas: 3`.
3. Use an agreed label such as `app: mp023-api` in both `spec.selector.matchLabels` and the Pod template labels.
4. Set container image to `mp023-api:1.0` and container port to 8000.
5. Configure an HTTP readiness probe at `/health` port 8000, for example initial delay 5 seconds and period 5 seconds.
6. Configure an HTTP liveness probe at `/health` port 8000, for example initial delay 15 seconds and period 10 seconds. The liveness delay must be longer than readiness.

For `k8s/service.yaml`:

1. Use `v1`, kind `Service`, metadata name `mp023-svc`.
2. Match the Pod label with selector `app: mp023-api`.
3. Set service port 80 and target port 8000, using TCP.

Parse/review both YAML files and check every exact value against `PROBLEM.md`. A real cluster is not required. Local Docker images also do not automatically become available to an arbitrary Kubernetes cluster; if demonstrating a cluster, separately arrange image availability.

### Day 3.10 — Finalize and hand over

Run the tests, inspect the workflow's green run, and update README with API startup, sample input/response shape, validation behavior, Docker commands, manifest explanation, and verification limits. Commit/push under Aanya's identity and have Rudra review/merge.

**Day 3 handoff package:** working API, tests, green CI URL/SHA, logging check, Docker build/test status, manifests, runtime commands, model path/version metadata, and instructions to restart/rebuild after champion replacement. No endpoint should hard-code v1.

---

## Day 4 — Rudra: monitoring, retraining, and completion

### Day 4.1 — Establish the starting state

Pull accepted Day 3 work into `day4-monitoring-rudra`. Install the agreed environment, obtain original data, confirm the training hash, reproduce cleaning, and run all tests. Load preserved `models/v1.joblib` and inspect the registry's version 1 and current alias.

Record the starting commit, model version, runtime versions, and cleaned/later row counts in `reports/monitoring_report.json` or an equivalent readable report. Preserve v1 before replacing any champion artifact. Coordinate exclusive write access to `mlflow.db` for today.

**Check:** you can reproduce a v1 prediction and API health before making changes. Resolve existing failures with their owners first.

### Day 4.2 — Implement PSI following P13

Create reusable PSI functions in `src/mp023/monitoring.py`:

1. Load cleaned training and clean later data without applying historical training-only repairs to later.
2. Identify all numeric columns comparable between the two datasets. Keep the six required input-feature PSI entries separate from any additional numeric diagnostic results.
3. Follow the course P13 procedure to create 10 bins from the reference training distribution. Check the lab's binning and smoothing convention; do not silently substitute a different method if exact comparison is expected.
4. Use the same edges for later values. Ensure the boundary treatment accounts for later values beyond the reference range.
5. Count reference and later observations per bin and convert to proportions.
6. Handle zero proportions using P13's documented epsilon/smoothing method.
7. Sum `(later_proportion - reference_proportion) * log(later_proportion / reference_proportion)` across bins.
8. Handle missing values and constant columns explicitly; repeated quantile edges may reduce effective bins. Report the handling/effective bin count rather than crashing or inventing bin counts.
9. Save edges, counts, proportions, PSI, and comparable-row counts for auditability.

The problem says every numeric column while the template names six numeric input features. Populate every original template entry, report PSI for additional comparable numeric columns separately, and label which ranking you report. Preserve template keys. If P13/faculty gives a specific convention for the most-drifted answer, use that convention.

**Check:** PSI is finite and non-negative apart from numerical rounding; comparing a reference distribution with itself gives approximately zero. Use one small synthetic check for this mathematical behavior and a shifted distribution.

### Day 4.3 — Fill the required drift findings

For `drivers_nearby`, `distance_to_driver_km`, `hour`, `rain_mm`, `surge`, and `road_closures`, copy actual computed PSI values into `monitoring.psi`. Compute the largest required-feature PSI and record the corresponding exact column name in `most_drifted_feature`, unless clarified course instructions require another scope. Document any tie and the deterministic tie-break.

Write a short interpretation in the report: what changed, how large the measured change was, and why it may affect pick-up estimates. PSI measures distribution change; it does not by itself prove model accuracy worsened.

**Check:** findings values match saved calculations, not rounded values guessed from plots.

### Day 4.4 — Evaluate v1 by zone

1. Predict all later rows with preserved v1, using only the eight features.
2. Align predictions with original rows/targets by retained row order or explicit identity.
3. Group by clean `zone` labels and compute `mean(abs(target - prediction))` separately.
4. Record group sample counts as well as MAE in the detailed report.
5. Populate the three original `mae_by_group` entries.
6. Set `worst_served_group` to the exact zone with the greatest v1 MAE; document tie handling if needed.

**Check:** these metrics use all of later data with v1. They are distinct from the final-30% model comparison and should not be overwritten with v2 group metrics.

### Day 4.5 — Create the retraining/check split

In `src/mp023/retraining.py`:

1. Parse later dates and use a stable date sort preserving original order among equal dates, or document another deterministic tie-break.
2. Compute `split_index = floor(0.70 * len(later))`.
3. Take rows before that index as `later_train` and remaining rows as `later_check`. For 300 rows, expect 210 and 90; use actual file length.
4. Record each partition's size, dates, and IDs in the report.
5. Assert no row appears in both partitions.
6. Combine cleaned original training rows with only `later_train` for v2 fitting.

The assignment specifies the first 70% by date-sorted rows. Unlike the optional v1 validation choice, do not change this to an arbitrary whole-day split that violates the required row fraction.

**Check:** `later_check` is untouched by v2 fitting and hyperparameter choice. Do not use holdout for either purpose.

### Day 4.6 — Fit v2 and compare fairly

1. Reuse Ayush's pipeline factory and a documented configuration, preferably the already selected setting to keep the exercise manageable.
2. Build a fresh unfitted pipeline and fit it on cleaned train plus `later_train`. Refit preprocessing as part of the pipeline on this combined fitting dataset.
3. Predict `later_check` with preserved v1 and the newly fitted v2.
4. Compute both MAEs against exactly the same targets in the same order.
5. Save `models/v2.joblib`, comparison metrics, partition metadata, and optional row-level check predictions in a report.
6. Log v2 in MLflow with `data_sha256` of the original training CSV, fitting counts, settings, and MAE metric(s). Log later data's hash separately if useful.
7. Register the v2 artifact under the same model name as version **2**, once. Verify both versions exist before changing the alias.

**Check:** comparison MAEs are finite and based on held-out later rows; full fitting-data MAE is not substituted for the required check MAE.

### Day 4.7 — Apply and record promotion

Apply the client's rule exactly when `mae_v1 > 0`:

```text
promote if mae_v2 <= 0.90 × mae_v1
otherwise keep v1
```

At exactly 10% improvement, promotion qualifies. If v1 MAE is exactly zero, a strictly lower non-negative MAE is impossible: keep v1 and document this exceptional case rather than interpreting a zero-to-zero tie as a 10% improvement. Do not divide by zero when reporting the percentage.

For illustration only: 5.0 to 4.4 minutes qualifies; 5.0 to 4.6 does not. These are examples, not your project's results.

1. Fill `mae_v1_on_check`, `mae_v2_on_check`, and `decision` (`promote` or `keep`) from your real comparison.
2. If promoted, set alias `champion` to version 2; otherwise retain version 1.
3. Update `tracking.champion_version` to the chosen version. Preserve `best_run_id` as the v1 tracking reference requested by the template.
4. Export the chosen version to `models/model.joblib` and update `champion_metadata.json` with version, run ID, and artifact hash.
5. Reload it in a fresh process and check it matches the selected candidate's predictions on the same sample rows within numerical tolerance.
6. Save a short decision explanation with the actual two MAEs and improvement.

**Check:** registry alias, metadata, findings, and serving artifact select the same version. Do not refit on `later_check` after this comparison and silently replace the evaluated champion.

### Day 4.8 — Generate final holdout predictions

Implement `src/mp023/predict_holdout.py`:

1. Load configuration, inspect registry champion/associated metadata, and load the selected champion artifact. Prefer resolving the alias directly when the shared artifact store is available; otherwise use the verified exported artifact associated with that alias.
2. Read `data/raw/holdout_features.csv` and preserve original row order and `record_id` text.
3. Verify all eight required inputs are available. Select them explicitly and call the same pipeline used by the service.
4. Create a dataframe with precisely `record_id` and `prediction`.
5. Save `predictions/holdout_predictions.csv` using `index=False`.
6. Reload the saved file to verify serialization did not introduce an extra index column or missing values.

Validate all of these:

- Exact column order is `record_id,prediction`.
- Output and input row counts match; expect 250 only if the actual file has 250.
- ID sequence matches the input exactly, and uniqueness is checked against the source rather than assumed.
- Predictions are numeric, finite, and non-null.
- The prediction model version equals the current champion.

**Check:** no target data was invented or used. You cannot calculate the true holdout MAE because those labels are not provided.

### Day 4.9 — Complete findings without breaking its schema

Review every original template section:

| Section | Verify |
| --- | --- |
| Identity | `group_id: G175`, `problem_id: MP023` |
| Data issues | Seven actual booleans; required evidence fields filled for present issues; absent details null |
| Tracking | Existing experiment/run/model references and final champion version |
| PSI | All six original numeric-feature entries populated |
| Group metrics | All three exact zone labels and actual v1 MAEs |
| Comparison | Both last-30% MAEs and correct decision |

Parse with `yaml.safe_load` to catch syntax/type mistakes. Keep original keys and use plain YAML numbers/booleans rather than serialized NumPy objects or strings such as `"true"`. Put extra explanation in separate reports instead of replacing required fields.

**Check:** required nulls are gone, permitted nulls remain only where a data issue is absent, and each recorded result can be traced to executable code/report output.

### Day 4.10 — Perform final integrated verification

Run:

```powershell
python -m pytest -q
python -m pip check
git diff --check
git status --short
```

Then verify the actual final model/API flow: fresh-process artifact load, service startup, health, valid prediction, distance rejection, rainfall rejection, and JSON event logging. Restart the service after changing the model because startup-loaded pipelines do not update automatically. If Docker is available, rebuild `mp023-api:1.0` with the final artifact and repeat the smoke tests.

Inspect the MLflow registry and database for at least three runs, required hashes/MAE metrics, two versions, and correct champion. Confirm a new checkout can obtain original data, install requirements, import the package, run tests, and reproduce documented steps without relying on an author's absolute paths.

Do not rerun training/registration commands blindly during this final audit: doing so may append versions or change the evidence. Use inspection/loading and the documented rerun policy.

### Day 4.11 — Finish README and collect contribution evidence

README should contain:

1. Project purpose, target, and MAE explanation.
2. Confirmed group ID, problem ID, and every official member's enrolment number.
3. Setup commands for Python environment, requirements, editable package, and raw-data retrieval.
4. Required command order, expected artifacts, and configuration explanation.
5. Data cleaning summary and original data hash.
6. Actual model comparison/registry information.
7. API startup, request example, response shape, and validation constraints.
8. Test, Docker, and Kubernetes instructions, including what was actually executed.
9. Drift/group results, promotion rationale, and holdout output path.
10. Green CI link and honest per-person ownership/contribution summary.

Each person reviews their own code and contribution description. Link actual commits/PRs where helpful. Do not manufacture commits, hours, successful checks, or member contributions.

### Day 4.12 — Push, verify GitHub, and submit

1. Close database writers, review intended files, and commit final outputs under Rudra's identity.
2. Push, review/merge through the team's normal process, and wait for the actual final push-triggered Actions job to pass.
3. Open the public repository in a private browser window. Verify key files, final model/database, and predictions are present on the remote, not just locally.
4. Record the final commit SHA and green run URL.
5. Have each official member fill the course submission form independently with the same repository URL and truthful personal work details.
6. Follow the handbook's timing rule: the assessed commit must precede the relevant final submission cutoff. Finish and push before forms; do not assume later fixes will count.
7. Aim to submit by 29 November 2026, 11:59 PM; the course email controls the form link and detailed timeline.

**Day 4 completion package:** merged final commit, green CI URL, complete findings, v1/v2 artifacts and registry evidence, final champion export, valid holdout CSV, reproducible README, and confirmation each official member submitted their form.

---

## Daily time budget and recovery rules

| Owner | Suggested focused work blocks |
| --- | --- |
| Neeraj | Setup/DVC 1–2 h; inspection and seven checks 2–3 h; cleaning/tests 1–2 h; handoff 1 h |
| Ayush | Reproduce/setup 1 h; pipeline/splits 1–2 h; experiments/MLflow 2–3 h; portability/tests/handoff 1–2 h |
| Aanya | API/logging 2 h; tests/CI 2 h; Docker/Kubernetes 2 h; documentation/handoff 1 h |
| Rudra | Reproduce/monitoring 2 h; retraining/registry 2 h; predictions/findings 1 h; integration/submission 2 h |

If time slips, keep the estimator and documentation straightforward; finish the mandatory lifecycle before polishing optional extras. Ask the original owner to repair their interface while the current owner continues independent tasks. Never skip a failed handoff, fabricate results, or leave the final champion inconsistent across outputs.

## Four questions each teammate must answer at handoff

1. What did you implement, and which exact files contain it?
2. What command recreates or verifies it from the agreed starting point?
3. What evidence shows the result is correct, and what remains unverified?
4. What does the next person need, and have they successfully used it?

Use the checklists in `FOUR_DAY_PLAN.md` as the acceptance record and this guide as the detailed working instructions.
