.PHONY: phase1 report inventory clean-pyc

phase1:
	bash scripts/run_phase1_kemp_pipeline.sh

report:
	python scripts/phase1_sarscov2/27_generate_phase1_summary_report.py

inventory:
	find metadata results/phase1_sarscov2 figures/phase1_sarscov2 docs logs -type f | sort > metadata/phase1_completed_artifact_inventory.txt
	wc -l metadata/phase1_completed_artifact_inventory.txt

clean-pyc:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
