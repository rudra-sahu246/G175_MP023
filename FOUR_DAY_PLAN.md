# G175 / MP023 — Four-day team execution plan

Repository: https://github.com/rudra-sahu246/G175_MP023

Project: predict cab pick-up time in Lucknow, then deliver the complete MLOps pipeline required by `PROBLEM.md` and `STUDENT_HANDBOOK.md`.

**Detailed working instructions:** follow [DAY_BY_DAY_GUIDE.md](DAY_BY_DAY_GUIDE.md) for numbered tasks, commands, expected outputs, checks, and handoffs for each owner. This file remains the team overview and acceptance checklist.

This is a work plan for the team to implement and understand. Results, findings, experiment IDs, and scores must come from running your own code on your supplied data.

## 1. Team order and schedule

| Day | Owner | Main responsibility | Must hand over |
| --- | --- | --- | --- |
| Day 1 | **Neeraj** | Repository setup, data investigation, DVC, cleaning | Reproducible cleaning code, seven data checks, documented feature contract |
| Day 2 | **Ayush** | Model training, experiment tracking, registry | Trained v1 champion, MLflow database, loadable prediction pipeline |
| Day 3 | **Aanya** | API, tests, Docker, CI, Kubernetes, logging | Tested service and deployment files, green GitHub Actions run |
| Day 4 | **Rudra** | Monitoring, retraining, final predictions, integration and submission checks | v2 comparison, final champion, complete findings, holdout predictions, verified submission package |

Suggested dates if starting on 20 November 2026: **20–23 November**. If starting later, keep the same order and finish all four days before the handbook deadline of **29 November 2026, 11:59 PM**. Confirm the timeline and submission link in the course email.

Each day depends on the previous day's accepted handoff. Everyone reviews the handoff and learns the full pipeline; the listed owner implements their day's work and commits it from their own account. Owners remain available for fixes on subsequent days.

### Roster detail to settle on Day 1

The requested work split has four people: Neeraj, Ayush, Aanya, Rudra. The supplied `GROUP.md` lists **five**, including Paridhi. Confirm the official roster with faculty before preparing the final README and submission. Preserve the supplied group document; do not silently remove an assigned member. If Paridhi remains officially assigned, arrange and document her real contribution and submission too.

## 2. Shared rules and interfaces

### Repository and contributions

- Use this single public repository for the group.
- Aanya, as repository owner, should give all teammates collaborator access before Day 1 work begins. This small setup step does not change her Day 3 implementation assignment.
- Each person clones the repository, configures their own Git identity, and commits their own work. Do not create commits pretending to be another person.
- Use branches such as `day1-data-neeraj`, `day2-model-ayush`, `day3-service-aanya`, and `day4-monitoring-rudra`. Merge each accepted day's work before the next owner starts dependent work.
- Pull the latest merged work before starting. Coordinate changes to shared files, especially `requirements.txt`, `params.yaml`, README, and `reports/findings.yaml`.
- Keep the original supplied data unchanged. Never open and save `train.csv` through Excel.
- Track training and later CSVs with DVC; do not commit those CSVs directly. Commit `mlflow.db`, the serving model, and final predictions as required.
- The CSVs are not available in CI. Tests must create their own small data or use the committed serving model.
- AI assistance should remain tutoring and explanation, consistent with the handbook. Every owner must understand and be able to modify their implementation during viva.

### Agree on this contract on Day 1

| Item | Contract |
| --- | --- |
| Target | `pickup_eta_min` |
| Score | MAE, measured in minutes; smaller is better |
| Input features | `drivers_nearby`, `distance_to_driver_km`, `hour`, `rain_mm`, `surge`, `road_closures`, `car_type`, `zone` |
| Metadata | `record_id` and `date` support identity, checks and splitting; exclude them from model inputs for this plan |
| Leakage | Investigate `actual_pickup_after_min`; exclude post-event information from prediction features |
| Serving artifact | `models/model.joblib`, containing preprocessing and estimator together |
| Registry | One agreed registered model name, recorded in configuration and findings; v1 is version 1, v2 is version 2 |
| Champion | MLflow registry alias `champion`; local serving artifact must match that selected version |
| Configuration | `params.yaml`, loaded using `yaml.safe_load` |
| Package | Suggested name `src/mp023/`, with `__init__.py` and multiple modules |

