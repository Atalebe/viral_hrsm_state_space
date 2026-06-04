from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_transition_states.csv"
OUT = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_phase_velocity.csv"
OUT_SUMMARY = ROOT / "metadata" / "kemp_fig5a_phase_velocity_summary.csv"

AXES = ["H_v", "R_v", "S_v", "M_v", "Phi_v"]

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing transition-state table: {INPUT}")

    df = pd.read_csv(INPUT)
    df = df.sort_values(["day_from_first_positive_proxy", "within_day_order", "timepoint"]).reset_index(drop=True)

    df["dt_raw"] = df["day_from_first_positive_proxy"].diff()
    df["same_day_step"] = df["dt_raw"].eq(0)

    # Calendar divisor only applies when a true positive day interval exists.
    df["dt_calendar"] = df["dt_raw"].where(df["dt_raw"] > 0, np.nan)

    # Step divisor treats every ordered transition as one state-space step.
    # This prevents same-day samples from exploding numerically.
    df["ds_step"] = 1.0
    df.loc[0, "ds_step"] = np.nan

    for axis in AXES:
        df[f"delta_{axis}"] = df[axis].diff()

        df[f"d_{axis}_dstep"] = df[f"delta_{axis}"] / df["ds_step"]
        df[f"d_{axis}_dcalendar"] = df[f"delta_{axis}"] / df["dt_calendar"]

    step_cols = [f"d_{axis}_dstep" for axis in AXES]
    calendar_cols = [f"d_{axis}_dcalendar" for axis in AXES]

    df["velocity_norm_step_HRSM"] = np.sqrt(
        (df[[f"d_{a}_dstep" for a in ["H_v", "R_v", "S_v", "M_v"]]] ** 2).sum(axis=1)
    )
    df["velocity_norm_step_total"] = np.sqrt((df[step_cols] ** 2).sum(axis=1))

    df["velocity_norm_calendar_HRSM"] = np.sqrt(
        (df[[f"d_{a}_dcalendar" for a in ["H_v", "R_v", "S_v", "M_v"]]] ** 2).sum(axis=1)
    )
    df["velocity_norm_calendar_total"] = np.sqrt((df[calendar_cols] ** 2).sum(axis=1))

    # Acceleration in step space. This is stable for same-day ordered transitions.
    df["acceleration_step_proxy"] = df["velocity_norm_step_total"].diff()

    # Calendar acceleration only for positive calendar-day intervals.
    df["acceleration_calendar_proxy"] = df["velocity_norm_calendar_total"].diff() / df["dt_calendar"]
    df["acceleration_calendar_proxy"] = df["acceleration_calendar_proxy"].replace([np.inf, -np.inf], np.nan)

    df["entering_retained_escape"] = (
        df["transition_state"].eq("retained_escape_state")
        & df["transition_state"].shift(1).ne("retained_escape_state")
    )

    df["entering_high_memory_return"] = (
        df["transition_state"].eq("high_memory_escape_return")
        & df["transition_state"].shift(1).ne("high_memory_escape_return")
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    summary = (
        df.groupby("transition_state")
        .agg(
            n=("transition_state", "size"),
            first_day=("day_from_first_positive_proxy", "first"),
            last_day=("day_from_first_positive_proxy", "last"),
            mean_step_velocity=("velocity_norm_step_total", "mean"),
            median_step_velocity=("velocity_norm_step_total", "median"),
            max_step_velocity=("velocity_norm_step_total", "max"),
            mean_calendar_velocity=("velocity_norm_calendar_total", "mean"),
            median_calendar_velocity=("velocity_norm_calendar_total", "median"),
            max_calendar_velocity=("velocity_norm_calendar_total", "max"),
            mean_step_acceleration=("acceleration_step_proxy", "mean"),
            max_step_acceleration=("acceleration_step_proxy", "max"),
            mean_calendar_acceleration=("acceleration_calendar_proxy", "mean"),
            max_calendar_acceleration=("acceleration_calendar_proxy", "max"),
            same_day_steps=("same_day_step", "sum"),
        )
        .reset_index()
        .sort_values("first_day")
    )

    OUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_SUMMARY, index=False)

    print({
        "status": "wrote",
        "velocity_table": str(OUT),
        "summary": str(OUT_SUMMARY),
        "n_rows": len(df),
        "same_day_steps": int(df["same_day_step"].sum()),
        "velocity_method": "step_normalized_plus_calendar_positive_dt",
    })

    cols = [
        "timepoint_label",
        "day_from_first_positive_proxy",
        "within_day_order",
        "dt_raw",
        "same_day_step",
        "transition_state",
        "velocity_norm_step_total",
        "velocity_norm_calendar_total",
        "acceleration_step_proxy",
        "acceleration_calendar_proxy",
        "entering_retained_escape",
        "entering_high_memory_return",
    ]
    print(df[cols].to_string(index=False))
    print(summary.to_string(index=False))

if __name__ == "__main__":
    main()
