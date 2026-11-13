# Evidence captured on 13 November 2026

All eight screenshots are user-supplied captures of an actual local workflow / MLflow execution. They are not mockups.

| File | Evidence |
|---|---|
| 01_pipeline_success.png | Seven workflow stages SUCCESS and evaluation metrics (terminal) |
| 02_validation_summary.png | JSON validation report: 6507 raw; 6500 valid; 7 quarantined |
| 03_quarantined_records.png | Invalid CSV rows with reason codes |
| 04_mlflow_experiment_overview.png | MLflow experiment listing |
| 05_project_structure.png | VS Code project structure |
| 06_mlflow_personalized_run.png | Personalized run: Finished, five metrics and five parameters |
| 07_mlflow_popularity_run.png | Popularity run: Finished, five metrics and five parameters |
| 08_mlflow_both_runs.png | Both runs in the MLflow experiment; completed status |

Note: A previous transient MLflow file-backend error is visible in some terminal captures above the subsequent successful run. The user resolved it by setting `MLFLOW_ALLOW_FILE_STORE=true`, and the successful execution and completed MLflow runs are visible in these captures.
