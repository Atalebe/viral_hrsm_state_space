# Kemp et al. Phase I Data Availability Audit

Generated: 2026-06-04

## Role in viral HRSM

Kemp et al. is currently the leading Phase I SARS-CoV-2 HRSM opener because it reports 23 whole-genome ultra-deep sequencing timepoints across 101 days in an immunosuppressed individual under remdesivir and convalescent plasma pressure.

## Known anchors

- **paper_url**: https://www.nature.com/articles/s41586-021-03291-y. Nature paper for Kemp et al. SARS-CoV-2 evolution during treatment of chronic infection.
- **open_full_text**: https://pmc.ncbi.nlm.nih.gov/articles/PMC7610568/. PMC full-text mirror useful for methods, clinical timeline, and data availability inspection.
- **reported_timepoints**: 23. Paper reports whole-genome ultra-deep sequencing across 23 timepoints.
- **reported_duration_days**: 101. Persistent infection trajectory spans 101 days.
- **host_context**: immunosuppressed individual. Case involved immune compromise, including lymphoma history and prior B-cell depletion context.
- **treatment_pressure**: remdesivir; convalescent plasma. Two remdesivir courses early, then convalescent plasma, then final unsuccessful treatment course.
- **major_escape_mutations**: Spike D796H; Spike ΔH69/ΔV70. Dynamic escape genotype after convalescent plasma, useful for M_v and S_v design.
- **compensatory_structure**: ΔH69/ΔV70 may compensate D796H infectivity defect. Useful for M_v because memory should not collapse into simple divergence.

## Pending audit items

- **raw_reads_or_fastq**: Next script should inspect Data Availability and supplementary files for accessions or downloadable tables.
- **variant_frequency_tables**: Critical for first-pass H_v, S_v, and M_v without full FASTQ processing.
- **ct_or_viral_load_table**: Needed for R_v. If unavailable, R_v must be limited to clinical/treatment-timeline proxies.
- **sample_day_mapping**: Needed to map the 23 timepoints into ordered viral HRSM states.

## Immediate next data step

Inspect Data Availability, supplementary tables, and repository links for accession-level sequence files or variant-frequency tables. Do not download large FASTQ files until file sizes and sample mapping are known.

## HRSM relevance

- H_v can begin from sequence diversity or variant breadth across the 23 timepoints.
- R_v can begin from Ct, viral-load, culture, or treatment-response proxies if available.
- S_v can begin from coherence of the escape genotype and lineage backbone.
- M_v can begin from retained, disappearing, and re-emerging escape genotype structure.

## Failure guard

Kemp remains a biological priority, but it becomes a computational priority only if the sample-day mapping and sequence or variant-frequency data can be recovered.