Keep training-data repairs separate from inference preprocessing. Repairs to training targets and historical unit mistakes must not be blindly applied to already-clean later or holdout data. Share reusable feature preprocessing so training, API, and holdout prediction handle categories and missing values consistently.

## 3. Day 1 — Neeraj: data foundation

**Goal:** Ayush can train tomorrow without guessing how the data should be cleaned.

### Step 1: Establish the repository structure

- Clone the shared repository and read the supplied problem, handbook, group file, and findings template.
- Add the assignment documents to the repository for reference.
- Place the original CSVs under `data/raw/`, preserving their bytes.
- Move the findings template to `reports/findings.yaml`, keeping every original key.
- Create `src/mp023/__init__.py`, initial `params.yaml`, pinned `requirements.txt`, and appropriate `.gitignore` entries.
- Start a README containing the project purpose, repository layout, confirmed group details, and setup instructions.

### Step 2: Configure DVC and verify data identity

- Run `dvc init` and track `data/raw/train.csv` and `data/raw/later.csv` using DVC.
- Commit `.dvc/config`, both `.dvc` pointers, and generated ignore rules.
- Calculate and record the original training file's SHA-256 so Ayush can log it in every MLflow run.
- Arrange how teammates obtain the original datasets: a configured accessible DVC remote, or each member's original supplied zip. DVC pointers alone do not transfer the CSV contents.
- Keep `data/raw/holdout_features.csv` in the required layout; the handbook permits this feature file to be committed.

### Step 3: Investigate all seven data problems

Write reusable inspection code in `src/mp023/data_checks.py`. For each issue, determine presence from the actual data and collect the template's required details.

| Check | Evidence to investigate | Findings fields |
| --- | --- | --- |
| Leaking column | Availability at booking time, comparison with target, absence from holdout | `present`, `column` |
| Unit mix-up | Numeric ranges by `zone`; exact plausible unit conversion | `present`, `column`, `group_value`, `factor` |
| Sentinel value | Repeated impossible numeric value and frequency | `present`, `column`, `value`, `count` |
| Duplicate rows | Full-row duplicates; count extra copies | `present`, `count` |
| Stuck sensor | Date-sorted constant readings over a sustained interval | `present`, `column`, `start_date`, `end_date` |
| Target typos | Isolated targets roughly ten times too large and gap in distribution | `present`, `count` |
| Spelling variants | Category spellings compared with clean later data | `present`, `column`, `true_levels` |

Do not assume every issue exists. Do not replace an exact conversion factor with a rough group-average ratio. Counts should follow the handbook: original rows, or consistently after removing duplicates.

### Step 4: Implement and explain cleaning

- Write `src/mp023/cleaning.py` with explicit, evidence-based repairs.
- Document how missing/sentinel values, duplicates, spellings, target typos, and any stuck interval are handled.
- Preserve record identity and dates for auditing and chronological comparisons.
- Fill only the `data_issues` part of `reports/findings.yaml`; leave later stages to their owners.
- Add meaningful small-data tests for the cleaning behavior.
- Document a real command that runs checks and cleaning, plus its output locations and before/after row counts.

### Day 1 acceptance checklist

- [ ] Original training hash is reproducible and original bytes are preserved.
- [ ] DVC setup and pointers are committed; raw training/later CSVs are ignored.
- [ ] All seven data checks are implemented and their findings are justified.
- [ ] Cleaning can be rerun from the original data without manual spreadsheet edits.
- [ ] Feature columns and cleaning behavior are documented for Ayush.
- [ ] Relevant tests pass and Neeraj's own commits are merged.

