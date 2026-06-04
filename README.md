# Viral HRSM State Space

Initial scaffold for a phased Homeostatic Reserve, Recoverability, Stability, and Memory vector-space programme for viral persistence dynamics.

This repository is scaffold-only. It provides the directory layout, configuration files, dataset registry templates, and starter scripts for Phase 0 and Phase I.

## Core state vector

\[
\phi_v(t) = [H_v(t), R_v(t), S_v(t), M_v(t)]
\]

Where:

- `H_v`: viral adaptive reserve
- `R_v`: rebound or recoverability after perturbation
- `S_v`: swarm coherence or stability
- `M_v`: retained evolutionary memory

## Phase order

1. Phase 0, branch charter and dataset audit
2. Phase I, SARS-CoV-2 persistent infection
3. Phase II, HIV longitudinal memory and reservoir persistence
4. Phase III, HCV treatment, relapse, and reinfection
5. Phase IV, influenza antigenic drift
6. Phase V, phage experimental evolution
7. Cross-viral synthesis

## Immediate execution path

Start with:

```bash
python scripts/phase0/00_initialize_registry.py
python scripts/phase0/01_score_candidate_datasets.py
python scripts/phase1_sarscov2/10_build_case_table.py
python scripts/phase1_sarscov2/20_compute_sarscov2_hrsm_axes.py
python scripts/phase1_sarscov2/30_memory_model_baseline.py
```

The scripts are safe starters. They generate templates and validate inputs, but they do not download protected or third-party datasets.

# Viral HRSM State Space

A reproducible pilot repository for testing a viral Homeostatic Reserve, Recoverability, Stability, and Memory state-space framework on persistent SARS-CoV-2 infection.

This repository currently contains a Phase I figure-source reconstruction of the Kemp et al. chronic SARS-CoV-2 infection trajectory. The analysis reconstructs a time-indexed viral HRSM pilot from Fig. 5a source data, then applies chronological correction, memory-kernel construction, state classification, velocity diagnostics, potential-well mapping, daily-collapsed transition matrices, and stationary-distribution analysis.

## Status

Phase I is locked as a figure-source reconstruction.

Current final audit:

- HRSM rows: 20
- Transition rows: 20
- Daily-collapsed rows: 16
- Figures listed: 9
- Missing figures: 0
- Stationary terminal states: retained_escape_state and high_memory_escape_return, each with probability 0.5

## Scientific boundary

This is not a raw sequencing analysis. It is a figure-source reconstruction used for method validation and hypothesis generation. The results should not be described as universal viral laws, clinical classes, or population-level transition probabilities.

## Core state vector

The viral HRSM state vector is:

\[
\phi_v(t) = [H_v(t), R_v(t), S_v(t), M_v(t)]
\]

where:

- `H_v`: adaptive reserve
- `R_v`: CT-derived rebound/recoverability proxy
- `S_v`: swarm coherence proxy
- `M_v`: chronological memory proxy

## Main Phase I result

The daily-corrected Kemp trajectory separates into:

1. low_escape_baseline
2. coherent_escape_surge
3. alternate_diversity_state
4. retained_escape_state
5. high_memory_escape_return

The strongest pilot contrast is between alternate diversity, where reserve-like diversity is present but memory/coherence are weak, and the retained/high-memory escape states, where D796H plus ΔH69/ΔV70 structure returns with positive memory and coherence.

## Reproduce Phase I

Create the environment:

```bash
conda env create -f environment.yml
conda activate viral_hrsm
