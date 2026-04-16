"""Grid, orbit rings, asteroid belt, and Kuiper belt rendering."""

from __future__ import annotations

import math
import random

import cairo

from solar_system_wallpaper.catalog import (
    BELT_COLOR,
    GRID_COLOR,
    KUIPER_COLOR,
    ORBIT_COLOR,
    TEXT_COLOR,
)
from solar_system_wallpaper.coordinates import SolarView


def draw_grid(ctx: cairo.Context[cairo.ImageSurface], view: SolarView) -> None:
    """Draw concentric AU distance rings with labels."""
    for au in [1, 2, 5, 10, 20, 30, 40]:
        r = view.orbit_radius_px(au)
        ctx.set_source_rgba(*GRID_COLOR, 0.25)
        ctx.set_line_width(0.5)
        ctx.arc(view.cx, view.cy, r, 0, 2 * math.pi)
        ctx.stroke()
        ctx.set_source_rgba(*TEXT_COLOR, 0.2)
        ctx.set_font_size(9)
        ctx.move_to(view.cx + r + 3, view.cy - 3)
        ctx.show_text(f"{au} AU")


def draw_asteroid_belt(
    ctx: cairo.Context[cairo.ImageSurface], view: SolarView, t: float
) -> None:
    """Draw a scattered band for the main asteroid belt (2.1-3.3 AU)."""
    rng = random.Random(123)
    for _ in range(900):
        r_au = 2.1 + rng.random() * 1.2
        angle = rng.random() * 2 * math.pi
        r_px = view.au_to_radius(r_au)
        x = view.cx + r_px * math.cos(angle)
        y = view.cy - r_px * math.sin(angle)
        size = rng.random() * 1.0 + 0.3
        alpha = rng.random() * 0.22 + 0.06
        ctx.set_source_rgba(*BELT_COLOR, alpha)
        ctx.arc(x, y, size, 0, 2 * math.pi)
        ctx.fill()


def draw_kuiper_belt(
    ctx: cairo.Context[cairo.ImageSurface], view: SolarView, t: float
) -> None:
    """Draw a subtle scattered band for the Kuiper belt (30-50 AU)."""
    rng = random.Random(456)
    for _ in range(400):
        r_au = 30 + rng.random() * 20
        angle = rng.random() * 2 * math.pi
        r_px = view.au_to_radius(r_au)
        x = view.cx + r_px * math.cos(angle)
        y = view.cy - r_px * math.sin(angle)
        size = rng.random() * 0.6 + 0.2
        alpha = rng.random() * 0.08 + 0.02
        ctx.set_source_rgba(*KUIPER_COLOR, alpha)
        ctx.arc(x, y, size, 0, 2 * math.pi)
        ctx.fill()


def draw_orbit_ring(
    ctx: cairo.Context[cairo.ImageSurface],
    view: SolarView,
    sma_au: float,
    alpha: float = 0.3,
) -> None:
    """Draw a single orbit ring at the given semi-major axis."""
    r = view.orbit_radius_px(sma_au)
    ctx.set_source_rgba(*ORBIT_COLOR, alpha)
    ctx.set_line_width(0.8)
    ctx.arc(view.cx, view.cy, r, 0, 2 * math.pi)
    ctx.stroke()
