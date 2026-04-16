"""Body rendering: sun, planets, moons, comets, spacecraft."""

from __future__ import annotations

import math

import cairo

from solar_system_wallpaper.catalog import SUN_COLOR, SUN_RADIUS_PX, TEXT_COLOR
from solar_system_wallpaper.coordinates import SolarView
from solar_system_wallpaper.types import BodyCategory, CelestialBody, Color, Position


def draw_sun(ctx: cairo.Context[cairo.ImageSurface], view: SolarView, t: float) -> None:
    """Draw the Sun with animated corona glow."""
    sr = SUN_RADIUS_PX
    pulse = 1.0 + 0.03 * math.sin(t * 0.15)

    # Subtle outer glow
    for i in range(5):
        r = (sr + i * sr * 0.35) * pulse
        cr = 1.0
        cg = 0.85 - i * 0.06
        cb = 0.3 - i * 0.04
        alpha = 0.02 * (1 - i / 5)
        ctx.set_source_rgba(cr, cg, max(0.0, cb), alpha)
        ctx.arc(view.cx, view.cy, r, 0, 2 * math.pi)
        ctx.fill()

    # Core body
    grad = cairo.RadialGradient(view.cx, view.cy, 0, view.cx, view.cy, sr * pulse)
    grad.add_color_stop_rgba(0, 1.0, 0.98, 0.92, 1.0)
    grad.add_color_stop_rgba(0.5, 1.0, 0.90, 0.65, 1.0)
    grad.add_color_stop_rgba(0.8, *SUN_COLOR, 0.9)
    grad.add_color_stop_rgba(1.0, 0.9, 0.50, 0.1, 0.6)
    ctx.set_source(grad)
    ctx.arc(view.cx, view.cy, sr * pulse, 0, 2 * math.pi)
    ctx.fill()


def draw_body(
    ctx: cairo.Context[cairo.ImageSurface],
    view: SolarView,
    body: CelestialBody,
    pos: Position,
    t: float,
    show_labels: bool,
) -> None:
    """Draw any body (planet, dwarf, moon, asteroid, comet, spacecraft)."""
    color = body.color
    radius = body.display_radius_px
    cat = body.category
    sx, sy = view.au_to_screen(pos.x, pos.y)

    # Comet tail
    if cat == BodyCategory.COMET:
        _draw_comet_tail(ctx, view, sx, sy, pos.x, pos.y, color, t)

    # Spacecraft icon (diamond instead of circle)
    if cat == BodyCategory.SPACECRAFT:
        _draw_spacecraft(ctx, sx, sy, color, radius, body.name, show_labels)
        return

    # Moon: draw smaller, no glow, label offset
    if cat == BodyCategory.MOON:
        ctx.set_source_rgba(*color, 0.8)
        ctx.arc(sx, sy, radius, 0, 2 * math.pi)
        ctx.fill()
        if show_labels:
            ctx.set_source_rgba(*TEXT_COLOR, 0.45)
            ctx.set_font_size(8)
            ctx.select_font_face(
                "monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL
            )
            ext = ctx.text_extents(body.name)
            ctx.move_to(sx - ext.width / 2, sy + radius + 10)
            ctx.show_text(body.name)
        return

    # Glow (planets + dwarf planets) with pulsing
    glow_layers = 4 if cat == BodyCategory.PLANET else 2
    glow_spread = 4.0 if cat == BodyCategory.PLANET else 2.5
    glow_pulse = 0.85 + 0.15 * math.sin(t * 0.12 + hash(body.name) % 100 * 0.1)
    for i in range(glow_layers):
        r = (radius + (i + 1) * glow_spread) * glow_pulse
        alpha = 0.15 * (1 - i / glow_layers) * glow_pulse
        ctx.set_source_rgba(*color, alpha)
        ctx.arc(sx, sy, r, 0, 2 * math.pi)
        ctx.fill()

    # Body gradient
    grad = cairo.RadialGradient(
        sx - radius * 0.3, sy - radius * 0.3, 0, sx, sy, radius
    )
    grad.add_color_stop_rgba(
        0,
        min(color[0] + 0.3, 1.0),
        min(color[1] + 0.3, 1.0),
        min(color[2] + 0.3, 1.0),
        1,
    )
    grad.add_color_stop_rgba(1, color[0] * 0.7, color[1] * 0.7, color[2] * 0.7, 1)
    ctx.set_source(grad)
    ctx.arc(sx, sy, radius, 0, 2 * math.pi)
    ctx.fill()

    # Saturn's ring
    if body.name == "Saturn":
        ctx.save()
        ctx.set_source_rgba(*color, 0.5)
        ctx.set_line_width(1.5)
        ctx.save()
        ctx.translate(sx, sy)
        ctx.scale(1, 0.35)
        ctx.arc(0, 0, radius * 2.2, 0, 2 * math.pi)
        ctx.restore()
        ctx.stroke()
        ctx.restore()

    # Label
    if show_labels:
        font_size = 12 if cat == BodyCategory.PLANET else 10
        label_alpha = 0.75 if cat == BodyCategory.PLANET else 0.55
        ctx.set_source_rgba(*TEXT_COLOR, label_alpha)
        ctx.set_font_size(font_size)
        ctx.select_font_face(
            "monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL
        )
        ext = ctx.text_extents(body.name)
        ctx.move_to(sx - ext.width / 2, sy + radius + 14)
        ctx.show_text(body.name)


