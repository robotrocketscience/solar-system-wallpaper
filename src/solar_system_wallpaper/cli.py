"""Command-line interface for solar-system-wallpaper."""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

from solar_system_wallpaper.types import (
    CATEGORY_FILTERS,
    BodyCategory,
    RenderConfig,
    TimelapseConfig,
)

log = logging.getLogger("solar-system-wallpaper")


def _parse_datetime(value: str) -> datetime:
    """Parse a date/datetime string, returning a timezone-aware datetime."""
    if value.lower() == "now":
        return datetime.now(timezone.utc)

    from dateutil import parser as dateutil_parser

    dt = dateutil_parser.parse(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _parse_categories(value: str) -> frozenset[BodyCategory]:
    """Parse comma-separated category filter string."""
    cats: list[BodyCategory] = []
    for name in value.split(","):
        name = name.strip()
        if name in CATEGORY_FILTERS:
            cats.extend(CATEGORY_FILTERS[name])
        else:
            log.warning("Unknown category filter: %s", name)
    return frozenset(cats) if cats else frozenset(BodyCategory)


def _cmd_render(args: argparse.Namespace) -> None:
    """Handle the 'render' subcommand."""
    from solar_system_wallpaper.horizons import fetch_all_positions
    from solar_system_wallpaper.render.core import render_frame

    target_time = _parse_datetime(args.date)
    log.info("Rendering for %s", target_time.isoformat())

    categories = _parse_categories(args.bodies) if args.bodies else frozenset(BodyCategory)

    config = RenderConfig(
        width=args.width,
        height=args.height,
        categories=categories,
        cosmetic=not args.no_cosmetic,
        informational=not args.no_informational,
        show_labels=not args.no_labels,
        show_info_panel=not args.no_info_panel,
    )

    log.info("Fetching positions from JPL Horizons...")
    positions = fetch_all_positions(target_time)
    if len(positions) < 5:
        log.error("Too few bodies fetched (%d). Check network connectivity.", len(positions))
        sys.exit(1)

    log.info("Rendering %dx%d frame...", config.width, config.height)
    surface = render_frame(
        positions, t=0.0, config=config, display_time=target_time
    )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    surface.write_to_png(str(output))
    log.info("Saved to %s", output)


def _cmd_timelapse(args: argparse.Namespace) -> None:
    """Handle the 'timelapse' subcommand."""
    from solar_system_wallpaper.timelapse import generate_timelapse

    categories = _parse_categories(args.bodies) if args.bodies else frozenset(BodyCategory)

    # Parse speed string like "1d/frame" -> step_days
    step_days = 1
    if args.speed:
        speed_str = args.speed.lower().replace("/frame", "").strip()
        if speed_str.endswith("d"):
            step_days = int(speed_str[:-1])

    config = TimelapseConfig(
        start_date=args.start,
        num_days=args.days,
        step_days=step_days,
        width=args.width,
        height=args.height,
        fps=args.fps,
        output_path=args.output,
        categories=categories,
        cosmetic=not args.no_cosmetic,
        informational=not args.no_informational,
        show_labels=not args.no_labels,
    )

    generate_timelapse(config)


def main() -> None:
    """Entry point for the CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        prog="solar-system-wallpaper",
        description="Render solar system wallpapers using real JPL Horizons ephemeris data",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # render subcommand
    render_parser = subparsers.add_parser(
        "render", help="Render a single wallpaper image"
    )
    render_parser.add_argument(
        "--date",
        default="now",
        help="Date/time for the scene (ISO format or 'now'). Default: now",
    )
    render_parser.add_argument(
        "--output", "-o",
        default="wallpaper.png",
        help="Output PNG file path. Default: wallpaper.png",
    )
    render_parser.add_argument(
        "--width", type=int, default=2560,
        help="Image width in pixels. Default: 2560",
    )
    render_parser.add_argument(
        "--height", type=int, default=1440,
        help="Image height in pixels. Default: 1440",
    )
    render_parser.add_argument(
        "--bodies",
        help="Comma-separated body categories to show: planets,dwarf_planets,moons,asteroids,comets,spacecraft",
    )
    render_parser.add_argument(
        "--no-cosmetic", action="store_true",
        help="Disable cosmetic effects (stars, nebulae, milky way, shooting stars)",
    )
    render_parser.add_argument(
        "--no-labels", action="store_true",
        help="Disable body name labels",
    )
    render_parser.add_argument(
        "--no-informational", action="store_true",
        help="Disable informational overlays (grid, belts, orbit rings, trails)",
    )
    render_parser.add_argument(
        "--no-info-panel", action="store_true",
        help="Disable the info panel (title, legend, distance table)",
    )
    render_parser.set_defaults(func=_cmd_render)

    # timelapse subcommand
    tl_parser = subparsers.add_parser(
        "timelapse", help="Generate a timelapse video"
    )
    tl_parser.add_argument(
        "--start", required=True,
        help="Start date (YYYY-MM-DD)",
    )
    tl_parser.add_argument(
        "--days", type=int, required=True,
        help="Number of days to cover",
    )
    tl_parser.add_argument(
        "--speed", default="1d/frame",
        help="Time per frame, e.g. '1d/frame', '7d/frame'. Default: 1d/frame",
    )
    tl_parser.add_argument(
        "--output", "-o", default="timelapse.mp4",
        help="Output video file path. Default: timelapse.mp4",
    )
    tl_parser.add_argument(
        "--width", type=int, default=2560,
        help="Frame width in pixels. Default: 2560",
    )
    tl_parser.add_argument(
        "--height", type=int, default=1440,
        help="Frame height in pixels. Default: 1440",
    )
    tl_parser.add_argument(
        "--fps", type=int, default=30,
        help="Video framerate. Default: 30",
    )
    tl_parser.add_argument(
        "--bodies",
        help="Comma-separated body categories to show",
    )
    tl_parser.add_argument(
        "--no-cosmetic", action="store_true",
        help="Disable cosmetic effects",
    )
    tl_parser.add_argument(
        "--no-labels", action="store_true",
        help="Disable body name labels",
    )
    tl_parser.add_argument(
        "--no-informational", action="store_true",
        help="Disable informational overlays",
    )
    tl_parser.set_defaults(func=_cmd_timelapse)

    args = parser.parse_args()
    args.func(args)
