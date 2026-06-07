from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "metadata" / "phase2_sarscov2_multicase" / "phase2_dataset_registry.csv"

ROWS = [
    {
        "case_id": "BOYLE_2025_PRJNA1295507",
        "dataset_name": "Boyle et al. persistent SARS-CoV-2 intra-host evolution",
        "virus": "SARS-CoV-2",
        "lineage_or_variant": "mixed_or_to_audit",
        "source_reference": "Boyle et al., 2025, Intra-Host Evolution of SARS-CoV-2 During Persistent Infection",
        "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12567731/",
        "data_type": "raw_reads_sra_plus_supplemental_metadata",
        "n_timepoints": "to_audit",
        "has_day_mapping": "to_audit",
        "has_variant_frequencies": "to_audit",
        "has_ct_or_viral_load": "to_audit",
        "has_treatment_metadata": "to_audit",
        "has_host_context": "yes",
        "has_endpoint": "to_audit",
        "admissibility_status": "candidate",
        "notes": "Data Availability reports raw reads under NCBI BioProject PRJNA1295507 and SRA accessions in Supplemental Table S1. Strong first Phase II data-contact target."
    },
    {
        "case_id": "WEIGANG_2021_IMMUNOSUPPRESSED",
        "dataset_name": "Weigang et al. within-host evolution in an immunosuppressed patient",
        "virus": "SARS-CoV-2",
        "lineage_or_variant": "to_audit",
        "source_reference": "Weigang et al., Nature Communications 2021",
        "source_url": "https://www.nature.com/articles/s41467-021-26602-3",
        "data_type": "longitudinal_sequence_case",
        "n_timepoints": "to_audit",
        "has_day_mapping": "yes",
        "has_variant_frequencies": "to_audit",
        "has_ct_or_viral_load": "to_audit",
        "has_treatment_metadata": "yes",
        "has_host_context": "yes",
        "has_endpoint": "to_audit",
        "admissibility_status": "candidate",
        "notes": "Longitudinal immunosuppressed-patient case. Needs accession and table audit before modelling."
    },
    {
        "case_id": "CHAGUZA_2023_471DAY",
        "dataset_name": "Chaguza et al. accelerated intrahost evolution 471-day infection",
        "virus": "SARS-CoV-2",
        "lineage_or_variant": "to_audit",
        "source_reference": "Chaguza et al., 2023, accelerated SARS-CoV-2 intrahost evolution",
        "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9906997/",
        "data_type": "longitudinal_persistent_case",
        "n_timepoints": "to_audit",
        "has_day_mapping": "yes",
        "has_variant_frequencies": "to_audit",
        "has_ct_or_viral_load": "yes",
        "has_treatment_metadata": "to_audit",
        "has_host_context": "yes",
        "has_endpoint": "persistent_471_days",
        "admissibility_status": "candidate",
        "notes": "Long-duration infection. Useful for memory and persistence topology if sequence tables/accessions are recoverable."
    },
    {
        "case_id": "HARARI_2022_27_CHRONIC",
        "dataset_name": "Harari et al. drivers of adaptive evolution during chronic infections",
        "virus": "SARS-CoV-2",
        "lineage_or_variant": "mixed",
        "source_reference": "Harari et al., Nature Medicine 2022",
        "source_url": "https://www.nature.com/articles/s41591-022-01882-4",
        "data_type": "multi_case_chronic_infection_consolidation",
        "n_timepoints": "multi_case",
        "has_day_mapping": "to_audit",
        "has_variant_frequencies": "to_audit",
        "has_ct_or_viral_load": "to_audit",
        "has_treatment_metadata": "yes",
        "has_host_context": "yes",
        "has_endpoint": "yes",
        "admissibility_status": "context_or_candidate",
        "notes": "Important multi-case chronic infection set. Use after checking whether case-level timepoint tables are available."
    },
    {
        "case_id": "GHAFARI_2024_SURVEILLANCE",
        "dataset_name": "Ghafari et al. persistent SARS-CoV-2 community surveillance",
        "virus": "SARS-CoV-2",
        "lineage_or_variant": "mixed",
        "source_reference": "Ghafari et al., Nature 2024 / Lancet Microbe 2025 related work",
        "source_url": "https://www.nature.com/articles/s41586-024-07029-4",
        "data_type": "large_surveillance_persistent_infections",
        "n_timepoints": "large_surveillance",
        "has_day_mapping": "yes",
        "has_variant_frequencies": "to_audit",
        "has_ct_or_viral_load": "yes",
        "has_treatment_metadata": "limited",
        "has_host_context": "limited",
        "has_endpoint": "yes",
        "admissibility_status": "background_or_population_reference",
        "notes": "Best for prevalence/background and maybe later cohort topology, not first mechanistic within-host Phase II reconstruction."
    },
    {
        "case_id": "VOLKOW_2026_THREE_CASES",
        "dataset_name": "Volkow-Fernández et al. molecular characterization of persistent SARS-CoV-2",
        "virus": "SARS-CoV-2",
        "lineage_or_variant": "to_audit",
        "source_reference": "Volkow-Fernández et al., 2026",
        "source_url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12944910/",
        "data_type": "three_persistent_infection_cases",
        "n_timepoints": "to_audit",
        "has_day_mapping": "yes",
        "has_variant_frequencies": "to_audit",
        "has_ct_or_viral_load": "to_audit",
        "has_treatment_metadata": "yes",
        "has_host_context": "yes",
        "has_endpoint": "yes",
        "admissibility_status": "candidate",
        "notes": "Three immunocompromised persistent infections, including very long persistence. Audit sequence tables and accessions before use."
    }
]

def main():
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)

    new = pd.DataFrame(ROWS)

    if REGISTRY.exists():
        old = pd.read_csv(REGISTRY)
        old = old[~old["case_id"].astype(str).eq("PLACEHOLDER_CASE")]
        combined = pd.concat([old, new], ignore_index=True)
        combined = combined.drop_duplicates(subset=["case_id"], keep="last")
    else:
        combined = new

    combined.to_csv(REGISTRY, index=False)

    print({
        "status": "wrote",
        "registry": str(REGISTRY),
        "n_rows": len(combined),
    })
    print(combined[["case_id", "dataset_name", "admissibility_status", "notes"]].to_string(index=False))

if __name__ == "__main__":
    main()
