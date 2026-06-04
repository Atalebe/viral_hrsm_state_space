#!/usr/bin/env bash
set -euo pipefail

echo "[phase1] Starting Kemp Fig. 5a HRSM reproducibility pipeline"

python scripts/phase0/01_score_candidate_datasets.py || true
python scripts/phase1_sarscov2/13_audit_kemp_data_availability.py
python scripts/phase1_sarscov2/14_record_kemp_data_anchors.py
python scripts/phase1_sarscov2/15_inventory_kemp_github.py
python scripts/phase1_sarscov2/16_download_kemp_small_candidate_tables.py
python scripts/phase1_sarscov2/17_extract_kemp_fig5a_proxy_features.py
python scripts/phase1_sarscov2/18_plot_kemp_fig5a_hrsm_trajectory.py
python scripts/phase1_sarscov2/19_classify_kemp_fig5a_transition_states.py
python scripts/phase1_sarscov2/20_plot_transition_states_colored.py
python scripts/phase1_sarscov2/21_compute_phase_velocity.py
python scripts/phase1_sarscov2/22_plot_potential_wells.py
python scripts/phase1_sarscov2/23_summarize_velocity_sensitivity.py
python scripts/phase1_sarscov2/24_plot_velocity_profiles.py
python scripts/phase1_sarscov2/25_build_state_transition_matrix.py
python scripts/phase1_sarscov2/26_plot_transition_heatmap_and_stationary.py
python scripts/phase1_sarscov2/27_generate_phase1_summary_report.py

find metadata results/phase1_sarscov2 figures/phase1_sarscov2 docs logs -type f | sort > metadata/phase1_completed_artifact_inventory.txt

echo "[phase1] Completed"
echo "[phase1] Summary report: docs/phase1_kemp_fig5a_summary_report.md"
echo "[phase1] Artifact inventory: metadata/phase1_completed_artifact_inventory.txt"
