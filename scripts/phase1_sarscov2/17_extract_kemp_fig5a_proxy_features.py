from pathlib import Path
import numpy as np
import pandas as pd
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from viral_hrsm.axes import compute_axis_table

XLSX = ROOT / "data" / "interim" / "kemp_github_small" / "figure_data__Rawdata_forfigures.xlsx"

OUT_RAW = ROOT / "data" / "interim" / "kemp_fig5a_raw.csv"
OUT_FEATURES = ROOT / "data" / "processed" / "kemp_fig5a_proxy_features.csv"
OUT_HRSM = ROOT / "results" / "phase1_sarscov2" / "kemp_fig5a_hrsm_state_table.csv"
OUT_AUDIT = ROOT / "metadata" / "kemp_fig5a_proxy_audit.csv"

MUTATION_COLUMNS_EXPECTED = ["D796H", "del69/70", "W64G", "P330S", "Y200H", "T240I"]

ETA_DAY_MAP = {
    "93ETA*": 93.0,
    "99ETA*": 99.0,
    "100ETA*": 100.0,
    "101ETA*": 101.0,
}

def numeric_clean(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, str):
        s = x.strip().replace("%", "").replace(",", "")
        if s in {"", "NA", "NaN", "nan", "None"}:
            return np.nan
        try:
            return float(s)
        except ValueError:
            return np.nan
    try:
        return float(x)
    except Exception:
        return np.nan

def clean_small(x, eps=1e-10):
    if pd.isna(x):
        return x
    return 0.0 if abs(float(x)) < eps else float(x)

def safe_z(x):
    x = pd.Series(x).astype(float)
    if x.notna().sum() < 2 or np.nanstd(x) == 0:
        return pd.Series(np.zeros(len(x)), index=x.index)
    z = (x - np.nanmean(x)) / np.nanstd(x)
    return z.apply(clean_small)

def row_entropy(values):
    vals = np.asarray(values, dtype=float)
    vals = np.nan_to_num(vals, nan=0.0)
    vals = np.clip(vals, 0, None)

    if vals.max(initial=0) > 1.5:
        vals = vals / 100.0

    total = vals.sum()
    if total <= 0:
        return 0.0

    p = vals / total
    p = p[p > 0]
    h = float(-(p * np.log(p)).sum())
    return clean_small(h)

def cosine_similarity(a, b):
    a = np.nan_to_num(np.asarray(a, dtype=float), nan=0.0)
    b = np.nan_to_num(np.asarray(b, dtype=float), nan=0.0)
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return clean_small(float(np.dot(a, b) / (na * nb)))

def interpolate_ct_by_day(out):
    """
    Interpolate CT on explicit day anchors, then map the interpolated values
    back to every row. Duplicate-day ETA rows receive the same day-level CT.
    """
    day_ct = (
        out.dropna(subset=["day_from_first_positive_proxy"])
        .groupby("day_from_first_positive_proxy", as_index=False)["CT"]
        .mean()
        .sort_values("day_from_first_positive_proxy")
    )

    full_days = pd.DataFrame({
        "day_from_first_positive_proxy": sorted(out["day_from_first_positive_proxy"].dropna().unique())
    })

    full = full_days.merge(day_ct, on="day_from_first_positive_proxy", how="left")
    full["CT_interpolated"] = full["CT"].interpolate(method="linear").ffill().bfill()

    out = out.merge(
        full[["day_from_first_positive_proxy", "CT_interpolated"]],
        on="day_from_first_positive_proxy",
        how="left"
    )

    return out

