"""Coordinate mapping from AU to screen pixels with power-law radial scaling."""

from __future__ import annotations

import math


class SolarView:
    """Maps heliocentric AU coordinates to screen pixels.

    Uses power-law radial scaling: r_px = max_r_px * (r_au / max_au)^0.4
    This stretches the inner solar system so Mercury-Mars aren't swallowed
    by the Sun, while still fitting Pluto comfortably on screen.
    """

    def __init__(self, width: int, height: int) -> None:
        self.w: int = width
        self.h: int = height
        self.cx: float = width * 0.42  # sun offset left for legend room
        self.cy: float = height * 0.50
        self.max_r_px: float = min(width, height) * 0.44
        self.max_au: float = 42.0  # show out to Pluto's orbit comfortably

    def au_to_radius(self, r_au: float) -> float:
        """Convert a radial distance in AU to pixel distance from center."""
        return self.max_r_px * (min(r_au, 200.0) / self.max_au) ** 0.4

    def au_to_screen(self, x_au: float, y_au: float) -> tuple[float, float]:
        """Convert heliocentric ecliptic (x, y) in AU to screen (px, py)."""
        r_au = math.sqrt(x_au ** 2 + y_au ** 2)
        if r_au < 1e-10:
            return (self.cx, self.cy)
        angle = math.atan2(y_au, x_au)
        r_px = self.au_to_radius(r_au)
        return (self.cx + r_px * math.cos(angle), self.cy - r_px * math.sin(angle))

    def orbit_radius_px(self, sma_au: float) -> float:
        """Get pixel radius for a circular orbit at the given semi-major axis."""
        return self.au_to_radius(sma_au)
