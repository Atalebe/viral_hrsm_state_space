# Weigang Phase II Raw-Feature Extraction Protocol

## Purpose

This protocol defines the raw-derived feature extraction plan for the Weigang primary swab SARS-CoV-2 trajectory before any FASTQ files are downloaded.

The goal is to convert nine mapped primary swab timepoints into a longitudinal mutation-frequency matrix suitable for viral HRSM testing.

## Scope

Primary trajectory:

- day 0
- day 7
- day 14
- day 42
- day 56
- day 59
- day 71
- day 105
- day 140

Excluded from the first raw-feature branch:

- isolate day 14
- isolate day 105
- isolate day 105 deletion sample

The isolate samples are retained as controls and must not be mixed into the primary swab trajectory.

## Input data

Use submitted paired FASTQ files from ENA for the nine primary swab samples only.

The download plan is recorded in:

```text
metadata/phase2_sarscov2_multicase/weigang_primary_swab_download_plan.csv
