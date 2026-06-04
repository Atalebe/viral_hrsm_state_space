from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_phase_velocity.csv"

OUT_DIR = ROOT / "figures" / "phase1_sarscov2"
OUT_SUMMARY = ROOT / "metadata" / "kemp_fig5a_potential_well_summary.csv"
OUT_TABLE = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_potential_wells.csv"

STATE_MARKERS = {
    "low_escape_baseline": "o",
    "intermediate_transition": "s",
    "coherent_escape_surge": "*",
    "alternate_diversity_state": "^",
    "retained_escape_state": "D",
    "high_memory_escape_return": "X",
}

def require_columns(df, cols):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(
            "Missing required columns in velocity table: "
            + ", ".join(missing)
            + ". Rerun scripts/phase1_sarscov2/21_compute_phase_velocity.py first."
        )

def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing corrected velocity table: {INPUT}. "
            "Run scripts/phase1_sarscov2/21_compute_phase_velocity.py first."
        )

    df = pd.read_csv(INPUT)
    df = df.sort_values(
        ["day_from_first_positive_proxy", "within_day_order", "timepoint"]
    ).reset_index(drop=True)

    require_columns(
        df,
        [
            "Phi_v",
            "transition_state",
            "D796H",
            "del69/70",
            "velocity_norm_step_total",
            "velocity_norm_calendar_total",
        ],
    )

    df["U_v"] = -df["Phi_v"]
    df["escape_pair_mean"] = df[["D796H", "del69/70"]].mean(axis=1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    p1 = OUT_DIR / "kemp_fig5a_potential_well_over_days.png"
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        df["day_from_first_positive_proxy"],
        df["U_v"],
        linewidth=1.4,
        alpha=0.55,
    )

    for state, sub in df.groupby("transition_state", sort=False):
        ax.scatter(
            sub["day_from_first_positive_proxy"],
            sub["U_v"],
            label=state,
            marker=STATE_MARKERS.get(state, "o"),
            s=85,
            alpha=0.9,
        )

    ax.axhline(0, linewidth=1, alpha=0.25)
    ax.set_xlabel("Days since first positive RT-PCR")
    ax.set_ylabel("Potential well proxy, U_v = -Phi_v")
    ax.set_title("Kemp Fig. 5a viral potential-well proxy over chronological days")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(p1, dpi=300)
    plt.close(fig)

    p2 = OUT_DIR / "kemp_fig5a_potential_vs_escape_pair.png"
    fig, ax = plt.subplots(figsize=(7, 5))

    for state, sub in df.groupby("transition_state", sort=False):
        ax.scatter(
            sub["escape_pair_mean"],
            sub["U_v"],
            label=state,
            marker=STATE_MARKERS.get(state, "o"),
            s=85,
            alpha=0.9,
        )

    ax.axhline(0, linewidth=1, alpha=0.25)
    ax.set_xlabel("Mean D796H and ΔH69/ΔV70 frequency proxy")
    ax.set_ylabel("Potential well proxy, U_v = -Phi_v")
    ax.set_title("Potential-well proxy versus escape-pair structure")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(p2, dpi=300)
    plt.close(fig)

    p3 = OUT_DIR / "kemp_fig5a_potential_vs_step_velocity.png"
    fig, ax = plt.subplots(figsize=(7, 5))

    for state, sub in df.groupby("transition_state", sort=False):
        ax.scatter(
            sub["velocity_norm_step_total"],
            sub["U_v"],
            label=state,
            marker=STATE_MARKERS.get(state, "o"),
            s=85,
            alpha=0.9,
        )

    ax.axhline(0, linewidth=1, alpha=0.25)
    ax.set_xlabel("Step-normalized velocity norm")
    ax.set_ylabel("Potential well proxy, U_v = -Phi_v")
    ax.set_title("Potential-well proxy versus corrected step velocity")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(p3, dpi=300)
    plt.close(fig)

    well_summary = (
        df.groupby("transition_state")
        .agg(
            n=("transition_state", "size"),
            first_day=("day_from_first_positive_proxy", "first"),
            last_day=("day_from_first_positive_proxy", "last"),
            mean_U=("U_v", "mean"),
            min_U=("U_v", "min"),
            max_U=("U_v", "max"),
            mean_Phi=("Phi_v", "mean"),
            mean_escape=("escape_pair_mean", "mean"),
            mean_step_velocity=("velocity_norm_step_total", "mean"),
            median_step_velocity=("velocity_norm_step_total", "median"),
            max_step_velocity=("velocity_norm_step_total", "max"),
            mean_calendar_velocity=("velocity_norm_calendar_total", "mean"),
            median_calendar_velocity=("velocity_norm_calendar_total", "median"),
            max_calendar_velocity=("velocity_norm_calendar_total", "max"),
            same_day_steps=("same_day_step", "sum"),
        )
        .reset_index()
        .sort_values("first_day")
    )

    OUT_TABLE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_TABLE, index=False)

    OUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    well_summary.to_csv(OUT_SUMMARY, index=False)

    print({
        "status": "wrote",
        "potential_table": str(OUT_TABLE),
        "summary": str(OUT_SUMMARY),
        "figures": [
            str(p1.relative_to(ROOT)),
            str(p2.relative_to(ROOT)),
            str(p3.relative_to(ROOT)),
        ],
        "n_rows": len(df),
        "velocity_source": "corrected_step_and_calendar_velocity_from_script_21",
    })

    print(well_summary.to_string(index=False))

if __name__ == "__main__":
    main()
