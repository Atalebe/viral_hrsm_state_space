from pathlib import Path
import urllib.parse
import urllib.request
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

ACCESSION = "PRJEB77414"
OUT_RAW = ROOT / "metadata" / "schmidt_prjeb77414_ena_read_run.tsv"
OUT_SUMMARY = ROOT / "metadata" / "schmidt_prjeb77414_ena_audit_summary.csv"

FIELDS = [
    "study_accession",
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
]

def fetch_ena_filereport(accession: str) -> pd.DataFrame:
    params = {
        "accession": accession,
        "result": "read_run",
        "fields": ",".join(FIELDS),
        "format": "tsv",
        "download": "true",
        "limit": "0",
    }
    url = "https://www.ebi.ac.uk/ena/portal/api/filereport?" + urllib.parse.urlencode(params)
    print({"status": "fetching", "url": url})

    with urllib.request.urlopen(url, timeout=60) as response:
        text = response.read().decode("utf-8")

    if not text.strip():
        raise RuntimeError(f"ENA returned an empty response for {accession}")

    OUT_RAW.parent.mkdir(parents=True, exist_ok=True)
    OUT_RAW.write_text(text, encoding="utf-8")

    df = pd.read_csv(OUT_RAW, sep="\t")
    return df

def main():
    df = fetch_ena_filereport(ACCESSION)

    summary = {
        "accession": ACCESSION,
        "n_rows": len(df),
        "n_unique_runs": df["run_accession"].nunique() if "run_accession" in df else 0,
        "n_unique_samples": df["sample_accession"].nunique() if "sample_accession" in df else 0,
        "has_fastq_ftp": bool(df.get("fastq_ftp", pd.Series(dtype=str)).fillna("").astype(str).str.len().gt(0).any()),
        "has_submitted_ftp": bool(df.get("submitted_ftp", pd.Series(dtype=str)).fillna("").astype(str).str.len().gt(0).any()),
        "has_bam_ftp": bool(df.get("bam_ftp", pd.Series(dtype=str)).fillna("").astype(str).str.len().gt(0).any()),
    }

    pd.DataFrame([summary]).to_csv(OUT_SUMMARY, index=False)

    print({"status": "wrote", "raw": str(OUT_RAW), "summary": str(OUT_SUMMARY)})
    print(pd.DataFrame([summary]).to_string(index=False))

    if len(df) > 0:
        preview_cols = [c for c in ["run_accession", "sample_accession", "scientific_name", "read_count", "fastq_ftp"] if c in df.columns]
        print(df[preview_cols].head(20).to_string(index=False))

if __name__ == "__main__":
    main()
