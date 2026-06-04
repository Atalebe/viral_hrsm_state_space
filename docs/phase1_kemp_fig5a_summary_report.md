# Phase I SARS-CoV-2 HRSM Pilot Summary

Generated: 2026-06-04

## Scope

This report summarizes the Phase I figure-source reconstruction of the Kemp et al. chronic SARS-CoV-2 infection trajectory. The analysis uses the Fig. 5a workbook sheet from the Kemp figure-source data and should not be described as raw FASTQ or full variant-calling analysis.

## Data status

- Retained biological rows: 20
- Removed footer or blank rows: 3
- Source level: figure-source reconstruction
- Main mutation pair: D796H and ΔH69/ΔV70
- CT values: interpolated by explicit day anchors for pilot rebound proxy construction
- Memory kernel: chronological exponential decay, tau = 7 days, max lag = 30 days

## Main result

The daily-corrected HRSM trajectory separates the chronic infection into a low-escape baseline, a coherent escape surge at day 82, an alternate diversity state between days 89 and 95, and a retained escape/high-memory return cycle from day 98 onward.

The strongest HRSM contrast is between the alternate diversity state and the retained escape/high-memory return states. The alternate diversity state has high reserve-like diversity but weak or negative memory/coherence, while the retained escape and high-memory return states recover positive memory and coherence around the D796H plus ΔH69/ΔV70 structure.

## Transition-state summary

| transition_state          |   n |   first_day |   last_day |   mean_escape |    mean_H |    mean_R |   mean_S |    mean_M |   mean_Phi |
|:--------------------------|----:|------------:|-----------:|--------------:|----------:|----------:|---------:|----------:|-----------:|
| low_escape_baseline       |   6 |           1 |         66 |    0.00351667 | -1.4334   |  0.164675 | -0.7733  | -0.89602  |  -0.734511 |
| intermediate_transition   |   2 |          55 |         86 |    0.0141     |  0.100269 |  0.353476 | -0.90864 | -0.597477 |  -0.263093 |
| coherent_escape_surge     |   1 |          82 |         82 |    0.9126     |  0.564727 |  0.461743 |  1.54767 |  1.59504  |   1.0423   |
| alternate_diversity_state |   4 |          89 |         95 |    0.0438125  |  0.785961 |  1.2637   | -0.26951 | -0.60985  |   0.292575 |
| retained_escape_state     |   5 |          98 |        101 |    0.67663    |  0.680403 | -0.747426 |  0.69877 |  0.903314 |   0.383765 |
| high_memory_escape_return |   2 |          99 |        101 |    0.836425   |  0.644637 | -1.73721  |  1.2468  |  1.44943  |   0.400915 |

## Daily-collapsed transition probability matrix

| from_state                |   low_escape_baseline |   intermediate_transition |   alternate_diversity_state |   coherent_escape_surge |   retained_escape_state |   high_memory_escape_return |
|:--------------------------|----------------------:|--------------------------:|----------------------------:|------------------------:|------------------------:|----------------------------:|
| low_escape_baseline       |              0.666667 |                  0.166667 |                    0        |                0.166667 |                0        |                           0 |
| intermediate_transition   |              0.5      |                  0        |                    0.5      |                0        |                0        |                           0 |
| alternate_diversity_state |              0        |                  0        |                    0.666667 |                0        |                0.333333 |                           0 |
| coherent_escape_surge     |              0        |                  1        |                    0        |                0        |                0        |                           0 |
| retained_escape_state     |              0        |                  0        |                    0        |                0        |                0        |                           1 |
| high_memory_escape_return |              0        |                  0        |                    0        |                0        |                1        |                           0 |

## Stationary distribution

| state                     |   stationary_probability |
|:--------------------------|-------------------------:|
| retained_escape_state     |                      0.5 |
| high_memory_escape_return |                      0.5 |
| intermediate_transition   |                      0   |
| low_escape_baseline       |                      0   |
| coherent_escape_surge     |                      0   |
| alternate_diversity_state |                      0   |

The stationary distribution is computed by solving the linear stationary equations, not by power iteration. This matters because the daily-collapsed matrix contains a deterministic two-state terminal cycle. The stationary mass is therefore split evenly between retained_escape_state and high_memory_escape_return.

## Velocity summary

The corrected velocity engine reports step-normalized velocity for ordered sample contrasts and calendar-day velocity only where positive day gaps exist. This prevents same-day samples from creating artificial velocity explosions.

