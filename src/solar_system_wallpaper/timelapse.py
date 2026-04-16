"""Timelapse video generation: bulk JPL fetch + sequential frame render."""

from __future__ import annotations

import logging
import subprocess
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from solar_system_wallpaper.catalog import OBJECTS
from solar_system_wallpaper.horizons import RATE_DELAY, fetch_bulk
from solar_system_wallpaper.render.core import render_frame
from solar_system_wallpaper.types import Position, RenderConfig, TimelapseConfig

log = logging.getLogger("solar-system-wallpaper")


def _bulk_fetch_all(
    start_date: str,
    num_days: int,
    step_days: int,
) -> dict[str, list[Position]]:
    """Fetch full date-range ephemeris for all bodies in one API call per body.

    Returns mapping of body name to list of Position objects (one per step).
    """
    start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    end_dt = start_dt + timedelta(days=num_days)
    stop_str = end_dt.strftime("%Y-%m-%d")
    step_size = f"{step_days} d"

    all_positions: dict[str, list[Position]] = {}
    total = len(OBJECTS)

    for i, (name, body) in enumerate(OBJECTS.items()):
        log.info("  [%2d/%d] %-20s ... ", i + 1, total, name)

        results = fetch_bulk(name, body.horizons_cmd, start_date, stop_str, step_size)
        if results is not None:
            all_positions[name] = results
            log.info("  %-20s  %d points", name, len(results))
        else:
            log.warning("  %-20s  FAILED", name)

        if i < total - 1:
            time.sleep(RATE_DELAY)

    return all_positions


def _positions_at_index(
    all_data: dict[str, list[Position]],
    index: int,
) -> dict[str, Position]:
    """Extract single-frame positions from bulk data at the given index."""
    frame_positions: dict[str, Position] = {}
    for name, pos_list in all_data.items():
        if index < len(pos_list):
            frame_positions[name] = pos_list[index]
    return frame_positions


def generate_timelapse(tlc: TimelapseConfig) -> None:
    """Generate a timelapse video from bulk ephemeris data.

    Steps:
    1. Bulk-fetch ephemeris for all bodies over the date range
    2. Render each frame as a PNG to a temp directory
    3. Encode frames to video using ffmpeg
    """
    log.info("Timelapse: %s + %d days (step=%dd)", tlc.start_date, tlc.num_days, tlc.step_days)
    log.info("Output: %s (%dx%d @ %d fps)", tlc.output_path, tlc.width, tlc.height, tlc.fps)

    # Step 1: Bulk fetch
    log.info("Fetching ephemeris data from JPL Horizons...")
    all_data = _bulk_fetch_all(tlc.start_date, tlc.num_days, tlc.step_days)

    if len(all_data) < 5:
        log.error("Too few bodies fetched (%d). Aborting.", len(all_data))
        return

    num_frames = tlc.num_days // tlc.step_days
    log.info("Rendering %d frames...", num_frames)

    config = RenderConfig(
        width=tlc.width,
        height=tlc.height,
        categories=tlc.categories,
        cosmetic=tlc.cosmetic,
        informational=tlc.informational,
        show_labels=tlc.show_labels,
    )

    start_dt = datetime.strptime(tlc.start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    with tempfile.TemporaryDirectory(prefix="solar-timelapse-") as tmpdir:
        frame_dir = Path(tmpdir)

        # Step 2: Render frames
        for frame_idx in range(num_frames):
            positions = _positions_at_index(all_data, frame_idx)
            if not positions:
                continue

            # Use a smooth cosmetic_t to prevent strobing
            cosmetic_t = float(frame_idx) * 0.5
            frame_time = start_dt + timedelta(days=frame_idx * tlc.step_days)

            surface = render_frame(
                positions,
                t=cosmetic_t,
                config=config,
                cosmetic_t=cosmetic_t,
                display_time=frame_time,
            )

            frame_path = frame_dir / f"frame_{frame_idx:06d}.png"
            surface.write_to_png(str(frame_path))

            if (frame_idx + 1) % 50 == 0 or frame_idx == num_frames - 1:
                log.info("  Frame %d/%d", frame_idx + 1, num_frames)

        # Step 3: Encode with ffmpeg
        log.info("Encoding video with ffmpeg...")
        pattern = str(frame_dir / "frame_%06d.png")
        cmd = [
            "ffmpeg",
            "-y",
            "-framerate", str(tlc.fps),
            "-i", pattern,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "18",
            "-preset", "medium",
            tlc.output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if result.returncode != 0:
            log.error("ffmpeg failed: %s", result.stderr)
            return

    log.info("Timelapse saved to %s", tlc.output_path)
