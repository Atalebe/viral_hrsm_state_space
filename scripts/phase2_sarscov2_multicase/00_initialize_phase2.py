from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

DIRS = [
    "scripts/phase2_sarscov2_multicase",
    "data/raw/phase2_sarscov2_multicase",
    "data/interim/phase2_sarscov2_multicase",
    "data/processed/phase2_sarscov2_multicase",
    "results/phase2_sarscov2_multicase",
    "figures/phase2_sarscov2_multicase",
    "metadata/phase2_sarscov2_multicase",
    "docs/phase2_sarscov2_multicase",
]

REGISTRY = ROOT / "metadata" / "phase2_sarscov2_multicase" / "phase2_dataset_registry.csv"

COLUMNS = [
    "case_id",
    "dataset_name",
    "virus",
    "lineage_or_variant",
    "source_reference",
    "source_url",
    "data_type",
    "n_timepoints",
    "has_day_mapping",
    "has_variant_frequencies",
    "has_ct_or_viral_load",
    "has_treatment_metadata",
    "has_host_context",
    "has_endpoint",
    "admissibility_status",
    "notes",
]

PLACEHOLDER = {
    "case_id": "PLACEHOLDER_CASE",
    "dataset_name": "TO_BE_FILLED",
    "virus": "SARS-CoV-2",
    "lineage_or_variant": "TO_BE_FILLED",
    "source_reference": "TO_BE_FILLED",
    "source_url": "TO_BE_FILLED",
    "data_type": "unknown",
    "n_timepoints": 0,
    "has_day_mapping": "unknown",
    "has_variant_frequencies": "unknown",
    "has_ct_or_viral_load": "unknown",
    "has_treatment_metadata": "unknown",
    "has_host_context": "unknown",
    "has_endpoint": "unknown",
    "admissibility_status": "pending",
    "notes": "Replace with real Phase II candidate after audit",
}

def main():
    for d in DIRS:
        path = ROOT / d
        path.mkdir(parents=True, exist_ok=True)
        keep = path / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")

    if not REGISTRY.exists():
        pd.DataFrame([PLACEHOLDER], columns=COLUMNS).to_csv(REGISTRY, index=False)
        status = "created"
    else:
        df = pd.read_csv(REGISTRY)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df[COLUMNS]
        if df.empty:
            df = pd.DataFrame([PLACEHOLDER], columns=COLUMNS)
        df.to_csv(REGISTRY, index=False)
        status = "validated_existing"

    print({
        "status": status,
        "registry": str(REGISTRY),
        "phase": "phase2_sarscov2_multicase",
    })

if __name__ == "__main__":
    main()
