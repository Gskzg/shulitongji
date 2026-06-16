"""Empirical covariance propagation helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd

COMPONENTS = {
    "teme": ["dx_km", "dy_km", "dz_km"],
    "ric": ["radial_error_km", "along_track_error_km", "cross_track_error_km"],
}


def propagate_covariance(phi: np.ndarray, sigma0: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Apply Sigma(dt) = Phi Sigma0 Phi^T + Q."""

    return phi @ sigma0 @ phi.T + q


def empirical_covariance_table(df: pd.DataFrame, frame: str = "ric") -> pd.DataFrame:
    """Estimate empirical 3x3 covariance matrices by orbit type and horizon."""

    columns = COMPONENTS[frame]
    rows = []
    for (orbit_type, horizon), group in df.groupby(["orbit_type", "horizon_days"]):
        values = group[columns].dropna().to_numpy(dtype=float)
        if values.shape[0] < 2:
            continue
        cov = np.cov(values, rowvar=False)
        row = {
            "frame": frame,
            "orbit_type": orbit_type,
            "horizon_days": horizon,
            "n": int(values.shape[0]),
        }
        row.update(_flatten_matrix("cov", cov))
        rows.append(row)
    table = pd.DataFrame(rows)
    if table.empty:
        return table
    return table.sort_values(["frame", "orbit_type", "horizon_days"])


def identity_process_noise_table(covariance_table: pd.DataFrame) -> pd.DataFrame:
    """Estimate Q(dt) under a Phi=I baseline using the shortest horizon as Sigma0."""

    if covariance_table.empty:
        return pd.DataFrame()
    rows = []
    for (frame, orbit_type), group in covariance_table.groupby(["frame", "orbit_type"]):
        group = group.sort_values("horizon_days")
        sigma0 = _unflatten_matrix(group.iloc[0], "cov")
        for _, row in group.iterrows():
            sigma = _unflatten_matrix(row, "cov")
            q = regularize_psd(sigma - sigma0)
            out = {
                "frame": frame,
                "orbit_type": orbit_type,
                "horizon_days": row["horizon_days"],
                "baseline_horizon_days": group.iloc[0]["horizon_days"],
            }
            out.update(_flatten_matrix("q", q))
            rows.append(out)
    return pd.DataFrame(rows)


def regularize_psd(matrix: np.ndarray, eps: float = 1e-10) -> np.ndarray:
    """Symmetrize a matrix and clip negative eigenvalues."""

    sym = 0.5 * (matrix + matrix.T)
    eigvals, eigvecs = np.linalg.eigh(sym)
    eigvals = np.clip(eigvals, eps, None)
    return eigvecs @ np.diag(eigvals) @ eigvecs.T


def _flatten_matrix(prefix: str, matrix: np.ndarray) -> dict[str, float]:
    return {
        f"{prefix}_{i + 1}{j + 1}": float(matrix[i, j])
        for i in range(matrix.shape[0])
        for j in range(matrix.shape[1])
    }


def _unflatten_matrix(row: pd.Series, prefix: str) -> np.ndarray:
    return np.array([[row[f"{prefix}_{i + 1}{j + 1}"] for j in range(3)] for i in range(3)], dtype=float)
