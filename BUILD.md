# Build Process

This project uses a build system to keep large files out of git while allowing them to be regenerated locally.

## Quick Start

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Build everything
python build.py

# Or build only essential maps (committed to git)
python build.py --essential-only

# Or build only comprehensive maps (local reference)
python build.py --comprehensive-only
```

## What Gets Built

### Essential Maps (Committed to Git)
These are the core maps needed for the website:

- **Lake Champlain NY & VT Combined Maps**
  - `docs/champlain_ny_vt.html` - Interactive map with OpenStreetMap
  - `docs/champlain_ny_vt_vector.html` - Vector-only version
  - JSON data files in `docs/json/`

- **Vermont Towns/Cities Boundary Maps**
  - `docs/vt_towns.html` - Interactive map with OpenStreetMap
  - `docs/vt_towns_vector.html` - Vector-only version
  - `docs/json/vt_towns.json` - Town boundary data (~5.6 MB)

### Comprehensive Maps (Local Only)
These large reference maps (50+ MB) are excluded from git:

- **NY Census Water (All 62 Counties)**
  - `docs/ny_census_water_all.html` (~53 MB)
  - `docs/ny_census_water_all_vector.html` (~54 MB)

- **VT Census Water (All 14 Counties)**
  - `docs/vt_census_water_all.html` (~12 MB)
  - `docs/vt_census_water_all_vector.html` (~12 MB)

- **VT OpenData Water**
  - `docs/vt_opendata_water.html` (~25 MB)
  - `docs/vt_opendata_water_vector.html` (~25 MB)

## How It Works

1. **Data Download**: Build scripts download Census TIGER data from census.gov as needed
2. **Processing**: Data is categorized and filtered for specific regions
3. **Map Generation**: Folium generates interactive HTML maps with embedded GeoJSON
4. **Git Exclusion**: Large comprehensive maps are excluded via `.gitignore`

## Data Sources

All data is downloaded during the build process from:

- **US Census TIGER/Line Shapefiles 2022-2023**
  - State boundaries
  - County boundaries
  - County subdivisions (towns/cities)
  - Area water features
  - Linear water features

- **Vermont Open Geodata Portal**
  - State boundary
  - Hydrography polygons

No source data files are committed to git - they're regenerated on demand.

## File Size Management

- Essential maps: ~20 MB (committed to git)
  - Lake Champlain maps: ~5 MB
  - Vermont towns maps: ~10 MB
  - JSON data files: ~5 MB
- Comprehensive maps: ~150 MB total (local only, excluded from git)
- Source data: Downloaded as needed, cached locally, excluded from git

This approach keeps the git repository lean while allowing full map generation locally.
