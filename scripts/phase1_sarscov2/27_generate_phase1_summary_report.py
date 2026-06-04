from pathlib import Path
from datetime import date
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]

OUT_MD = ROOT / "docs" / "phase1_kemp_fig5a_summary_report.md"
OUT_TEX = ROOT / "docs" / "phase1_kemp_fig5a_summary_report.tex"
OUT_AUDIT = ROOT / "metadata" / "phase1_kemp_fig5a_summary_report_audit.csv"

PATHS = {
    "proxy_audit": ROOT / "metadata" / "kemp_fig5a_proxy_audit.csv",
    "hrsm": ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_hrsm_state_table.csv",
    "transition_states": ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_transition_states.csv",
    "daily_states": ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_collapsed_daily_states.csv",
    "daily_probs": ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_state_transition_probability_matrix_daily_collapsed.csv",
    "stationary": ROOT / "metadata" / "kemp_fig5a_daily_collapsed_stationary_distribution.csv",
    "velocity_summary": ROOT / "metadata" / "kemp_fig5a_phase_velocity_summary.csv",
    "potential_summary": ROOT / "metadata" / "kemp_fig5a_potential_well_summary.csv",
}

FIGURES = [
    "figures/phase1_sarscov2/kemp_fig5a_colored_hrsm_axes_over_days.png",
    "figures/phase1_sarscov2/kemp_fig5a_colored_memory_stability_states.png",
    "figures/phase1_sarscov2/kemp_fig5a_colored_escape_memory_over_days.png",
    "figures/phase1_sarscov2/kemp_fig5a_velocity_profiles_over_days.png",
    "figures/phase1_sarscov2/kemp_fig5a_daily_collapsed_transition_heatmap.png",
    "figures/phase1_sarscov2/kemp_fig5a_daily_collapsed_stationary_distribution.png",
    "figures/phase1_sarscov2/kemp_fig5a_potential_well_over_days.png",
    "figures/phase1_sarscov2/kemp_fig5a_potential_vs_escape_pair.png",
    "figures/phase1_sarscov2/kemp_fig5a_potential_vs_step_velocity.png",
]

def read_csv_required(key):
    p = PATHS[key]
    if not p.exists():
        raise FileNotFoundError(f"Missing required file for {key}: {p}")
    return pd.read_csv(p)

def read_matrix_required(key):
    p = PATHS[key]
    if not p.exists():
        raise FileNotFoundError(f"Missing required matrix for {key}: {p}")
    return pd.read_csv(p, index_col=0)

def rel(path):
    return str(Path(path).relative_to(ROOT)) if Path(path).is_absolute() else str(path)

def md_table(df, max_rows=20):
    if len(df) > max_rows:
        df = df.head(max_rows).copy()
    return df.to_markdown(index=False)

def tex_escape(s):
    s = str(s)
    repl = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    return s

