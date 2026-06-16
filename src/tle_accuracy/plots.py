"""Plot generation for TLE forecast-error analysis."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def make_all_plots(errors: pd.DataFrame, output_dir: Path, ci: pd.DataFrame | None = None) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook")
    paths = [
        _boxplot(errors, output_dir / "error_boxplot_by_orbit_horizon.png"),
        _growth_plot(errors, output_dir / "error_growth_median_iqr.png"),
        _distribution_plot(errors, output_dir / "error_distribution_log10.png"),
    ]
    if ci is not None and not ci.empty:
        paths.append(_ci_comparison_plot(ci, output_dir / "ci_gaussian_vs_bootstrap.png"))
    return [path for path in paths if path is not None]


def _boxplot(errors: pd.DataFrame, path: Path) -> Path | None:
    if errors.empty:
        return None
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=errors, x="horizon_days", y="position_error_km", hue="orbit_type", showfliers=False, ax=ax)
    ax.set_yscale("log")
    ax.set_xlabel("Forecast horizon (days)")
    ax.set_ylabel("3D position error (km, log scale)")
    ax.set_title("SGP4/TLE forecast error by orbit class")
    ax.legend(title="Orbit type")
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)
    return path


def _growth_plot(errors: pd.DataFrame, path: Path) -> Path | None:
    if errors.empty:
        return None
    summary = (
        errors.groupby(["orbit_type", "horizon_days"])["position_error_km"]
        .agg(median="median", q25=lambda x: x.quantile(0.25), q75=lambda x: x.quantile(0.75))
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(9, 6))
    palette = sns.color_palette("Dark2", n_colors=summary["orbit_type"].nunique())
    for color, (orbit_type, group) in zip(palette, summary.groupby("orbit_type")):
        group = group.sort_values("horizon_days")
        ax.plot(group["horizon_days"], group["median"], marker="o", label=orbit_type, color=color)
        ax.fill_between(group["horizon_days"], group["q25"], group["q75"], color=color, alpha=0.18)
    ax.set_yscale("log")
    ax.set_xlabel("Forecast horizon (days)")
    ax.set_ylabel("Median 3D error (km, log scale)")
    ax.set_title("Error growth curve with interquartile band")
    ax.legend(title="Orbit type")
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)
    return path


def _distribution_plot(errors: pd.DataFrame, path: Path) -> Path | None:
    if errors.empty:
        return None
    plot_df = errors.copy()
    plot_df["log10_error_km"] = plot_df["position_error_km"].clip(lower=1e-6).map(lambda x: __import__("math").log10(x))
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=plot_df, x="log10_error_km", hue="orbit_type", element="step", stat="density", common_norm=False, ax=ax)
    ax.set_xlabel("log10(3D position error / km)")
    ax.set_ylabel("Density")
    ax.set_title("Forecast-error distribution")
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)
    return path


def _ci_comparison_plot(ci: pd.DataFrame, path: Path) -> Path | None:
    mean_ci = ci[ci["statistic"] == "mean"].copy()
    if mean_ci.empty:
        return None
    mean_ci = mean_ci.sort_values(["orbit_type", "horizon_days"])
    fig, ax = plt.subplots(figsize=(10, 6))
    x_labels = [f"{row.orbit_type}-{row.horizon_days:g}d" for row in mean_ci.itertuples()]
    x = range(len(mean_ci))
    ax.errorbar(
        x,
        mean_ci["estimate"],
        yerr=[mean_ci["estimate"] - mean_ci["gaussian_low"], mean_ci["gaussian_high"] - mean_ci["estimate"]],
        fmt="o",
        capsize=3,
        label="Gaussian/bootstrap-SE CI",
    )
    ax.errorbar(
        x,
        mean_ci["estimate"],
        yerr=[mean_ci["estimate"] - mean_ci["bca_low"], mean_ci["bca_high"] - mean_ci["estimate"]],
        fmt="s",
        capsize=3,
        alpha=0.75,
        label="BCa bootstrap CI",
    )
    ax.set_xticks(list(x), x_labels, rotation=40, ha="right")
    ax.set_yscale("log")
    ax.set_ylabel("Mean 3D error (km, log scale)")
    ax.set_title("Gaussian vs BCa bootstrap confidence intervals")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=220)
    plt.close(fig)
    return path
