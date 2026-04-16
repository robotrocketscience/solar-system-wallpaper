"""Tests for SolarView coordinate mapping."""

from __future__ import annotations

from solar_system_wallpaper.coordinates import SolarView


def test_origin_maps_to_center() -> None:
    """(0, 0) AU should map to the Sun center on screen."""
    view = SolarView(2560, 1440)
    sx, sy = view.au_to_screen(0.0, 0.0)
    assert abs(sx - view.cx) < 1e-6
    assert abs(sy - view.cy) < 1e-6


def test_au_to_radius_scaling() -> None:
    """Verify the power-law scaling: r_px = max_r_px * (r_au / max_au)^0.4."""
    view = SolarView(2560, 1440)
    r_au = 1.0
    expected = view.max_r_px * (r_au / view.max_au) ** 0.4
    actual = view.au_to_radius(r_au)
    assert abs(actual - expected) < 1e-6


def test_further_objects_have_larger_radius() -> None:
    """Objects further from the Sun should have larger pixel radii."""
    view = SolarView(2560, 1440)
    r1 = view.au_to_radius(1.0)
    r5 = view.au_to_radius(5.0)
    r30 = view.au_to_radius(30.0)
    assert r1 < r5 < r30


def test_au_to_screen_positive_x() -> None:
    """Positive x_au should map to the right of center."""
    view = SolarView(2560, 1440)
    sx, sy = view.au_to_screen(5.0, 0.0)
    assert sx > view.cx
    assert abs(sy - view.cy) < 1e-6


def test_au_to_screen_positive_y() -> None:
    """Positive y_au should map above center (lower pixel y)."""
    view = SolarView(2560, 1440)
    sx, sy = view.au_to_screen(0.0, 5.0)
    assert abs(sx - view.cx) < 1e-6
    assert sy < view.cy


def test_orbit_radius_matches_au_to_radius() -> None:
    """orbit_radius_px should give the same result as au_to_radius."""
    view = SolarView(1920, 1080)
    for au in [0.387, 1.0, 5.2, 30.0]:
        assert abs(view.orbit_radius_px(au) - view.au_to_radius(au)) < 1e-10


def test_different_resolutions() -> None:
    """SolarView should scale with resolution."""
    view_small = SolarView(1280, 720)
    view_large = SolarView(3840, 2160)
    # Larger resolution should produce larger pixel radii
    assert view_large.au_to_radius(1.0) > view_small.au_to_radius(1.0)
