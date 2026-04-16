"""Tests for render output validation."""

from __future__ import annotations

import struct
import tempfile
from pathlib import Path

from solar_system_wallpaper.render.core import render_frame
from solar_system_wallpaper.types import BodyCategory, Position, RenderConfig


def _make_test_positions() -> dict[str, Position]:
    """Create minimal test positions for a few planets."""
    return {
        "Earth": Position(x=1.0, y=0.0, z=0.0, vx=0.0, vy=0.017, vz=0.0),
        "Mars": Position(x=-1.5, y=0.3, z=0.01, vx=0.01, vy=-0.013, vz=0.0),
        "Jupiter": Position(x=4.0, y=-3.0, z=-0.1, vx=0.005, vy=0.007, vz=0.0),
        "Saturn": Position(x=-8.0, y=-4.0, z=0.2, vx=0.003, vy=-0.004, vz=0.0),
        "Venus": Position(x=-0.5, y=0.5, z=0.01, vx=-0.01, vy=-0.02, vz=0.0),
        "Mercury": Position(x=0.3, y=-0.2, z=0.01, vx=0.02, vy=0.03, vz=0.0),
    }


def test_render_produces_valid_png() -> None:
    """Render a frame and verify it writes a valid PNG file."""
    positions = _make_test_positions()
    config = RenderConfig(width=640, height=360)
    surface = render_frame(positions, t=0.0, config=config)

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        surface.write_to_png(f.name)
        path = Path(f.name)

    assert path.exists()
    data = path.read_bytes()
    # PNG magic bytes
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    # Check IHDR chunk for correct dimensions
    _ihdr_length = struct.unpack(">I", data[8:12])[0]  # noqa: F841
    assert data[12:16] == b"IHDR"
    w = struct.unpack(">I", data[16:20])[0]
    h = struct.unpack(">I", data[20:24])[0]
    assert w == 640
    assert h == 360

    path.unlink()


def test_render_no_cosmetic() -> None:
    """Render with cosmetic effects disabled."""
    positions = _make_test_positions()
    config = RenderConfig(width=320, height=180, cosmetic=False)
    surface = render_frame(positions, t=0.0, config=config)
    assert surface.get_width() == 320
    assert surface.get_height() == 180


def test_render_filtered_categories() -> None:
    """Render with only planets selected."""
    positions = _make_test_positions()
    config = RenderConfig(
        width=320,
        height=180,
        categories=frozenset([BodyCategory.PLANET]),
    )
    surface = render_frame(positions, t=0.0, config=config)
    assert surface.get_width() == 320


def test_render_empty_positions() -> None:
    """Render with no positions should still produce a valid surface."""
    config = RenderConfig(width=320, height=180)
    surface = render_frame({}, t=0.0, config=config)
    assert surface.get_width() == 320
    assert surface.get_height() == 180
