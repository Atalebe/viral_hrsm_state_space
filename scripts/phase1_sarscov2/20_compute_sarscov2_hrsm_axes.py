from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from viral_hrsm.axes import compute_axis_table

INPUT = ROOT / "data" / "processed" / "sarscov2_proxy_features.csv"
OUT = ROOT / "results" / "phase1_sarscov2" / "sarscov2_hrsm_state_table.csv"

def main():
    if not INPUT.exists():
        template = pd.DataFrame({
            "case_id": ["example_case"],
            "timepoint": [0],
            "diversity": [0.0],
            "sequence_entropy": [0.0],
            "near_neutral_proxy": [0.0],
            "ct_decline_inverse": [0.0],
            "post_nadir_growth": [0.0],
            "culture_positive": [0.0],
            "haplotype_concentration": [0.0],
            "lineage_backbone": [0.0],
            "fragmentation_inverse": [0.0],
            "lagged_similarity": [0.0],
            "retained_escape": [0.0],
            "compensatory_structure": [0.0],
            "outcome_persistent": [1],
        })
        INPUT.parent.mkdir(parents=True, exist_ok=True)
        template.to_csv(INPUT, index=False)
        print({"status": "created_template", "path": str(INPUT)})
        return

    df = pd.read_csv(INPUT)
    out = compute_axis_table(df)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print({"status": "wrote", "path": str(OUT), "n_rows": len(out)})

if __name__ == "__main__":
    main()