def _draw_comet_tail(
    ctx: cairo.Context[cairo.ImageSurface],
    view: SolarView,
    sx: float,
    sy: float,
    x_au: float,
    y_au: float,
    color: Color,
    t: float,
) -> None:
    """Draw a comet tail pointing away from the Sun."""
    r_au = math.sqrt(x_au ** 2 + y_au ** 2)
    if r_au < 0.01:
        return

    # Tail length in pixels (longer when closer to sun)
    tail_len = max(20.0, min(80.0, 60.0 / max(r_au, 0.5)))

    # Screen direction: outward from sun center
    tail_dx = sx - view.cx
    tail_dy = sy - view.cy
    td = math.sqrt(tail_dx ** 2 + tail_dy ** 2)
    if td < 1:
        return
    tail_dx /= td
    tail_dy /= td
    tx = sx + tail_len * tail_dx
    ty = sy + tail_len * tail_dy

    # Fuzzy tail
    grad = cairo.LinearGradient(sx, sy, tx, ty)
    grad.add_color_stop_rgba(0, *color, 0.5)
    grad.add_color_stop_rgba(0.3, *color, 0.2)
    grad.add_color_stop_rgba(1, *color, 0.0)
    ctx.set_source(grad)
    ctx.set_line_width(4)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(sx, sy)
    ctx.line_to(tx, ty)
    ctx.stroke()

    # Thinner bright core
    grad2 = cairo.LinearGradient(sx, sy, tx, ty)
    grad2.add_color_stop_rgba(0, 1, 1, 1, 0.6)
    grad2.add_color_stop_rgba(0.2, *color, 0.3)
    grad2.add_color_stop_rgba(1, *color, 0.0)
    ctx.set_source(grad2)
    ctx.set_line_width(1.5)
    ctx.move_to(sx, sy)
    ctx.line_to(tx, ty)
    ctx.stroke()


def _draw_spacecraft(
    ctx: cairo.Context[cairo.ImageSurface],
    sx: float,
    sy: float,
    color: Color,
    radius: float,
    name: str,
    show_labels: bool,
) -> None:
    """Draw spacecraft as a small diamond with a label."""
    r = radius + 1
    ctx.set_source_rgba(*color, 0.85)
    ctx.move_to(sx, sy - r)
    ctx.line_to(sx + r, sy)
    ctx.line_to(sx, sy + r)
    ctx.line_to(sx - r, sy)
    ctx.close_path()
    ctx.fill()

    # Pulsing signal rings
    for i in range(2):
        ri = r + 3 + i * 3
        ctx.set_source_rgba(*color, 0.15 - i * 0.05)
        ctx.set_line_width(0.5)
        ctx.arc(sx, sy, ri, 0, 2 * math.pi)
        ctx.stroke()

    # Label
    if show_labels:
        ctx.set_source_rgba(*color, 0.6)
        ctx.set_font_size(9)
        ctx.select_font_face(
            "monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL
        )
        ext = ctx.text_extents(name)
        ctx.move_to(sx - ext.width / 2, sy + r + 12)
        ctx.show_text(name)
