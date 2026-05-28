# Restaurant survival — Machine Learning  project

Binary classification: predict **`status_closed`** (0 = open, 1 = closed) from tabular restaurant features.

**Main artifact:** `ML_RESTAURANTS.ipynb`

## Models

| Model |
|-------|
| **1. Linear SVM** (`LinearSVC`) |
| **2. Logistic regression** (L2) |
| **3. k-NN** | 


## Notebook steps

| Step | What is done |
|------|----------------|
| **Setup** | Task definition, paths, data file checks, environment note. |
| **1 — EDA** | Explores `restaurants_train.csv`: class balance (~10% closed), missing values, distributions, categories, correlations. |
| **2 — Splits & preprocessing** | Stratified **70% / 15% / 15%** train / validation / test. Drops sparse columns, **log1p** features, preprocessing (imputation, missing flags, **RobustScaler**, grouped one-hot → **155** features). |
| **3 — Models, tuning & submission** | Trains and tunes **three Machine Learning models** (logistic regression, k-NN, linear SVM). Picks the winner by validation balanced accuracy and writes **`restaurant_submission.csv`**. |
| **4 — Evaluation** | Classification report and confusion matrix for the winner on the **internal 15% test**. |
| **5 — Report summary** | Prints model comparison table and CV / validation / internal-test balanced accuracy for the winner. |
| **6 — Hand-in checks** | Verifies `restaurant_submission.csv`. |



## Files

| Path | Description |
|------|-------------|
| `data/restaurants_train.csv` | Labeled training data |
| `data/restaurants_test.csv` | Unlabeled test rows |
| `data/restaurant_sample_submission.csv` | Required output format |
| `restaurant_submission.csv` | Predictions |
| `requirements.txt` | Python dependencies |
