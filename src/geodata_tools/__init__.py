"""
geodata-tools: A toolkit for processing geographic data for print maps.

Core modules:
- geometry: Shapely-based geometry operations (union, difference, cutouts)
- geojson: Load, save, and transform GeoJSON files
- svg: Generate SVG files from GeoJSON with styling
- colors: Color utilities (HSL, per-feature coloring)
"""

__version__ = "0.1.0"

from .geometry import (
    cut_features_from_polygon,
    identify_islands,
    merge_features,
    simplify_geometry,
)
from .geojson import load_geojson, save_geojson
from .svg import generate_svg, geometry_to_path
from .colors import hsl_to_hex, get_feature_color