**Handoff to Ayush:** cleaning entry point, input/output paths, row counts, original SHA-256, feature list, data-access instructions, findings, and known uncertainties. Ayush runs the cleaning command himself before accepting.

## 4. Day 2 — Ayush: training and MLflow

**Goal:** Aanya receives a model she can load and serve through the agreed eight-feature interface.

### Step 1: Reproduce Day 1 and define evaluation

- Obtain the original datasets and run Neeraj's cleaning code.
- Define and document a reproducible validation strategy using cleaned training data only. A date-based validation split is sensible for this prediction setting.
- Fit learned preprocessing only on each training partition, avoiding validation leakage.
- Keep `later.csv` out of v1 training and tuning; Rudra needs it for the later monitoring/retraining scenario.

### Step 2: Build a reusable model pipeline

- Implement `src/mp023/training.py` and shared model-loading/prediction helpers if needed.
- Combine missing-value handling, categorical encoding, and the regression estimator in one serializable pipeline.
- Try at least three sensible settings and compare validation MAE using the same validation rows.
- After selection, fit the selected v1 configuration on cleaned training data as documented. Distinguish validation scores from any full-data refit.
- Store paths, settings, feature names, seed, and registry name in `params.yaml`; load configuration with `yaml.safe_load`.

### Step 3: Track and register the model

- Set MLflow tracking to `sqlite:///mlflow.db`.
- In every run, log `data_sha256` for the original supplied training file, relevant model parameters, and a metric with `mae` in its name.
- Keep at least three tracked experiment runs.
- Register the chosen v1 as **version 1** and set its `champion` alias. Do not register every tuning candidate as a new version; version 2 is reserved for the retrained v2.
- Export the same champion pipeline to `models/model.joblib`.
- Fill `tracking.experiment_name`, `tracking.best_run_id`, `tracking.registered_model_name`, and the current `tracking.champion_version` in findings. `best_run_id` refers to v1 even if Rudra later promotes v2.
- Commit `mlflow.db` after writes finish. Coordinate exclusive database ownership: Ayush writes it on Day 2, Rudra on Day 4.
- Arrange access to logged model artifacts if later registry loading requires them. A database containing local absolute artifact paths is not sufficient on another teammate's computer; verify transfer or provide a documented portable artifact-loading route tied to the registered version.

### Step 4: Verify the handoff artifact

- Load the saved pipeline in a fresh Python process and predict from a sample with the exact eight fields.
- Confirm that prediction needs neither target nor post-event information.
- Confirm preprocessing handles valid clean categories and the chosen policy for unseen categories.
- Add relevant model tests and pin newly added dependencies.
- Document training and model-loading commands in README.

### Day 2 acceptance checklist

- [ ] At least three MLflow runs exist with the required hash and MAE metrics.
- [ ] v1 is registered as version 1 and has the `champion` alias.
- [ ] `models/model.joblib` loads and predicts using the agreed features.
- [ ] `mlflow.db`, model artifact, configuration, and tracking findings are committed.
- [ ] Validation method and selected result are documented; later data was not used to train v1.
- [ ] Ayush's own commits are merged.

**Handoff to Aanya:** prediction helper, sample input/output, artifact path, exact dependency versions, expected prediction shape, and a fresh-process loading demonstration. Retain a recoverable copy of v1 for Rudra's comparisons.

## 5. Day 3 — Aanya: service and deployment

**Goal:** Rudra receives an integrated service that can continue working with whichever compatible champion he selects tomorrow.

### Step 1: Build `app/main.py`

- Implement `GET /health`, returning at least `{"status": "ok"}`.
- Implement `POST /predict`, loading the pipeline from `models/model.joblib` and returning a clearly documented numeric prediction.
- Declare exactly the eight request fields from the shared contract and reject extra fields.
- Put `le=15` on `distance_to_driver_km` and `ge=0` on `rain_mm` using Pydantic `Field`. Invalid requests must return 422 before model prediction.
- Reuse the pipeline's preprocessing and preserve the expected feature names/order.
- Use Python `logging` with a JSON formatter: one JSON line per prediction, written to stdout. Avoid personal details.

