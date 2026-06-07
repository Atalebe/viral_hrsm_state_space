from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "metadata" / "phase2_sarscov2_multicase" / "boyle_run_manifest_with_biosample_metadata.csv"

OUT_TIMELINE = ROOT / "metadata" / "phase2_sarscov2_multicase" / "boyle_temporal_metadata_timeline.csv"
OUT_SUMMARY = ROOT / "metadata" / "phase2_sarscov2_multicase" / "boyle_temporal_grouping_audit_summary.csv"
OUT_DATE_COUNTS = ROOT / "metadata" / "phase2_sarscov2_multicase" / "boyle_collection_date_counts.csv"
OUT_CANDIDATE_SERIES = ROOT / "metadata" / "phase2_sarscov2_multicase" / "boyle_candidate_date_series.csv"

def extract_gisaid(attr):
    if pd.isna(attr):
        return ""
    m = re.search(r"gisaid_accession=([^|]+)", str(attr))
    return m.group(1).strip() if m else ""

def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing joined BioSample manifest: {INPUT}. "
            "Run 04_build_boyle_run_manifest.py and 08_expand_boyle_biosample_metadata.py first."
        )

    df = pd.read_csv(INPUT)

    required = ["sample_title", "sample_accession", "run_accession", "collection_date"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    df["collection_date_parsed"] = pd.to_datetime(df["collection_date"], errors="coerce")
    df["gisaid_accession"] = df["all_attributes"].apply(extract_gisaid) if "all_attributes" in df.columns else ""

    # BioSample does not expose true patient ID in the fields seen so far.
    possible_patient_cols = [
        c for c in df.columns
        if any(k in c.lower() for k in ["patient", "subject", "participant", "infection"])
    ]

    timeline_cols = [
        "case_id",
        "sample_title",
        "sample_accession",
        "run_accession",
        "collection_date",
        "collection_date_parsed",
        "gisaid_accession",
        "host",
        "host_disease",
        "isolate",
        "isolation_source",
        "geo_loc_name",
        "read_count",
        "base_count",
    ]
    timeline_cols = [c for c in timeline_cols if c in df.columns]

    timeline = df[timeline_cols].sort_values(
        ["collection_date_parsed", "sample_title", "run_accession"],
        na_position="last"
    ).reset_index(drop=True)

    if not timeline.empty:
        first_date = timeline["collection_date_parsed"].dropna().min()
        timeline["days_from_first_collection"] = (
            timeline["collection_date_parsed"] - first_date
        ).dt.days
        timeline["global_timepoint_order"] = range(len(timeline))
    else:
        timeline["days_from_first_collection"] = []
        timeline["global_timepoint_order"] = []

    OUT_TIMELINE.parent.mkdir(parents=True, exist_ok=True)
    timeline.to_csv(OUT_TIMELINE, index=False)

    date_counts = (
        timeline.groupby("collection_date", dropna=False)
        .agg(
            n_samples=("sample_title", "count"),
            sample_titles=("sample_title", lambda x: "|".join(map(str, x))),
            run_accessions=("run_accession", lambda x: "|".join(map(str, x))),
        )
        .reset_index()
        .sort_values("collection_date")
    )
    date_counts.to_csv(OUT_DATE_COUNTS, index=False)

    # Candidate date series are date clusters only, not patient trajectories.
    candidate_series = date_counts[date_counts["n_samples"].ge(2)].copy()
    candidate_series["interpretation"] = (
        "same collection date cluster only; not patient-level longitudinal grouping"
    )
    candidate_series.to_csv(OUT_CANDIDATE_SERIES, index=False)

    summary = pd.DataFrame([{
        "case_id": "BOYLE_2025_PRJNA1295507",
        "n_rows": len(df),
        "n_unique_samples": df["sample_accession"].nunique(),
        "n_unique_runs": df["run_accession"].nunique(),
        "n_collection_dates": timeline["collection_date"].nunique(),
        "n_gisaid_accessions": timeline["gisaid_accession"].replace("", pd.NA).dropna().nunique(),
        "n_possible_patient_columns": len(possible_patient_cols),
        "possible_patient_columns": "|".join(possible_patient_cols),
        "has_patient_or_infection_grouping": False,
        "has_collection_date_mapping": timeline["collection_date_parsed"].notna().all(),
        "phase2_status": "date_mapped_but_not_patient_grouped",
        "next_required": "recover Supplemental Table S1 or another source with patient/infection IDs and timepoint grouping",
    }])
    OUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_SUMMARY, index=False)

    print({
        "status": "wrote",
        "timeline": str(OUT_TIMELINE),
        "summary": str(OUT_SUMMARY),
        "date_counts": str(OUT_DATE_COUNTS),
        "candidate_series": str(OUT_CANDIDATE_SERIES),
        "n_rows": len(df),
    })

    print("\nSUMMARY")
    print(summary.to_string(index=False))

    print("\nTIMELINE PREVIEW")
    print(timeline.head(80).to_string(index=False))

    print("\nDATE CLUSTERS")
    print(date_counts[date_counts["n_samples"].ge(2)].to_string(index=False))

if __name__ == "__main__":
    main()
