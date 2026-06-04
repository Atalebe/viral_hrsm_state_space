import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


def compare_markovian_vs_memory(df, outcome_col):
    """
    Starter classifier comparison.

    Markovian features: H_v, R_v, S_v
    Memory features: H_v, R_v, S_v, M_v

    This is intentionally simple. Later branches can replace it with Bayesian evidence,
    survival models, mixed models, or trajectory models.
    """
    required = ["H_v", "R_v", "S_v", "M_v", outcome_col]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    clean = df[required].dropna()
    y = clean[outcome_col]

    if y.nunique() < 2:
        raise ValueError("Outcome must contain at least two classes.")

    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))

    X_markov = clean[["H_v", "R_v", "S_v"]]
    X_memory = clean[["H_v", "R_v", "S_v", "M_v"]]

    cv = min(5, y.value_counts().min())
    if cv < 2:
        raise ValueError("Not enough samples per class for cross-validation.")

    return pd.DataFrame([
        {
            "model": "markovian_current_state",
            "features": "H_v,R_v,S_v",
            "cv_accuracy_mean": cross_val_score(model, X_markov, y, cv=cv).mean(),
            "cv_folds": cv,
        },
        {
            "model": "non_markovian_memory",
            "features": "H_v,R_v,S_v,M_v",
            "cv_accuracy_mean": cross_val_score(model, X_memory, y, cv=cv).mean(),
            "cv_folds": cv,
        },
    ])
