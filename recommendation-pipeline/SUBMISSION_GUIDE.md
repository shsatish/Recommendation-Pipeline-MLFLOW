# Submission guide — Assignment 2

**Student:** M K S Shanmugam  
**ID:** 2025AG05451  
**Course:** Data Management for Machine Learning  
**Title:** End-to-End Data Management Pipeline for a Recommendation System

## Submit these two items

1. Public GitHub repository URL for the `recommendation-pipeline/` project.
2. `Final_Report_M_K_S_Shanmugam_2025AG05451.pdf` (3-page final report). This report also exists under `reports/final_report.pdf`.

Optional but helpful: provide `Execution_Evidence_MKSS.pdf` as a separate evidence appendix. It shows actual screenshots of validation, quarantining, orchestration and the two MLflow runs. The assignment explicitly requires a screenshot of a successful run, which is also under `screenshots/01_pipeline_success.png`.

## Verify locally before uploading

From the `recommendation-pipeline` folder in PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:MLFLOW_ALLOW_FILE_STORE = "true"
.\.venv\Scripts\python.exe -m dags.workflow
.\.venv\Scripts\python.exe -m mlflow ui --backend-store-uri ./reports/mlruns --port 5000
```

The workflow must show STATUS: SUCCESS. In MLflow, choose Model training, select `movie_recommendation_pipeline`, and check the `popularity` and `personalized` runs. Both are evidenced in the screenshots. The local `reports/mlruns/` directory is ignored in Git; running the pipeline regenerates MLflow tracking for the instructor.

## Important

The original terminal capture contains an earlier transient MLflow storage exception, followed by a later successful rerun. The later run and the MLflow screenshots verify success. Do not commit `.venv/`. The `screenshots/` manifest explains the evidence. GitHub upload has **not** been performed in this package.
