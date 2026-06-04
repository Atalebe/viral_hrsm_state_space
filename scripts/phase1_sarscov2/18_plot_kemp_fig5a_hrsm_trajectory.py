from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_hrsm_state_table.csv"
OUT_DIR = ROOT / "figures" / "phase1_sarscov2"
OUT_SUMMARY = ROOT / "metadata" / "kemp_fig5a_hrsm_plot_summary.csv"

def label_day(row):
    label = str(row.get("timepoint_label", ""))
    day = row.get("day_from_first_positive_proxy", None)
    if pd.notna(day):
        return f"day {int(day)}"
    return label

def save_line_plot(df, ycols, outpath, title, ylabel):
    fig, ax = plt.subplots(figsize=(9, 5))
    x = df["day_from_first_positive_proxy"]

    for y in ycols:
        ax.plot(x, df[y], marker="o", label=y)

    ax.set_xlabel("Days since first positive RT-PCR")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(frameon=False)
    ax.grid(True, alpha=0.25)

    for _, row in df.iterrows():
        if str(row["timepoint_label"]) in ["82", "93", "95", "98", "99", "101"]:
            ax.annotate(
                label_day(row),
                (row["timepoint"], row[ycols[0]]),
                textcoords="offset points",
                xytext=(4, 6),
                fontsize=8,
            )

    fig.tight_layout()
    fig.savefig(outpath, dpi=300)
    plt.close(fig)

def save_scatter(df, xcol, ycol, outpath, title):
    fig, ax = plt.subplots(figsize=(6, 5))

    ax.scatter(df[xcol], df[ycol], s=60)

    for _, row in df.iterrows():
        ax.annotate(
            str(row["timepoint_label"]),
            (row[xcol], row[ycol]),
            textcoords="offset points",
            xytext=(4, 4),
            fontsize=8,
        )

    ax.set_xlabel(xcol)
    ax.set_ylabel(ycol)
    ax.set_title(title)
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(outpath, dpi=300)
    plt.close(fig)

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing HRSM state table: {INPUT}")

    df = pd.read_csv(INPUT)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Preserve ordered figure-source trajectory, including ETA rows.
    df = df.sort_values("timepoint").reset_index(drop=True)

    p1 = OUT_DIR / "kemp_fig5a_hrsm_axes_over_time.png"
    p2 = OUT_DIR / "kemp_fig5a_escape_mutations_over_time.png"
    p3 = OUT_DIR / "kemp_fig5a_phi_over_time.png"
    p4 = OUT_DIR / "kemp_fig5a_memory_vs_stability.png"
    p5 = OUT_DIR / "kemp_fig5a_reserve_vs_memory.png"

    save_line_plot(
        df,
        ["H_v", "R_v", "S_v", "M_v"],
        p1,
        "Kemp Fig. 5a viral HRSM axes over ordered time",
        "Standardized HRSM proxy value",
    )

    save_line_plot(
        df,
        ["D796H", "del69/70"],
        p2,
        "Kemp Fig. 5a escape genotype trajectory",
        "Figure-source mutation frequency proxy",
    )

    save_line_plot(
        df,
        ["Phi_v"],
        p3,
        "Kemp Fig. 5a viral potential proxy over ordered time",
        "Phi_v",
    )

    save_scatter(
        df,
        "M_v",
        "S_v",
        p4,
        "Kemp Fig. 5a memory-stability projection",
    )

    save_scatter(
        df,
        "H_v",
        "M_v",
        p5,
        "Kemp Fig. 5a reserve-memory projection",
    )

    # Simple event summary for inspection.
    summary = pd.DataFrame([
        {
            "figure": str(p1.relative_to(ROOT)),
            "description": "All four HRSM axes over ordered Fig. 5a timepoints.",
        },
        {
            "figure": str(p2.relative_to(ROOT)),
            "description": "D796H and del69/70 escape genotype frequency proxies.",
        },
        {
            "figure": str(p3.relative_to(ROOT)),
            "description": "Composite viral potential proxy Phi_v over ordered time.",
        },
        {
            "figure": str(p4.relative_to(ROOT)),
            "description": "Memory-stability projection, useful for escape-state geometry.",
        },
        {
            "figure": str(p5.relative_to(ROOT)),
            "description": "Reserve-memory projection, useful for retained adaptive structure.",
        },
    ])
    summary.to_csv(OUT_SUMMARY, index=False)

    key = df[[
        "timepoint",
        "timepoint_label",
        "D796H",
        "del69/70",
        "H_v",
        "R_v",
        "S_v",
        "M_v",
        "Phi_v",
    ]].copy()

    print({
        "status": "wrote",
        "summary": str(OUT_SUMMARY),
        "n_rows": len(df),
        "figures": [str(p.relative_to(ROOT)) for p in [p1, p2, p3, p4, p5]],
    })
    print(key.to_string(index=False))

if __name__ == "__main__":
    main()
