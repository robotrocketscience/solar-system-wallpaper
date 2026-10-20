# Solar System Wallpaper

A CLI that renders the solar system for a given date and time as a PNG or timelapse video.

## Prerequisites

You need Python 3.11 or later and Cairo. The commands below use [uv](https://docs.astral.sh/uv/).

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

Current time:

```bash
uv run solar-system-wallpaper render --date now --output wallpaper.png
```

Specific date:

```bash
uv run solar-system-wallpaper render --date "2024-07-20 16:17:00" --output wallpaper.png
```

4K resolution:

```bash
uv run solar-system-wallpaper render --date now --width 3840 --height 2160 --output 4k.png
```

## CLI reference

### `render`

Renders one image.

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

Planets and dwarf planets only:

```bash
uv run solar-system-wallpaper render --date now --bodies planets,dwarf_planets --output minimal.png
```

No cosmetic effects or labels:

```bash
uv run solar-system-wallpaper render --date now --no-cosmetic --no-labels --output clean.png
```

One-year timelapse at one frame per day:

```bash
uv run solar-system-wallpaper timelapse --start "2024-01-01" --days 365 --speed 1d/frame --output year.mp4
```

5-year timelapse at one frame per week:

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

Each body's heliocentric ecliptic position (x, y, z in AU) and velocity (vx, vy, vz in AU/day) come from [NASA JPL Horizons](https://ssd.jpl.nasa.gov/horizons/). A power-law radial scale, `r_px = max_r_px * (r_au / max_au)^0.4`, spreads out Mercury through Mars and keeps Pluto on screen.

[PyCairo](https://pycairo.readthedocs.io/) draws the layers back to front: milky way, nebulae, twinkling star field, shooting stars, distance grid, asteroid/Kuiper belts, orbit rings, the Sun with animated corona, and all bodies. Planets are drawn as gradient spheres, spacecraft as diamonds, and comets with tails.

The `timelapse` command fetches each body's full date range in one API call and encodes the frames with ffmpeg.

### JPL Horizons rate limiting

The CLI waits 0.3 seconds between requests and retries a failed body request up to 2 times. If a spacecraft's ephemeris does not cover the requested date range, it requests a narrower one.

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

MIT. See [LICENSE](LICENSE).
