"""Celestial body catalog with 61 objects and their visual properties.

Data sources: NASA planetary fact sheets for radii, JPL Horizons for
orbital elements. Colors are hand-tuned for visual clarity on dark backgrounds.
"""

from __future__ import annotations

from solar_system_wallpaper.types import BodyCategory, CelestialBody, Color

# ---------------------------------------------------------------------------
# Real equatorial radii in km (NASA planetary fact sheets)
# ---------------------------------------------------------------------------

REAL_RADII_KM: dict[str, float] = {
    # Planets
    "Mercury": 2439.7,
    "Venus": 6051.8,
    "Earth": 6371.0,
    "Mars": 3389.5,
    "Jupiter": 69911.0,
    "Saturn": 58232.0,
    "Uranus": 25362.0,
    "Neptune": 24622.0,
    # Dwarf planets
    "Pluto": 1188.3,
    "Ceres": 473.0,
    "Eris": 1163.0,
    "Haumea": 816.0,
    "Makemake": 715.0,
    # Moons - Earth
    "Moon": 1737.4,
    # Moons - Mars
    "Phobos": 11.1,
    "Deimos": 6.2,
    # Moons - Jupiter (Galilean)
    "Io": 1821.6,
    "Europa": 1560.8,
    "Ganymede": 2634.1,
    "Callisto": 2410.3,
    # Moons - Saturn
    "Mimas": 198.2,
    "Enceladus": 252.1,
    "Tethys": 531.0,
    "Dione": 561.4,
    "Rhea": 763.8,
    "Titan": 2574.7,
    "Hyperion": 135.0,
    "Iapetus": 734.5,
    # Moons - Uranus
    "Miranda": 235.8,
    "Ariel": 578.9,
    "Umbriel": 584.7,
    "Titania": 788.9,
    "Oberon": 761.4,
    # Moons - Neptune
    "Triton": 1353.4,
    # Moons - Pluto
    "Charon": 606.0,
    # Asteroids (mean radius)
    "Vesta": 262.7,
    "Pallas": 256.0,
    "Juno": 127.0,
    "Hygiea": 217.0,
    "Psyche": 113.0,
    "Eros": 8.4,
    "Bennu": 0.245,
    "Apophis": 0.185,
    "Ida": 15.7,
    "Lutetia": 49.0,
    "Itokawa": 0.165,
}


def _compute_display_radius(name: str, cat: BodyCategory) -> float:
    """Compute pixel radius from real radius using cube-root scaling.

    Cube root compresses the huge range (Jupiter is 29x Mercury) into
    something visible (becomes ~3x), then we scale so Earth ~ 8px.
    Minimum 1.5px so tiny things remain visible.
    """
    if cat in (BodyCategory.COMET, BodyCategory.SPACECRAFT):
        return 2.5  # fixed, no real size

    real_km = REAL_RADII_KM.get(name)
    if not real_km:
        return 2.0

    # Cube-root scaling: px = scale * radius_km^(1/3)
    # Calibrate: Earth (6371 km) -> 8 px => scale = 8 / 6371^(1/3) = 0.431
    scale = 0.431
    px = scale * (real_km ** (1.0 / 3.0))
    return max(1.5, px)


# Sun radius for reference: 695,700 km
SUN_RADIUS_PX: float = 0.431 * (695700.0 ** (1.0 / 3.0))  # ~38 px


# ---------------------------------------------------------------------------
# Visual style constants
# ---------------------------------------------------------------------------

BG_COLOR: Color = (0.02, 0.02, 0.06)
GRID_COLOR: Color = (0.08, 0.08, 0.15)
ORBIT_COLOR: Color = (0.12, 0.14, 0.22)
TEXT_COLOR: Color = (0.55, 0.58, 0.70)
SUN_COLOR: Color = (1.0, 0.85, 0.3)
TITLE_COLOR: Color = (0.35, 0.38, 0.50)
BELT_COLOR: Color = (0.15, 0.14, 0.12)
KUIPER_COLOR: Color = (0.10, 0.10, 0.14)

# Category display labels for the legend
CAT_LABELS: dict[BodyCategory, str] = {
    BodyCategory.PLANET: "PLANETS",
    BodyCategory.DWARF: "DWARF PLANETS",
    BodyCategory.MOON: "MOONS",
    BodyCategory.ASTEROID: "ASTEROIDS",
    BodyCategory.COMET: "COMETS",
    BodyCategory.SPACECRAFT: "SPACECRAFT",
}

