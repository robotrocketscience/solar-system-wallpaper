"""Tests for JPL Horizons API response parsing."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from solar_system_wallpaper.horizons import parse_ephemeris_block, fetch_one


SAMPLE_RESPONSE = """
Some header text
*******************************************************************************
$$SOE
2460510.500000000, A.D. 2024-Jul-20 00:00:00.0000,  3.071426839826953E-01, -3.576680399684543E-01, -5.561567893741621E-02,  1.877649518028478E-02,  2.062413610321567E-02, -6.371783032505693E-05,
$$EOE
*******************************************************************************
"""

SAMPLE_MULTI_LINE = """
$$SOE
2460510.500000000, A.D. 2024-Jul-20 00:00:00.0000,  1.0E+00, -2.0E+00, -3.0E-01,  1.0E-02,  2.0E-02, -1.0E-04,
2460511.500000000, A.D. 2024-Jul-21 00:00:00.0000,  1.1E+00, -1.9E+00, -2.9E-01,  1.1E-02,  1.9E-02, -2.0E-04,
$$EOE
"""


def testparse_ephemeris_block_single_line() -> None:
    """Parse a single-line response between SOE/EOE markers."""
    results = parse_ephemeris_block(SAMPLE_RESPONSE)
    assert results is not None
    assert len(results) == 1
    pos = results[0]
    assert abs(pos.x - 0.3071426839826953) < 1e-10
    assert abs(pos.y - (-0.3576680399684543)) < 1e-10
    assert abs(pos.z - (-0.05561567893741621)) < 1e-10
    assert abs(pos.vx - 0.01877649518028478) < 1e-10
    # Verify timestamp conversion (JD 2460510.5 -> Unix)
    expected_unix = (2460510.5 - 2440587.5) * 86400.0
    assert abs(pos.timestamp - expected_unix) < 1.0


def testparse_ephemeris_block_multi_line() -> None:
    """Parse a multi-line response."""
    results = parse_ephemeris_block(SAMPLE_MULTI_LINE)
    assert results is not None
    assert len(results) == 2
    assert abs(results[0].x - 1.0) < 1e-6
    assert abs(results[1].x - 1.1) < 1e-6


def testparse_ephemeris_block_no_markers() -> None:
    """Return None when SOE/EOE markers are missing."""
    result = parse_ephemeris_block("no data here")
    assert result is None


def test_fetch_one_mocked() -> None:
    """Test fetch_one with a mocked HTTP response."""
    mock_resp = MagicMock()
    mock_resp.read.return_value = SAMPLE_RESPONSE.encode()
    mock_resp.__enter__ = MagicMock(return_value=mock_resp)
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("solar_system_wallpaper.horizons.urlopen", return_value=mock_resp):
        results = fetch_one("Earth", "399", "2024-07-20", "2024-07-20 00:30")
        assert results is not None
        assert len(results) == 1
        assert abs(results[0].x - 0.3071426839826953) < 1e-10
