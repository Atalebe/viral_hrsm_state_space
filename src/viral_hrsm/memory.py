import numpy as np
import pandas as pd


def exponential_kernel(lags, decay=0.5):
    lags = np.asarray(lags, dtype=float)
    weights = np.exp(-decay * lags)
    if weights.sum() == 0:
        return weights
    return weights / weights.sum()


def add_lagged_memory(df, group_col, time_col, value_cols, max_lag=3, decay=0.5):
    """
    Add simple lagged memory columns within each trajectory.

    This is a scaffold function. It assumes rows are already valid ordered viral states.
    """
    out = df.copy()
    out = out.sort_values([group_col, time_col]).reset_index(drop=True)
    weights = exponential_kernel(np.arange(1, max_lag + 1), decay=decay)

    for value_col in value_cols:
        mem_col = f"{value_col}_memory"
        out[mem_col] = 0.0
        for _, idx in out.groupby(group_col).groups.items():
            sub = out.loc[idx, value_col].astype(float).to_numpy()
            mem = np.zeros(len(sub))
            for i in range(len(sub)):
                vals = []
                ws = []
                for lag, w in zip(range(1, max_lag + 1), weights):
                    j = i - lag
                    if j >= 0:
                        vals.append(sub[j])
                        ws.append(w)
                mem[i] = np.average(vals, weights=ws) if vals else 0.0
            out.loc[idx, mem_col] = mem
    return out
