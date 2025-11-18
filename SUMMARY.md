# VT-GEODATA Project Summary

**Last Updated:** 2025-11-18

## Project Status
- **Git Branch:** main (clean working directory)
- **Outstanding PRs:** None
- **Recent Work:** Tag filtering system, neighboring states data, simplification tool enhancements

---

## Project Overview

**VT GeoData** is a geospatial data processing pipeline for creating pen plotter-ready vector maps of Vermont and Lake Champlain. The project downloads and processes royalty-free vector datasets from multiple authoritative sources, visualizes and compares dataset quality, and generates clean SVG files optimized for pen plotting.

**Key Focus:** Vermont boundaries with detailed Lake Champlain islands representation

---

## Directory Structure

```
vt-geodata/
├── data/              # Downloaded raw geospatial data (gitignored)
│   ├── raw/          # Original shapefiles (Census TIGER, etc.)
│   └── processed/    # Cleaned and merged datasets (GeoJSON)
├── output/           # Generated files (HTML maps, SVGs - local only)
├── docs/             # GitHub Pages hosted visualizations (COMMITTED)
│   ├── json/         # Processed GeoJSON data for web maps
│   └── *.html        # Interactive Leaflet/Folium visualizations
├── screenshots/      # Automated screenshots using Playwright
├── notebooks/        # Jupyter notebooks (currently empty)
└── src/              # Python processing scripts (22 files)
```

---

## Data Sources

### Primary Sources
1. **Vermont Open Geodata Portal** - State boundaries and hydrography
   - Best representation of Lake Champlain islands
   - ~2,000 water features

2. **US Census TIGER/Line** - Water bodies and administrative boundaries
   - TIGER 2022 & 2023 data
   - County-level water data for 4 Lake Champlain counties:
     - Grand Isle (50013)
     - Chittenden (50007)
     - Franklin (50011)
     - Addison (50001)

3. **Neighboring States Data**
   - New York: 3 Lake Champlain counties (Clinton, Essex, Washington)
   - New Hampshire: state boundary
   - Massachusetts: state boundary

---

## Key Scripts & Functionality

### Core Pipeline
- **`download.py`** - Downloads Census TIGER shapefiles automatically
- **`explore.py`** - Inspects shapefiles and generates interactive maps
- **`process.py`** - Clips, simplifies, and merges datasets
- **`export.py`** - Converts to pen plotter-ready SVG (A4 landscape, 0.2-0.5mm strokes)

### Advanced Processing
- **`categorize_water.py`** - Categorizes Lake Champlain water into 3 datasets:
  - **Big Lake**: Main body (>100 sq km) - 23 features
  - **Rivers/Streams**: Elongated features (ratio >5) - 21 features
  - **Small Ponds**: Everything else - 5,082 features
  - Applies 42 manual corrections from `categorized_water_edits.json`

- **`create_vt_with_islands.py`** - Creates comprehensive Vermont map with Champlain Islands
  - Islands appear as "holes" in Lake Champlain polygons
  - Exports detailed boundary (12,890 points)

- **`export_to_json.py`** - Converts shapefiles to clean GeoJSON with metadata

### Map Generation
- **`generate_all_maps.py` / `generate_all_maps_v2.py`** - Batch map creation
- **`generate_comparison_maps.py`** - Side-by-side data source comparisons
- **`generate_vector_only_maps.py`** - Pure vector visualization (no basemaps)

### Regional Context
- **`get_neighboring_states_data.py`** - Adds NY, NH, MA boundary data
- **`get_ny_lake_champlain_data.py`** - NY Lake Champlain water features

---

## Composite Data Products

### The "Composite Data" Issue Context

The project generates several processed/composite datasets:

#### Categorized Water (Main Composite Data)
- `champlain_big_lake.json` - Main lake body (23 features, 760 sq km)
- `champlain_rivers.json` - Rivers and streams (21 features)
- `champlain_small_ponds.json` - Small water bodies (5,082 features)
- **Created by:** Algorithmic categorization + 42 manual corrections
- **Manual edits tracked in:** `categorized_water_edits.json`

#### Other Composite Datasets
- `vermont_boundary_detailed.json` - Complete VT boundary with island representation (12,890 points)
- `vt_border.json` - State boundary from Census
- `vt_counties.json` - 14 counties with colors and centroids
- Neighboring states data (NY, NH, MA)

---

## Interactive Web Tools

Hosted on GitHub Pages: https://dirtybirdnj.github.io/vt-geodata/

