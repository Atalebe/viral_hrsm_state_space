from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]

PRIMARY = ROOT / "data" / "processed" / "phase2_sarscov2_multicase" / "weigang_primary_swab_longitudinal_map.csv"
CONTROLS = ROOT / "data" / "processed" / "phase2_sarscov2_multicase" / "weigang_isolate_control_map.csv"

OUT_FEATURES = ROOT / "data" / "processed" / "phase2_sarscov2_multicase" / "weigang_metadata_proxy_features.csv"
OUT_AUDIT = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_metadata_hrsm_scaffold_audit.csv"
OUT_READINESS = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_raw_feature_readiness_table.csv"

def safe_z(x):
    s = pd.Series(x).astype(float)
    if s.notna().sum() < 2 or np.nanstd(s) == 0:
        return pd.Series(np.zeros(len(s)), index=s.index)
    return (s - np.nanmean(s)) / np.nanstd(s)

def main():
    if not PRIMARY.exists():
        raise FileNotFoundError(
            f"Missing primary Weigang map: {PRIMARY}. "
            "Run 15_build_weigang_longitudinal_map.py first."
        )

    primary = pd.read_csv(PRIMARY)
    controls = pd.read_csv(CONTROLS) if CONTROLS.exists() else pd.DataFrame()

    primary = primary.sort_values(["sample_day", "timepoint_order"]).reset_index(drop=True)

    required = ["sample_day", "timepoint_order", "sample_title", "run_accession", "read_count", "base_count"]
    missing = [c for c in required if c not in primary.columns]
    if missing:
        raise ValueError(f"Primary map missing expected columns: {missing}")

    out = pd.DataFrame()
    out["case_id"] = "WEIGANG_2021_ERP132087"
    out["patient_or_infection_id"] = primary.get("patient_or_infection_id", "1")
    out["sample_title"] = primary["sample_title"]
    out["sample_accession"] = primary["sample_accession"]
    out["run_accession"] = primary["run_accession"]
    out["sample_day"] = primary["sample_day"].astype(int)
    out["timepoint_order"] = primary["timepoint_order"].astype(int)
    out["collection_date"] = primary.get("collection_date_from_attributes", "")
    out["sample_type_hrsm"] = "swab_primary"
    out["source_level"] = "metadata_scaffold_only"

    out["read_count"] = pd.to_numeric(primary["read_count"], errors="coerce")
    out["base_count"] = pd.to_numeric(primary["base_count"], errors="coerce")
    out["mean_bases_per_read"] = out["base_count"] / out["read_count"].replace(0, np.nan)

    # Metadata-only placeholders.
    # These are not biological HRSM axes yet. They exist to make the raw-feature requirements explicit.
    out["coverage_proxy_z"] = safe_z(np.log1p(out["read_count"]))
    out["base_depth_proxy_z"] = safe_z(np.log1p(out["base_count"]))

    # Required raw-derived feature placeholders.
    out["mutation_count"] = np.nan
    out["variant_frequency_entropy"] = np.nan
    out["escape_mutation_frequency"] = np.nan
    out["lineage_backbone_frequency"] = np.nan
    out["within_host_consensus_distance"] = np.nan
    out["lagged_genotype_similarity"] = np.nan
    out["ct_value"] = np.nan
    out["viral_load"] = np.nan

    out["H_v_metadata_proxy"] = out["coverage_proxy_z"]
    out["R_v_metadata_proxy"] = np.nan
    out["S_v_metadata_proxy"] = np.nan
    out["M_v_metadata_proxy"] = np.nan
    out["Phi_v_metadata_proxy"] = np.nan

    out["hrsm_ready"] = False
    out["blocking_reason"] = (
        "Raw-derived mutation-frequency or consensus-distance features are required. "
        "Metadata-only scaffold must not be interpreted as viral HRSM output."
    )

    OUT_FEATURES.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_FEATURES, index=False)

    readiness = pd.DataFrame([
        {
            "feature_family": "H_v reserve",
            "required_feature": "mutation_count or within-host diversity",
            "current_status": "missing",
            "possible_source": "FASTQ/BAM variant calling or published mutation table",
            "notes": "Read depth alone is only a technical proxy and must not be used as biological reserve."
        },
        {
            "feature_family": "R_v recoverability",
            "required_feature": "Ct, viral load, culture status, or rebound/clearance proxy",
            "current_status": "missing",
            "possible_source": "paper clinical timeline or supplementary tables",
            "notes": "No recoverability axis should be computed from sequencing depth."
        },
        {
            "feature_family": "S_v stability/coherence",
            "required_feature": "dominant genotype/escape backbone coherence",
            "current_status": "missing",
            "possible_source": "variant frequency table or raw-derived allele frequencies",
            "notes": "Can be estimated after mutation-frequency extraction."
        },
        {
            "feature_family": "M_v memory",
            "required_feature": "lagged genotype similarity or retained mutation structure",
            "current_status": "missing",
            "possible_source": "longitudinal mutation-frequency matrix",
            "notes": "Weigang days are mapped, so M_v can be computed once mutation features exist."
        },
    ])

    OUT_READINESS.parent.mkdir(parents=True, exist_ok=True)
    readiness.to_csv(OUT_READINESS, index=False)

    audit = pd.DataFrame([{
        "case_id": "WEIGANG_2021_ERP132087",
        "n_primary_swab_timepoints": len(out),
        "min_day": int(out["sample_day"].min()),
        "max_day": int(out["sample_day"].max()),
        "days": "|".join(map(str, out["sample_day"].astype(int).tolist())),
        "n_isolate_controls": len(controls),
        "metadata_scaffold_written": True,
        "hrsm_ready": False,
        "interpretation": "Mapped longitudinal scaffold only. Raw-derived viral features are required before HRSM axes can be interpreted.",
    }])

    OUT_AUDIT.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(OUT_AUDIT, index=False)

    print({
        "status": "wrote",
        "features": str(OUT_FEATURES),
        "audit": str(OUT_AUDIT),
        "readiness": str(OUT_READINESS),
        "n_timepoints": len(out),
    })

    print("\nAUDIT")
    print(audit.to_string(index=False))

    print("\nSCAFFOLD")
    print(out.to_string(index=False))

    print("\nREADINESS")
    print(readiness.to_string(index=False))

if __name__ == "__main__":
    main()
