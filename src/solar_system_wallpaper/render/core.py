"""Core rendering: compose all layers into a final frame."""

from __future__ import annotations

from datetime import datetime

import cairo

from solar_system_wallpaper.catalog import (
    BG_COLOR,
    DRAW_ORDER,
    OBJECTS,
    ORBIT_RINGS,
)
from solar_system_wallpaper.coordinates import SolarView
from solar_system_wallpaper.render.bodies import draw_body, draw_sun
from solar_system_wallpaper.render.grid import (
    draw_asteroid_belt,
    draw_grid,
    draw_kuiper_belt,
    draw_orbit_ring,
)
from solar_system_wallpaper.render.info import draw_info_panel, draw_velocity_trail
from solar_system_wallpaper.render.sky import (
    draw_milky_way,
    draw_nebulae,
    draw_shooting_stars,
    draw_stars,
)
from solar_system_wallpaper.types import BodyCategory, Position, RenderConfig


def render_frame(
    positions: dict[str, Position],
    t: float,
    config: RenderConfig | None = None,
    cosmetic_t: float | None = None,
    display_time: datetime | None = None,
) -> cairo.ImageSurface:
    """Render a complete solar system frame.

    Args:
        positions: Body name -> Position mapping.
        t: Time value for animation effects (star twinkling, glow pulse).
        config: Render configuration. Uses defaults if None.
        cosmetic_t: Override for animation time. When set, used for all
                    cosmetic effects instead of t. Useful for timelapse to
                    prevent strobing from sin() aliasing across time jumps.
        display_time: The datetime to show in the info panel. Defaults to now.

    Returns:
        A Cairo ImageSurface with the rendered frame.
    """
    if config is None:
        config = RenderConfig()

    w = config.width
    h = config.height
    anim_t = cosmetic_t if cosmetic_t is not None else t

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surface)
    view = SolarView(w, h)

    # Background
    ctx.set_source_rgb(*BG_COLOR)
    ctx.paint()

    # Cosmetic sky layers
    if config.cosmetic:
        draw_milky_way(ctx, w, h)
        draw_nebulae(ctx, w, h, anim_t)
        draw_stars(ctx, w, h, anim_t)
        draw_shooting_stars(ctx, w, h, anim_t)

    # Informational grid and belts
    if config.informational:
        draw_grid(ctx, view)
        draw_asteroid_belt(ctx, view, anim_t)
        draw_kuiper_belt(ctx, view, anim_t)

        # Orbit rings (planets)
        for _name, sma in ORBIT_RINGS.items():
            draw_orbit_ring(ctx, view, sma)

        # Dwarf planet orbit rings (dimmer)
        for _name, body in OBJECTS.items():
            if body.category == BodyCategory.DWARF and body.orbit_sma_au > 0:
                draw_orbit_ring(ctx, view, body.orbit_sma_au, alpha=0.15)

    # Sun
    draw_sun(ctx, view, anim_t)

    # Draw bodies by category order (back to front)
    for cat in DRAW_ORDER:
        if cat not in config.categories:
            continue
        for name, body in OBJECTS.items():
            if body.category != cat:
                continue
            if name not in positions:
                continue
            pos = positions[name]

            # Velocity trail (informational layer)
            if config.informational:
                draw_velocity_trail(ctx, view, body, pos)

            draw_body(ctx, view, body, pos, anim_t, config.show_labels)

    # Info panel
    if config.show_info_panel and config.informational:
        draw_info_panel(ctx, positions, anim_t, w, h, display_time)

    return surface