1. **Boundary Simplification Tool** (`vermont_simplify.html`)
   - Interactive slider to adjust simplification tolerance
   - Real-time preview with Chaikin's algorithm smoothing
   - Shows point count reduction
   - Export to GeoJSON

2. **Water Categorization Editor** (`champlain_categorized.html`)
   - Visual map showing 3 water categories
   - Click features to recategorize
   - Edit history tracking with timestamps
   - Export corrections to JSON
   - **42 manual corrections currently applied**

---

## Technology Stack

### Python GIS Stack
- **geopandas** (>=0.14.0) - Primary geospatial data handling
- **shapely** (>=2.0.0) - Geometry operations
- **fiona** (>=1.9.0) - File I/O for shapefiles
- **pyproj** (>=3.6.0) - Coordinate reference system transformations

### Visualization
- **folium** (>=0.15.0) - Interactive Leaflet maps
- **matplotlib** (>=3.8.0) - Static plots
- **contextily** (>=1.4.0) - Basemap tiles

### SVG Generation
- **svgwrite** (>=1.4.3) - SVG file creation
- **svgpathtools** (>=1.6.0) - SVG path manipulation

### Utilities
- **simplification** (>=0.6.0) - Geometry simplification
- **playwright** (>=1.40.0) - Screenshot automation
- **jupyter** / **notebook** - Exploratory analysis

---

## Data Flow

```
Raw Sources (Census TIGER, VT Open Geodata)
    ↓
Download Scripts (download.py)
    ↓
Raw Data (data/raw/*.shp)
    ↓
Processing (process.py, categorize_water.py)
    ↓
Processed GeoJSON (data/processed/, docs/json/)
    ↓
Visualizations (generate_*_maps.py)
    ↓
Interactive HTML Maps (docs/*.html)
    ↓
GitHub Pages
```

---

## Manual Correction Workflow

1. Interactive web editor (`champlain_categorized.html`) for visual categorization
2. JSON-based edit tracking (`categorized_water_edits.json`)
3. Persistent edits applied on regeneration
4. 42 manual corrections currently tracked with:
   - HYDROID (feature identifier)
   - Timestamp
   - From/to categories
   - Notes

---

## Output Specifications

### For Pen Plotting
- **Format:** SVG (SVG Tiny profile)
- **Paper Size:** A4 landscape (297 × 210 mm)
- **Stroke Widths:** 0.2-0.5 mm
- **Fill:** None (only strokes)
- **Coordinate System:** WGS84 or Vermont State Plane
- **Simplification:** Minimal detail, optimized paths

### For Web Visualization
- **Format:** HTML with Leaflet.js
- **File Sizes:** 3.7KB - 26MB
- **Basemaps:** OpenStreetMap or vector-only
- **Interactivity:** Layer controls, tooltips, popups

---

## Standard Workflow

```bash
# 1. Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Download data
python src/download.py

# 3. Explore data
python src/explore.py

# 4. Process geometries
python src/process.py

# 5. Export to SVG
python src/export.py

# 6. Generate web maps
python src/generate_comparison_maps.py

# 7. Screenshot automation
python src/screenshot.py

# 8. Publish to GitHub Pages
cp output/*.html docs/
git add docs/ && git commit -m "Update visualizations" && git push
```

---

## Recent Commits

- `812bf4c` - Add tag filtering system to Data Sources section
- `02f4d1c` - Add small colored icon boxes next to dataset titles
- `bbe16d9` - Add neighboring states as data sources with horizontal layout
- `1782ca9` - Add smoothing slider with Chaikin's algorithm to simplification tool
- `53cc81c` - Add NY data to Lake Champlain map and fix zoom control

---

## Next Steps for Composite Data Fixes

Based on the codebase review, potential areas for composite data improvement:

1. **Water Categorization Refinement**
   - Review algorithmic thresholds (>100 sq km for big lake, >5 elongation for rivers)
   - Validate the 42 manual corrections
   - Identify additional features needing manual correction

2. **Vermont Boundary with Islands**
   - Verify island topology (holes in polygons)
   - Check for gaps or overlaps in composite geometry
   - Simplification vs. accuracy trade-offs

3. **Multi-Source Integration**
   - Resolve conflicts between VT Open Geodata and Census TIGER data
   - Validate clipping to Vermont bounding box
   - Check coordinate system transformations

4. **Data Quality**
   - Verify feature counts (23 big lake, 21 rivers, 5,082 ponds)
   - Check area calculations
   - Validate elongation ratio calculations
