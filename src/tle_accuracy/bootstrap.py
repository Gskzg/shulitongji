"""Bootstrap confidence intervals, including percentile and BCa."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy.stats import norm


Statistic = Callable[[np.ndarray], float]


def mean_stat(values: np.ndarray) -> float:
    return float(np.mean(values))


def median_stat(values: np.ndarray) -> float:
    return float(np.median(values))


def rmse_stat(values: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(values))))


STATISTICS: dict[str, Statistic] = {
    "mean": mean_stat,
    "median": median_stat,
    "rmse": rmse_stat,
}


@dataclass(frozen=True)
class BootstrapResult:
    statistic: str
    estimate: float
    n: int
    n_bootstrap: int
    gaussian_low: float
    gaussian_high: float
    percentile_low: float
    percentile_high: float
    bca_low: float
    bca_high: float
    bootstrap_se: float


def bootstrap_ci(
    values: np.ndarray,
    statistic_name: str = "mean",
    n_bootstrap: int = 5000,
    confidence: float = 0.95,
    seed: int = 20240609,
) -> BootstrapResult:
    """Compute Gaussian, percentile, and BCa confidence intervals."""

    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if statistic_name not in STATISTICS:
        raise ValueError(f"Unknown statistic: {statistic_name}")
    if values.size < 2:
        raise ValueError("At least two observations are required for bootstrap intervals")

    statistic = STATISTICS[statistic_name]
    estimate = statistic(values)
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, values.size, size=(n_bootstrap, values.size))
    bootstrap_stats = np.apply_along_axis(statistic, 1, values[indices])
    alpha = 1.0 - confidence
    lower_q, upper_q = alpha / 2.0, 1.0 - alpha / 2.0

    percentile_low, percentile_high = np.quantile(bootstrap_stats, [lower_q, upper_q])
    bootstrap_se = float(np.std(bootstrap_stats, ddof=1))
    z = norm.ppf(upper_q)
    gaussian_low = estimate - z * bootstrap_se
    gaussian_high = estimate + z * bootstrap_se
    bca_low, bca_high = _bca_interval(values, estimate, bootstrap_stats, statistic, lower_q, upper_q)

    return BootstrapResult(
        statistic=statistic_name,
        estimate=estimate,
        n=int(values.size),
        n_bootstrap=int(n_bootstrap),
        gaussian_low=float(gaussian_low),
        gaussian_high=float(gaussian_high),
        percentile_low=float(percentile_low),
        percentile_high=float(percentile_high),
        bca_low=float(bca_low),
        bca_high=float(bca_high),
        bootstrap_se=bootstrap_se,
    )


def _bca_interval(
    values: np.ndarray,
    estimate: float,
    bootstrap_stats: np.ndarray,
    statistic: Statistic,
    lower_q: float,
    upper_q: float,
) -> tuple[float, float]:
    less = np.mean(bootstrap_stats < estimate)
    less = min(max(float(less), 1.0 / (2.0 * bootstrap_stats.size)), 1.0 - 1.0 / (2.0 * bootstrap_stats.size))
    z0 = norm.ppf(less)

    jackknife = np.array([statistic(np.delete(values, i)) for i in range(values.size)])
    jack_mean = np.mean(jackknife)
    diffs = jack_mean - jackknife
    denom = 6.0 * np.power(np.sum(diffs**2), 1.5)
    acceleration = float(np.sum(diffs**3) / denom) if denom > 0.0 else 0.0

    adjusted_quantiles = []
    for quantile in (lower_q, upper_q):
        z_alpha = norm.ppf(quantile)
        numerator = z0 + z_alpha
        denominator = 1.0 - acceleration * numerator
        adjusted_quantiles.append(norm.cdf(z0 + numerator / denominator))
    adjusted_quantiles = np.clip(adjusted_quantiles, 0.0, 1.0)
    return tuple(np.quantile(bootstrap_stats, adjusted_quantiles))
