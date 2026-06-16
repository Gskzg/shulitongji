"""Download helpers for CelesTrak and Space-Track GP/TLE data."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
from urllib.parse import quote

import requests

CELESTRAK_GP_URL = "https://celestrak.org/NORAD/elements/gp.php"
SPACETRACK_LOGIN_URL = "https://www.space-track.org/ajaxauth/login"
SPACETRACK_QUERY_URL = "https://www.space-track.org/basicspacedata/query"
USER_AGENT = "tle-accuracy-statistics/1.0 (student project; contact: local)"


def download_celestrak(
    out_dir: Path,
    groups: list[str] | None = None,
    catalog_numbers: list[str] | None = None,
    fmt: str = "TLE",
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    groups = groups or []
    catalog_numbers = catalog_numbers or []
    written: list[Path] = []
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for group in groups:
        params = {"GROUP": group.upper(), "FORMAT": fmt.upper()}
        content = _get_celestrak(params)
        suffix = _suffix_for_format(fmt)
        path = out_dir / f"celestrak_group_{group.lower()}_{timestamp}.{suffix}"
        path.write_text(content, encoding="utf-8")
        written.append(path)

    for catnr in catalog_numbers:
        params = {"CATNR": str(catnr), "FORMAT": fmt.upper()}
        content = _get_celestrak(params)
        suffix = _suffix_for_format(fmt)
        path = out_dir / f"celestrak_catnr_{catnr}_{timestamp}.{suffix}"
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


def download_spacetrack_history(
    out_dir: Path,
    catalog_numbers: list[str],
    start_date: str,
    end_date: str,
    identity: str | None = None,
    password: str | None = None,
    chunk_size: int = 50,
) -> list[Path]:
    """Download Space-Track gp_history records as JSON.

    Dates should be ISO-like values accepted by Space-Track, e.g. 2025-01-01.
    """

    identity = identity or os.getenv("SPACE_TRACK_IDENTITY")
    password = password or os.getenv("SPACE_TRACK_PASSWORD")
    if not identity or not password:
        raise RuntimeError("Set SPACE_TRACK_IDENTITY and SPACE_TRACK_PASSWORD for Space-Track downloads")
    if not catalog_numbers:
        raise ValueError("Space-Track history downloads require at least one NORAD catalog number")

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    with requests.Session() as session:
        session.headers.update({"User-Agent": USER_AGENT})
        login_response = session.post(
            SPACETRACK_LOGIN_URL,
            data={"identity": identity, "password": password},
            timeout=60,
        )
        login_response.raise_for_status()

        for index, chunk in enumerate(_chunks(catalog_numbers, chunk_size), start=1):
            ids = ",".join(str(item) for item in chunk)
            query_path = (
                f"/class/gp_history/NORAD_CAT_ID/{quote(ids)}"
                f"/EPOCH/{quote(start_date + '--' + end_date)}"
                "/orderby/NORAD_CAT_ID,EPOCH/format/json"
            )
            response = session.get(SPACETRACK_QUERY_URL + query_path, timeout=180)
            response.raise_for_status()
            path = out_dir / f"spacetrack_gp_history_{start_date}_{end_date}_chunk{index:03d}.json"
            path.write_text(response.text, encoding="utf-8")
            written.append(path)
    return written


def _get_celestrak(params: dict[str, str]) -> str:
    response = requests.get(CELESTRAK_GP_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=60)
    response.raise_for_status()
    text = response.text
    if "No GP data found" in text:
        raise RuntimeError(f"CelesTrak returned no data for {params}")
    return text


def _suffix_for_format(fmt: str) -> str:
    fmt = fmt.upper()
    if fmt in {"TLE", "3LE", "2LE"}:
        return "tle"
    if fmt == "CSV":
        return "csv"
    if fmt in {"JSON", "JSON-PRETTY"}:
        return "json"
    return fmt.lower()


def _chunks(items: list[str], size: int) -> list[list[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]
