"""Background sky rendering: milky way, nebulae, stars, shooting stars."""

from __future__ import annotations

import math
import random

import cairo


def draw_milky_way(ctx: cairo.Context[cairo.ImageSurface], w: int, h: int) -> None:
    """Draw a visible milky way band across the background.

    A diffuse luminous band running diagonally, built from many
    overlapping translucent ellipses to simulate galactic dust lanes.
    """
    rng = random.Random(777)

    band_cx = w * 0.5
    band_cy = h * 0.5
    band_angle = -0.35

    ctx.save()
    ctx.translate(band_cx, band_cy)
    ctx.rotate(band_angle)

    # Large diffuse core glow
    for _ in range(120):
        ox = rng.gauss(0, w * 0.30)
        oy = rng.gauss(0, h * 0.07)
        rx = rng.uniform(60, 250)
        ry = rng.uniform(20, 70)
        r = 0.12 + rng.random() * 0.08
        g = 0.14 + rng.random() * 0.08
        b = 0.20 + rng.random() * 0.10
        a = rng.uniform(0.03, 0.08)

        ctx.set_source_rgba(r, g, b, a)
        ctx.save()
        ctx.translate(ox, oy)
        ctx.scale(rx, ry)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.fill()

    # Dense star clusters within the band
    for _ in range(500):
        sx = rng.gauss(0, w * 0.32)
        sy = rng.gauss(0, h * 0.05)
        size = rng.uniform(0.3, 1.0)
        brightness = rng.uniform(0.10, 0.35)
        ctx.set_source_rgba(brightness, brightness, brightness * 1.15, 1)
        ctx.arc(sx, sy, size, 0, 2 * math.pi)
        ctx.fill()

    ctx.restore()


def draw_nebulae(ctx: cairo.Context[cairo.ImageSurface], w: int, h: int, t: float) -> None:
    """Draw subtle nebula patches with colored gas clouds."""
    rng = random.Random(314)

    nebulae: list[tuple[float, float, int, tuple[float, float, float], float]] = [
        (0.08, 0.15, 180, (0.35, 0.06, 0.08), 0.5),
        (0.88, 0.80, 140, (0.10, 0.06, 0.30), -0.3),
        (0.15, 0.82, 120, (0.05, 0.18, 0.22), 0.8),
        (0.92, 0.12, 150, (0.22, 0.05, 0.18), -0.6),
        (0.05, 0.50, 100, (0.12, 0.10, 0.28), 0.2),
    ]

    for xf, yf, base_size, color, rot in nebulae:
        cx = w * xf
        cy = h * yf
        drift_x = 3 * math.sin(t * 0.1 + xf * 10)
        drift_y = 2 * math.cos(t * 0.1 + yf * 10)

        ctx.save()
        ctx.translate(cx + drift_x, cy + drift_y)
        ctx.rotate(rot + t * 0.02)

        for _ in range(40):
            ox = rng.gauss(0, base_size * 0.45)
            oy = rng.gauss(0, base_size * 0.35)
            rx = rng.uniform(base_size * 0.4, base_size * 1.0)
            ry = rng.uniform(base_size * 0.25, base_size * 0.6)
            cr = min(1.0, color[0] + rng.uniform(-0.03, 0.05))
            cg = min(1.0, color[1] + rng.uniform(-0.03, 0.05))
            cb = min(1.0, color[2] + rng.uniform(-0.03, 0.05))
            a = rng.uniform(0.03, 0.09)

            grad = cairo.RadialGradient(ox, oy, 0, ox, oy, rx)
            grad.add_color_stop_rgba(0, cr, cg, cb, a * 2.0)
            grad.add_color_stop_rgba(0.4, cr, cg, cb, a * 1.0)
            grad.add_color_stop_rgba(0.7, cr, cg, cb, a * 0.3)
            grad.add_color_stop_rgba(1, cr, cg, cb, 0)
            ctx.set_source(grad)
            ctx.save()
            ctx.translate(ox, oy)
            ctx.scale(rx, ry)
            ctx.arc(0, 0, 1, 0, 2 * math.pi)
            ctx.restore()
            ctx.fill()

        ctx.restore()


