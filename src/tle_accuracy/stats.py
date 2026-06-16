"""Summary statistics, growth-law fits, and group tests."""

from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

from .bootstrap import bootstrap_ci


def summarize_errors(df: pd.DataFrame, value_col: str = "position_error_km") -> pd.DataFrame:
    rows = []
    for (orbit_type, horizon), group in df.groupby(["orbit_type", "horizon_days"], dropna=False):
        values = group[value_col].dropna().to_numpy(dtype=float)
        if values.size == 0:
            continue
        rows.append(
            {
                "orbit_type": orbit_type,
                "horizon_days": horizon,
                "n": int(values.size),
                "mean_km": float(np.mean(values)),
                "std_km": float(np.std(values, ddof=1)) if values.size > 1 else 0.0,
                "median_km": float(np.median(values)),
                "rmse_km": float(np.sqrt(np.mean(values**2))),
                "q25_km": float(np.quantile(values, 0.25)),
                "q75_km": float(np.quantile(values, 0.75)),
                "q95_km": float(np.quantile(values, 0.95)),
                "min_km": float(np.min(values)),
                "max_km": float(np.max(values)),
            }
        )
    return pd.DataFrame(rows).sort_values(["orbit_type", "horizon_days"]) if rows else pd.DataFrame()


def bootstrap_table(
    df: pd.DataFrame,
    value_col: str = "position_error_km",
    statistics: list[str] | None = None,
    n_bootstrap: int = 5000,
    confidence: float = 0.95,
    seed: int = 20240609,
) -> pd.DataFrame:
    statistics = statistics or ["mean", "median", "rmse"]
    rows = []
    for (orbit_type, horizon), group in df.groupby(["orbit_type", "horizon_days"], dropna=False):
        values = group[value_col].dropna().to_numpy(dtype=float)
        if values.size < 2:
            continue
        for offset, statistic in enumerate(statistics):
            result = bootstrap_ci(values, statistic, n_bootstrap, confidence, seed + offset)
            rows.append({"orbit_type": orbit_type, "horizon_days": horizon, **result.__dict__})
    return pd.DataFrame(rows).sort_values(["statistic", "orbit_type", "horizon_days"]) if rows else pd.DataFrame()


def fit_growth_laws(
    summary: pd.DataFrame,
    statistic_col: str = "median_km",
) -> pd.DataFrame:
    """Fit linear and power-law error growth by orbit type."""

    rows = []
    if summary.empty:
        return pd.DataFrame()
    for orbit_type, group in summary.groupby("orbit_type"):
        group = group.sort_values("horizon_days")
        x = group["horizon_days"].to_numpy(dtype=float)
        y = group[statistic_col].to_numpy(dtype=float)
        mask = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
        x, y = x[mask], y[mask]
        if x.size < 2:
            continue

        linear_coef = np.polyfit(x, y, deg=1)
        linear_pred = np.polyval(linear_coef, x)
        rows.append(
            {
                "orbit_type": orbit_type,
                "model": "linear",
                "statistic": statistic_col,
                "intercept": float(linear_coef[1]),
                "slope": float(linear_coef[0]),
                "a": np.nan,
                "b": np.nan,
                "r2": _r2(y, linear_pred),
            }
        )
        if x.size >= 2:
            power_coef = np.polyfit(np.log(x), np.log(y), deg=1)
            b = float(power_coef[0])
            a = float(np.exp(power_coef[1]))
            power_pred = a * np.power(x, b)
            rows.append(
                {
                    "orbit_type": orbit_type,
                    "model": "power_law",
                    "statistic": statistic_col,
                    "intercept": np.nan,
                    "slope": np.nan,
                    "a": a,
                    "b": b,
                    "r2": _r2(y, power_pred),
                }
            )
    return pd.DataFrame(rows)


def group_tests(
    df: pd.DataFrame,
    value_col: str = "position_error_km",
    min_n: int = 5,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run ANOVA/Kruskal-Wallis and pairwise Mann-Whitney tests per horizon."""

    omnibus_rows = []
    pairwise_rows = []
    for horizon, horizon_df in df.groupby("horizon_days"):
        groups = {
            orbit_type: group[value_col].dropna().to_numpy(dtype=float)
            for orbit_type, group in horizon_df.groupby("orbit_type")
        }
        groups = {key: value for key, value in groups.items() if value.size >= min_n}
        if len(groups) < 2:
            continue
        arrays = list(groups.values())
        labels = list(groups.keys())

        try:
            anova_stat, anova_p = scipy_stats.f_oneway(*arrays)
        except ValueError:
            anova_stat, anova_p = np.nan, np.nan
        try:
            kruskal_stat, kruskal_p = scipy_stats.kruskal(*arrays)
        except ValueError:
            kruskal_stat, kruskal_p = np.nan, np.nan
        try:
            levene_stat, levene_p = scipy_stats.levene(*arrays, center="median")
        except ValueError:
            levene_stat, levene_p = np.nan, np.nan

        omnibus_rows.append(
            {
                "horizon_days": horizon,
                "orbit_types": ",".join(labels),
                "n_groups": len(groups),
                "anova_F": float(anova_stat),
                "anova_p": float(anova_p),
                "kruskal_H": float(kruskal_stat),
                "kruskal_p": float(kruskal_p),
                "levene_W": float(levene_stat),
                "levene_p": float(levene_p),
            }
        )

        raw_pairwise = []
        for left, right in combinations(labels, 2):
            stat, p_value = scipy_stats.mannwhitneyu(groups[left], groups[right], alternative="two-sided")
            raw_pairwise.append(
                {
                    "horizon_days": horizon,
                    "orbit_type_a": left,
                    "orbit_type_b": right,
                    "mannwhitney_U": float(stat),
                    "p_raw": float(p_value),
                    "median_a_km": float(np.median(groups[left])),
                    "median_b_km": float(np.median(groups[right])),
                }
            )
        pairwise_rows.extend(_holm_adjust(raw_pairwise))

    return pd.DataFrame(omnibus_rows), pd.DataFrame(pairwise_rows)


def _holm_adjust(rows: list[dict]) -> list[dict]:
    if not rows:
        return rows
    order = np.argsort([row["p_raw"] for row in rows])
    adjusted = [None] * len(rows)
    running_max = 0.0
    m = len(rows)
    for rank, idx in enumerate(order):
        row = rows[idx].copy()
        p_adj = min(1.0, (m - rank) * row["p_raw"])
        running_max = max(running_max, p_adj)
        row["p_holm"] = running_max
        adjusted[idx] = row
    return adjusted


def _r2(observed: np.ndarray, predicted: np.ndarray) -> float:
    ss_res = float(np.sum((observed - predicted) ** 2))
    ss_tot = float(np.sum((observed - np.mean(observed)) ** 2))
    return float(1.0 - ss_res / ss_tot) if ss_tot > 0.0 else np.nan
