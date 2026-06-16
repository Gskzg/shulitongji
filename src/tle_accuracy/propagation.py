"""SGP4 propagation and forecast-error computation."""

from __future__ import annotations

from bisect import bisect_left
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
from sgp4.api import SGP4_ERRORS, Satrec, jday

from .tle import TLERecord, orbital_features, classify_orbit

ERROR_COLUMNS = [
    "norad_id",
    "name",
    "orbit_type",
    "horizon_days",
    "initial_epoch",
    "reference_epoch",
    "target_time",
    "reference_offset_hours",
    "initial_source",
    "reference_source",
    "dx_km",
    "dy_km",
    "dz_km",
    "radial_error_km",
    "along_track_error_km",
    "cross_track_error_km",
    "position_error_km",
    "inclination_deg",
    "eccentricity",
    "mean_motion_rev_day",
    "period_min",
    "semi_major_axis_km",
    "perigee_km",
    "apogee_km",
]


def propagate(record: TLERecord, when: datetime) -> tuple[np.ndarray, np.ndarray, int]:
    """Propagate a TLE to a UTC datetime and return TEME position/velocity."""

    when = when.astimezone(timezone.utc)
    second = when.second + when.microsecond / 1_000_000.0
    jd, fr = jday(when.year, when.month, when.day, when.hour, when.minute, second)
    sat = Satrec.twoline2rv(record.line1, record.line2)
    error_code, position_km, velocity_km_s = sat.sgp4(jd, fr)
    if error_code:
        raise RuntimeError(SGP4_ERRORS.get(error_code, f"SGP4 error {error_code}"))
    return np.asarray(position_km, dtype=float), np.asarray(velocity_km_s, dtype=float), error_code


def ric_components(delta_km: np.ndarray, reference_position_km: np.ndarray, reference_velocity_km_s: np.ndarray) -> tuple[float, float, float]:
    """Resolve a TEME position residual into radial, along-track, cross-track components."""

    r_hat = _unit(reference_position_km)
    h_hat = _unit(np.cross(reference_position_km, reference_velocity_km_s))
    along_hat = _unit(np.cross(h_hat, r_hat))
    return (
        float(np.dot(delta_km, r_hat)),
        float(np.dot(delta_km, along_hat)),
        float(np.dot(delta_km, h_hat)),
    )


def compute_error_rows(
    records: list[TLERecord],
    horizons_days: list[float],
    max_reference_offset_hours: float = 12.0,
    orbit_types: set[str] | None = None,
    min_records_per_object: int = 2,
) -> list[dict]:
    """Pair old and future TLEs and compute SGP4 forecast errors."""

    by_sat: dict[str, list[TLERecord]] = defaultdict(list)
    for record in records:
        by_sat[record.norad_id].append(record)

    rows: list[dict] = []
    max_offset = timedelta(hours=max_reference_offset_hours)
    for norad_id, sat_records in by_sat.items():
        unique_records = _dedupe_records(sorted(sat_records, key=lambda item: item.epoch))
        if len(unique_records) < min_records_per_object:
            continue
        epochs = [item.epoch for item in unique_records]

        for initial_index, initial in enumerate(unique_records):
            features = orbital_features(initial.line2)
            orbit_type = classify_orbit(features["period_min"], features["perigee_km"], features["apogee_km"])
            if orbit_types and orbit_type not in orbit_types:
                continue

            for horizon in horizons_days:
                target_time = initial.epoch + timedelta(days=float(horizon))
                reference = _nearest_future_record(unique_records, epochs, target_time, initial_index, max_offset)
                if reference is None:
                    continue
                try:
                    predicted_position, _, _ = propagate(initial, target_time)
                    reference_position, reference_velocity, _ = propagate(reference, target_time)
                except RuntimeError:
                    continue

                delta = predicted_position - reference_position
                radial, along, cross = ric_components(delta, reference_position, reference_velocity)
                ref_offset_hours = (reference.epoch - target_time).total_seconds() / 3600.0
                rows.append(
                    {
                        "norad_id": norad_id,
                        "name": initial.name or reference.name,
                        "orbit_type": orbit_type,
                        "horizon_days": float(horizon),
                        "initial_epoch": initial.epoch.isoformat(),
                        "reference_epoch": reference.epoch.isoformat(),
                        "target_time": target_time.isoformat(),
                        "reference_offset_hours": ref_offset_hours,
                        "initial_source": initial.source,
                        "reference_source": reference.source,
                        "dx_km": float(delta[0]),
                        "dy_km": float(delta[1]),
                        "dz_km": float(delta[2]),
                        "radial_error_km": radial,
                        "along_track_error_km": along,
                        "cross_track_error_km": cross,
                        "position_error_km": float(np.linalg.norm(delta)),
                        **features,
                    }
                )
    return rows


def compute_errors_frame(*args, **kwargs) -> pd.DataFrame:
    rows = compute_error_rows(*args, **kwargs)
    if not rows:
        return pd.DataFrame(columns=ERROR_COLUMNS)
    return pd.DataFrame(rows).sort_values(["orbit_type", "horizon_days", "norad_id", "initial_epoch"])


def _nearest_future_record(
    records: list[TLERecord],
    epochs: list[datetime],
    target_time: datetime,
    initial_index: int,
    max_offset: timedelta,
) -> TLERecord | None:
    idx = bisect_left(epochs, target_time)
    candidates: list[TLERecord] = []
    for candidate_index in (idx - 2, idx - 1, idx, idx + 1, idx + 2):
        if candidate_index <= initial_index or candidate_index < 0 or candidate_index >= len(records):
            continue
        candidate = records[candidate_index]
        if abs(candidate.epoch - target_time) <= max_offset:
            candidates.append(candidate)
    if not candidates:
        return None
    return min(candidates, key=lambda item: abs(item.epoch - target_time))


def _dedupe_records(records: list[TLERecord]) -> list[TLERecord]:
    seen: set[tuple[str, str, datetime]] = set()
    unique: list[TLERecord] = []
    for record in records:
        key = (record.line1, record.line2, record.epoch)
        if key in seen:
            continue
        seen.add(key)
        unique.append(record)
    return unique


def _unit(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm == 0.0:
        raise ValueError("Cannot normalize zero vector")
    return vector / norm
