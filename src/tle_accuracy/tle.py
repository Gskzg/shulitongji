"""TLE parsing and orbit-type helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Iterable

import pandas as pd

MU_EARTH_KM3_S2 = 398600.4418
EARTH_RADIUS_KM = 6378.137


@dataclass(frozen=True)
class TLERecord:
    """A single two-line element set with parsed metadata."""

    name: str
    norad_id: str
    line1: str
    line2: str
    epoch: datetime
    source: str = ""
    snapshot_time: datetime | None = None

    def to_dict(self) -> dict:
        row = asdict(self)
        row["epoch"] = self.epoch.isoformat()
        row["snapshot_time"] = self.snapshot_time.isoformat() if self.snapshot_time else ""
        row.update(orbital_features(self.line2))
        row["orbit_type"] = classify_orbit(row["period_min"], row["perigee_km"], row["apogee_km"])
        return row


def parse_tle_epoch(line1: str) -> datetime:
    """Parse the YYDDD.DDDDDDDD epoch field from TLE line 1."""

    year_2 = int(line1[18:20])
    year = 2000 + year_2 if year_2 < 57 else 1900 + year_2
    day_of_year = float(line1[20:32])
    return datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=day_of_year - 1)


def parse_tle_lines(lines: Iterable[str], source: str = "") -> list[TLERecord]:
    """Parse mixed 2LE/3LE text into records."""

    clean = [line.rstrip("\n") for line in lines if line.strip()]
    records: list[TLERecord] = []
    i = 0
    while i < len(clean):
        name = ""
        if clean[i].startswith("1 ") and i + 1 < len(clean) and clean[i + 1].startswith("2 "):
            line1, line2 = clean[i].strip(), clean[i + 1].strip()
            i += 2
        elif (
            i + 2 < len(clean)
            and clean[i + 1].startswith("1 ")
            and clean[i + 2].startswith("2 ")
        ):
            name = clean[i].strip()
            if name.startswith("0 "):
                name = name[2:].strip()
            line1, line2 = clean[i + 1].strip(), clean[i + 2].strip()
            i += 3
        else:
            i += 1
            continue

        try:
            epoch = parse_tle_epoch(line1)
            norad_id = line1[2:7].strip()
        except ValueError:
            continue
        records.append(TLERecord(name=name, norad_id=norad_id, line1=line1, line2=line2, epoch=epoch, source=source))
    return records


def parse_tle_file(path: Path) -> list[TLERecord]:
    return parse_tle_lines(path.read_text(encoding="utf-8", errors="replace").splitlines(), source=str(path))


def records_from_csv(path: Path) -> list[TLERecord]:
    df = pd.read_csv(path)
    return records_from_frame(df, source=str(path))


def records_from_json(path: Path) -> list[TLERecord]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("data", data.get("records", []))
    return records_from_frame(pd.DataFrame(data), source=str(path))


def records_from_frame(df: pd.DataFrame, source: str = "") -> list[TLERecord]:
    """Parse Space-Track/CelesTrak JSON or CSV tables containing TLE_LINE fields."""

    records: list[TLERecord] = []
    line1_col = _first_existing(df, ["TLE_LINE1", "tle_line1", "line1"])
    line2_col = _first_existing(df, ["TLE_LINE2", "tle_line2", "line2"])
    if not line1_col or not line2_col:
        return records

    name_col = _first_existing(df, ["TLE_LINE0", "OBJECT_NAME", "object_name", "name"])
    id_col = _first_existing(df, ["NORAD_CAT_ID", "norad_cat_id"])
    for _, row in df.iterrows():
        line1 = str(row[line1_col]).strip()
        line2 = str(row[line2_col]).strip()
        if not line1.startswith("1 ") or not line2.startswith("2 "):
            continue
        name = str(row[name_col]).strip() if name_col and pd.notna(row[name_col]) else ""
        if name.startswith("0 "):
            name = name[2:].strip()
        norad_id = str(row[id_col]).strip() if id_col and pd.notna(row[id_col]) else line1[2:7].strip()
        try:
            epoch = parse_tle_epoch(line1)
        except ValueError:
            continue
        records.append(TLERecord(name=name, norad_id=norad_id, line1=line1, line2=line2, epoch=epoch, source=source))
    return records


def load_records(input_paths: Iterable[Path]) -> list[TLERecord]:
    """Load TLE records from files or directories."""

    paths: list[Path] = []
    for item in input_paths:
        if item.is_dir():
            for pattern in ("*.tle", "*.3le", "*.2le", "*.txt", "*.csv", "*.json"):
                paths.extend(sorted(item.rglob(pattern)))
        elif item.exists():
            paths.append(item)

    records: list[TLERecord] = []
    for path in sorted(set(paths)):
        suffix = path.suffix.lower()
        if suffix in {".tle", ".3le", ".2le", ".txt"}:
            records.extend(parse_tle_file(path))
        elif suffix == ".csv":
            records.extend(records_from_csv(path))
        elif suffix == ".json":
            records.extend(records_from_json(path))
    return records


def orbital_features(line2: str) -> dict[str, float]:
    """Return simple orbital features parsed from TLE line 2."""

    inclination_deg = float(line2[8:16])
    eccentricity = float("0." + line2[26:33].strip())
    mean_motion_rev_day = float(line2[52:63])
    period_min = 1440.0 / mean_motion_rev_day
    mean_motion_rad_s = mean_motion_rev_day * 2.0 * 3.141592653589793 / 86400.0
    semi_major_axis_km = (MU_EARTH_KM3_S2 / (mean_motion_rad_s**2)) ** (1.0 / 3.0)
    perigee_km = semi_major_axis_km * (1.0 - eccentricity) - EARTH_RADIUS_KM
    apogee_km = semi_major_axis_km * (1.0 + eccentricity) - EARTH_RADIUS_KM
    return {
        "inclination_deg": inclination_deg,
        "eccentricity": eccentricity,
        "mean_motion_rev_day": mean_motion_rev_day,
        "period_min": period_min,
        "semi_major_axis_km": semi_major_axis_km,
        "perigee_km": perigee_km,
        "apogee_km": apogee_km,
    }


def classify_orbit(period_min: float, perigee_km: float, apogee_km: float) -> str:
    """Classify an object into broad LEO/MEO/GEO/OTHER classes."""

    if period_min < 225.0 or perigee_km < 2000.0:
        return "LEO"
    if 1200.0 <= period_min <= 1600.0 and 30000.0 <= apogee_km <= 50000.0:
        return "GEO"
    if 225.0 <= period_min < 1200.0:
        return "MEO"
    return "OTHER"


def records_to_frame(records: list[TLERecord]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
    return pd.DataFrame([record.to_dict() for record in records]).sort_values(["norad_id", "epoch"])


def _first_existing(df: pd.DataFrame, candidates: list[str]) -> str | None:
    columns = set(df.columns)
    for col in candidates:
        if col in columns:
            return col
    return None
