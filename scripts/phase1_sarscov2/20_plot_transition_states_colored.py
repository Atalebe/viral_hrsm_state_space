from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_transition_states.csv"
OUT_DIR = ROOT / "figures" / "phase1_sarscov2"
OUT_SUMMARY = ROOT / "metadata" / "kemp_fig5a_colored_transition_plot_summary.csv"

STATE_MARKERS = {
    "low_escape_baseline": "o",
    "intermediate_transition": "s",
    "coherent_escape_surge": "*",
    "alternate_diversity_state": "^",
    "retained_escape_state": "D",
    "high_memory_escape_return": "X",
}

def load_table():
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing transition-state table: {INPUT}")
    df = pd.read_csv(INPUT)
    df = df.sort_values(["day_from_first_positive_proxy", "within_day_order", "timepoint"]).reset_index(drop=True)
    return df

def state_scatter(ax, df, xcol, ycol):
    for state, sub in df.groupby("transition_state", sort=False):
        marker = STATE_MARKERS.get(state, "o")
        ax.scatter(
            sub[xcol],
            sub[ycol],
            label=state,
            marker=marker,
            s=85,
            alpha=0.9,
        )

    ax.plot(df[xcol], df[ycol], linewidth=1.2, alpha=0.45)

    for _, row in df.iterrows():
        label = str(row["timepoint_label"])
        if label in {"82", "86", "89", "95", "98", "99", "100", "101"} or "ETA" in label:
            ax.annotate(
                label,
                (row[xcol], row[ycol]),
                textcoords="offset points",
                xytext=(4, 4),
                fontsize=8,
            )

def save_state_axis_plot(df):
    outpath = OUT_DIR / "kemp_fig5a_colored_hrsm_axes_over_days.png"

    axes = ["H_v", "R_v", "S_v", "M_v", "Phi_v"]
    fig, ax = plt.subplots(figsize=(10, 6))

    for axis in axes:
        ax.plot(
            df["day_from_first_positive_proxy"],
            df[axis],
            marker="o",
            linewidth=1.5,
            label=axis,
            alpha=0.8,
        )

    for _, row in df.iterrows():
        if row["transition_state"] in {"coherent_escape_surge", "high_memory_escape_return", "retained_escape_state"}:
            ax.axvline(row["day_from_first_positive_proxy"], alpha=0.10)

    ax.set_xlabel("Days since first positive RT-PCR")
    ax.set_ylabel("Standardized HRSM proxy value")
    ax.set_title("Kemp Fig. 5a corrected HRSM trajectory over chronological days")
    ax.legend(frameon=False)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(outpath, dpi=300)
    plt.close(fig)
    return outpath

def save_memory_stability_plot(df):
    outpath = OUT_DIR / "kemp_fig5a_colored_memory_stability_states.png"

    fig, ax = plt.subplots(figsize=(7, 6))
    state_scatter(ax, df, "M_v", "S_v")

    ax.axhline(0, linewidth=1, alpha=0.3)
    ax.axvline(0, linewidth=1, alpha=0.3)
    ax.set_xlabel("M_v, chronological memory proxy")
    ax.set_ylabel("S_v, swarm coherence proxy")
    ax.set_title("Kemp Fig. 5a transition states in memory-stability space")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(outpath, dpi=300)
    plt.close(fig)
    return outpath

def save_escape_memory_plot(df):
    outpath = OUT_DIR / "kemp_fig5a_colored_escape_memory_over_days.png"

    fig, ax = plt.subplots(figsize=(10, 5))

    for state, sub in df.groupby("transition_state", sort=False):
        marker = STATE_MARKERS.get(state, "o")
        ax.scatter(
            sub["day_from_first_positive_proxy"],
            sub["escape_pair_mean"],
            label=state,
            marker=marker,
            s=85,
            alpha=0.9,
        )

    ax.plot(
        df["day_from_first_positive_proxy"],
        df["escape_pair_mean"],
        linewidth=1.2,
        alpha=0.45,
    )

    ax.set_xlabel("Days since first positive RT-PCR")
    ax.set_ylabel("Mean D796H and ΔH69/ΔV70 frequency proxy")
    ax.set_title("Kemp Fig. 5a escape-pair trajectory by transition state")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(outpath, dpi=300)
    plt.close(fig)
    return outpath

def main():
    df = load_table()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    figures = [
        save_state_axis_plot(df),
        save_memory_stability_plot(df),
        save_escape_memory_plot(df),
    ]

    summary = pd.DataFrame([
        {
            "figure": str(p.relative_to(ROOT)),
            "description": desc,
        }
        for p, desc in zip(
            figures,
            [
                "Corrected HRSM axes plotted against true chronological days.",
                "Colored transition states in M_v versus S_v space.",
                "Escape-pair trajectory colored by transition state.",
            ],
        )
    ])

    OUT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_SUMMARY, index=False)

    print({
        "status": "wrote",
        "summary": str(OUT_SUMMARY),
        "figures": [str(p.relative_to(ROOT)) for p in figures],
        "n_rows": len(df),
        "states": sorted(df["transition_state"].unique()),
    })

    print(summary.to_string(index=False))

if __name__ == "__main__":
    main()
