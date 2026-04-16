"""Typed data structures for the solar system wallpaper renderer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class BodyCategory(str, Enum):
    """Categories of celestial bodies."""

    PLANET = "planet"
    DWARF = "dwarf"
    MOON = "moon"
    ASTEROID = "asteroid"
    COMET = "comet"
    SPACECRAFT = "spacecraft"


class EffectGroup(str, Enum):
    """Toggleable visual effect groups."""

    COSMETIC = "cosmetic"  # stars, nebulae, shooting_stars, milky_way
    INFORMATIONAL = "informational"  # orbit_rings, labels, belts, trails


# CLI-facing category filter names that map to internal BodyCategory values
CATEGORY_FILTERS: dict[str, list[BodyCategory]] = {
    "planets": [BodyCategory.PLANET],
    "dwarf_planets": [BodyCategory.DWARF],
    "moons": [BodyCategory.MOON],
    "asteroids": [BodyCategory.ASTEROID],
    "comets": [BodyCategory.COMET],
    "spacecraft": [BodyCategory.SPACECRAFT],
}


Color = tuple[float, float, float]


@dataclass(frozen=True)
class CelestialBody:
    """A celestial body in the catalog."""

    name: str
    horizons_cmd: str
    category: BodyCategory
    color: Color
    display_radius_px: float
    orbit_sma_au: float
    parent: str | None = None


@dataclass
class Position:
    """Heliocentric ecliptic position and velocity of a body."""

    x: float  # AU
    y: float  # AU
    z: float  # AU
    vx: float = 0.0  # AU/day
    vy: float = 0.0  # AU/day
    vz: float = 0.0  # AU/day
    timestamp: float = 0.0  # Unix epoch


@dataclass
class RenderConfig:
    """Configuration for rendering a single frame."""

    width: int = 2560
    height: int = 1440
    categories: frozenset[BodyCategory] = field(
        default_factory=lambda: frozenset(BodyCategory)
    )
    cosmetic: bool = True
    informational: bool = True
    show_labels: bool = True
    show_info_panel: bool = True


@dataclass
class TimelapseConfig:
    """Configuration for timelapse video generation."""

    start_date: str  # ISO date string
    num_days: int
    step_days: int = 1
    width: int = 2560
    height: int = 1440
    fps: int = 30
    output_path: str = "timelapse.mp4"
    categories: frozenset[BodyCategory] = field(
        default_factory=lambda: frozenset(BodyCategory)
    )
    cosmetic: bool = True
    informational: bool = True
    show_labels: bool = True