def day_decay_memory(mut_fraction, days, mutation_cols, tau_days=7.0, max_lag_days=30.0):
    """
    Chronological memory kernel.

    Each row is compared to earlier rows, weighted by exp(-dt/tau_days).
    This is not a final biological memory model. It is a day-aware pilot
    that removes the row-index blind spot.
    """
    vals = mut_fraction[mutation_cols].to_numpy(dtype=float)
    days = np.asarray(days, dtype=float)

    memory_similarity = []
    memory_weight_sum = []

    for i in range(len(vals)):
        if np.isnan(days[i]):
            memory_similarity.append(0.0)
            memory_weight_sum.append(0.0)
            continue

        weighted_sims = []
        weights = []

        for j in range(i):
            if np.isnan(days[j]):
                continue
            dt = days[i] - days[j]
            if dt <= 0 or dt > max_lag_days:
                continue
            w = np.exp(-dt / tau_days)
            sim = cosine_similarity(vals[i], vals[j])
            weighted_sims.append(sim * w)
            weights.append(w)

        if weights:
            memory_similarity.append(clean_small(sum(weighted_sims) / sum(weights)))
            memory_weight_sum.append(clean_small(sum(weights)))
        else:
            memory_similarity.append(0.0)
            memory_weight_sum.append(0.0)

    return pd.Series(memory_similarity), pd.Series(memory_weight_sum)

