# Solar System Wallpaper

A CLI tool that renders solar system wallpapers using real ephemeris data from NASA's JPL Horizons system. Specify a date and time, and it fetches the planetary positions, then renders the scene with Cairo to produce a high-resolution PNG wallpaper. Also supports timelapse video generation with bulk API fetching and ffmpeg encoding.

## Prerequisites

### System dependencies

**macOS:**
```bash
brew install cairo
brew install ffmpeg  # only needed for timelapse video generation
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install libcairo2-dev
sudo apt-get install ffmpeg  # only needed for timelapse video generation
```

### Python

Requires Python 3.11 or later. We recommend using [uv](https://docs.astral.sh/uv/) as the package manager.

## Installation

```bash
git clone git@github.com:robotrocketscience/solar-system-wallpaper.git
cd solar-system-wallpaper
uv sync
```

## Quick start

Render a wallpaper for right now:
```bash
uv run solar-system-wallpaper render --date now --output wallpaper.png
```

Render for a specific date:
```bash
uv run solar-system-wallpaper render --date "2024-07-20 16:17:00" --output wallpaper.png
```

4K resolution:
```bash
uv run solar-system-wallpaper render --date now --width 3840 --height 2160 --output 4k.png
```

## CLI reference

### `render` -- Render a single wallpaper image

```
solar-system-wallpaper render [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--date` | `now` | Date/time for the scene. Accepts ISO format (`2024-07-20 16:17:00`) or `now`. |
| `--output`, `-o` | `wallpaper.png` | Output PNG file path. |
| `--width` | `2560` | Image width in pixels. |
| `--height` | `1440` | Image height in pixels. |
| `--bodies` | all | Comma-separated category filters (see categories below). |
| `--no-cosmetic` | | Disable cosmetic effects (stars, nebulae, milky way, shooting stars). |
| `--no-labels` | | Disable body name labels. |
| `--no-informational` | | Disable informational overlays (grid, distance rings, belts, orbit rings, velocity trails). |
| `--no-info-panel` | | Disable the info panel (title, legend, distance table). |

### `timelapse` -- Generate a timelapse video

```
solar-system-wallpaper timelapse [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--start` | required | Start date (`YYYY-MM-DD`). |
| `--days` | required | Number of days to cover. |
| `--speed` | `1d/frame` | Time per frame (e.g., `1d/frame`, `7d/frame`). |
| `--output`, `-o` | `timelapse.mp4` | Output video file path. |
| `--width` | `2560` | Frame width in pixels. |
| `--height` | `1440` | Frame height in pixels. |
| `--fps` | `30` | Video framerate. |
| `--bodies` | all | Comma-separated category filters. |
| `--no-cosmetic` | | Disable cosmetic effects. |
| `--no-labels` | | Disable body name labels. |
| `--no-informational` | | Disable informational overlays. |

### Examples

Only planets and dwarf planets:
```bash
uv run solar-system-wallpaper render --date now --bodies planets,dwarf_planets --output minimal.png
```

Clean render with no overlays:
```bash
uv run solar-system-wallpaper render --date now --no-cosmetic --no-labels --output clean.png
```

One year timelapse, one frame per day:
```bash
uv run solar-system-wallpaper timelapse --start "2024-01-01" --days 365 --speed 1d/frame --output year.mp4
```

Weekly timelapse over 5 years:
```bash
uv run solar-system-wallpaper timelapse --start "2020-01-01" --days 1825 --speed 7d/frame --fps 24 --output 5years.mp4
```

## Body categories

| Filter name | Description | Count |
|-------------|-------------|-------|
| `planets` | Mercury through Neptune | 8 |
| `dwarf_planets` | Pluto, Ceres, Eris, Haumea, Makemake | 5 |
| `moons` | Major moons of Earth, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto | 21 |
| `asteroids` | Vesta, Pallas, Juno, Hygiea, Psyche, Eros, Bennu, Apophis, Ida, Lutetia, Itokawa | 11 |
| `comets` | Halley, Tsuchinshan-ATLAS, C/2024 G3, Encke, Tempel 1, Wild 2, 67P C-G, Hale-Bopp, NEOWISE, Leonard | 10 |
| `spacecraft` | Voyager 1 & 2, New Horizons, JWST, Pioneer 10 & 11, Parker Solar Probe, Juno, SOHO, OSIRIS-REx, Lucy, STEREO-A, Mars Odyssey, MRO | 14 |

Total: 69 objects (61 bodies + 8 planets).

## How it works

1. **Ephemeris data** is fetched from [NASA's JPL Horizons](https://ssd.jpl.nasa.gov/horizons/) API. Each body's heliocentric ecliptic position (x, y, z in AU) and velocity (vx, vy, vz in AU/day) are retrieved.

2. **Coordinate mapping** uses a power-law radial scaling (`r_px = max_r_px * (r_au / max_au)^0.4`) that stretches the inner solar system so Mercury through Mars are clearly visible while still fitting Pluto on screen.

3. **Rendering** is done with [PyCairo](https://pycairo.readthedocs.io/). Layers are drawn back to front: milky way band, nebulae, star field with twinkling, shooting stars, distance grid, asteroid/Kuiper belts, orbit rings, the Sun with animated corona, and all celestial bodies with category-appropriate visual styles (gradient spheres for planets, diamonds for spacecraft, tails for comets).

4. **Timelapse mode** performs one bulk JPL Horizons API call per body for the entire date range (instead of per-frame), then renders each frame sequentially, and finally encodes to video using ffmpeg.

### JPL Horizons rate limiting

The tool respects JPL Horizons rate limits:
- 0.3 second delay between requests
- 2 retries per object on failure
- Spacecraft have limited ephemeris coverage windows and will fall back to narrower date ranges if the full range is unavailable

## Development

### Type checking

This project uses [pyright](https://github.com/microsoft/pyright) in strict mode:

```bash
uv run pyright
```

### Testing

```bash
uv run pytest
```

### Running via module

```bash
uv run python -m solar_system_wallpaper render --date now --output test.png
```

## License

MIT License. See [LICENSE](LICENSE) for details.
