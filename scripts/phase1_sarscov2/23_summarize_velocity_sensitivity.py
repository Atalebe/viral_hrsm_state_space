from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_phase_velocity.csv"
OUT_ALL = ROOT / "metadata" / "kemp_fig5a_velocity_summary_all_steps.csv"
OUT_CALENDAR = ROOT / "metadata" / "kemp_fig5a_velocity_summary_calendar_only.csv"
OUT_FLAGGED = ROOT / "metadata" / "kemp_fig5a_velocity_same_day_flags.csv"

def summarize(df):
    return (
        df.groupby("transition_state")
        .agg(
            n=("transition_state", "size"),
            first_day=("day_from_first_positive_proxy", "first"),
            last_day=("day_from_first_positive_proxy", "last"),
            mean_velocity=("velocity_norm_total", "mean"),
            median_velocity=("velocity_norm_total", "median"),
            max_velocity=("velocity_norm_total", "max"),
            mean_acceleration=("acceleration_proxy", "mean"),
            median_acceleration=("acceleration_proxy", "median"),
            max_acceleration=("acceleration_proxy", "max"),
            same_day_steps=("same_day_step", "sum"),
        )
        .reset_index()
        .sort_values("first_day")
    )

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing velocity table: {INPUT}")

    df = pd.read_csv(INPUT)
    df = df.sort_values(["day_from_first_positive_proxy", "within_day_order", "timepoint"]).reset_index(drop=True)

    all_summary = summarize(df)
    calendar_only = summarize(df[~df["same_day_step"].fillna(False)].copy())

    flagged = df[df["same_day_step"].fillna(False)].copy()
    flagged = flagged[[
        "timepoint_label",
        "day_from_first_positive_proxy",
        "within_day_order",
        "transition_state",
        "dt_raw",
        "dt_effective",
        "velocity_norm_total",
        "acceleration_proxy",
        "H_v",
        "R_v",
        "S_v",
        "M_v",
        "Phi_v",
    ]]

    OUT_ALL.parent.mkdir(parents=True, exist_ok=True)
    all_summary.to_csv(OUT_ALL, index=False)
    calendar_only.to_csv(OUT_CALENDAR, index=False)
    flagged.to_csv(OUT_FLAGGED, index=False)

    print({
        "status": "wrote",
        "all_steps": str(OUT_ALL),
        "calendar_only": str(OUT_CALENDAR),
        "same_day_flags": str(OUT_FLAGGED),
        "n_all": len(df),
        "n_calendar_only": len(df[~df["same_day_step"].fillna(False)]),
        "n_same_day": len(flagged),
    })

    print("\nALL STEPS")
    print(all_summary.to_string(index=False))

    print("\nCALENDAR-DAY ONLY")
    print(calendar_only.to_string(index=False))

    print("\nSAME-DAY FLAGS")
    print(flagged.to_string(index=False))

if __name__ == "__main__":
    main()