def tex_table(df, columns=None, max_rows=20):
    if columns is not None:
        df = df[columns].copy()
    if len(df) > max_rows:
        df = df.head(max_rows).copy()

    lines = []
    colspec = "l" * len(df.columns)
    lines.append(r"\begin{tabular}{" + colspec + "}")
    lines.append(r"\toprule")
    lines.append(" & ".join(tex_escape(c) for c in df.columns) + r" \\")
    lines.append(r"\midrule")
    for _, row in df.iterrows():
        vals = []
        for v in row:
            if isinstance(v, float):
                vals.append(f"{v:.4g}")
            else:
                vals.append(tex_escape(v))
        lines.append(" & ".join(vals) + r" \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    return "\n".join(lines)

def summarize_states(transitions):
    summary = (
        transitions.groupby("transition_state")
        .agg(
            n=("transition_state", "size"),
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
        .sort_values("first_day")
    )
    return summary

def main():
    proxy_audit = read_csv_required("proxy_audit")
    hrsm = read_csv_required("hrsm")
    transitions = read_csv_required("transition_states")
    daily_states = read_csv_required("daily_states")
    daily_probs = read_matrix_required("daily_probs")
    stationary = read_csv_required("stationary")
    velocity_summary = read_csv_required("velocity_summary")
    potential_summary = read_csv_required("potential_summary")

    state_summary = summarize_states(transitions)

    missing_figs = [f for f in FIGURES if not (ROOT / f).exists()]
    if missing_figs:
        print({"warning": "missing_figures", "figures": missing_figs})

    n_rows = int(proxy_audit.loc[0, "n_rows_retained"]) if "n_rows_retained" in proxy_audit.columns else len(hrsm)
    n_removed = int(proxy_audit.loc[0, "n_rows_removed_as_footer_or_blank"]) if "n_rows_removed_as_footer_or_blank" in proxy_audit.columns else np.nan

    stationary_top = stationary.sort_values("stationary_probability", ascending=False).head(2)

    md = []
    md.append("# Phase I SARS-CoV-2 HRSM Pilot Summary")
    md.append("")
    md.append(f"Generated: {date.today().isoformat()}")
    md.append("")
    md.append("## Scope")
    md.append("")
    md.append(
        "This report summarizes the Phase I figure-source reconstruction of the Kemp et al. chronic SARS-CoV-2 infection trajectory. "
        "The analysis uses the Fig. 5a workbook sheet from the Kemp figure-source data and should not be described as raw FASTQ or full variant-calling analysis."
    )
    md.append("")
    md.append("## Data status")
    md.append("")
    md.append(f"- Retained biological rows: {n_rows}")
    md.append(f"- Removed footer or blank rows: {n_removed}")
    md.append("- Source level: figure-source reconstruction")
    md.append("- Main mutation pair: D796H and ΔH69/ΔV70")
    md.append("- CT values: interpolated by explicit day anchors for pilot rebound proxy construction")
    md.append("- Memory kernel: chronological exponential decay, tau = 7 days, max lag = 30 days")
    md.append("")
    md.append("## Main result")
    md.append("")
    md.append(
        "The daily-corrected HRSM trajectory separates the chronic infection into a low-escape baseline, "
        "a coherent escape surge at day 82, an alternate diversity state between days 89 and 95, "
        "and a retained escape/high-memory return cycle from day 98 onward."
    )
    md.append("")
    md.append(
        "The strongest HRSM contrast is between the alternate diversity state and the retained escape/high-memory return states. "
        "The alternate diversity state has high reserve-like diversity but weak or negative memory/coherence, while the retained escape and high-memory return states recover positive memory and coherence around the D796H plus ΔH69/ΔV70 structure."
    )
    md.append("")
    md.append("## Transition-state summary")
    md.append("")
    md.append(md_table(state_summary))
    md.append("")
    md.append("## Daily-collapsed transition probability matrix")
    md.append("")
    md.append(daily_probs.to_markdown())
    md.append("")
    md.append("## Stationary distribution")
    md.append("")
    md.append(md_table(stationary))
    md.append("")
    md.append(
        "The stationary distribution is computed by solving the linear stationary equations, not by power iteration. "
        "This matters because the daily-collapsed matrix contains a deterministic two-state terminal cycle. "
        "The stationary mass is therefore split evenly between retained_escape_state and high_memory_escape_return."
    )
    md.append("")
    md.append("## Velocity summary")
    md.append("")
    md.append(
        "The corrected velocity engine reports step-normalized velocity for ordered sample contrasts and calendar-day velocity only where positive day gaps exist. "
        "This prevents same-day samples from creating artificial velocity explosions."
    )
    md.append("")
    md.append(md_table(velocity_summary))
    md.append("")
    md.append("## Potential-well summary")
    md.append("")
    md.append(md_table(potential_summary))
    md.append("")
    md.append("## Figures")
    md.append("")
    for f in FIGURES:
        md.append(f"- `{f}`")
    md.append("")
    md.append("## Interpretation boundary")
    md.append("")
    md.append(
        "This Phase I result is a pilot topology from one figure-source reconstruction. "
        "It supports continued testing of a viral HRSM memory branch, but it does not prove a universal viral attractor, does not establish clinical phenotype classes, and does not replace raw sequencing analysis."
    )

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    tex = []
    tex.append(r"\section*{Phase I SARS-CoV-2 HRSM Pilot Summary}")
    tex.append("")
    tex.append(r"\textbf{Generated:} " + str(date.today().isoformat()))
    tex.append("")
    tex.append(r"\subsection*{Scope}")
    tex.append(
        "This report summarizes the Phase I figure-source reconstruction of the Kemp et al. chronic SARS-CoV-2 infection trajectory. "
        "The analysis uses the Fig. 5a workbook sheet from the Kemp figure-source data and should not be described as raw FASTQ or full variant-calling analysis."
    )
    tex.append("")
    tex.append(r"\subsection*{Data status}")
    tex.append(r"\begin{itemize}")
    tex.append(r"\item Retained biological rows: " + str(n_rows))
    tex.append(r"\item Removed footer or blank rows: " + str(n_removed))
    tex.append(r"\item Source level: figure-source reconstruction")
    tex.append(r"\item Main mutation pair: D796H and \(\Delta H69/\Delta V70\)")
    tex.append(r"\item CT values: interpolated by explicit day anchors for pilot rebound proxy construction")
    tex.append(r"\item Memory kernel: chronological exponential decay, \(\tau=7\) days, max lag \(=30\) days")
    tex.append(r"\end{itemize}")
    tex.append("")
    tex.append(r"\subsection*{Main result}")
    tex.append(
        "The daily-corrected HRSM trajectory separates the chronic infection into a low-escape baseline, "
        "a coherent escape surge at day 82, an alternate diversity state between days 89 and 95, "
        "and a retained escape/high-memory return cycle from day 98 onward."
    )
    tex.append("")
    tex.append(
        "The strongest HRSM contrast is between the alternate diversity state and the retained escape/high-memory return states. "
        r"The alternate diversity state has high reserve-like diversity but weak or negative memory/coherence, while the retained escape and high-memory return states recover positive memory and coherence around the D796H plus \(\Delta H69/\Delta V70\) structure."
    )
    tex.append("")
    tex.append(r"\subsection*{Transition-state summary}")
    tex.append(tex_table(state_summary, max_rows=20))
    tex.append("")
    tex.append(r"\subsection*{Daily-collapsed transition matrix}")
    tex.append(tex_table(daily_probs.reset_index(), max_rows=20))
    tex.append("")
    tex.append(r"\subsection*{Stationary distribution}")
    tex.append(tex_table(stationary, max_rows=20))
    tex.append("")
    tex.append(
        "The stationary distribution is computed by solving the linear stationary equations, not by power iteration. "
        "This matters because the daily-collapsed matrix contains a deterministic two-state terminal cycle. "
        "The stationary mass is therefore split evenly between retained escape and high-memory escape return."
    )
    tex.append("")
    tex.append(r"\subsection*{Velocity summary}")
    tex.append(tex_table(velocity_summary, max_rows=20))
    tex.append("")
    tex.append(r"\subsection*{Potential-well summary}")
    tex.append(tex_table(potential_summary, max_rows=20))
    tex.append("")
    tex.append(r"\subsection*{Figures}")
    for f in FIGURES:
        tex.append(r"\begin{figure}[h]")
        tex.append(r"\centering")
        tex.append(r"\includegraphics[width=0.9\textwidth]{" + f + "}")
        tex.append(r"\caption{" + tex_escape(Path(f).stem.replace("_", " ")) + "}")
        tex.append(r"\end{figure}")
        tex.append("")
    tex.append(r"\subsection*{Interpretation boundary}")
    tex.append(
        "This Phase I result is a pilot topology from one figure-source reconstruction. "
        "It supports continued testing of a viral HRSM memory branch, but it does not prove a universal viral attractor, does not establish clinical phenotype classes, and does not replace raw sequencing analysis."
    )

    OUT_TEX.write_text("\n".join(tex), encoding="utf-8")

    audit = pd.DataFrame([{
        "report_md": str(OUT_MD.relative_to(ROOT)),
        "report_tex": str(OUT_TEX.relative_to(ROOT)),
        "n_hrsm_rows": len(hrsm),
        "n_transition_rows": len(transitions),
        "n_daily_rows": len(daily_states),
        "n_figures_listed": len(FIGURES),
        "n_missing_figures": len(missing_figs),
        "stationary_top_states": "|".join(stationary_top["state"].astype(str)),
        "stationary_top_probs": "|".join(stationary_top["stationary_probability"].astype(str)),
    }])
    OUT_AUDIT.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(OUT_AUDIT, index=False)

    print({
        "status": "wrote",
        "markdown": str(OUT_MD),
        "latex": str(OUT_TEX),
        "audit": str(OUT_AUDIT),
        "n_figures": len(FIGURES),
        "n_missing_figures": len(missing_figs),
    })

    print(audit.to_string(index=False))

if __name__ == "__main__":
    main()