# Draw ordering (back to front)
DRAW_ORDER: list[BodyCategory] = [
    BodyCategory.COMET,
    BodyCategory.ASTEROID,
    BodyCategory.SPACECRAFT,
    BodyCategory.DWARF,
    BodyCategory.MOON,
    BodyCategory.PLANET,
]

# Category ordering for info panel
CATEGORIES: list[BodyCategory] = [
    BodyCategory.PLANET,
    BodyCategory.DWARF,
    BodyCategory.MOON,
    BodyCategory.ASTEROID,
    BodyCategory.COMET,
    BodyCategory.SPACECRAFT,
]


def _body(
    name: str,
    cmd: str,
    cat: BodyCategory,
    color: Color,
    sma: float,
    parent: str | None = None,
) -> CelestialBody:
    """Helper to build a CelestialBody with computed display radius."""
    return CelestialBody(
        name=name,
        horizons_cmd=cmd,
        category=cat,
        color=color,
        display_radius_px=_compute_display_radius(name, cat),
        orbit_sma_au=sma,
        parent=parent,
    )


P = BodyCategory.PLANET
D = BodyCategory.DWARF
M = BodyCategory.MOON
A = BodyCategory.ASTEROID
C = BodyCategory.COMET
S = BodyCategory.SPACECRAFT

# ---------------------------------------------------------------------------
# Object catalog (61 bodies)
# ---------------------------------------------------------------------------

