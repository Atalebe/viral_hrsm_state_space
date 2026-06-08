from pathlib import Path
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]

CONFIG = ROOT / "configs" / "phase2_weigang_raw_feature_protocol.yaml"
DOWNLOAD_PLAN = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_primary_swab_download_plan.csv"
OUT = ROOT / "metadata" / "phase2_sarscov2_multicase" / "weigang_raw_feature_protocol_audit.csv"

def main():
    if not CONFIG.exists():
        raise FileNotFoundError(f"Missing config: {CONFIG}")
    if not DOWNLOAD_PLAN.exists():
        raise FileNotFoundError(f"Missing download plan: {DOWNLOAD_PLAN}")

    cfg = yaml.safe_load(CONFIG.read_text())
    plan = pd.read_csv(DOWNLOAD_PLAN)

    expected_days = list(cfg["primary_trajectory"]["days"])
    observed_days = sorted(plan["sample_day"].dropna().astype(int).unique().tolist())

    n_files = len(plan)
    n_runs = plan["run_accession"].nunique()
    n_timepoints = plan["sample_day"].nunique()

    protocol_ok = (
        observed_days == expected_days
        and n_timepoints == cfg["primary_trajectory"]["n_timepoints"]
        and n_files == n_runs * 2
        and cfg["input"]["raw_download_ready"] is False
    )

    audit = pd.DataFrame([{
        "case_id": cfg["case_id"],
        "protocol_status": cfg["status"],
        "expected_days": "|".join(map(str, expected_days)),
        "observed_days": "|".join(map(str, observed_days)),
        "n_timepoints": n_timepoints,
        "n_runs": n_runs,
        "n_planned_files": n_files,
        "raw_download_ready": cfg["input"]["raw_download_ready"],
        "min_depth": cfg["variant_filters"]["min_depth"],
        "min_alt_count": cfg["variant_filters"]["min_alt_count"],
        "min_alt_frequency": cfg["variant_filters"]["min_alt_frequency"],
        "consensus_frequency": cfg["variant_filters"]["consensus_frequency"],
        "protocol_ok": protocol_ok,
        "next_required": "only after this audit passes, create raw download script with explicit user-run command",
    }])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(OUT, index=False)

    print({
        "status": "wrote",
        "audit": str(OUT),
        "protocol_ok": bool(protocol_ok),
    })
    print(audit.to_string(index=False))

    if not protocol_ok:
        raise SystemExit("Protocol audit failed. Do not download raw files.")

if __name__ == "__main__":
    main()