| transition_state          |   n |   first_day |   last_day |   mean_step_velocity |   median_step_velocity |   max_step_velocity |   mean_calendar_velocity |   median_calendar_velocity |   max_calendar_velocity |   mean_step_acceleration |   max_step_acceleration |   mean_calendar_acceleration |   max_calendar_acceleration |   same_day_steps |
|:--------------------------|----:|------------:|-----------:|---------------------:|-----------------------:|--------------------:|-------------------------:|---------------------------:|------------------------:|-------------------------:|------------------------:|-----------------------------:|----------------------------:|-----------------:|
| low_escape_baseline       |   6 |           1 |         66 |              1.22543 |               1.2877   |             2.64123 |                 0.24876  |                   0.17693  |                0.660306 |                 0.223085 |                2.39104  |                   0.0103197  |                  0.163339   |                0 |
| intermediate_transition   |   2 |          55 |         86 |              2.3871  |               2.3871   |             3.31423 |                 0.560277 |                   0.560277 |                0.828558 |                -0.321269 |                0.362429 |                   0.0770746  |                  0.139652   |                0 |
| coherent_escape_surge     |   1 |          82 |         82 |              4.3192  |               4.3192   |             4.3192  |                 0.26995  |                   0.26995  |                0.26995  |                 2.84135  |                2.84135  |                   0.00847498 |                  0.00847498 |                0 |
| alternate_diversity_state |   4 |          89 |         95 |              1.0632  |               1.20199  |             1.68761 |                 0.389116 |                   0.35633  |                0.843806 |                -0.406655 |                1.5264   |                   0.0831466  |                  0.421903   |                1 |
| retained_escape_state     |   5 |          98 |        101 |              1.53364 |               0.585904 |             3.67008 |                 0.46305  |                   0.518676 |                1.22336  |                 0.170247 |                1.98247  |                   0.406136   |                  0.573215   |                2 |
| high_memory_escape_return |   2 |          99 |        101 |              1.56137 |               1.56137  |             1.70445 |                 0.852226 |                   0.852226 |                1.70445  |                -0.560277 |                0.845076 |                   0.481091   |                  0.481091   |                1 |

## Potential-well summary

| transition_state          |   n |   first_day |   last_day |    mean_U |      min_U |       max_U |   mean_Phi |   mean_escape |   mean_step_velocity |   median_step_velocity |   max_step_velocity |   mean_calendar_velocity |   median_calendar_velocity |   max_calendar_velocity |   same_day_steps |
|:--------------------------|----:|------------:|-----------:|----------:|-----------:|------------:|-----------:|--------------:|---------------------:|-----------------------:|--------------------:|-------------------------:|---------------------------:|------------------------:|-----------------:|
| low_escape_baseline       |   6 |           1 |         66 |  0.734511 |  0.39311   |  0.8921     |  -0.734511 |    0.00351667 |              1.22543 |               1.2877   |             2.64123 |                 0.24876  |                   0.17693  |                0.660306 |                0 |
| intermediate_transition   |   2 |          55 |         86 |  0.263093 |  0.0806735 |  0.445512   |  -0.263093 |    0.0141     |              2.3871  |               2.3871   |             3.31423 |                 0.560277 |                   0.560277 |                0.828558 |                0 |
| coherent_escape_surge     |   1 |          82 |         82 | -1.0423   | -1.0423    | -1.0423     |   1.0423   |    0.9126     |              4.3192  |               4.3192   |             4.3192  |                 0.26995  |                   0.26995  |                0.26995  |                0 |
| alternate_diversity_state |   4 |          89 |         95 | -0.292575 | -0.665342  | -0.0589718  |   0.292575 |    0.0438125  |              1.0632  |               1.20199  |             1.68761 |                 0.389116 |                   0.35633  |                0.843806 |                1 |
| retained_escape_state     |   5 |          98 |        101 | -0.383765 | -0.555965  | -0.215962   |   0.383765 |    0.67663    |              1.53364 |               0.585904 |             3.67008 |                 0.46305  |                   0.518676 |                1.22336  |                2 |
| high_memory_escape_return |   2 |          99 |        101 | -0.400915 | -0.796481  | -0.00534956 |   0.400915 |    0.836425   |              1.56137 |               1.56137  |             1.70445 |                 0.852226 |                   0.852226 |                1.70445  |                1 |

## Figures

- `figures/phase1_sarscov2/kemp_fig5a_colored_hrsm_axes_over_days.png`
- `figures/phase1_sarscov2/kemp_fig5a_colored_memory_stability_states.png`
- `figures/phase1_sarscov2/kemp_fig5a_colored_escape_memory_over_days.png`
- `figures/phase1_sarscov2/kemp_fig5a_velocity_profiles_over_days.png`
- `figures/phase1_sarscov2/kemp_fig5a_daily_collapsed_transition_heatmap.png`
- `figures/phase1_sarscov2/kemp_fig5a_daily_collapsed_stationary_distribution.png`
- `figures/phase1_sarscov2/kemp_fig5a_potential_well_over_days.png`
- `figures/phase1_sarscov2/kemp_fig5a_potential_vs_escape_pair.png`
- `figures/phase1_sarscov2/kemp_fig5a_potential_vs_step_velocity.png`

## Interpretation boundary

This Phase I result is a pilot topology from one figure-source reconstruction. It supports continued testing of a viral HRSM memory branch, but it does not prove a universal viral attractor, does not establish clinical phenotype classes, and does not replace raw sequencing analysis.