def draw_shooting_stars(ctx: cairo.Context[cairo.ImageSurface], w: int, h: int, t: float) -> None:
    """Draw 1-3 shooting stars per snapshot with glowing trails."""
    rng = random.Random(int(t * 1000) + 99)
    count = rng.randint(1, 3)

    for _ in range(count):
        sx = rng.uniform(w * 0.05, w * 0.95)
        sy = rng.uniform(h * 0.03, h * 0.55)

        angle = rng.uniform(-0.8, 0.8) + math.pi * 0.5
        if rng.random() > 0.5:
            angle = math.pi - angle

        length = rng.uniform(60, 180)
        ex = sx + length * math.cos(angle)
        ey = sy + length * math.sin(angle)

        progress = rng.uniform(0.2, 0.9)

        head_x = sx + (ex - sx) * progress
        head_y = sy + (ey - sy) * progress

        trail_sx = sx + (ex - sx) * max(0.0, progress - 0.7)
        trail_sy = sy + (ey - sy) * max(0.0, progress - 0.7)

        grad = cairo.LinearGradient(trail_sx, trail_sy, head_x, head_y)
        grad.add_color_stop_rgba(0, 0.5, 0.8, 1.0, 0.0)
        grad.add_color_stop_rgba(0.6, 0.7, 0.9, 1.0, 0.15)
        grad.add_color_stop_rgba(1.0, 1.0, 1.0, 1.0, 0.6)
        ctx.set_source(grad)
        ctx.set_line_width(2.0)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(trail_sx, trail_sy)
        ctx.line_to(head_x, head_y)
        ctx.stroke()

        grad2 = cairo.LinearGradient(trail_sx, trail_sy, head_x, head_y)
        grad2.add_color_stop_rgba(0, 1.0, 1.0, 1.0, 0.0)
        grad2.add_color_stop_rgba(0.7, 1.0, 1.0, 1.0, 0.1)
        grad2.add_color_stop_rgba(1.0, 1.0, 1.0, 1.0, 0.8)
        ctx.set_source(grad2)
        ctx.set_line_width(0.8)
        ctx.move_to(trail_sx, trail_sy)
        ctx.line_to(head_x, head_y)
        ctx.stroke()

        head_grad = cairo.RadialGradient(head_x, head_y, 0, head_x, head_y, 4)
        head_grad.add_color_stop_rgba(0, 1, 1, 1, 0.7)
        head_grad.add_color_stop_rgba(1, 0.5, 0.8, 1.0, 0)
        ctx.set_source(head_grad)
        ctx.arc(head_x, head_y, 4, 0, 2 * math.pi)
        ctx.fill()


def draw_stars(ctx: cairo.Context[cairo.ImageSurface], w: int, h: int, t: float) -> None:
    """Rich star field with color temperature, brightness layers, and twinkling."""
    # Layer 1: Dim background dust (800 tiny dots)
    rng = random.Random(42)
    for _ in range(800):
        sx = rng.random() * w
        sy = rng.random() * h
        brightness = rng.random() * 0.08 + 0.02
        size = rng.random() * 0.6 + 0.2
        ctx.set_source_rgba(brightness, brightness, brightness * 1.05, 1)
        ctx.arc(sx, sy, size, 0, 2 * math.pi)
        ctx.fill()

    # Layer 2: Mid-brightness stars (400, with color temperature)
    rng2 = random.Random(84)
    for _ in range(400):
        sx = rng2.random() * w
        sy = rng2.random() * h
        brightness = rng2.random() * 0.25 + 0.08
        size = rng2.random() * 1.0 + 0.3

        freq = rng2.random() * 0.3 + 0.08
        phase_off = rng2.random() * 6.28
        twinkle = 0.65 + 0.35 * math.sin(t * freq + phase_off)
        b = brightness * twinkle

        temp = rng2.random()
        if temp < 0.3:
            ctx.set_source_rgba(b * 0.85, b * 0.92, b * 1.15, 1)
        elif temp < 0.7:
            ctx.set_source_rgba(b, b, b * 1.05, 1)
        else:
            ctx.set_source_rgba(b * 1.1, b * 0.95, b * 0.7, 1)

        ctx.arc(sx, sy, size, 0, 2 * math.pi)
        ctx.fill()

    # Layer 3: Bright feature stars (40, with visible glow halos)
    rng3 = random.Random(126)
    for _ in range(40):
        sx = rng3.random() * w
        sy = rng3.random() * h
        brightness = rng3.random() * 0.35 + 0.35
        size = rng3.random() * 1.8 + 1.0

        freq = rng3.random() * 0.25 + 0.06
        phase_off = rng3.random() * 6.28
        twinkle = 0.5 + 0.5 * math.sin(t * freq + phase_off)
        b = brightness * twinkle

        temp = rng3.random()
        if temp < 0.25:
            sr, sg, sb = b * 0.7, b * 0.85, b * 1.3
        elif temp < 0.5:
            sr, sg, sb = b * 1.2, b * 0.85, b * 0.5
        elif temp < 0.75:
            sr, sg, sb = b * 1.15, b * 0.5, b * 0.4
        else:
            sr, sg, sb = b * 1.05, b * 1.05, b * 1.1

        glow_r = size * 5
        grad = cairo.RadialGradient(sx, sy, 0, sx, sy, glow_r)
        grad.add_color_stop_rgba(0, sr, sg, sb, 0.35 * twinkle)
        grad.add_color_stop_rgba(0.3, sr, sg, sb, 0.12 * twinkle)
        grad.add_color_stop_rgba(1, sr, sg, sb, 0)
        ctx.set_source(grad)
        ctx.arc(sx, sy, glow_r, 0, 2 * math.pi)
        ctx.fill()

        ctx.set_source_rgba(min(1.0, sr * 1.3), min(1.0, sg * 1.3), min(1.0, sb * 1.3), 1)
        ctx.arc(sx, sy, size, 0, 2 * math.pi)
        ctx.fill()

        ctx.set_source_rgba(sr, sg, sb, 1)
        ctx.arc(sx, sy, size, 0, 2 * math.pi)
        ctx.fill()