def main():
    if not XLSX.exists():
        raise FileNotFoundError(f"Missing workbook: {XLSX}")

    df0 = pd.read_excel(XLSX, sheet_name="Fig 5a")
    OUT_RAW.parent.mkdir(parents=True, exist_ok=True)
    df0.to_csv(OUT_RAW, index=False)

    first_col = df0.columns[0]
    df = df0.rename(columns={first_col: "timepoint_label"}).copy()
    df["original_row_order"] = np.arange(len(df))

    mutation_cols = [c for c in MUTATION_COLUMNS_EXPECTED if c in df.columns]
    if not mutation_cols:
        raise ValueError(f"No expected mutation columns found. Available columns: {list(df.columns)}")

    mut = pd.DataFrame()
    for col in mutation_cols:
        mut[col] = df[col].map(numeric_clean)

    df["n_mutation_values_present"] = mut.notna().sum(axis=1)

    keep = df["n_mutation_values_present"].gt(0)
    df = df.loc[keep].reset_index(drop=True)
    mut = mut.loc[keep].reset_index(drop=True)

    mut_fraction = mut.copy()
    if np.nanmax(mut_fraction.to_numpy(dtype=float)) > 1.5:
        mut_fraction = mut_fraction / 100.0

    out = pd.DataFrame(index=df.index)
    out["case_id"] = "Kemp_chronic_infection"
    out["timepoint"] = np.arange(len(df))
    out["original_row_order"] = df["original_row_order"]
    out["timepoint_label"] = df["timepoint_label"].astype(str)

    out["day_from_first_positive_proxy"] = df["timepoint_label"].map(numeric_clean)
    eta_mask = out["day_from_first_positive_proxy"].isna() & out["timepoint_label"].isin(ETA_DAY_MAP)
    out.loc[eta_mask, "day_from_first_positive_proxy"] = out.loc[eta_mask, "timepoint_label"].map(ETA_DAY_MAP)

    out["is_eta_sample"] = out["timepoint_label"].str.contains("ETA", case=False, na=False)
    out["within_day_order"] = out.groupby("day_from_first_positive_proxy").cumcount()

    for col in mutation_cols:
        out[col] = mut_fraction[col].apply(clean_small)

    out["CT"] = df["CT"].map(numeric_clean) if "CT" in df.columns else np.nan

    out = out.sort_values(
        ["day_from_first_positive_proxy", "within_day_order", "original_row_order"],
        na_position="last"
    ).reset_index(drop=True)
    mut_fraction = out[mutation_cols].copy()

    out = interpolate_ct_by_day(out)

    out["diversity"] = mut_fraction.std(axis=1, skipna=True).fillna(0.0).apply(clean_small)
    out["sequence_entropy"] = mut_fraction.apply(row_entropy, axis=1).apply(clean_small)
    out["near_neutral_proxy"] = mut_fraction.gt(0).sum(axis=1)

    # R_v proxies now use interpolated CT and real day differences.
    out["ct_decline_inverse"] = -safe_z(out["CT_interpolated"])

    dt = out["day_from_first_positive_proxy"].diff()
    dct = out["CT_interpolated"].diff()
    ct_slope = dct / dt.replace(0, np.nan)
    out["ct_per_day_change"] = ct_slope.replace([np.inf, -np.inf], np.nan).fillna(0.0).apply(clean_small)
    out["post_nadir_growth"] = (-out["ct_per_day_change"]).apply(clean_small)
    out["culture_positive"] = 0.0

    out["haplotype_concentration"] = mut_fraction.max(axis=1, skipna=True).fillna(0.0).apply(clean_small)

    if {"D796H", "del69/70"}.issubset(mut_fraction.columns):
        out["lineage_backbone"] = mut_fraction[["D796H", "del69/70"]].mean(axis=1).apply(clean_small)
    else:
        out["lineage_backbone"] = mut_fraction.mean(axis=1).apply(clean_small)

    out["fragmentation_inverse"] = (1.0 / (1.0 + mut_fraction.gt(0).sum(axis=1))).apply(clean_small)

    # Chronological memory.
    memory_similarity, memory_weight_sum = day_decay_memory(
        mut_fraction,
        out["day_from_first_positive_proxy"],
        mutation_cols,
        tau_days=7.0,
        max_lag_days=30.0,
    )
    out["lagged_similarity"] = memory_similarity
    out["memory_kernel_weight_sum"] = memory_weight_sum

    if {"D796H", "del69/70"}.issubset(mut_fraction.columns):
        out["retained_escape"] = mut_fraction[["D796H", "del69/70"]].mean(axis=1).apply(clean_small)
        out["compensatory_structure"] = (mut_fraction["D796H"] * mut_fraction["del69/70"]).apply(clean_small)
    else:
        out["retained_escape"] = mut_fraction.mean(axis=1).apply(clean_small)
        out["compensatory_structure"] = 0.0

    out["outcome_persistent"] = 1
    out["source_level"] = "figure_source_reconstruction"
    out["source_sheet"] = "Fig 5a"
    out["memory_kernel_type"] = "chronological_exp_decay_tau7_maxlag30"

    OUT_FEATURES.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_FEATURES, index=False)

    hrsm = compute_axis_table(out)
    OUT_HRSM.parent.mkdir(parents=True, exist_ok=True)
    hrsm.to_csv(OUT_HRSM, index=False)

    audit = pd.DataFrame([{
        "source_workbook": str(XLSX.relative_to(ROOT)),
        "source_sheet": "Fig 5a",
        "n_rows_raw": len(df0),
        "n_rows_retained": len(out),
        "n_rows_removed_as_footer_or_blank": len(df0) - len(out),
        "eta_day_map_applied": True,
        "ct_interpolation": "linear_by_day_then_ffill_bfill",
        "memory_kernel": "chronological_exp_decay_tau7_maxlag30",
        "mutation_columns_used": "|".join(mutation_cols),
        "has_ct": bool(out["CT"].notna().any()),
        "has_ct_interpolated": bool(out["CT_interpolated"].notna().all()),
        "source_level": "figure_source_reconstruction",
        "interpretation_limit": "Pilot HRSM proxy table derived from figure-source workbook, not raw FASTQ or full variant calling."
    }])

    OUT_AUDIT.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(OUT_AUDIT, index=False)

    print({
        "status": "wrote",
        "features": str(OUT_FEATURES),
        "hrsm": str(OUT_HRSM),
        "audit": str(OUT_AUDIT),
        "n_rows_raw": len(df0),
        "n_rows_retained": len(out),
        "n_rows_removed": len(df0) - len(out),
        "eta_day_map_applied": True,
        "ct_interpolation": "linear_by_day_then_ffill_bfill",
        "memory_kernel": "chronological_exp_decay_tau7_maxlag30",
    })

    print(out[[
        "case_id", "timepoint", "timepoint_label", "day_from_first_positive_proxy",
        "is_eta_sample", "CT", "CT_interpolated", "ct_per_day_change",
        "D796H", "del69/70", "sequence_entropy",
        "lagged_similarity", "memory_kernel_weight_sum",
        "retained_escape", "compensatory_structure"
    ]].to_string(index=False))

    print(hrsm[[
        "timepoint", "timepoint_label", "day_from_first_positive_proxy",
        "H_v", "R_v", "S_v", "M_v", "Phi_v"
    ]].to_string(index=False))

if __name__ == "__main__":
    main()