OBJECTS: dict[str, CelestialBody] = {b.name: b for b in [
    # --- Planets ---
    _body("Mercury", "199", P, (0.70, 0.65, 0.60), 0.387),
    _body("Venus", "299", P, (0.90, 0.80, 0.50), 0.723),
    _body("Earth", "399", P, (0.20, 0.50, 0.90), 1.0),
    _body("Mars", "499", P, (0.85, 0.35, 0.20), 1.524),
    _body("Jupiter", "599", P, (0.80, 0.70, 0.50), 5.203),
    _body("Saturn", "699", P, (0.85, 0.75, 0.45), 9.537),
    _body("Uranus", "799", P, (0.50, 0.80, 0.85), 19.19),
    _body("Neptune", "899", P, (0.25, 0.40, 0.85), 30.07),
    # --- Dwarf planets ---
    _body("Pluto", "999", D, (0.75, 0.65, 0.55), 39.48),
    _body("Ceres", "1;", D, (0.60, 0.58, 0.55), 2.77),
    _body("Eris", "136199;", D, (0.70, 0.70, 0.75), 67.7),
    _body("Haumea", "136108;", D, (0.65, 0.55, 0.50), 43.2),
    _body("Makemake", "136472;", D, (0.72, 0.60, 0.50), 45.8),
    # --- Moons: Earth ---
    _body("Moon", "301", M, (0.65, 0.65, 0.65), 0.0, parent="Earth"),
    # --- Moons: Mars ---
    _body("Phobos", "401", M, (0.55, 0.50, 0.45), 0.0, parent="Mars"),
    _body("Deimos", "402", M, (0.50, 0.48, 0.44), 0.0, parent="Mars"),
    # --- Moons: Jupiter (Galilean) ---
    _body("Io", "501", M, (0.85, 0.80, 0.35), 0.0, parent="Jupiter"),
    _body("Europa", "502", M, (0.70, 0.65, 0.55), 0.0, parent="Jupiter"),
    _body("Ganymede", "503", M, (0.60, 0.55, 0.50), 0.0, parent="Jupiter"),
    _body("Callisto", "504", M, (0.45, 0.42, 0.40), 0.0, parent="Jupiter"),
    # --- Moons: Saturn ---
    _body("Mimas", "601", M, (0.68, 0.68, 0.68), 0.0, parent="Saturn"),
    _body("Enceladus", "602", M, (0.80, 0.82, 0.85), 0.0, parent="Saturn"),
    _body("Tethys", "603", M, (0.70, 0.70, 0.68), 0.0, parent="Saturn"),
    _body("Dione", "604", M, (0.65, 0.65, 0.63), 0.0, parent="Saturn"),
    _body("Rhea", "605", M, (0.62, 0.62, 0.60), 0.0, parent="Saturn"),
    _body("Titan", "606", M, (0.80, 0.65, 0.30), 0.0, parent="Saturn"),
    _body("Hyperion", "607", M, (0.58, 0.55, 0.50), 0.0, parent="Saturn"),
    _body("Iapetus", "608", M, (0.50, 0.45, 0.40), 0.0, parent="Saturn"),
    # --- Moons: Uranus ---
    _body("Miranda", "705", M, (0.60, 0.62, 0.65), 0.0, parent="Uranus"),
    _body("Ariel", "701", M, (0.65, 0.67, 0.70), 0.0, parent="Uranus"),
    _body("Umbriel", "702", M, (0.48, 0.48, 0.50), 0.0, parent="Uranus"),
    _body("Titania", "703", M, (0.58, 0.60, 0.62), 0.0, parent="Uranus"),
    _body("Oberon", "704", M, (0.55, 0.55, 0.57), 0.0, parent="Uranus"),
    # --- Moons: Neptune ---
    _body("Triton", "801", M, (0.60, 0.70, 0.75), 0.0, parent="Neptune"),
    # --- Moons: Pluto ---
    _body("Charon", "901", M, (0.55, 0.52, 0.50), 0.0, parent="Pluto"),
    # --- Asteroids ---
    _body("Vesta", "4;", A, (0.65, 0.60, 0.55), 2.36),
    _body("Pallas", "2;", A, (0.55, 0.55, 0.50), 2.77),
    _body("Juno", "3;", A, (0.60, 0.55, 0.50), 2.67),
    _body("Hygiea", "10;", A, (0.50, 0.48, 0.45), 3.14),
    _body("Psyche", "16;", A, (0.70, 0.65, 0.55), 2.92),
    _body("Eros", "433;", A, (0.75, 0.60, 0.45), 1.46),
    _body("Bennu", "101955;", A, (0.45, 0.43, 0.40), 1.13),
    _body("Apophis", "99942;", A, (0.80, 0.40, 0.35), 0.92),
    _body("Ida", "243;", A, (0.58, 0.55, 0.50), 2.86),
    _body("Lutetia", "21;", A, (0.52, 0.50, 0.48), 2.44),
    _body("Itokawa", "25143;", A, (0.60, 0.55, 0.45), 1.32),
    # --- Comets ---
    _body("Halley", "COMNAM=Halley;CAP", C, (0.50, 0.75, 0.85), 0.0),
    _body("Tsuchinshan-ATLAS", "DES=2023 A3;CAP", C, (0.45, 0.80, 0.70), 0.0),
    _body("C/2024 G3", "DES=2024 G3;CAP", C, (0.55, 0.75, 0.80), 0.0),
    _body("Encke", "DES=2P;CAP", C, (0.60, 0.70, 0.80), 0.0),
    _body("Tempel 1", "DES=9P;CAP", C, (0.55, 0.65, 0.75), 0.0),
    _body("Wild 2", "DES=81P;CAP", C, (0.50, 0.70, 0.75), 0.0),
    _body("67P C-G", "DES=67P;CAP", C, (0.48, 0.68, 0.72), 0.0),
    _body("Hale-Bopp", "COMNAM=Hale-Bopp;CAP", C, (0.55, 0.80, 0.90), 0.0),
    _body("NEOWISE", "DES=2020 F3;CAP", C, (0.50, 0.75, 0.65), 0.0),
    _body("Leonard", "DES=2021 A1;CAP", C, (0.45, 0.72, 0.78), 0.0),
    # --- Spacecraft ---
    _body("Voyager 1", "-31", S, (0.40, 0.90, 0.40), 0.0),
    _body("Voyager 2", "-32", S, (0.40, 0.85, 0.50), 0.0),
    _body("New Horizons", "-98", S, (0.50, 0.80, 0.90), 0.0),
    _body("JWST", "-170", S, (0.90, 0.70, 0.90), 0.0),
    _body("Pioneer 10", "-23", S, (0.45, 0.85, 0.45), 0.0),
    _body("Pioneer 11", "-24", S, (0.50, 0.80, 0.45), 0.0),
    _body("Parker Solar Probe", "-96", S, (0.95, 0.80, 0.30), 0.0),
    _body("Juno Probe", "-61", S, (0.60, 0.75, 0.90), 0.0),
    _body("SOHO", "-21", S, (0.90, 0.85, 0.50), 0.0),
    _body("OSIRIS-REx", "-64", S, (0.70, 0.80, 0.60), 0.0),
    _body("Lucy", "-49", S, (0.65, 0.75, 0.85), 0.0),
    _body("STEREO-A", "-234", S, (0.85, 0.70, 0.50), 0.0),
    _body("Mars Odyssey", "-53", S, (0.80, 0.55, 0.40), 0.0),
    _body("MRO", "-74", S, (0.75, 0.60, 0.45), 0.0),
]}

# Orbit rings only for planets with sma > 0
ORBIT_RINGS: dict[str, float] = {
    name: body.orbit_sma_au
    for name, body in OBJECTS.items()
    if body.orbit_sma_au > 0 and body.category == BodyCategory.PLANET
}
