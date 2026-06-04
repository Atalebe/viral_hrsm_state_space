from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "phase1_sarscov2" / "sarscov2_case_table_template.csv"

COLUMNS = [
    "case_id", "sample_id", "timepoint", "sample_date", "days_from_first_sample",
    "lineage", "consensus_fasta_path", "variant_table_path",
    "ct_value", "viral_load", "culture_status", "treatment_exposure",
    "host_context", "clinical_endpoint", "notes"
]

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        print({"status": "exists", "path": str(OUT)})
        return
    pd.DataFrame(columns=COLUMNS).to_csv(OUT, index=False)
    print({"status": "created", "path": str(OUT)})

if __name__ == "__main__":
    main()
