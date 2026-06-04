from pathlib import Path
import pandas as pd
import sys
import math

ROOT = Path(__file__).resolve().parents[1]

audit_path = ROOT / "metadata" / "phase1_kemp_fig5a_summary_report_audit.csv"
if not audit_path.exists():
    raise FileNotFoundError(f"Missing audit file: {audit_path}")

audit = pd.read_csv(audit_path).iloc[0].to_dict()

expected = {
    "n_hrsm_rows": 20,
    "n_transition_rows": 20,
    "n_daily_rows": 16,
    "n_figures_listed": 9,
    "n_missing_figures": 0,
}

errors = []
for k, v in expected.items():
    observed = int(audit[k])
    if observed != v:
        errors.append(f"{k}: expected {v}, observed {observed}")

expected_states = "retained_escape_state|high_memory_escape_return"
if str(audit["stationary_top_states"]) != expected_states:
    errors.append(
        f"stationary_top_states expected {expected_states}, observed {audit['stationary_top_states']}"
    )

try:
    probs = [float(x) for x in str(audit["stationary_top_probs"]).split("|")]
except Exception:
    probs = []
    errors.append(f"Could not parse stationary_top_probs: {audit['stationary_top_probs']}")

if len(probs) != 2:
    errors.append(f"stationary_top_probs expected two values, observed {audit['stationary_top_probs']}")
else:
    for observed, expected_prob in zip(probs, [0.5, 0.5]):
        if not math.isclose(observed, expected_prob, rel_tol=1e-9, abs_tol=1e-9):
            errors.append(
                f"stationary probability expected {expected_prob}, observed {observed}"
            )

if errors:
    print("[FAIL] Phase I locked-output check failed:")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print("[OK] Phase I locked-output check passed.")
print(audit)
