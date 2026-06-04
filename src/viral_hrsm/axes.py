import numpy as np
import pandas as pd
from scipy.stats import zscore


def safe_zscore(series):
    x = pd.to_numeric(series, errors="coerce")
    if x.notna().sum() < 2 or np.nanstd(x) == 0:
        return pd.Series(np.zeros(len(x)), index=series.index)
    return pd.Series(zscore(x, nan_policy="omit"), index=series.index).fillna(0.0)


def compute_axis_table(df, config=None):
    """
    Compute starter viral HRSM axes from generic proxy columns.

    Expected optional columns:
    - diversity
    - sequence_entropy
    - near_neutral_proxy
    - ct_decline_inverse
    - post_nadir_growth
    - culture_positive
    - haplotype_concentration
    - lineage_backbone
    - fragmentation_inverse
    - lagged_similarity
    - retained_escape
    - compensatory_structure

    Missing columns are treated as zero contribution.
    """
    out = df.copy()

    def col(name):
        if name in out.columns:
            return safe_zscore(out[name])
        return pd.Series(np.zeros(len(out)), index=out.index)

    out["H_v"] = col("diversity") + col("sequence_entropy") + col("near_neutral_proxy")
    out["R_v"] = col("ct_decline_inverse") + col("post_nadir_growth") + col("culture_positive")
    out["S_v"] = col("haplotype_concentration") + col("lineage_backbone") + col("fragmentation_inverse")
    out["M_v"] = col("lagged_similarity") + col("retained_escape") + col("compensatory_structure")

    for axis in ["H_v", "R_v", "S_v", "M_v"]:
        out[axis] = safe_zscore(out[axis])

    out["Phi_v"] = out[["H_v", "R_v", "S_v", "M_v"]].mean(axis=1)
    return out
