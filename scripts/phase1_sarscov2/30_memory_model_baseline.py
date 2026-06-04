from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from viral_hrsm.models import compare_markovian_vs_memory

INPUT = ROOT / "results" / "phase1_sarscov2" / "sarscov2_hrsm_state_table.csv"
OUT = ROOT / "results" / "phase1_sarscov2" / "memory_model_comparison.csv"

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing input HRSM state table: {INPUT}")

    df = pd.read_csv(INPUT)
    if "outcome_persistent" not in df.columns:
        raise ValueError("Expected binary outcome column: outcome_persistent")

    comparison = compare_markovian_vs_memory(df, outcome_col="outcome_persistent")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(OUT, index=False)
    print({"status": "wrote", "path": str(OUT)})

if __name__ == "__main__":
    main()
