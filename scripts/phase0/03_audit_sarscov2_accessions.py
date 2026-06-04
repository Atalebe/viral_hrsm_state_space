from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "metadata" / "sarscov2_accession_audit.csv"

ROWS = [
    {
        "dataset_name": "Kemp et al. chronic infection under convalescent plasma",
        "paper": "Kemp et al., Nature 2021",
        "primary_url": "https://www.nature.com/articles/s41586-021-03291-y",
        "known_accession_or_data_anchor": "Check paper Data Availability and supplementary materials",
        "n_timepoints_reported": 23,
        "duration_days_reported": 101,
        "data_strength": "very_high",
        "hrsm_priority": 1,
        "recommended_role": "primary_phase1_test_case",
        "audit_note": "Best first target. Whole-genome ultra-deep sequencing across 23 timepoints. Strong treatment-pressure structure."
    },
    {
        "dataset_name": "Schmidt et al. 521-day persistent infection",
        "paper": "Schmidt et al., npj Genomic Medicine 2025",
        "primary_url": "https://www.nature.com/articles/s41525-025-00463-x",
        "known_accession_or_data_anchor": "ENA PRJEB77414",
        "n_timepoints_reported": 5,
        "duration_days_reported": 521,
        "data_strength": "high",
        "hrsm_priority": 2,
        "recommended_role": "long_memory_case",
        "audit_note": "Excellent memory branch because duration is extreme. Fewer timepoints than Kemp, but long temporal span is useful for M_v."
    },
    {
        "dataset_name": "Weigang et al. immunosuppressed within-host evolution",
        "paper": "Weigang et al., Nature Communications 2021",
        "primary_url": "https://www.nature.com/articles/s41467-021-26602-3",
        "known_accession_or_data_anchor": "Check Data Availability, supplementary files, and sequence repositories",
        "n_timepoints_reported": "to_audit",
        "duration_days_reported": "to_audit",
        "data_strength": "medium_high",
        "hrsm_priority": 3,
        "recommended_role": "immune_escape_validation_case",
        "audit_note": "Good immune-escape trajectory. Needs accession-level check before becoming a primary case."
    },
    {
        "dataset_name": "Harari et al. chronic infection adaptive evolution drivers",
        "paper": "Harari et al., Nature Medicine 2022",
        "primary_url": "https://www.nature.com/articles/s41591-022-01882-4",
        "known_accession_or_data_anchor": "Check supplementary tables and public sequence identifiers",
        "n_timepoints_reported": "multi_case",
        "duration_days_reported": "multi_case",
        "data_strength": "medium",
        "hrsm_priority": 4,
        "recommended_role": "cross_case_context_and_robustness",
        "audit_note": "Important chronic-infection context across 27 infections, but may be less clean as the first mechanistic HRSM case."
    },
    {
        "dataset_name": "Ghafari et al. community surveillance persistent infections",
        "paper": "Ghafari et al., Nature 2024",
        "primary_url": "https://www.nature.com/articles/s41586-024-07029-4",
        "known_accession_or_data_anchor": "Check study data access conditions and supplementary metadata",
        "n_timepoints_reported": "large_surveillance",
        "duration_days_reported": "30_to_60_plus",
        "data_strength": "medium",
        "hrsm_priority": 5,
        "recommended_role": "background_population_reference",
        "audit_note": "Excellent for population-scale framing, not the first mechanistic within-host HRSM case."
    }
]

def main():
    df = pd.DataFrame(ROWS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print({"status": "wrote", "path": str(OUT), "n_rows": len(df)})
    print(df[["dataset_name", "hrsm_priority", "recommended_role", "known_accession_or_data_anchor"]].to_string(index=False))

if __name__ == "__main__":
    main()
