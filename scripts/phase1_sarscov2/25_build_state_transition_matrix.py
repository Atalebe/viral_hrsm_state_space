from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

INPUT = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_transition_states.csv"

OUT_EDGES_SAMPLE = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_state_transition_edges_sample_order.csv"
OUT_COUNTS_SAMPLE = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_state_transition_count_matrix_sample_order.csv"
OUT_PROBS_SAMPLE = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_state_transition_probability_matrix_sample_order.csv"

OUT_DAILY_STATES = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_collapsed_daily_states.csv"
OUT_EDGES_DAILY = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_state_transition_edges_daily_collapsed.csv"
OUT_COUNTS_DAILY = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_state_transition_count_matrix_daily_collapsed.csv"
OUT_PROBS_DAILY = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_state_transition_probability_matrix_daily_collapsed.csv"
OUT_SUMMARY = ROOT / "metadata" / "kemp_fig5a_state_transition_matrix_summary.csv"

STATE_PRIORITY = {
    "low_escape_baseline": 0,
    "intermediate_transition": 1,
    "alternate_diversity_state": 2,
    "coherent_escape_surge": 3,
    "retained_escape_state": 4,
    "high_memory_escape_return": 5,
}

def build_edges(df):
    edges = []
    for i in range(1, len(df)):
        prev = df.iloc[i - 1]
        cur = df.iloc[i]
        edges.append({
            "from_timepoint_label": prev["timepoint_label"],
            "to_timepoint_label": cur["timepoint_label"],
            "from_day": prev["day_from_first_positive_proxy"],
            "to_day": cur["day_from_first_positive_proxy"],
            "dt_raw": cur["day_from_first_positive_proxy"] - prev["day_from_first_positive_proxy"],
            "same_day_step": cur["day_from_first_positive_proxy"] == prev["day_from_first_positive_proxy"],
            "from_state": prev["transition_state"],
            "to_state": cur["transition_state"],
        })
    return pd.DataFrame(edges)

def matrices_from_edges(edge_df, states):
    counts = pd.crosstab(edge_df["from_state"], edge_df["to_state"])
    counts = counts.reindex(index=states, columns=states, fill_value=0)
    probs = counts.div(counts.sum(axis=1).replace(0, pd.NA), axis=0).fillna(0.0)
    return counts, probs

def collapse_same_day(df):
    """
    Collapse multiple rows from the same calendar day into one daily state.

    Rule:
    - use the state with highest predefined biological priority on that day;
    - if tied, keep the latest within-day row;
    - record all sample labels and states for audit.
    """
    daily_rows = []

    for day, sub in df.groupby("day_from_first_positive_proxy", sort=True):
        sub = sub.sort_values(["within_day_order", "timepoint"]).copy()
        sub["state_priority"] = sub["transition_state"].map(STATE_PRIORITY).fillna(-1)

        # Highest-priority state wins; latest sample breaks ties.
        chosen = sub.sort_values(["state_priority", "within_day_order", "timepoint"]).iloc[-1]

        row = chosen.to_dict()
        row["daily_n_samples"] = len(sub)
        row["daily_sample_labels"] = "|".join(sub["timepoint_label"].astype(str))
        row["daily_states_observed"] = "|".join(sub["transition_state"].astype(str))
        row["daily_collapse_rule"] = "highest_state_priority_then_latest_within_day"
        daily_rows.append(row)

    daily = pd.DataFrame(daily_rows)
    daily = daily.sort_values("day_from_first_positive_proxy").reset_index(drop=True)
    return daily

def summarize(probs, counts, states, label):
    rows = []
    for state in states:
        outgoing_n = float(counts.loc[state].sum()) if state in counts.index else 0.0
        if outgoing_n > 0:
            top_to = probs.loc[state].idxmax()
            top_prob = float(probs.loc[state, top_to])
        else:
            top_to = ""
            top_prob = 0.0

        rows.append({
            "matrix_type": label,
            "state": state,
            "n_outgoing_transitions": outgoing_n,
            "most_likely_next_state": top_to,
            "most_likely_next_probability": top_prob,
        })
    return pd.DataFrame(rows)

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing transition-state table: {INPUT}")

    df = pd.read_csv(INPUT)
    df = df.sort_values(["day_from_first_positive_proxy", "within_day_order", "timepoint"]).reset_index(drop=True)

    states = [s for s, _ in sorted(STATE_PRIORITY.items(), key=lambda kv: kv[1]) if s in set(df["transition_state"])]

    sample_edges = build_edges(df)
    sample_counts, sample_probs = matrices_from_edges(sample_edges, states)

    daily = collapse_same_day(df)
    daily_edges = build_edges(daily)
    daily_counts, daily_probs = matrices_from_edges(daily_edges, states)

    OUT_EDGES_SAMPLE.parent.mkdir(parents=True, exist_ok=True)

    sample_edges.to_csv(OUT_EDGES_SAMPLE, index=False)
    sample_counts.to_csv(OUT_COUNTS_SAMPLE)
    sample_probs.to_csv(OUT_PROBS_SAMPLE)

    daily.to_csv(OUT_DAILY_STATES, index=False)
    daily_edges.to_csv(OUT_EDGES_DAILY, index=False)
    daily_counts.to_csv(OUT_COUNTS_DAILY)
    daily_probs.to_csv(OUT_PROBS_DAILY)

    summary = pd.concat([
        summarize(sample_probs, sample_counts, states, "sample_order"),
        summarize(daily_probs, daily_counts, states, "daily_collapsed"),
    ], ignore_index=True)
    summary.to_csv(OUT_SUMMARY, index=False)

    print({
        "status": "wrote",
        "sample_edges": str(OUT_EDGES_SAMPLE),
        "daily_states": str(OUT_DAILY_STATES),
        "daily_edges": str(OUT_EDGES_DAILY),
        "daily_probs": str(OUT_PROBS_DAILY),
        "summary": str(OUT_SUMMARY),
        "n_sample_rows": len(df),
        "n_daily_rows": len(daily),
        "n_sample_edges": len(sample_edges),
        "n_daily_edges": len(daily_edges),
        "states": states,
    })

    print("\nDAILY COLLAPSED STATES")
    print(daily[[
        "day_from_first_positive_proxy",
        "timepoint_label",
        "transition_state",
        "daily_n_samples",
        "daily_sample_labels",
        "daily_states_observed"
    ]].to_string(index=False))

    print("\nDAILY COLLAPSED EDGES")
    print(daily_edges.to_string(index=False))

    print("\nDAILY COLLAPSED PROBABILITY MATRIX")
    print(daily_probs.to_string())

    print("\nSUMMARY")
    print(summary.to_string(index=False))

if __name__ == "__main__":
    main()
