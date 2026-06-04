from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

SUMMARY = ROOT / "metadata" / "schmidt_prjeb77414_ena_audit_summary.csv"
AUDIT = ROOT / "metadata" / "sarscov2_accession_audit.csv"
OUT = ROOT / "metadata" / "sarscov2_accession_audit_updated.csv"

TARGET = "Schmidt et al. 521-day persistent infection"

def main():
    summary = pd.read_csv(SUMMARY)
    audit = pd.read_csv(AUDIT)

    n_rows = int(summary.loc[0, "n_rows"])
    has_fastq = bool(summary.loc[0, "has_fastq_ftp"])

    mask = audit["dataset_name"].eq(TARGET)

    if n_rows == 0 or not has_fastq:
        audit.loc[mask, "data_strength"] = "biologically_high_but_no_run_level_ena_files"
        audit.loc[mask, "recommended_role"] = "long_memory_context_until_files_recovered"
        audit.loc[mask, "audit_note"] = (
            "ENA Portal read_run query for PRJEB77414 returned zero rows and no FASTQ links. "
            "Keep as long-memory biological context unless supplementary files or another accession path is recovered."
        )
    else:
        audit.loc[mask, "data_strength"] = "high_with_run_level_files"
        audit.loc[mask, "recommended_role"] = "long_memory_case_with_downloadable_runs"
        audit.loc[mask, "audit_note"] = (
            f"ENA query returned {n_rows} rows with FASTQ availability. Candidate can proceed to sample-level extraction."
        )

    audit.to_csv(OUT, index=False)
    print({"status": "wrote", "path": str(OUT), "n_rows": len(audit)})
    print(audit[["dataset_name", "data_strength", "recommended_role", "audit_note"]].to_string(index=False))

if __name__ == "__main__":
    main()
