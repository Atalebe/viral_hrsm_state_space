from pathlib import Path
import pandas as pd
from datetime import date

ROOT = Path(__file__).resolve().parents[2]

OUT_CHECKLIST = ROOT / "metadata" / "kemp_data_availability_checklist.csv"
OUT_SUMMARY = ROOT / "metadata" / "kemp_data_availability_summary.md"
OUT_CASE_TEMPLATE = ROOT / "results" / "phase1_sarscov2" / "kemp_case_table_template.csv"

KEMP_URL = "https://www.nature.com/articles/s41586-021-03291-y"
KEMP_PMC = "https://pmc.ncbi.nlm.nih.gov/articles/PMC7610568/"

CHECKLIST_ROWS = [
    {
        "item": "paper_url",
        "status": "known",
        "value": KEMP_URL,
        "notes": "Nature paper for Kemp et al. SARS-CoV-2 evolution during treatment of chronic infection."
    },
    {
        "item": "open_full_text",
        "status": "known",
        "value": KEMP_PMC,
        "notes": "PMC full-text mirror useful for methods, clinical timeline, and data availability inspection."
    },
    {
        "item": "reported_timepoints",
        "status": "known",
        "value": "23",
        "notes": "Paper reports whole-genome ultra-deep sequencing across 23 timepoints."
    },
    {
        "item": "reported_duration_days",
        "status": "known",
        "value": "101",
        "notes": "Persistent infection trajectory spans 101 days."
    },
    {
        "item": "host_context",
        "status": "known",
        "value": "immunosuppressed individual",
        "notes": "Case involved immune compromise, including lymphoma history and prior B-cell depletion context."
    },
    {
        "item": "treatment_pressure",
        "status": "known",
        "value": "remdesivir; convalescent plasma",
        "notes": "Two remdesivir courses early, then convalescent plasma, then final unsuccessful treatment course."
    },
    {
        "item": "major_escape_mutations",
        "status": "known",
        "value": "Spike D796H; Spike ΔH69/ΔV70",
        "notes": "Dynamic escape genotype after convalescent plasma, useful for M_v and S_v design."
    },
    {
        "item": "compensatory_structure",
        "status": "known",
        "value": "ΔH69/ΔV70 may compensate D796H infectivity defect",
        "notes": "Useful for M_v because memory should not collapse into simple divergence."
    },
    {
        "item": "raw_reads_or_fastq",
        "status": "to_audit",
        "value": "unknown",
        "notes": "Next script should inspect Data Availability and supplementary files for accessions or downloadable tables."
    },
    {
        "item": "variant_frequency_tables",
        "status": "to_audit",
        "value": "unknown",
        "notes": "Critical for first-pass H_v, S_v, and M_v without full FASTQ processing."
    },
    {
        "item": "ct_or_viral_load_table",
        "status": "to_audit",
        "value": "unknown",
        "notes": "Needed for R_v. If unavailable, R_v must be limited to clinical/treatment-timeline proxies."
    },
    {
        "item": "sample_day_mapping",
        "status": "to_audit",
        "value": "unknown",
        "notes": "Needed to map the 23 timepoints into ordered viral HRSM states."
    }
]

CASE_COLUMNS = [
    "case_id",
    "sample_id",
    "timepoint_index",
    "day_from_first_positive",
    "day_from_admission",
    "sample_type",
    "consensus_sequence_id",
    "variant_table_id",
    "ct_value",
    "viral_load",
    "culture_status",
    "treatment_phase",
    "remdesivir_exposure",
    "convalescent_plasma_exposure",
    "major_spike_state",
    "notes"
]

def main():
    OUT_CHECKLIST.parent.mkdir(parents=True, exist_ok=True)
    OUT_CASE_TEMPLATE.parent.mkdir(parents=True, exist_ok=True)

    checklist = pd.DataFrame(CHECKLIST_ROWS)
    checklist.to_csv(OUT_CHECKLIST, index=False)

    case_template = pd.DataFrame(columns=CASE_COLUMNS)
    case_template.to_csv(OUT_CASE_TEMPLATE, index=False)

    known = checklist[checklist["status"].eq("known")]
    pending = checklist[checklist["status"].eq("to_audit")]

    md = []
    md.append("# Kemp et al. Phase I Data Availability Audit")
    md.append("")
    md.append(f"Generated: {date.today().isoformat()}")
    md.append("")
    md.append("## Role in viral HRSM")
    md.append("")
    md.append(
        "Kemp et al. is currently the leading Phase I SARS-CoV-2 HRSM opener because it reports "
        "23 whole-genome ultra-deep sequencing timepoints across 101 days in an immunosuppressed individual "
        "under remdesivir and convalescent plasma pressure."
    )
    md.append("")
    md.append("## Known anchors")
    md.append("")
    for _, row in known.iterrows():
        md.append(f"- **{row['item']}**: {row['value']}. {row['notes']}")
    md.append("")
    md.append("## Pending audit items")
    md.append("")
    for _, row in pending.iterrows():
        md.append(f"- **{row['item']}**: {row['notes']}")
    md.append("")
    md.append("## Immediate next data step")
    md.append("")
    md.append(
        "Inspect Data Availability, supplementary tables, and repository links for accession-level sequence files "
        "or variant-frequency tables. Do not download large FASTQ files until file sizes and sample mapping are known."
    )
    md.append("")
    md.append("## HRSM relevance")
    md.append("")
    md.append("- H_v can begin from sequence diversity or variant breadth across the 23 timepoints.")
    md.append("- R_v can begin from Ct, viral-load, culture, or treatment-response proxies if available.")
    md.append("- S_v can begin from coherence of the escape genotype and lineage backbone.")
    md.append("- M_v can begin from retained, disappearing, and re-emerging escape genotype structure.")
    md.append("")
    md.append("## Failure guard")
    md.append("")
    md.append(
        "Kemp remains a biological priority, but it becomes a computational priority only if the sample-day mapping "
        "and sequence or variant-frequency data can be recovered."
    )

    OUT_SUMMARY.write_text("\n".join(md), encoding="utf-8")

    print({
        "status": "wrote",
        "checklist": str(OUT_CHECKLIST),
        "summary": str(OUT_SUMMARY),
        "case_template": str(OUT_CASE_TEMPLATE),
        "n_known": len(known),
        "n_pending": len(pending),
    })

    print(checklist.to_string(index=False))

if __name__ == "__main__":
    main()
