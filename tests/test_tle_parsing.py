from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tle_accuracy.tle import classify_orbit, parse_tle_lines
from tle_accuracy.propagation import compute_errors_frame


def test_parse_3le_epoch_and_classification():
    text = """ISS (ZARYA)
1 25544U 98067A   20344.91782528  .00001264  00000-0  29602-4 0  9993
2 25544  51.6462  21.2141 0002182  88.3576  21.7385 15.49374026256337
"""
    records = parse_tle_lines(text.splitlines(), source="fixture")
    assert len(records) == 1
    assert records[0].norad_id == "25544"
    assert records[0].epoch.year == 2020
    features_period = 1440.0 / 15.49374026
    assert classify_orbit(features_period, 420.0, 430.0) == "LEO"


def test_compute_errors_from_fixture():
    records = parse_tle_lines((ROOT / "tests" / "fixtures" / "mini_history.tle").read_text().splitlines(), source="fixture")
    errors = compute_errors_frame(records, horizons_days=[1, 3, 7], max_reference_offset_hours=1)
    assert set(errors["horizon_days"]) == {1.0, 3.0, 7.0}
    assert (errors["position_error_km"] >= 0).all()
