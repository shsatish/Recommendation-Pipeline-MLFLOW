# Data Management for Machine Learning — Assignment 2
## End-to-End Movie Recommendation Data Pipeline

This project implements a reproducible, modular recommendation pipeline covering **Ingestion → Validation → Preparation → Transformation → Feature Management → Model Training → Model Evaluation → Orchestration**.

### Technology

Python 3.10/3.11, Pandas, NumPy, MLflow, CSV-based feature store, deterministic synthetic data, schedulable Python orchestration.

## Run it on Windows PowerShell

```powershell
cd recommendation-pipeline
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m dags.workflow
```

If your command is `python` instead of `py -3.11`, use `python -m venv .venv` for the first command.

### Linux / macOS

```bash
cd recommendation-pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m dags.workflow
```

### View experiments in MLflow

After installing the full requirements and rerunning the workflow:

```bash
mlflow ui --backend-store-uri ./reports/mlruns --port 5000
```

Open http://127.0.0.1:5000 . Experiment name: `movie_recommendation_pipeline`. Each model creates its own run, recording parameters, five ranking metrics, and artifacts. **The supplied sample run was executed without MLflow installed; the JSON audit is not an MLflow experiment. Run with full requirements to generate MLflow evidence.**

## Data and validation

The seeded generator creates 180 users, 95 movies, and 6,500 unique rated interactions with UTC timestamps, then deliberately injects seven invalid rows. Rules: required columns and nulls, integer types, rating 1–5, parsable timestamps, unique IDs/user-item combinations and valid user/item references. Invalid rows and their reasons are exported to `data/errors/`; clean source tables are written to `data/processed/`.

## Preparation and features

The global chronological split reserves the latest 25% of interactions as test. **No test interactions are used for model fitting, item/user aggregate features or the item prior.** Derived outputs include `user_activity.csv`, `item_popularity.csv`, `user_item_matrix.csv`, user/item features and training feature rows. The feature catalog includes names, entity, type, meaning and source.

## Algorithms

**Popularity baseline:** smoothed average rating × `log1p(historical interaction count)`. Smoothing weight: 8.

**Personalized model:** weighted combination of user/category historical mean rating affinity, declared genre preference, smoothed item average rating and small popularity tie-breaker. The transparent category-profile approach qualifies as **content-based personalization**. It is not collaborative matrix factorization.

Recommendations exclude movies that the user already rated in the training period. A cold-start user can use the declared preference; users without prior rating history have zero learned genre affinity.

## Evaluation details

- `K = 5`; relevant test interaction means rating ≥ 4.
- Precision@5 = relevant recommended items / 5.
- Recall@5 = relevant recommended items / relevant held-out user items.
- NDCG@5 = discounted ranking gains / ideal discounted gains.
- Coverage = distinct recommended items / total catalog items.
- Diversity = mean fraction of recommended item pairs belonging to different genres.
- Evaluate only users with at least one positive held-out item, and evaluate exactly the same users for both models. Treat unobserved held-out items as non-relevant (offline evaluation caveat).
- RMSE and MAE are not applicable because these models output ranking scores rather than calibrated predictions of 1–5 ratings.

See `reports/model_comparison.csv` for observed metrics.

## Automated orchestration

`dags/workflow.py` runs seven dependent modules in order, stops immediately on failure and records per-stage status, timings and results in `reports/last_workflow_run.json`. Repeated runs regenerate deterministic input and overwrite output artifacts (idempotent outputs). This satisfies the assignment's **structured scheduled Python workflow** option.

**Linux cron:** add the following line to `crontab -e` (replace path):

```cron
0 2 * * * cd /absolute/path/recommendation-pipeline && /absolute/path/recommendation-pipeline/.venv/bin/python -m dags.workflow
```

**Windows Task Scheduler:** Create Basic Task → Daily → Start program `.venv\Scripts\python.exe`, arguments `-m dags.workflow`, 'Start in' the full project directory. Execute it manually first.

## Artifact map

| Requirement | Evidence |
|---|---|
| Modular source code | `src/` and `dags/workflow.py` |
| Setup / dependencies | `README.md`, `requirements.txt` |
| Architecture | `reports/architecture.png`, `reports/architecture.md` |
| Validation / quarantined rows | `reports/validation_report.json`, `data/errors/` |
| Feature catalog | `reports/feature_catalog.csv` |
| Model comparison | `reports/model_comparison.csv` |
| Orchestration status | `reports/last_workflow_run.json`, `reports/successful_run.txt`, `screenshots/successful_run.png` |
| Final 2–3 page PDF report | `reports/final_report.pdf` |

## Limitations and potential next steps

Synthetic feedback is much simpler than real behavioral data. Offline feedback is biased toward rated content; users/items with no training history get weaker personalization. Genre-only recommendations yield low diversity; ranking diversification, richer text embeddings and A/B testing are future enhancements. This project has no online serving endpoint, data drift detection or distributed scale; those are outside assignment scope.

## Evidence honesty

`screenshots/successful_run.png` is a **generated visual rendering of the real workflow execution log**, not a screenshot of a local terminal application. To submit a literal screenshot requested by your evaluator, run the workflow yourself and capture the terminal window using `Win+Shift+S`. The included PDF documents the tested results; MLflow tracking should be verified after installing full dependencies.
