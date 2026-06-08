from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_run_manifest_with_biosample_metadata.csv"

OUT_MAP = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_longitudinal_sample_map.csv"
OUT_PRIMARY = ROOT / "data" / "processed" / "phase2_sarscov2_multicase" / "weigang_primary_swab_longitudinal_map.csv"
OUT_CONTROLS = ROOT / "data" / "processed" / "phase2_sarscov2_multicase" / "weigang_isolate_control_map.csv"
OUT_SUMMARY = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_longitudinal_map_summary.csv"

def extract_day(sample_title):
    m = re.search(r"_d(\d+)(?:\(|$|_)", str(sample_title))
    if not m:
        # fallback catches final d105(del)
        m = re.search(r"_d(\d+)", str(sample_title))
    return int(m.group(1)) if m else None

def classify_sample_type(sample_title):
    s = str(sample_title).lower()
    if "swab" in s:
        return "swab_primary"
    if "isolate" in s:
        return "isolate_control"
    return "unknown"

def extract_attr(all_attributes, key):
    if pd.isna(all_attributes):
        return ""
    pattern = rf"{re.escape(key)}=([^|]+)"
    m = re.search(pattern, str(all_attributes))
    return m.group(1).strip() if m else ""

def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing Weigang joined manifest: {INPUT}. "
            "Run 13_build_weigang_run_manifest.py and 14_expand_weigang_biosample_metadata.py first."
        )

    df = pd.read_csv(INPUT)

    required = ["sample_title", "sample_accession", "run_accession"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    out = df.copy()
    out["sample_day"] = out["sample_title"].apply(extract_day)
    out["sample_type_hrsm"] = out["sample_title"].apply(classify_sample_type)

    if "all_attributes" in out.columns:
        out["host_subject_id"] = out["all_attributes"].apply(lambda x: extract_attr(x, "host subject id"))
        out["collection_date_from_attributes"] = out["all_attributes"].apply(lambda x: extract_attr(x, "collection date"))
        out["host_age_from_attributes"] = out["all_attributes"].apply(lambda x: extract_attr(x, "host age"))
        out["host_sex_from_attributes"] = out["all_attributes"].apply(lambda x: extract_attr(x, "host sex"))
        out["host_scientific_name_from_attributes"] = out["all_attributes"].apply(lambda x: extract_attr(x, "host scientific name"))
        out["geographic_location_from_attributes"] = out["all_attributes"].apply(lambda x: extract_attr(x, "geographic location (country and/or sea)"))
    else:
        out["host_subject_id"] = ""
        out["collection_date_from_attributes"] = ""

    out["patient_or_infection_id"] = out["host_subject_id"].replace("", pd.NA).fillna("WEIGANG_SUBJECT_1")
    out["timepoint_order"] = out.groupby(["patient_or_infection_id", "sample_type_hrsm"])["sample_day"].rank(method="dense").astype("Int64") - 1

    out["phase2_mapping_status"] = "mapped"
    out.loc[out["sample_day"].isna(), "phase2_mapping_status"] = "missing_day"
    out.loc[out["sample_type_hrsm"].eq("unknown"), "phase2_mapping_status"] = "unknown_sample_type"

    # Primary HRSM trajectory: swabs only, one ordered within-host trajectory.
    primary = out[out["sample_type_hrsm"].eq("swab_primary")].copy()
    primary = primary.sort_values(["sample_day", "run_accession"]).reset_index(drop=True)
    primary["timepoint_order"] = range(len(primary))
    primary["is_primary_hrsm_trajectory"] = True

    controls = out[out["sample_type_hrsm"].eq("isolate_control")].copy()
    controls = controls.sort_values(["sample_day", "run_accession"]).reset_index(drop=True)
    controls["is_primary_hrsm_trajectory"] = False

    out = out.sort_values(["sample_type_hrsm", "sample_day", "run_accession"]).reset_index(drop=True)

    OUT_MAP.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_MAP, index=False)

    OUT_PRIMARY.parent.mkdir(parents=True, exist_ok=True)
    primary.to_csv(OUT_PRIMARY, index=False)
    controls.to_csv(OUT_CONTROLS, index=False)

    summary = pd.DataFrame([{
        "case_id": "WEIGANG_2021_ERP132087",
        "n_total_runs": len(out),
        "n_primary_swab_runs": len(primary),
        "n_isolate_controls": len(controls),
        "n_unknown_sample_type": int(out["sample_type_hrsm"].eq("unknown").sum()),
        "n_missing_day": int(out["sample_day"].isna().sum()),
        "primary_min_day": int(primary["sample_day"].min()) if len(primary) else None,
        "primary_max_day": int(primary["sample_day"].max()) if len(primary) else None,
        "primary_days": "|".join(map(str, primary["sample_day"].astype(int).tolist())) if len(primary) else "",
        "host_subject_ids": "|".join(sorted(out["patient_or_infection_id"].astype(str).unique())),
        "mapping_status": "hrsm_ready_primary_swab_trajectory" if len(primary) >= 3 and out["sample_day"].notna().all() else "not_ready",
        "interpretation": "Use swab samples as the primary within-host HRSM trajectory; retain isolate samples as controls or validation material.",
    }])

    OUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_SUMMARY, index=False)

    print({
        "status": "wrote",
        "map": str(OUT_MAP),
        "primary": str(OUT_PRIMARY),
        "controls": str(OUT_CONTROLS),
        "summary": str(OUT_SUMMARY),
    })

    print("\nSUMMARY")
    print(summary.to_string(index=False))

    cols = [
        "sample_title",
        "sample_type_hrsm",
        "sample_day",
        "timepoint_order",
        "patient_or_infection_id",
        "collection_date_from_attributes",
        "run_accession",
        "sample_accession",
        "library_strategy",
        "read_count",
        "base_count",
    ]
    cols = [c for c in cols if c in out.columns]

    print("\nFULL MAP")
    print(out[cols].to_string(index=False))

    print("\nPRIMARY SWAB TRAJECTORY")
    print(primary[cols].to_string(index=False))

    print("\nISOLATE CONTROLS")
    print(controls[cols].to_string(index=False))

if __name__ == "__main__":
    main()
