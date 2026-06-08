from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_erp132087_ena_read_run.tsv"

OUT_MANIFEST = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_run_manifest.csv"
OUT_SUMMARY = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_run_manifest_summary.csv"
OUT_SAMPLE_TEMPLATE = ROOT / "data" / "interim" / "phase2_sarscov2_multicase" / "weigang_sample_day_mapping_template.csv"

def split_links(x):
    if pd.isna(x) or str(x).strip() == "":
        return []
    return [v for v in str(x).split(";") if v.strip()]

def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing Weigang ENA run table: {INPUT}. "
            "Run scripts/phase2_sarscov2_multicase/12_audit_weigang_accessions.py first."
        )

    df = pd.read_csv(INPUT, sep="\t")

    required = [
        "run_accession",
        "sample_accession",
        "study_accession",
        "scientific_name",
        "read_count",
        "base_count",
        "fastq_ftp",
        "submitted_ftp",
        "sample_title",
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing expected ENA columns: {missing}")

    out = pd.DataFrame(index=df.index)
    out["case_id"] = "WEIGANG_2021_ERP132087"
    out["run_accession"] = df["run_accession"]
    out["sample_accession"] = df["sample_accession"]
    out["study_accession"] = df["study_accession"]
    out["sample_title"] = df["sample_title"]
    out["scientific_name"] = df["scientific_name"]
    out["instrument_platform"] = df.get("instrument_platform", "")
    out["instrument_model"] = df.get("instrument_model", "")
    out["library_layout"] = df.get("library_layout", "")
    out["library_strategy"] = df.get("library_strategy", "")

    out["read_count"] = pd.to_numeric(df["read_count"], errors="coerce")
    out["base_count"] = pd.to_numeric(df["base_count"], errors="coerce")

    out["fastq_ftp"] = df["fastq_ftp"].fillna("")
    out["submitted_ftp"] = df["submitted_ftp"].fillna("")
    out["bam_ftp"] = df.get("bam_ftp", "").fillna("") if "bam_ftp" in df.columns else ""

    out["n_fastq_links"] = out["fastq_ftp"].apply(lambda x: len(split_links(x)))
    out["n_submitted_links"] = out["submitted_ftp"].apply(lambda x: len(split_links(x)))
    out["n_bam_links"] = out["bam_ftp"].apply(lambda x: len(split_links(x)))

    out["has_fastq"] = out["n_fastq_links"].gt(0)
    out["has_submitted"] = out["n_submitted_links"].gt(0)
    out["has_bam"] = out["n_bam_links"].gt(0)

    out["metadata_usable"] = (
        out["run_accession"].notna()
        & out["sample_accession"].notna()
        & out["sample_title"].notna()
        & (out["has_fastq"] | out["has_submitted"] | out["has_bam"])
    )

    out["needs_day_mapping"] = True
    out["needs_case_grouping"] = True
    out["download_status"] = "not_downloaded"

    OUT_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_MANIFEST, index=False)

    summary = pd.DataFrame([{
        "case_id": "WEIGANG_2021_ERP132087",
        "n_runs": len(out),
        "n_samples": out["sample_accession"].nunique(),
        "n_sample_titles": out["sample_title"].nunique(),
        "n_runs_with_fastq": int(out["has_fastq"].sum()),
        "n_runs_with_submitted": int(out["has_submitted"].sum()),
        "n_runs_with_bam": int(out["has_bam"].sum()),
        "total_read_count": float(out["read_count"].sum(skipna=True)),
        "total_base_count": float(out["base_count"].sum(skipna=True)),
        "metadata_usable_runs": int(out["metadata_usable"].sum()),
        "next_required": "recover sample-day mapping and confirm single-patient longitudinal ordering before HRSM extraction",
    }])

    OUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_SUMMARY, index=False)

    sample_template = out[[
        "case_id",
        "sample_title",
        "sample_accession",
        "run_accession",
        "read_count",
        "base_count",
    ]].copy()

    sample_template["patient_or_infection_id"] = ""
    sample_template["sample_day"] = ""
    sample_template["sample_date"] = ""
    sample_template["timepoint_order"] = ""
    sample_template["lineage_or_variant"] = ""
    sample_template["ct_value"] = ""
    sample_template["viral_load"] = ""
    sample_template["treatment_context"] = ""
    sample_template["host_context"] = ""
    sample_template["endpoint"] = ""
    sample_template["notes"] = ""

    OUT_SAMPLE_TEMPLATE.parent.mkdir(parents=True, exist_ok=True)
    sample_template.to_csv(OUT_SAMPLE_TEMPLATE, index=False)

    print({
        "status": "wrote",
        "manifest": str(OUT_MANIFEST),
        "summary": str(OUT_SUMMARY),
        "sample_day_template": str(OUT_SAMPLE_TEMPLATE),
        "n_runs": len(out),
    })

    print(summary.to_string(index=False))
    print(out[[
        "run_accession",
        "sample_accession",
        "sample_title",
        "read_count",
        "base_count",
        "n_fastq_links",
        "n_submitted_links",
        "metadata_usable",
    ]].to_string(index=False))

if __name__ == "__main__":
    main()
