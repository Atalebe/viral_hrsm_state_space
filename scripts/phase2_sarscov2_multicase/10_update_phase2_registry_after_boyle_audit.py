from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

REGISTRY = ROOT / "metadata" / "phase2_sarscov2_multicase" / "phase2_dataset_registry.csv"
SCORED = ROOT / "metadata" / "phase2_sarscov2_multicase" / "phase2_dataset_registry_scored.csv"
BOYLE_SUMMARY = ROOT / "metadata" / "phase2_sarscov2_multicase" / "boyle_temporal_grouping_audit_summary.csv"

TARGET = "BOYLE_2025_PRJNA1295507"

def main():
    if not REGISTRY.exists():
        raise FileNotFoundError(f"Missing registry: {REGISTRY}")
    if not BOYLE_SUMMARY.exists():
        raise FileNotFoundError(
            f"Missing Boyle temporal grouping audit: {BOYLE_SUMMARY}. "
            "Run scripts/phase2_sarscov2_multicase/09_audit_boyle_temporal_grouping.py first."
        )

    registry = pd.read_csv(REGISTRY)
    summary = pd.read_csv(BOYLE_SUMMARY).iloc[0].to_dict()

    mask = registry["case_id"].eq(TARGET)

    if not mask.any():
        raise RuntimeError(f"Could not find {TARGET} in registry.")

    has_dates = bool(summary.get("has_collection_date_mapping", False))
    has_grouping = bool(summary.get("has_patient_or_infection_grouping", False))

    registry.loc[mask, "n_timepoints"] = str(int(summary.get("n_unique_samples", 0)))
    registry.loc[mask, "has_day_mapping"] = "yes" if has_dates else "no"
    registry.loc[mask, "has_variant_frequencies"] = "no"
    registry.loc[mask, "has_ct_or_viral_load"] = "unknown"
    registry.loc[mask, "has_treatment_metadata"] = "unknown"
    registry.loc[mask, "has_host_context"] = "yes"
    registry.loc[mask, "has_endpoint"] = "unknown"

    if has_dates and not has_grouping:
        registry.loc[mask, "admissibility_status"] = "blocked_pending_patient_grouping"
        registry.loc[mask, "notes"] = (
            "BioProject returns 50 runs and BioSample metadata provides collection dates and GISAID accessions, "
            "but no patient or infection grouping is exposed. Do not model as a single trajectory. "
            "Recover Supplemental Table S1 or another grouping source before HRSM extraction."
        )
    elif has_dates and has_grouping:
        registry.loc[mask, "admissibility_status"] = "candidate_ready_for_mapping"
        registry.loc[mask, "notes"] = (
            "BioSample/date and patient grouping present. Proceed to case-level longitudinal mapping."
        )
    else:
        registry.loc[mask, "admissibility_status"] = "blocked_pending_temporal_mapping"
        registry.loc[mask, "notes"] = (
            "Run-level data exist, but temporal mapping remains incomplete."
        )

    registry.to_csv(REGISTRY, index=False)

    # Re-score with current known fields.
    def is_yes(x):
        return str(x).strip().lower() in {"yes", "true", "1", "available", "present"}

    scored = registry.copy()
    scored["n_timepoints_numeric"] = pd.to_numeric(scored["n_timepoints"], errors="coerce").fillna(0)

    has_sequence_features = (
        scored["has_variant_frequencies"].map(is_yes)
        | scored["data_type"].astype(str).str.contains("sequence|vcf|mutation|variant|raw_reads", case=False, na=False)
    )

    scored["phase2_minimum_pass"] = (
        scored["n_timepoints_numeric"].ge(3)
        & scored["has_day_mapping"].map(is_yes)
        & has_sequence_features
    )

    scored["phase2_quality_score"] = 0
    scored["phase2_quality_score"] += scored["n_timepoints_numeric"].ge(3).astype(int)
    scored["phase2_quality_score"] += scored["n_timepoints_numeric"].ge(5).astype(int)
    scored["phase2_quality_score"] += scored["has_day_mapping"].map(is_yes).astype(int)
    scored["phase2_quality_score"] += scored["has_variant_frequencies"].map(is_yes).astype(int)
    scored["phase2_quality_score"] += scored["has_ct_or_viral_load"].map(is_yes).astype(int)
    scored["phase2_quality_score"] += scored["has_treatment_metadata"].map(is_yes).astype(int)
    scored["phase2_quality_score"] += scored["has_endpoint"].map(is_yes).astype(int)

    scored["recommended_role"] = "reject_or_background"
    scored.loc[scored["phase2_minimum_pass"], "recommended_role"] = "candidate"

    # Explicitly block Boyle despite formal date+run completeness, because patient grouping is absent.
    scored.loc[scored["case_id"].eq(TARGET), "recommended_role"] = "blocked_pending_patient_grouping"

    scored.to_csv(SCORED, index=False)

    print({
        "status": "wrote",
        "registry": str(REGISTRY),
        "scored_registry": str(SCORED),
        "target": TARGET,
        "has_collection_date_mapping": has_dates,
        "has_patient_or_infection_grouping": has_grouping,
    })

    print(scored[[
        "case_id",
        "dataset_name",
        "n_timepoints",
        "has_day_mapping",
        "has_variant_frequencies",
        "admissibility_status",
        "phase2_minimum_pass",
        "phase2_quality_score",
        "recommended_role",
        "notes",
    ]].to_string(index=False))

if __name__ == "__main__":
    main()
