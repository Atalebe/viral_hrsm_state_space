from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

PRIMARY = ROOT / "data" / "processed" / "phase2_sarscov2_multicase" / "weigang_primary_swab_longitudinal_map.csv"

OUT_PLAN = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_primary_swab_download_plan.csv"
OUT_SUMMARY = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_primary_swab_download_plan_summary.csv"

def split_links(x):
    if pd.isna(x) or str(x).strip() == "":
        return []
    return [v.strip() for v in str(x).split(";") if v.strip()]

def main():
    if not PRIMARY.exists():
        raise FileNotFoundError(
            f"Missing primary Weigang swab map: {PRIMARY}. "
            "Run 15_build_weigang_longitudinal_map.py first."
        )

    df = pd.read_csv(PRIMARY)
    df = df.sort_values(["sample_day", "timepoint_order"]).reset_index(drop=True)

    rows = []

    for _, row in df.iterrows():
        submitted_links = split_links(row.get("submitted_ftp", ""))
        fastq_links = split_links(row.get("fastq_ftp", ""))

        preferred_links = submitted_links if submitted_links else fastq_links
        preferred_source = "submitted_ftp" if submitted_links else "fastq_ftp"

        for i, link in enumerate(preferred_links, start=1):
            rows.append({
                "case_id": "WEIGANG_2021_ERP132087",
                "sample_day": int(row["sample_day"]),
                "timepoint_order": int(row["timepoint_order"]),
                "sample_title": row["sample_title"],
                "run_accession": row["run_accession"],
                "sample_accession": row["sample_accession"],
                "library_strategy": row.get("library_strategy", ""),
                "read_count": row.get("read_count", ""),
                "base_count": row.get("base_count", ""),
                "preferred_source": preferred_source,
                "file_index": i,
                "ftp_url": link,
                "download_url": "https://" + link if not str(link).startswith("http") else link,
                "planned_local_dir": f"data/raw/phase2_sarscov2_multicase/weigang_primary_swabs/day_{int(row['sample_day']):03d}_{row['run_accession']}",
                "download_status": "planned_not_downloaded",
                "notes": "Primary swab only. Download only after raw-feature plan is frozen.",
            })

    plan = pd.DataFrame(rows)
    OUT_PLAN.parent.mkdir(parents=True, exist_ok=True)
    plan.to_csv(OUT_PLAN, index=False)

    summary = pd.DataFrame([{
        "case_id": "WEIGANG_2021_ERP132087",
        "n_primary_swab_timepoints": df["sample_day"].nunique(),
        "n_runs": df["run_accession"].nunique(),
        "n_planned_files": len(plan),
        "preferred_sources": "|".join(sorted(plan["preferred_source"].unique())) if len(plan) else "",
        "total_read_count": float(pd.to_numeric(df["read_count"], errors="coerce").sum()),
        "total_base_count": float(pd.to_numeric(df["base_count"], errors="coerce").sum()),
        "days": "|".join(map(str, df["sample_day"].astype(int).tolist())),
        "download_ready": False,
        "next_required": "freeze raw-feature extraction protocol before downloading FASTQ/BAM files",
    }])
    OUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_SUMMARY, index=False)

    print({
        "status": "wrote",
        "plan": str(OUT_PLAN),
        "summary": str(OUT_SUMMARY),
        "n_files": len(plan),
    })

    print("\nSUMMARY")
    print(summary.to_string(index=False))

    print("\nDOWNLOAD PLAN")
    print(plan.to_string(index=False))

if __name__ == "__main__":
    main()