### Step 2: Complete tests and GitHub Actions

- Ensure there are at least three pytest tests overall and at least one uses FastAPI `TestClient`.
- Cover health, valid prediction, distance above 15, and negative rainfall. Also check the valid boundary values of 15 km and 0 mm and the rejection of extra request fields.
- Use small synthetic inputs. Tests must not require the ignored original CSVs or a running MLflow server.
- Write `.github/workflows/ci.yml` with literal `on:` as required by the handbook, triggering on `push`, installing pinned requirements, and running pytest.
- Push and verify a **green GitHub Actions run**. Record its URL in the project notes or README.

### Step 3: Package with Docker

- Use `python:3.12-slim`.
- Copy `requirements.txt` and install dependencies before copying application code.
- Include the package, API code, configuration as needed, and serving model in the image.
- Expose port 8000 and start uvicorn on `0.0.0.0:8000`.
- Add `.dockerignore`; exclude original data, Git files, caches, and unnecessary experiment artifacts while keeping files the API needs.
- Build as `mp023-api:1.0` and smoke-test health and prediction if Docker is available. If unavailable, document that the container was not executed and ensure the local API is verified.

### Step 4: Write Kubernetes manifests

| Setting | Required value |
| --- | --- |
| Deployment name | `mp023-api` |
| Image | `mp023-api:1.0` |
| Replicas | `3` |
| Container port | `8000` |
| Service name | `mp023-svc` |
| Service port / target port | `80` / `8000` |
| Readiness probe | `/health` |
| Liveness probe | `/health`, with a longer initial delay than readiness |
| Selectors | Deployment selector, Pod labels, and Service selector must agree |

Save `k8s/deployment.yaml` and `k8s/service.yaml`. A real cluster is not required for marking.

### Day 3 acceptance checklist

- [ ] API accepts valid input and rejects both client-rule violations with 422.
- [ ] Prediction logs are valid JSON on stdout.
- [ ] Tests pass locally and a green push-triggered Actions run exists.
- [ ] Dockerfile and `.dockerignore` follow the required structure.
- [ ] Kubernetes names, image, replicas, ports, labels, and probes are correct.
- [ ] API setup and usage are documented; Aanya's own commits are merged.

**Handoff to Rudra:** passing test command, API startup command, request example, green CI URL, Docker verification status, and model replacement instructions. The API must use the artifact path rather than hard-code v1.

## 6. Day 4 — Rudra: monitoring, retraining and completion

**Goal:** finish the operational lifecycle, select the champion by the exact rule, and verify every required submission artifact.

### Step 1: Measure drift and group performance

- Reproduce the cleaned training data and load the original v1 before any artifact replacement.
- Implement `src/mp023/monitoring.py`.
- Calculate PSI using 10 bins between cleaned training data and `later.csv`, following the course P13 method. Use consistent bin edges derived from the reference data and document zero-count and constant-column handling.
- The problem says every numeric column; the findings template explicitly lists six numeric input features. Populate all six required entries, and report any additional comparable numeric-column PSI separately without deleting or renaming template keys. If the course convention is unclear, confirm it with faculty rather than silently changing the template.
- Record `monitoring.most_drifted_feature` based on the required numeric input-feature comparison; identify broader numeric-column results separately if different.
- Evaluate v1 on all of `later.csv`, separately for `Airport`, `Old City`, and `Tech Park`.
- Fill `monitoring.mae_by_group` and `monitoring.worst_served_group` from those actual results.

### Step 2: Retrain v2 and apply the promotion rule

