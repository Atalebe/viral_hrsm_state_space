from pathlib import Path
import pandas as pd
from datetime import date

ROOT = Path(__file__).resolve().parents[2]

OUT_ANCHORS = ROOT / "metadata" / "kemp_data_anchors.csv"
OUT_SAMPLES = ROOT / "metadata" / "kemp_expected_sra_samples.csv"
OUT_README = ROOT / "metadata" / "kemp_data_anchor_summary.md"

BIOPROJECT = "PRJNA682013"
SAMPLE_START = 16976824
SAMPLE_END = 16976846

anchors = [
    {
        "anchor_type": "paper",
        "label": "Nature article",
        "value": "https://www.nature.com/articles/s41586-021-03291-y",
        "status": "known",
        "notes": "Main paper."
    },
    {
        "anchor_type": "full_text",
        "label": "PMC full text",
        "value": "https://pmc.ncbi.nlm.nih.gov/articles/PMC7610568/",
        "status": "known",
        "notes": "Open full-text copy for methods and data availability inspection."
    },
    {
        "anchor_type": "bioproject",
        "label": "NCBI BioProject",
        "value": BIOPROJECT,
        "status": "known",
        "notes": "Reported BioProject for long-read sequencing data."
    },
    {
        "anchor_type": "sra_samples",
        "label": "NCBI SRA sample accession range",
        "value": f"SAMN{SAMPLE_START}-SAMN{SAMPLE_END}",
        "status": "known",
        "notes": "Reported sample accession range for long-read sequencing data."
    },
    {
        "anchor_type": "github",
        "label": "Steven-Kemp sequence_files",
        "value": "https://github.com/Steven-Kemp/sequence_files",
        "status": "known",
        "notes": "Reported location for short reads and data used to construct figures."
    },
    {
        "anchor_type": "next_required",
        "label": "NCBI run-level query",
        "value": "query BioProject PRJNA682013",
        "status": "pending",
        "notes": "Next script should query NCBI/ENA/SRA metadata for run accessions and file sizes before any download."
    },
    {
        "anchor_type": "next_required",
        "label": "GitHub file inventory",
        "value": "inventory Steven-Kemp/sequence_files",
        "status": "pending",
        "notes": "Next script should list repository files and identify variant-frequency, short-read, and figure-data tables."
    }
]

samples = []
for n in range(SAMPLE_START, SAMPLE_END + 1):
    samples.append({
        "expected_sample_accession": f"SAMN{n}",
        "bioproject": BIOPROJECT,
        "reported_source": "Kemp et al. Data Availability",
        "status": "expected_not_yet_verified",
    })

def main():
    OUT_ANCHORS.parent.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(anchors).to_csv(OUT_ANCHORS, index=False)
    pd.DataFrame(samples).to_csv(OUT_SAMPLES, index=False)

    md = []
    md.append("# Kemp et al. Data Anchors")
    md.append("")
    md.append(f"Generated: {date.today().isoformat()}")
    md.append("")
    md.append("## Confirmed reported anchors")
    md.append("")
    md.append(f"- NCBI BioProject: `{BIOPROJECT}`")
    md.append(f"- Expected SRA sample accession range: `SAMN{SAMPLE_START}` to `SAMN{SAMPLE_END}`")
    md.append("- GitHub repository: `https://github.com/Steven-Kemp/sequence_files`")
    md.append("")
    md.append("## Interpretation")
    md.append("")
    md.append(
        "Kemp et al. is now upgraded from biological candidate to concrete data-anchor candidate. "
        "The next step is still metadata-only: query run-level accessions, file names, file sizes, "
        "and repository inventory before downloading any sequence files."
    )
    md.append("")
    md.append("## HRSM implication")
    md.append("")
    md.append(
        "If the BioProject and GitHub repository expose sample-day mapping and variant-frequency tables, "
        "the first pass can avoid full FASTQ processing and directly build a time-indexed viral HRSM state table."
    )

    OUT_README.write_text('\\n'.join(md), encoding='utf-8')

    print({
        "status": "wrote",
        "anchors": str(OUT_ANCHORS),
        "samples": str(OUT_SAMPLES),
        "summary": str(OUT_README),
        "n_expected_samples": len(samples),
    })

    print(pd.DataFrame(anchors).to_string(index=False))

if __name__ == "__main__":
    main()
