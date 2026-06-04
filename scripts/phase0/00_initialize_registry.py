from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "metadata" / "dataset_candidate_registry.csv"

COLUMNS = [
    "virus", "dataset_name", "source_reference", "source_url",
    "longitudinal_structure", "raw_reads_available", "consensus_available",
    "viral_load_or_ct_available", "treatment_context_available",
    "host_context_available", "outcome_label_available", "phase",
    "admissibility_status", "notes"
]

def main():
    if REGISTRY.exists():
        print({"status": "exists", "path": str(REGISTRY)})
        return
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=COLUMNS).to_csv(REGISTRY, index=False)
    print({"status": "created", "path": str(REGISTRY)})

if __name__ == "__main__":
    main()