- Implement `src/mp023/retraining.py`.
- Sort later data by date, using a stable ordering for tied dates so the split is reproducible.
- Split by rows: first 70% for retraining, last 30% for comparison. For the stated 300 rows, this is 210 and 90; calculate from the actual file length and document rounding.
- Train v2 using cleaned original training data plus only that first 70%.
- Keep the final 30% out of fitting and tuning. Evaluate both v1 and v2 on exactly these same rows.
- Track the v2 run with the original training hash, relevant parameters, and MAE metrics; register it as version 2 under the same model name.
- Apply the rule exactly: when v1 MAE is positive, **promote if `mae_v2 <= 0.90 * mae_v1`; otherwise keep v1**. At exactly 10% improvement, promote. If v1 MAE is zero, keep v1: a zero-to-zero tie is not a 10% reduction. Document that exceptional case without dividing by zero.
- Fill `mae_v1_on_check`, `mae_v2_on_check`, and `decision` with `promote` or `keep`.
- Set the registry `champion` alias to the selected version. Update `tracking.champion_version` and export that same pipeline to `models/model.joblib`.
- Preserve v1 and v2 artifacts and the comparison evidence. Do not train on the final 30% after evaluation unless the course explicitly requires it; this plan's final artifact is the selected evaluated model.

### Step 3: Generate holdout predictions

- Implement a reproducible prediction entry point, such as `src/mp023/predict_holdout.py`.
- Load the selected champion, verifying its version matches the registry and serving artifact.
- Predict all rows in `data/raw/holdout_features.csv` without using unavailable targets or post-event columns.
- Write `predictions/holdout_predictions.csv` with exactly `record_id,prediction` and no saved dataframe index.
- Verify the output row count matches the input, record IDs match in order, and every prediction is finite and non-null. Do not invent a holdout MAE: its true targets are held by the marker.

### Step 4: Verify integration after champion selection

- Run the full test suite with the final serving artifact and check the resulting GitHub Actions run is green.
- Start the API and check health, a valid prediction, and both validation failures.
- If the champion artifact changed, rebuild and smoke-test the Docker image when Docker is available.
- Check `mlflow.db` contains at least three runs, both registered versions, the required parameters/metrics, and the correct alias.
- Review `reports/findings.yaml`: retain every original key, replace all required nulls, and leave issue-detail values null only for absent issues.
- Finish the README with exact reproducible commands, team details, model selection, drift/group findings, API usage, and known verification limits.
- Ask each previous owner to fix any issue in their area and commit that fix themselves. Rudra coordinates final acceptance.

### Day 4 acceptance checklist

- [ ] PSI and per-zone MAE are computed and recorded.
- [ ] Both model versions are registered and evaluated on the same final 30%.
- [ ] Promotion decision follows the exact 10% rule.
- [ ] Registry alias, `tracking.champion_version`, serving artifact, and holdout model agree.
- [ ] Holdout CSV has exactly the required columns and every input record.
- [ ] Findings are complete; final tests and GitHub Actions are green.
- [ ] Required artifacts are committed; Rudra's own contributions are visible.
- [ ] All members complete the final review and individual submission requirements.

## 7. File ownership and required final layout

The proposed module names below are team conventions. Implement them, then put the actual invocation commands in README; the filenames alone do not make a runnable pipeline.

```text
README.md                              Neeraj starts; everyone documents own stage; Rudra finalizes
PROBLEM.md / STUDENT_HANDBOOK.md        Neeraj copies supplied references
GROUP.md                               Neeraj preserves supplied roster
requirements.txt                       Each owner pins dependencies they add
params.yaml                            Neeraj starts; Ayush and Rudra extend
src/mp023/__init__.py                   Neeraj
src/mp023/data_checks.py                Neeraj
src/mp023/cleaning.py                   Neeraj
src/mp023/training.py                   Ayush
src/mp023/monitoring.py                 Rudra
src/mp023/retraining.py                 Rudra
src/mp023/predict_holdout.py            Rudra
tests/test_*.py                         Owners test their work; Aanya completes API coverage
data/raw/train.csv.dvc                  Neeraj
data/raw/later.csv.dvc                  Neeraj
data/raw/holdout_features.csv            Neeraj
.dvc/config                            Neeraj
.gitignore                             Neeraj starts; owners extend
mlflow.db                              Ayush creates; Rudra updates
models/model.joblib                    Ayush exports v1; Rudra exports final champion
app/main.py                            Aanya
Dockerfile                             Aanya
.dockerignore                          Aanya
.github/workflows/ci.yml                Aanya
k8s/deployment.yaml                    Aanya
k8s/service.yaml                       Aanya
reports/findings.yaml                  Neeraj: data; Ayush: tracking; Rudra: monitoring/final state
predictions/holdout_predictions.csv     Rudra
```

