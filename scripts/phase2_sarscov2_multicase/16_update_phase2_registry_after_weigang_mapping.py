from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

REGISTRY = ROOT / "metadata" / "phase2_sarscov2_multicase" / "phase2_dataset_registry.csv"
SCORED = ROOT / "metadata" / "phase2_sarscov2_multicase" / "phase2_dataset_registry_scored.csv"
SUMMARY = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_longitudinal_map_summary.csv"

TARGET = "WEIGANG_2021_IMMUNOSUPPRESSED"

def main():
    if not REGISTRY.exists():
        raise FileNotFoundError(f"Missing registry: {REGISTRY}")
    if not SUMMARY.exists():
        raise FileNotFoundError(f"Missing Weigang mapping summary: {SUMMARY}")

    registry = pd.read_csv(REGISTRY)
    summary = pd.read_csv(SUMMARY).iloc[0].to_dict()

    mask = registry["case_id"].eq(TARGET)
    if not mask.any():
        raise RuntimeError(f"Could not find {TARGET} in registry.")

    n_primary = int(summary.get("n_primary_swab_runs", 0))
    mapping_status = str(summary.get("mapping_status", ""))

    registry.loc[mask, "n_timepoints"] = str(n_primary)
    registry.loc[mask, "has_day_mapping"] = "yes"
    registry.loc[mask, "has_variant_frequencies"] = "no"
    registry.loc[mask, "has_ct_or_viral_load"] = "to_audit"
    registry.loc[mask, "has_treatment_metadata"] = "yes"
    registry.loc[mask, "has_host_context"] = "yes"
    registry.loc[mask, "has_endpoint"] = "to_audit"

    if mapping_status == "hrsm_ready_primary_swab_trajectory":
        registry.loc[mask, "admissibility_status"] = "mapped_primary_swab_trajectory"
        registry.loc[mask, "notes"] = (
            "ERP132087 returns 12 runs. Sample titles encode days. "
            "Nine swab samples define the primary within-host trajectory; isolate samples are retained as controls. "
            "Proceed to metadata-level HRSM scaffold or raw-derived feature planning."
        )
    else:
        registry.loc[mask, "admissibility_status"] = "blocked_pending_mapping"
        registry.loc[mask, "notes"] = "Weigang accession exists but longitudinal mapping did not pass."

    registry.to_csv(REGISTRY, index=False)

    def is_yes(x):
        return str(x).strip().lower() in {"yes", "true", "1", "available", "present"}

    scored = registry.copy()
    scored["n_timepoints_numeric"] = pd.to_numeric(scored["n_timepoints"], errors="coerce").fillna(0)

    has_sequence_features = (
        scored["has_variant_frequencies"].map(is_yes)
        | scored["data_type"].astype(str).str.contains("sequence|vcf|mutation|variant|raw_reads|longitudinal", case=False, na=False)
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
    scored.loc[scored["case_id"].eq(TARGET), "recommended_role"] = "first_true_phase2_mapping_candidate"
    scored.loc[scored["case_id"].eq("BOYLE_2025_PRJNA1295507"), "recommended_role"] = "blocked_pending_patient_grouping"

    scored.to_csv(SCORED, index=False)

    print({
        "status": "wrote",
        "registry": str(REGISTRY),
        "scored_registry": str(SCORED),
        "target": TARGET,
        "n_primary_swab_runs": n_primary,
        "mapping_status": mapping_status,
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
