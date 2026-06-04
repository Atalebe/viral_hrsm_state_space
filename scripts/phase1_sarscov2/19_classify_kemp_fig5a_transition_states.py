from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_hrsm_state_table.csv"
OUT = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_transition_states.csv"
OUT_SUMMARY = ROOT / "metadata" / "kemp_fig5a_transition_state_summary.csv"

def classify(row, prior_high_escape_seen):
    escape = row.get("escape_pair_mean", np.nan)
    h = row.get("H_v", 0.0)
    s = row.get("S_v", 0.0)
    m = row.get("M_v", 0.0)

    if escape >= 0.75 and s >= 1.0 and m >= 1.0:
        if prior_high_escape_seen:
            return "high_memory_escape_return"
        return "coherent_escape_surge"

    if escape >= 0.50 and m >= 0.5:
        return "retained_escape_state"

    if h >= 0.5 and escape < 0.20 and m < 0.0:
        return "alternate_diversity_state"

    if escape < 0.05 and h < 0.0:
        return "low_escape_baseline"

    return "intermediate_transition"

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing input: {INPUT}")

    df = pd.read_csv(INPUT)
    df = df.sort_values(["day_from_first_positive_proxy", "within_day_order", "timepoint"]).reset_index(drop=True)

    df["escape_pair_mean"] = df[["D796H", "del69/70"]].mean(axis=1)
    df["escape_pair_delta"] = df["escape_pair_mean"].diff()
    df["memory_delta"] = df["M_v"].diff()

    labels = []
    prior_high_escape_seen = False

    for _, row in df.iterrows():
        label = classify(row, prior_high_escape_seen)
        labels.append(label)

        if row["escape_pair_mean"] >= 0.75:
            prior_high_escape_seen = True

    df["transition_state"] = labels

    df["is_escape_return_jump"] = (
        (df["escape_pair_delta"] > 0.40)
        & (df["M_v"] > 0.5)
        & (df["S_v"] > 0.5)
        & df["transition_state"].isin(["retained_escape_state", "high_memory_escape_return"])
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    summary = (
        df.groupby("transition_state")
        .agg(
            n=("transition_state", "size"),
            first_timepoint=("timepoint_label", "first"),
            last_timepoint=("timepoint_label", "last"),
            first_day=("day_from_first_positive_proxy", "first"),
            last_day=("day_from_first_positive_proxy", "last"),
            mean_escape=("escape_pair_mean", "mean"),
            mean_H=("H_v", "mean"),
            mean_R=("R_v", "mean"),
            mean_S=("S_v", "mean"),
            mean_M=("M_v", "mean"),
            mean_Phi=("Phi_v", "mean"),
        )
        .reset_index()
        .sort_values(["first_day", "mean_M"], ascending=[True, False])
    )

    OUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_SUMMARY, index=False)

    print({"status": "wrote", "states": str(OUT), "summary": str(OUT_SUMMARY), "n_rows": len(df)})
    print(df[[
        "timepoint", "timepoint_label", "day_from_first_positive_proxy",
        "D796H", "del69/70", "escape_pair_mean",
        "H_v", "S_v", "M_v", "Phi_v",
        "transition_state", "is_escape_return_jump"
    ]].to_string(index=False))
    print(summary.to_string(index=False))

if __name__ == "__main__":
    main()
