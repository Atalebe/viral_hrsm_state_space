# Phase I SARS-CoV-2 HRSM Workplan

Generated: 2026-06-03

## Purpose

Phase I tests whether persistent SARS-CoV-2 infection can be represented as a viral HRSM state space defined by adaptive reserve, rebound capacity, swarm coherence, and retained evolutionary memory.

The first model comparison is deliberately narrow:

- Markovian current-state model: H_v, R_v, S_v
- Non-Markovian memory model: H_v, R_v, S_v, M_v

## Ranked candidate datasets

### 1. Kemp et al. chronic infection under convalescent plasma

- Paper: Kemp et al., Nature 2021
- URL: https://www.nature.com/articles/s41586-021-03291-y
- Data anchor: Check paper Data Availability and supplementary materials
- Reported timepoints: 23
- Reported duration days: 101
- Data strength: very_high
- Recommended role: primary_phase1_test_case
- Audit note: Best first target. Whole-genome ultra-deep sequencing across 23 timepoints. Strong treatment-pressure structure.

### 2. Schmidt et al. 521-day persistent infection

- Paper: Schmidt et al., npj Genomic Medicine 2025
- URL: https://www.nature.com/articles/s41525-025-00463-x
- Data anchor: ENA PRJEB77414
- Reported timepoints: 5
- Reported duration days: 521
- Data strength: high
- Recommended role: long_memory_case
- Audit note: Excellent memory branch because duration is extreme. Fewer timepoints than Kemp, but long temporal span is useful for M_v.

### 3. Weigang et al. immunosuppressed within-host evolution

- Paper: Weigang et al., Nature Communications 2021
- URL: https://www.nature.com/articles/s41467-021-26602-3
- Data anchor: Check Data Availability, supplementary files, and sequence repositories
- Reported timepoints: to_audit
- Reported duration days: to_audit
- Data strength: medium_high
- Recommended role: immune_escape_validation_case
- Audit note: Good immune-escape trajectory. Needs accession-level check before becoming a primary case.

### 4. Harari et al. chronic infection adaptive evolution drivers

- Paper: Harari et al., Nature Medicine 2022
- URL: https://www.nature.com/articles/s41591-022-01882-4
- Data anchor: Check supplementary tables and public sequence identifiers
- Reported timepoints: multi_case
- Reported duration days: multi_case
- Data strength: medium
- Recommended role: cross_case_context_and_robustness
- Audit note: Important chronic-infection context across 27 infections, but may be less clean as the first mechanistic HRSM case.

### 5. Ghafari et al. community surveillance persistent infections

- Paper: Ghafari et al., Nature 2024
- URL: https://www.nature.com/articles/s41586-024-07029-4
- Data anchor: Check study data access conditions and supplementary metadata
- Reported timepoints: large_surveillance
- Reported duration days: 30_to_60_plus
- Data strength: medium
- Recommended role: background_population_reference
- Audit note: Excellent for population-scale framing, not the first mechanistic within-host HRSM case.

## Phase I execution sequence

1. Verify accession and supplementary data availability for Kemp et al.
2. Build a case-level sample table for the Kemp trajectory.
3. Extract sequence, timepoint, treatment, and abundance proxies.
4. Compute first-pass H_v, R_v, S_v, and M_v axes.
5. Run leakage audit, axis correlation audit, and sampling-duration audit.
6. Compare current-state and memory-augmented models.
7. Repeat only after the first case pipeline is stable.

## Failure rules

- Do not treat dataset priority as proof of data usability.
- Do not use treatment status as both an axis component and a predicted endpoint.
- Do not let M_v collapse into ordinary genetic divergence.
- Do not interpret viral persistence as organism-level homeostasis.
