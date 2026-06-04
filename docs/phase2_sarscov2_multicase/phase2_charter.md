# Phase II SARS-CoV-2 Multi-Case HRSM Charter

## Purpose

Phase II tests whether the Phase I Kemp Fig. 5a viral HRSM topology generalizes beyond a single figure-source reconstruction.

The target is not to prove a universal viral law. The target is narrower: determine whether persistent SARS-CoV-2 infections from additional patients or cohorts reproduce any part of the Phase I structure, especially the separation between alternate diversity and retained escape or high-memory return.

## Phase I result being tested

Phase I identified five provisional states:

1. low_escape_baseline
2. coherent_escape_surge
3. alternate_diversity_state
4. retained_escape_state
5. high_memory_escape_return

The daily-collapsed transition matrix identified a terminal two-state closed class between retained_escape_state and high_memory_escape_return.

## Phase II test question

Does this topology recur across independent persistent SARS-CoV-2 trajectories, or is it specific to the Kemp case?

## Acceptable input types

Phase II can accept any of the following:

1. longitudinal variant-frequency tables
2. longitudinal mutation-frequency Excel workbooks
3. sample-by-mutation matrices
4. VCF-derived mutation tables
5. consensus-sequence trajectories with extracted mutation features
6. raw read data only after metadata and file-size audit

## Minimum admissibility

A Phase II case must have:

- at least three ordered timepoints
- explicit day or date mapping
- at least one mutation-frequency or sequence-derived feature set
- enough metadata to distinguish within-host trajectory from unrelated population samples

## High-quality case

A high-quality Phase II case has:

- at least five ordered timepoints
- mutation-frequency information
- treatment or immune-pressure metadata
- an abundance proxy such as Ct, viral load, or culture status
- documented persistence, rebound, clearance, or unresolved endpoint

## Phase II comparison targets

Each candidate case should be tested for:

- whether it reproduces the Phase I state topology
- whether alternate diversity separates from retained escape memory
- whether daily-collapsed transition matrices show terminal or recurrent state classes
- whether memory improves residual fit relative to a current-state baseline
- whether velocity and potential-well diagnostics remain stable after same-day collapse

## Failure guard

Phase II must not treat unrelated population consensus genomes as within-host trajectories. Each case must have ordered timepoints and explicit day or date mapping.

## Interpretation boundary

Phase II is a generalization test. It should compare topologies, transition structures, and memory contribution across cases. It should not assume that BA.5, JN.1, Omicron, or any lineage automatically follows the Kemp topology.