Use additional modules or reports where useful. Do not commit virtual environments, secrets, or disposable caches. Keep the exact marker-required paths above.

## 8. Daily handoff routine

1. Owner runs the day's verification and pushes their own commits.
2. Owner posts the commit/PR link, commands run, output summary, and remaining issues to the team.
3. Next owner pulls the work and reproduces the minimum handoff check.
4. Fix blocking issues before declaring the day complete.
5. Merge accepted work and update README so the next person starts from a known working state.

Suggested handoff note:

```text
Day / owner:
Commit or PR:
Files implemented:
Command(s) verified:
Observed result:
Artifacts / paths:
Known issues:
Next owner's first check:
```

If someone finishes early, review and explain the next stage, help debug it, or improve documentation. Keep original ownership clear and record real contributions. Avoid concurrent edits to the SQLite database.

## 9. Marking coverage

| Rubric area | Points | Primary owner |
| --- | --- | --- |
| README, pinned dependencies, configuration, package | 10 | Neeraj starts; everyone maintains; Rudra checks |
| Tests, including TestClient | 6 | Aanya, with earlier owners' tests |
| DVC and original data hash | 6 | Neeraj |
| Seven data problems | 14 | Neeraj |
| MLflow runs, hashes, metrics, versions, champion | 12 | Ayush + Rudra |
| API and request rules | 10 | Aanya |
| Docker packaging | 8 | Aanya |
| CI and green GitHub run | 8 | Aanya; Rudra checks final run |
| Kubernetes manifests | 8 | Aanya |
| JSON logging | 4 | Aanya |
| Drift, group performance, promotion decision | 8 | Rudra |
| Holdout predictions | 6 | Rudra |
| **Total repository score** | **100** | **Whole team** |

Workload differs by type: Neeraj owns investigation, Ayush owns experiments, Aanya owns several integration components, and Rudra owns monitoring plus final coordination. If Day 3 integration takes longer, the original owners help diagnose their interfaces while Aanya remains the service owner.

## 10. Final submission and viva checklist

- [ ] Public repository opens in a private browser window.
- [ ] Official membership is confirmed; README contains all required enrolment numbers.
- [ ] All assigned members have genuine commits under their own accounts.
- [ ] Original data fingerprints match the supplied files.
- [ ] Every mandatory file is in the location expected by the handbook.
- [ ] `mlflow.db` and final serving model are committed.
- [ ] Latest relevant GitHub Actions run is green before submission.
- [ ] Findings and predictions are final and committed before forms are submitted.
- [ ] Every official member separately fills the course form using the same repository URL and accurately describes their contribution.
- [ ] No one relies on pushing fixes after the selected submission cutoff. The handbook grades the last commit before the last member's form time, subject to its grace-period rules.
- [ ] Everyone understands the full pipeline, including work owned by other teammates.

Viva practice: Neeraj explains each data issue and its evidence; Ayush explains MAE, validation leakage, preprocessing, runs versus versions, and the registry; Aanya explains schema validation, tests, CI, ports, probes, and logs; Rudra explains PSI, date-based retraining, group MAE, promotion, and champion consistency. Then each person explains another teammate's stage.

The goal after four days is one reproducible, tested repository with a defensible result and four people who can explain how it works.
