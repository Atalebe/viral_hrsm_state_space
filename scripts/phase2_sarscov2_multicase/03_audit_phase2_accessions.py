from pathlib import Path
import urllib.parse
import urllib.request
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

OUT_DIR = ROOT / "metadata" / "phase2_sarscov2_multicase"
OUT_AUDIT = OUT_DIR / "phase2_accession_audit.csv"

ACCESSION_QUERIES = [
    {
        "case_id": "BOYLE_2025_PRJNA1295507",
        "dataset_name": "Boyle et al. persistent SARS-CoV-2 intra-host evolution",
        "accession": "PRJNA1295507",
        "accession_type": "bioproject",
        "query_backend": "ena_portal_read_run",
        "priority": 1,
        "notes": "First Phase II data-contact target. Paper reports raw reads under this NCBI BioProject.",
    },
]

FIELDS = [
    "study_accession",
    "secondary_study_accession",
    "sample_accession",
    "experiment_accession",
    "run_accession",
    "tax_id",
    "scientific_name",
    "instrument_platform",
    "instrument_model",
    "library_layout",
    "library_strategy",
    "read_count",
    "base_count",
    "fastq_ftp",
    "submitted_ftp",
    "bam_ftp",
    "sample_title",
    "experiment_title",
]

def fetch_ena_read_run(accession):
    params = {
        "accession": accession,
        "result": "read_run",
        "fields": ",".join(FIELDS),
        "format": "tsv",
        "download": "true",
        "limit": "0",
    }
    url = "https://www.ebi.ac.uk/ena/portal/api/filereport?" + urllib.parse.urlencode(params)
    print({"status": "fetching", "accession": accession, "url": url})

    with urllib.request.urlopen(url, timeout=90) as response:
        text = response.read().decode("utf-8")

    return text

def summarize_table(df, query):
    def has_nonempty(col):
        if col not in df.columns:
            return False
        return df[col].fillna("").astype(str).str.len().gt(0).any()

    summary = {
        "case_id": query["case_id"],
        "dataset_name": query["dataset_name"],
        "accession": query["accession"],
        "accession_type": query["accession_type"],
        "query_backend": query["query_backend"],
        "priority": query["priority"],
        "n_rows": len(df),
        "n_unique_studies": df["study_accession"].nunique() if "study_accession" in df else 0,
        "n_unique_samples": df["sample_accession"].nunique() if "sample_accession" in df else 0,
        "n_unique_experiments": df["experiment_accession"].nunique() if "experiment_accession" in df else 0,
        "n_unique_runs": df["run_accession"].nunique() if "run_accession" in df else 0,
        "has_fastq_ftp": has_nonempty("fastq_ftp"),
        "has_submitted_ftp": has_nonempty("submitted_ftp"),
        "has_bam_ftp": has_nonempty("bam_ftp"),
        "admissibility_after_accession": "pending_content_audit",
        "notes": query["notes"],
    }

    if len(df) == 0:
        summary["admissibility_after_accession"] = "no_run_rows_returned"
    elif summary["has_fastq_ftp"] or summary["has_submitted_ftp"] or summary["has_bam_ftp"]:
        summary["admissibility_after_accession"] = "run_level_files_available"
    else:
        summary["admissibility_after_accession"] = "run_rows_without_file_links"

    return summary

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    summaries = []

    for query in ACCESSION_QUERIES:
        accession = query["accession"]
        raw_path = OUT_DIR / f"{query['case_id'].lower()}_{accession.lower()}_ena_read_run.tsv"

        try:
            text = fetch_ena_read_run(accession)
            raw_path.write_text(text, encoding="utf-8")

            if not text.strip():
                df = pd.DataFrame()
            else:
                df = pd.read_csv(raw_path, sep="\t")

            summary = summarize_table(df, query)
            summary["raw_table"] = str(raw_path.relative_to(ROOT))

        except Exception as exc:
            summary = {
                "case_id": query["case_id"],
                "dataset_name": query["dataset_name"],
                "accession": accession,
                "accession_type": query["accession_type"],
                "query_backend": query["query_backend"],
                "priority": query["priority"],
                "n_rows": 0,
                "n_unique_studies": 0,
                "n_unique_samples": 0,
                "n_unique_experiments": 0,
                "n_unique_runs": 0,
                "has_fastq_ftp": False,
                "has_submitted_ftp": False,
                "has_bam_ftp": False,
                "admissibility_after_accession": "query_failed",
                "notes": f"{query['notes']} Query failed: {exc}",
                "raw_table": "",
            }

        summaries.append(summary)

    out = pd.DataFrame(summaries)
    out.to_csv(OUT_AUDIT, index=False)

    print({
        "status": "wrote",
        "audit": str(OUT_AUDIT),
        "n_queries": len(ACCESSION_QUERIES),
    })

    print(out.to_string(index=False))

    for _, row in out.iterrows():
        raw_table = row.get("raw_table", "")
        if raw_table and (ROOT / raw_table).exists():
            df = pd.read_csv(ROOT / raw_table, sep="\t")
            cols = [
                c for c in [
                    "run_accession",
                    "sample_accession",
                    "study_accession",
                    "scientific_name",
                    "read_count",
                    "base_count",
                    "fastq_ftp",
                    "sample_title",
                ]
                if c in df.columns
            ]
            print(f"\nPreview for {row['case_id']}:")
            if len(df):
                print(df[cols].head(30).to_string(index=False))
            else:
                print("No rows returned.")

if __name__ == "__main__":
    main()
