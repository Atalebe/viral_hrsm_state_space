from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_phase_velocity.csv"
OUT_DIR = ROOT / "figures" / "phase1_sarscov2"
OUT_SUMMARY = ROOT / "metadata" / "kemp_fig5a_velocity_profile_plot_summary.csv"

STATE_MARKERS = {
    "low_escape_baseline": "o",
    "intermediate_transition": "s",
    "coherent_escape_surge": "*",
    "alternate_diversity_state": "^",
    "retained_escape_state": "D",
    "high_memory_escape_return": "X",
}

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing velocity table: {INPUT}")

    df = pd.read_csv(INPUT)
    df = df.sort_values(["day_from_first_positive_proxy", "within_day_order", "timepoint"]).reset_index(drop=True)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    p1 = OUT_DIR / "kemp_fig5a_velocity_profiles_over_days.png"
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        df["day_from_first_positive_proxy"],
        df["velocity_norm_step_total"],
        marker="o",
        linewidth=1.4,
        label="Step-normalized velocity",
        alpha=0.85,
    )

    ax.plot(
        df["day_from_first_positive_proxy"],
        df["velocity_norm_calendar_total"],
        marker="s",
        linewidth=1.2,
        label="Calendar-day velocity, positive dt only",
        alpha=0.85,
    )

    for _, row in df[df["same_day_step"]].iterrows():
        ax.axvline(row["day_from_first_positive_proxy"], alpha=0.10)

    ax.set_xlabel("Days since first positive RT-PCR")
    ax.set_ylabel("Velocity norm")
    ax.set_title("Kemp Fig. 5a velocity profiles after sub-day correction")
    ax.legend(frameon=False)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(p1, dpi=300)
    plt.close(fig)

    p2 = OUT_DIR / "kemp_fig5a_step_velocity_by_transition_state.png"
    fig, ax = plt.subplots(figsize=(10, 5))

    for state, sub in df.groupby("transition_state", sort=False):
        ax.scatter(
            sub["day_from_first_positive_proxy"],
            sub["velocity_norm_step_total"],
            label=state,
            marker=STATE_MARKERS.get(state, "o"),
            s=80,
            alpha=0.9,
        )

    ax.plot(
        df["day_from_first_positive_proxy"],
        df["velocity_norm_step_total"],
        linewidth=1.1,
        alpha=0.45,
    )

    ax.set_xlabel("Days since first positive RT-PCR")
    ax.set_ylabel("Step-normalized velocity norm")
    ax.set_title("Kemp Fig. 5a step-normalized velocity by transition state")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(p2, dpi=300)
    plt.close(fig)

    summary = pd.DataFrame([
        {
            "figure": str(p1.relative_to(ROOT)),
            "description": "Step-normalized and calendar-day velocity profiles over true day axis.",
        },
        {
            "figure": str(p2.relative_to(ROOT)),
            "description": "Step-normalized velocity colored by transition state.",
        },
    ])

    OUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_SUMMARY, index=False)

    print({
        "status": "wrote",
        "summary": str(OUT_SUMMARY),
        "figures": [str(p1.relative_to(ROOT)), str(p2.relative_to(ROOT))],
        "n_rows": len(df),
    })
    print(summary.to_string(index=False))

if __name__ == "__main__":
    main()
