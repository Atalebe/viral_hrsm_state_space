from pathlib import Path
import pandas as pd
from datetime import date

ROOT = Path(__file__).resolve().parents[2]

REGISTRY = ROOT / "metadata" / "dataset_candidate_registry.csv"
AUDIT = ROOT / "metadata" / "sarscov2_accession_audit.csv"

OUT_MD = ROOT / "docs" / "phase1_sarscov2_workplan.md"
OUT_TEX = ROOT / "docs" / "phase1_sarscov2_workplan.tex"
OUT_RANKED = ROOT / "metadata" / "phase1_sarscov2_ranked_candidates.csv"

def clean_tex(s):
    s = str(s)
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "_": r"\_",
        "#": r"\#",
    }
    for a, b in replacements.items():
        s = s.replace(a, b)
    return s

def main():
    registry = pd.read_csv(REGISTRY)
    audit = pd.read_csv(AUDIT)

    sars = registry[registry["phase"].eq("phase1_sarscov2")].copy()

    merged = audit.merge(
        sars,
        on="dataset_name",
        how="left",
        suffixes=("_audit", "_registry")
    )

    merged = merged.sort_values("hrsm_priority").reset_index(drop=True)
    OUT_RANKED.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUT_RANKED, index=False)

    today = date.today().isoformat()

    md_lines = []
    md_lines.append("# Phase I SARS-CoV-2 HRSM Workplan")
    md_lines.append("")
    md_lines.append(f"Generated: {today}")
    md_lines.append("")
    md_lines.append("## Purpose")
    md_lines.append("")
    md_lines.append(
        "Phase I tests whether persistent SARS-CoV-2 infection can be represented as a viral HRSM state space "
        "defined by adaptive reserve, rebound capacity, swarm coherence, and retained evolutionary memory."
    )
    md_lines.append("")
    md_lines.append("The first model comparison is deliberately narrow:")
    md_lines.append("")
    md_lines.append("- Markovian current-state model: H_v, R_v, S_v")
    md_lines.append("- Non-Markovian memory model: H_v, R_v, S_v, M_v")
    md_lines.append("")
    md_lines.append("## Ranked candidate datasets")
    md_lines.append("")

    for _, row in merged.iterrows():
        md_lines.append(f"### {int(row['hrsm_priority'])}. {row['dataset_name']}")
        md_lines.append("")
        md_lines.append(f"- Paper: {row['paper']}")
        md_lines.append(f"- URL: {row['primary_url']}")
        md_lines.append(f"- Data anchor: {row['known_accession_or_data_anchor']}")
        md_lines.append(f"- Reported timepoints: {row['n_timepoints_reported']}")
        md_lines.append(f"- Reported duration days: {row['duration_days_reported']}")
        md_lines.append(f"- Data strength: {row['data_strength']}")
        md_lines.append(f"- Recommended role: {row['recommended_role']}")
        md_lines.append(f"- Audit note: {row['audit_note']}")
        md_lines.append("")

    md_lines.append("## Phase I execution sequence")
    md_lines.append("")
    md_lines.append("1. Verify accession and supplementary data availability for Kemp et al.")
    md_lines.append("2. Build a case-level sample table for the Kemp trajectory.")
    md_lines.append("3. Extract sequence, timepoint, treatment, and abundance proxies.")
    md_lines.append("4. Compute first-pass H_v, R_v, S_v, and M_v axes.")
    md_lines.append("5. Run leakage audit, axis correlation audit, and sampling-duration audit.")
    md_lines.append("6. Compare current-state and memory-augmented models.")
    md_lines.append("7. Repeat only after the first case pipeline is stable.")
    md_lines.append("")
    md_lines.append("## Failure rules")
    md_lines.append("")
    md_lines.append("- Do not treat dataset priority as proof of data usability.")
    md_lines.append("- Do not use treatment status as both an axis component and a predicted endpoint.")
    md_lines.append("- Do not let M_v collapse into ordinary genetic divergence.")
    md_lines.append("- Do not interpret viral persistence as organism-level homeostasis.")
    md_lines.append("")

    OUT_MD.write_text("\n".join(md_lines), encoding="utf-8")

    tex_lines = []
    tex_lines.append(r"\section*{Phase I SARS-CoV-2 HRSM Workplan}")
    tex_lines.append("")
    tex_lines.append(r"\textbf{Generated:} " + clean_tex(today))
    tex_lines.append("")
    tex_lines.append(r"\subsection*{Purpose}")
    tex_lines.append("")
    tex_lines.append(
        "Phase I tests whether persistent SARS-CoV-2 infection can be represented as a viral HRSM state space "
        "defined by adaptive reserve, rebound capacity, swarm coherence, and retained evolutionary memory."
    )
    tex_lines.append("")
    tex_lines.append(r"\subsection*{Model comparison}")
    tex_lines.append("")
    tex_lines.append(r"The first model comparison is deliberately narrow:")
    tex_lines.append("")
    tex_lines.append(r"\begin{itemize}")
    tex_lines.append(r"\item Markovian current-state model: \(H_v, R_v, S_v\).")
    tex_lines.append(r"\item Non-Markovian memory model: \(H_v, R_v, S_v, M_v\).")
    tex_lines.append(r"\end{itemize}")
    tex_lines.append("")
    tex_lines.append(r"\subsection*{Ranked candidate datasets}")
    tex_lines.append("")

    for _, row in merged.iterrows():
        tex_lines.append(r"\subsubsection*{" + str(int(row["hrsm_priority"])) + ". " + clean_tex(row["dataset_name"]) + "}")
        tex_lines.append(r"\begin{itemize}")
        tex_lines.append(r"\item \textbf{Paper:} " + clean_tex(row["paper"]))
        tex_lines.append(r"\item \textbf{URL:} " + clean_tex(row["primary_url"]))
        tex_lines.append(r"\item \textbf{Data anchor:} " + clean_tex(row["known_accession_or_data_anchor"]))
        tex_lines.append(r"\item \textbf{Reported timepoints:} " + clean_tex(row["n_timepoints_reported"]))
        tex_lines.append(r"\item \textbf{Reported duration days:} " + clean_tex(row["duration_days_reported"]))
        tex_lines.append(r"\item \textbf{Data strength:} " + clean_tex(row["data_strength"]))
        tex_lines.append(r"\item \textbf{Recommended role:} " + clean_tex(row["recommended_role"]))
        tex_lines.append(r"\item \textbf{Audit note:} " + clean_tex(row["audit_note"]))
        tex_lines.append(r"\end{itemize}")
        tex_lines.append("")

    tex_lines.append(r"\subsection*{Phase I execution sequence}")
    tex_lines.append(r"\begin{enumerate}")
    tex_lines.append(r"\item Verify accession and supplementary data availability for Kemp et al.")
    tex_lines.append(r"\item Build a case-level sample table for the Kemp trajectory.")
    tex_lines.append(r"\item Extract sequence, timepoint, treatment, and abundance proxies.")
    tex_lines.append(r"\item Compute first-pass \(H_v\), \(R_v\), \(S_v\), and \(M_v\) axes.")
    tex_lines.append(r"\item Run leakage audit, axis correlation audit, and sampling-duration audit.")
    tex_lines.append(r"\item Compare current-state and memory-augmented models.")
    tex_lines.append(r"\item Repeat only after the first case pipeline is stable.")
    tex_lines.append(r"\end{enumerate}")
    tex_lines.append("")
    tex_lines.append(r"\subsection*{Failure rules}")
    tex_lines.append(r"\begin{itemize}")
    tex_lines.append(r"\item Do not treat dataset priority as proof of data usability.")
    tex_lines.append(r"\item Do not use treatment status as both an axis component and a predicted endpoint.")
    tex_lines.append(r"\item Do not let \(M_v\) collapse into ordinary genetic divergence.")
    tex_lines.append(r"\item Do not interpret viral persistence as organism-level homeostasis.")
    tex_lines.append(r"\end{itemize}")

    OUT_TEX.write_text("\n".join(tex_lines), encoding="utf-8")

    print({
        "status": "wrote",
        "ranked_csv": str(OUT_RANKED),
        "markdown": str(OUT_MD),
        "latex": str(OUT_TEX),
        "n_candidates": len(merged),
    })

if __name__ == "__main__":
    main()
