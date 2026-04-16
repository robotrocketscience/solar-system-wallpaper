"""Info panel, legend, and velocity trail rendering."""

from __future__ import annotations

import math
from datetime import datetime, timezone

import cairo

from solar_system_wallpaper.catalog import (
    CAT_LABELS,
    CATEGORIES,
    OBJECTS,
    TEXT_COLOR,
    TITLE_COLOR,
)
from solar_system_wallpaper.coordinates import SolarView
from solar_system_wallpaper.types import BodyCategory, CelestialBody, Color, Position


def draw_info_panel(
    ctx: cairo.Context[cairo.ImageSurface],
    positions: dict[str, Position],
    t: float,
    width: int,
    height: int,
    display_time: datetime | None = None,
) -> None:
    """Draw info panel with date, legend, and distance table."""
    if display_time is None:
        display_time = datetime.now(timezone.utc)
    ts = display_time.strftime("%Y-%m-%d %H:%M UTC")
    ctx.select_font_face("monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

    # Title (top-left)
    ctx.set_font_size(16)
    ctx.set_source_rgba(*TITLE_COLOR, 0.6)
    ctx.move_to(30, 38)
    ctx.show_text("SOLAR SYSTEM  //  LIVE VIEW")
    ctx.set_font_size(11)
    ctx.set_source_rgba(*TEXT_COLOR, 0.35)
    ctx.move_to(30, 56)
    ctx.show_text(f"JPL Horizons  |  {ts}")

    # Right panel: grouped by category
    x_right = width - 230
    y = 36.0
    ctx.set_font_size(10)

    for cat in CATEGORIES:
        items: list[tuple[str, CelestialBody]] = [
            (n, o)
            for n, o in OBJECTS.items()
            if o.category == cat and n in positions
        ]
        if not items:
            continue

        # Category header
        ctx.set_source_rgba(*TITLE_COLOR, 0.4)
        ctx.set_font_size(8)
        ctx.move_to(x_right, y)
        ctx.show_text(CAT_LABELS.get(cat, cat.value.upper()))
        y += 14

        ctx.set_font_size(9)
        for name, body in items:
            p = positions[name]
            dist = math.sqrt(p.x ** 2 + p.y ** 2 + p.z ** 2)
            color = body.color
            # Dot
            if cat == BodyCategory.SPACECRAFT:
                ctx.set_source_rgba(*color, 0.6)
                ctx.move_to(x_right + 4, y - 4)
                ctx.line_to(x_right + 6, y - 2)
                ctx.line_to(x_right + 4, y)
                ctx.line_to(x_right + 2, y - 2)
                ctx.close_path()
                ctx.fill()
            else:
                ctx.set_source_rgba(*color, 0.6)
                ctx.arc(x_right + 4, y - 2, 2, 0, 2 * math.pi)
                ctx.fill()
            # Text
            ctx.set_source_rgba(*TEXT_COLOR, 0.4)
            ctx.move_to(x_right + 12, y)
            if dist > 100:
                ctx.show_text(f"{name:16s} {dist:8.1f} AU")
            else:
                ctx.show_text(f"{name:16s} {dist:8.3f} AU")
            y += 14

        y += 4  # gap between categories

    # Legend (bottom-left)
    ctx.set_font_size(8)
    legend_y = height - 30
    legend_items: list[tuple[Color, str, str]] = [
        ((0.70, 0.65, 0.60), "circle", "Planet"),
        ((0.65, 0.55, 0.50), "circle", "Dwarf planet"),
        ((0.65, 0.65, 0.65), "circle", "Moon"),
        ((0.60, 0.58, 0.55), "circle", "Asteroid"),
        ((0.50, 0.75, 0.85), "tail", "Comet"),
        ((0.40, 0.90, 0.40), "diamond", "Spacecraft"),
    ]
    lx = 30.0
    for color, shape, label in legend_items:
        if shape == "circle":
            ctx.set_source_rgba(*color, 0.5)
            ctx.arc(lx + 4, legend_y - 3, 3, 0, 2 * math.pi)
            ctx.fill()
        elif shape == "diamond":
            ctx.set_source_rgba(*color, 0.5)
            ctx.move_to(lx + 4, legend_y - 6)
            ctx.line_to(lx + 7, legend_y - 3)
            ctx.line_to(lx + 4, legend_y)
            ctx.line_to(lx + 1, legend_y - 3)
            ctx.close_path()
            ctx.fill()
        elif shape == "tail":
            ctx.set_source_rgba(*color, 0.5)
            ctx.arc(lx + 4, legend_y - 3, 2, 0, 2 * math.pi)
            ctx.fill()
            ctx.set_source_rgba(*color, 0.3)
            ctx.set_line_width(1)
            ctx.move_to(lx + 6, legend_y - 3)
            ctx.line_to(lx + 14, legend_y - 3)
            ctx.stroke()
        ctx.set_source_rgba(*TEXT_COLOR, 0.35)
        ctx.move_to(lx + 12, legend_y)
        ctx.show_text(label)
        lx += ctx.text_extents(label).width + 26


def draw_velocity_trail(
    ctx: cairo.Context[cairo.ImageSurface],
    view: SolarView,
    body: CelestialBody,
    pos: Position,
) -> None:
    """Draw a short velocity trail behind planets."""
    if body.category != BodyCategory.PLANET:
        return
    color = body.color
    radius = body.display_radius_px
    sx, sy = view.au_to_screen(pos.x, pos.y)
    trail_scale = 80.0
    tx, ty = view.au_to_screen(
        pos.x - pos.vx * trail_scale, pos.y - pos.vy * trail_scale
    )
    grad = cairo.LinearGradient(sx, sy, tx, ty)
    grad.add_color_stop_rgba(0, *color, 0.3)
    grad.add_color_stop_rgba(1, *color, 0.0)
    ctx.set_source(grad)
    ctx.set_line_width(radius * 0.5)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(sx, sy)
    ctx.line_to(tx, ty)
    ctx.stroke()
