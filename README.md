# Solar System Wallpaper

A CLI tool that renders solar system wallpapers from real ephemeris data. Give it a date and time and it fetches planetary positions from NASA's JPL Horizons system, then draws the scene with Cairo to a high-resolution PNG. It can also generate timelapse videos, using bulk API fetches and ffmpeg encoding.

## Prerequisites

Requires Python 3.11 or later. We recommend [uv](https://docs.astral.sh/uv/) as the package manager.

Install Cairo, and ffmpeg if you want timelapse videos.

On macOS:

```bash
brew install cairo
brew install ffmpeg  # only needed for timelapse video generation
```

On Linux (Debian/Ubuntu):

```bash
sudo apt-get install libcairo2-dev
sudo apt-get install ffmpeg  # only needed for timelapse video generation
```

## Installation

```bash
git clone git@github.com:robotrocketscience/solar-system-wallpaper.git
cd solar-system-wallpaper
uv sync
```

## Quick start

Render a wallpaper for the current time:

```bash
uv run solar-system-wallpaper render --date now --output wallpaper.png
```

Render for a specific date:

```bash
uv run solar-system-wallpaper render --date "2024-07-20 16:17:00" --output wallpaper.png
```

Render at 4K resolution:

```bash
uv run solar-system-wallpaper render --date now --width 3840 --height 2160 --output 4k.png
```

## CLI reference

### `render`

Renders a single wallpaper image.

```
solar-system-wallpaper render [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--date` | `now` | Date/time for the scene. Accepts ISO format (`2024-07-20 16:17:00`) or `now`. |
| `--output`, `-o` | `wallpaper.png` | Output PNG file path. |
| `--width` | `2560` | Image width in pixels. |
| `--height` | `1440` | Image height in pixels. |
| `--bodies` | all | Comma-separated category filters (see [Body categories](#body-categories)). |
| `--no-cosmetic` | | Disable cosmetic effects (stars, nebulae, milky way, shooting stars). |
| `--no-labels` | | Disable body name labels. |
| `--no-informational` | | Disable informational overlays (grid, distance rings, belts, orbit rings, velocity trails). |
| `--no-info-panel` | | Disable the info panel (title, legend, distance table). |

### `timelapse`

Generates a timelapse video.

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

Render only planets and dwarf planets:

```bash
uv run solar-system-wallpaper render --date now --bodies planets,dwarf_planets --output minimal.png
```

Render without cosmetic effects or labels:

```bash
uv run solar-system-wallpaper render --date now --no-cosmetic --no-labels --output clean.png
```

Generate a one-year timelapse at one frame per day:

```bash
uv run solar-system-wallpaper timelapse --start "2024-01-01" --days 365 --speed 1d/frame --output year.mp4
```

Generate a 5-year timelapse at one frame per week:

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

## Rendering pipeline

The tool fetches each body's heliocentric ecliptic position (x, y, z in AU) and velocity (vx, vy, vz in AU/day) from the [NASA JPL Horizons](https://ssd.jpl.nasa.gov/horizons/) API.

Positions map to the screen with power-law radial scaling, `r_px = max_r_px * (r_au / max_au)^0.4`. This stretches the inner solar system so Mercury through Mars are clearly visible while Pluto still fits on screen.

[PyCairo](https://pycairo.readthedocs.io/) draws the layers back to front: milky way band, nebulae, star field with twinkling, shooting stars, distance grid, asteroid/Kuiper belts, orbit rings, the Sun with animated corona, and all celestial bodies. Each category has its own style, such as gradient spheres for planets, diamonds for spacecraft, and tails for comets.

Timelapse mode makes one bulk JPL Horizons API call per body for the whole date range instead of one per frame. It then renders each frame in sequence and encodes the video with ffmpeg.

### JPL Horizons rate limiting

The tool waits 0.3 seconds between requests and retries each object up to 2 times on failure. Spacecraft have limited ephemeris coverage windows, so when the full range is unavailable the tool falls back to a narrower date range.

## Development

Type-check with [pyright](https://github.com/microsoft/pyright) in strict mode:

```bash
uv run pyright
```

Run the tests:

```bash
uv run pytest
```

Run the CLI as a module:

```bash
uv run python -m solar_system_wallpaper render --date now --output test.png
```

## License

MIT License. See [LICENSE](LICENSE) for details.
