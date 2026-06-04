from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "metadata" / "dataset_candidate_registry.csv"
OUT = ROOT / "metadata" / "dataset_candidate_scores.csv"

YES = {"yes", "true", "1", "available", "present"}

SCORE_COLUMNS = [
    "longitudinal_structure",
    "raw_reads_available",
    "consensus_available",
    "viral_load_or_ct_available",
    "treatment_context_available",
    "host_context_available",
    "outcome_label_available",
]

def as_yes(x):
    return str(x).strip().lower() in YES

def main():
    df = pd.read_csv(REGISTRY)
    for col in SCORE_COLUMNS:
        if col not in df.columns:
            df[col] = "unknown"

    df["admissibility_score"] = df[SCORE_COLUMNS].apply(lambda row: sum(as_yes(v) for v in row), axis=1)
    df["recommended_status"] = pd.cut(
        df["admissibility_score"],
        bins=[-1, 2, 4, 7],
        labels=["reject_or_background_only", "candidate", "high_priority"],
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print({"status": "wrote", "path": str(OUT), "n_rows": len(df)})

if __name__ == "__main__":
    main()
