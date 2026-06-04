from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "metadata" / "dataset_candidate_registry.csv"
OUT = REGISTRY

ROWS = [
    {
        "virus": "SARS-CoV-2",
        "dataset_name": "Kemp et al. chronic infection under convalescent plasma",
        "source_reference": "Kemp et al., Nature 2021, SARS-CoV-2 evolution during treatment of chronic infection",
        "source_url": "https://www.nature.com/articles/s41586-021-03291-y",
        "longitudinal_structure": "yes",
        "raw_reads_available": "likely",
        "consensus_available": "yes",
        "viral_load_or_ct_available": "yes",
        "treatment_context_available": "yes",
        "host_context_available": "yes",
        "outcome_label_available": "yes",
        "phase": "phase1_sarscov2",
        "admissibility_status": "high_priority",
        "notes": "Strong first candidate: 23 whole-genome ultra-deep sequencing timepoints across 101 days, with remdesivir and convalescent plasma treatment context."
    },
    {
        "virus": "SARS-CoV-2",
        "dataset_name": "Weigang et al. immunosuppressed within-host evolution",
        "source_reference": "Weigang et al., Nature Communications 2021, within-host evolution of SARS-CoV-2 in an immunosuppressed patient",
        "source_url": "https://www.nature.com/articles/s41467-021-26602-3",
        "longitudinal_structure": "yes",
        "raw_reads_available": "likely",
        "consensus_available": "yes",
        "viral_load_or_ct_available": "unclear",
        "treatment_context_available": "yes",
        "host_context_available": "yes",
        "outcome_label_available": "yes",
        "phase": "phase1_sarscov2",
        "admissibility_status": "candidate",
        "notes": "Useful immune-escape trajectory. Mutations accumulate from day 42 onward, including selected variants. Check accession and depth before high-priority use."
    },
    {
        "virus": "SARS-CoV-2",
        "dataset_name": "Schmidt et al. 521-day persistent infection",
        "source_reference": "Schmidt et al., npj Genomic Medicine 2025, adaptive evolution during persistent infection for 521 days",
        "source_url": "https://www.nature.com/articles/s41525-025-00463-x",
        "longitudinal_structure": "yes",
        "raw_reads_available": "yes",
        "consensus_available": "yes",
        "viral_load_or_ct_available": "unclear",
        "treatment_context_available": "yes",
        "host_context_available": "yes",
        "outcome_label_available": "yes",
        "phase": "phase1_sarscov2",
        "admissibility_status": "high_priority",
        "notes": "Five whole-genome sequencing timepoints across 521 days. ENA project accession PRJEB77414. Strong memory candidate despite low timepoint count."
    },
    {
        "virus": "SARS-CoV-2",
        "dataset_name": "Ghafari et al. community surveillance persistent infections",
        "source_reference": "Ghafari et al., Nature 2024, prevalence of persistent SARS-CoV-2 in a large community surveillance study",
        "source_url": "https://www.nature.com/articles/s41586-024-07029-4",
        "longitudinal_structure": "yes",
        "raw_reads_available": "unclear",
        "consensus_available": "yes",
        "viral_load_or_ct_available": "yes",
        "treatment_context_available": "unclear",
        "host_context_available": "limited",
        "outcome_label_available": "yes",
        "phase": "phase1_sarscov2",
        "admissibility_status": "background_or_population_reference",
        "notes": "Large-scale reference for persistent infection prevalence and rebounding high viral loads. Better as comparator/background than first mechanistic HRSM case study."
    },
    {
        "virus": "SARS-CoV-2",
        "dataset_name": "Harari et al. chronic infection adaptive evolution drivers",
        "source_reference": "Harari et al., Nature Medicine 2022, drivers of adaptive evolution during chronic SARS-CoV-2 infections",
        "source_url": "https://www.nature.com/articles/s41591-022-01882-4",
        "longitudinal_structure": "yes",
        "raw_reads_available": "likely",
        "consensus_available": "yes",
        "viral_load_or_ct_available": "unclear",
        "treatment_context_available": "yes",
        "host_context_available": "yes",
        "outcome_label_available": "yes",
        "phase": "phase1_sarscov2",
        "admissibility_status": "candidate",
        "notes": "Important for antibody-based treatment pressure and heterogeneity across chronic infections. Good for robustness and theory framing."
    }
]

def main():
    old = pd.read_csv(REGISTRY) if REGISTRY.exists() else pd.DataFrame()
    new = pd.DataFrame(ROWS)

    if not old.empty:
        old = old[~old["dataset_name"].astype(str).str.contains("PLACEHOLDER", case=False, na=False)]
        combined = pd.concat([old, new], ignore_index=True)
        combined = combined.drop_duplicates(subset=["virus", "dataset_name"], keep="last")
    else:
        combined = new

    combined.to_csv(OUT, index=False)
    print({"status": "wrote", "path": str(OUT), "n_rows": len(combined)})

if __name__ == "__main__":
    main()
