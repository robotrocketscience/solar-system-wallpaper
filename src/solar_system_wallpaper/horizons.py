"""JPL Horizons API client for fetching heliocentric ecliptic ephemeris data."""

from __future__ import annotations

import logging
import math
import time
from datetime import datetime, timedelta, timezone
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from solar_system_wallpaper.catalog import OBJECTS
from solar_system_wallpaper.types import Position

log = logging.getLogger("solar-system-wallpaper")

HORIZONS_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
RATE_DELAY = 0.3  # seconds between requests
MAX_RETRIES = 2

# Spacecraft with limited ephemeris coverage on JPL Horizons.
SPACECRAFT_FALLBACK_RANGES: dict[str, tuple[str, str]] = {
    "JWST": ("2021-12-26", "2031-02-22"),
    "Parker Solar Probe": ("2018-08-13", "2029-12-31"),
    "Juno Probe": ("2011-08-06", "2028-09-30"),
    "SOHO": ("2001-09-11", "2026-04-06"),
    "OSIRIS-REx": ("2016-09-09", "2026-03-01"),
    "Lucy": ("2021-10-17", "2031-03-01"),
    "STEREO-A": ("2006-10-26", "2026-06-10"),
    "Mars Odyssey": ("2001-09-11", "2026-03-08"),
    "MRO": ("2005-08-13", "2026-04-13"),
}


def _jd_to_unix(jd: float) -> float:
    """Convert Julian Date (TDB) to Unix timestamp."""
    return (jd - 2440587.5) * 86400.0


def parse_ephemeris_block(text: str) -> list[Position] | None:
    """Parse the $$SOE..$$EOE block from a Horizons API response.

    Returns a list of Position objects, or None if parsing fails.
    """
    if "$$SOE" not in text or "$$EOE" not in text:
        return None

    block = text.split("$$SOE")[1].split("$$EOE")[0].strip()
    results: list[Position] = []
    for line in block.split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = [x.strip() for x in line.split(",")]
        if len(parts) < 8:
            continue
        jd = float(parts[0])
        unix_ts = _jd_to_unix(jd)
        results.append(Position(
            x=float(parts[2]),
            y=float(parts[3]),
            z=float(parts[4]),
            vx=float(parts[5]),
            vy=float(parts[6]),
            vz=float(parts[7]),
            timestamp=unix_ts,
        ))
    return results if results else None


def fetch_one(
    name: str,
    cmd: str,
    start: str,
    stop: str,
    step_size: str = "30 m",
) -> list[Position] | None:
    """Fetch heliocentric ecliptic XYZ + velocity for one object.

    Args:
        name: Display name (for logging).
        cmd: JPL Horizons COMMAND string.
        start: Start time (e.g. "2024-07-20 16:17").
        stop: Stop time.
        step_size: Horizons STEP_SIZE (e.g. "30 m", "1 d").

    Returns:
        List of Position objects, or None on failure.
    """
    try:
        params = urlencode({
            "format": "text",
            "COMMAND": f"'{cmd}'",
            "OBJ_DATA": "'NO'",
            "MAKE_EPHEM": "'YES'",
            "EPHEM_TYPE": "'VECTORS'",
            "CENTER": "'@10'",
            "START_TIME": f"'{start}'",
            "STOP_TIME": f"'{stop}'",
            "STEP_SIZE": f"'{step_size}'",
            "REF_PLANE": "'ECLIPTIC'",
            "REF_SYSTEM": "'ICRF'",
            "OUT_UNITS": "'AU-D'",
            "VEC_TABLE": "'2'",
            "CSV_FORMAT": "'YES'",
        })
        url = f"{HORIZONS_URL}?{params}"
        req = Request(url, headers={"User-Agent": "SolarSystemWallpaper/1.0"})
        with urlopen(req, timeout=60) as resp:
            text = resp.read().decode()
        return parse_ephemeris_block(text)
    except (URLError, OSError, ValueError) as e:
        log.error("  %s: %s", name, e)
    return None


def fetch_all_positions(
    target_time: datetime | None = None,
) -> dict[str, Position]:
    """Fetch positions for every object in the catalog.

    Args:
        target_time: The datetime to fetch positions for. Defaults to now (UTC).

    Returns:
        Mapping of body name to Position.
    """
    if target_time is None:
        target_time = datetime.now(timezone.utc)

    start = target_time.strftime("%Y-%m-%d %H:%M")
    stop = (target_time + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M")

    positions: dict[str, Position] = {}
    total = len(OBJECTS)
    for i, (name, body) in enumerate(OBJECTS.items()):
        results = _fetch_with_retry(name, body.horizons_cmd, start, stop)
        if results:
            positions[name] = results[0]
            dist = math.sqrt(
                results[0].x ** 2 + results[0].y ** 2 + results[0].z ** 2
            )
            log.info("  %-20s  %10.3f AU", name, dist)
        else:
            log.warning("  %-20s  FAILED", name)

        if i < total - 1:
            time.sleep(RATE_DELAY)

    return positions


def fetch_bulk(
    name: str,
    cmd: str,
    start: str,
    stop: str,
    step_size: str = "1 d",
) -> list[Position] | None:
    """Fetch a full date range of positions for one body (for timelapse).

    Uses one API call per body for the entire range instead of per-frame.
    Includes retry logic and spacecraft fallback ranges.
    """
    result = _fetch_with_retry(name, cmd, start, stop, step_size)
    if result is not None:
        return result

    # Try fallback range for spacecraft
    if name in SPACECRAFT_FALLBACK_RANGES:
        fb_start, fb_end = SPACECRAFT_FALLBACK_RANGES[name]
        log.info("  %s: trying fallback range %s..%s", name, fb_start, fb_end)
        time.sleep(RATE_DELAY)
        return _fetch_with_retry(name, cmd, fb_start, fb_end, step_size)

    return None


def _fetch_with_retry(
    name: str,
    cmd: str,
    start: str,
    stop: str,
    step_size: str = "30 m",
) -> list[Position] | None:
    """Fetch with retry logic."""
    for attempt in range(1 + MAX_RETRIES):
        if attempt > 0:
            log.info("  %s: retry %d", name, attempt)
            time.sleep(2)
        result = fetch_one(name, cmd, start, stop, step_size)
        if result is not None:
            return result
    return None


def propagate_positions(
    positions: dict[str, Position],
    ref_timestamp: float,
    target_timestamp: float,
) -> dict[str, Position]:
    """Extrapolate body positions from reference epoch to target timestamp.

    Uses first-order (linear) propagation: x(t) = x0 + vx * dt_days.
    Accurate for days-to-weeks timescales; visually acceptable for months.
    """
    dt_days = (target_timestamp - ref_timestamp) / 86400.0
    if abs(dt_days) < 1e-6:
        return positions

    propagated: dict[str, Position] = {}
    for name, pos in positions.items():
        propagated[name] = Position(
            x=pos.x + pos.vx * dt_days,
            y=pos.y + pos.vy * dt_days,
            z=pos.z + pos.vz * dt_days,
            vx=pos.vx,
            vy=pos.vy,
            vz=pos.vz,
            timestamp=target_timestamp,
        )
    return propagated
