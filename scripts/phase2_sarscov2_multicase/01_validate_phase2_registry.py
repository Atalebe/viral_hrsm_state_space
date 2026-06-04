from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

REGISTRY = ROOT / "metadata" / "phase2_sarscov2_multicase" / "phase2_dataset_registry.csv"
OUT = ROOT / "metadata" / "phase2_sarscov2_multicase" / "phase2_dataset_registry_scored.csv"

YES = {"yes", "true", "1", "available", "present"}

def is_yes(x):
    return str(x).strip().lower() in YES

def main():
    if not REGISTRY.exists():
        raise FileNotFoundError(f"Missing Phase II registry: {REGISTRY}")

    df = pd.read_csv(REGISTRY)

    required = [
        "case_id",
        "dataset_name",
        "data_type",
        "n_timepoints",
        "has_day_mapping",
        "has_variant_frequencies",
        "admissibility_status",
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Registry missing required columns: {missing}")

    df["n_timepoints_numeric"] = pd.to_numeric(df["n_timepoints"], errors="coerce").fillna(0)

    df["phase2_minimum_pass"] = (
        df["n_timepoints_numeric"].ge(3)
        & df["has_day_mapping"].map(is_yes)
        & (
            df["has_variant_frequencies"].map(is_yes)
            | df["data_type"].astype(str).str.contains("sequence|vcf|mutation", case=False, na=False)
        )
    )

    df["phase2_quality_score"] = 0
    df["phase2_quality_score"] += df["n_timepoints_numeric"].ge(3).astype(int)
    df["phase2_quality_score"] += df["n_timepoints_numeric"].ge(5).astype(int)
    df["phase2_quality_score"] += df["has_day_mapping"].map(is_yes).astype(int)
    df["phase2_quality_score"] += df["has_variant_frequencies"].map(is_yes).astype(int)
    df["phase2_quality_score"] += df["has_ct_or_viral_load"].map(is_yes).astype(int)
    df["phase2_quality_score"] += df["has_treatment_metadata"].map(is_yes).astype(int)
    df["phase2_quality_score"] += df["has_endpoint"].map(is_yes).astype(int)

    df["recommended_role"] = "reject_or_background"
    df.loc[df["phase2_minimum_pass"], "recommended_role"] = "candidate"
    df.loc[df["phase2_quality_score"].ge(5), "recommended_role"] = "high_priority"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    print({
        "status": "wrote",
        "scored_registry": str(OUT),
        "n_rows": len(df),
        "n_candidates": int(df["phase2_minimum_pass"].sum()),
    })

    print(df[[
        "case_id",
        "dataset_name",
        "data_type",
        "n_timepoints",
        "phase2_minimum_pass",
        "phase2_quality_score",
        "recommended_role",
    ]].to_string(index=False))

if __name__ == "__main__":
    main()
