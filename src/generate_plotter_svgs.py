#!/usr/bin/env python3
"""
Generate SVG files at different simplification levels for pen plotter testing.
Outputs multiple versions to help determine optimal resolution for the plotter.
"""

import json
import os
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
import math

# Simplification levels (Douglas-Peucker tolerance in degrees)
# At ~44°N latitude, 1° ≈ 111km longitude, 85km latitude
SIMPLIFICATION_LEVELS = {
    'ultra_fine': 0.0001,   # ~10m - probably overkill
    'fine': 0.0005,         # ~50m - high detail
    'medium': 0.001,        # ~100m - good balance
    'coarse': 0.005,        # ~500m - faster plotting
    'very_coarse': 0.01,    # ~1km - quick tests
}

# Print dimensions (inches) and target SVG size
# Note: Bounds must account for latitude-dependent longitude scaling
# At 44°N, 1° longitude ≈ 80km vs 1° latitude ≈ 111km (factor: cos(44°) ≈ 0.719)
# For correct aspect ratio: lat_span / (lon_span * 0.719) = height / width
PRINT_CONFIGS = {
    'vermont_12x18': {
        'width_in': 12,
        'height_in': 18,
        # Target aspect: 18/12 = 1.5 (height/width)
        # Lat span: 42.7 to 45.1 = 2.4° (need to show full VT)
        # Required lon span: 2.4 / (1.5 * 0.719) = 2.22°
        # Centered on -72.7: -73.81 to -71.59
        # Adjusted to show full VT west border (-73.43) plus margin
        'bounds': [-73.85, 42.7, -71.63, 45.1],
    },
    'lake_champlain_12x24': {
        'width_in': 12,
        'height_in': 24,
        # Target aspect: 24/12 = 2.0 (height/width)
        # Lat span: 43.5 to 45.2 = 1.7° (lake extent)
        # Required lon span: 1.7 / (2.0 * 0.719) = 1.18°
        # Centered on -73.25 (lake center): -73.84 to -72.66
        'bounds': [-73.84, 43.5, -72.66, 45.2],
    }
}

# SVG output at 72 DPI for preview (scales perfectly in vector software)
DPI = 72

# Layer styles matching the viewer configs
# Colors from vermont_12x18.json for consistency
LAYER_STYLES = {
    'quebec': {
        'file': 'docs/json/quebec_border_mrc.json',
        'fill': '#f5f5f5',
        'stroke': '#bdbdbd',
        'stroke_width': 0.5,
        'fill_opacity': 0.5,
    },
    'ny': {
        'file': 'docs/json/ny_counties_grey.json',
        'fill': '#e8e8e8',
        'stroke': '#9e9e9e',
        'stroke_width': 0.75,
        'fill_opacity': 0.6,
    },
    'nh': {
        'file': 'docs/json/nh_counties_grey.json',
        'fill': '#e0e0e0',
        'stroke': '#9e9e9e',
        'stroke_width': 0.75,
        'fill_opacity': 0.6,
    },
    'ma': {
        'file': 'docs/json/ma_counties_grey.json',
        'fill': '#d8d8d8',
        'stroke': '#9e9e9e',
        'stroke_width': 0.75,
        'fill_opacity': 0.6,
    },
    'me': {
        'file': 'docs/json/me_counties_grey.json',
        'fill': '#e4e4e4',
        'stroke': '#9e9e9e',
        'stroke_width': 0.75,
        'fill_opacity': 0.6,
    },
    'quebec_municipalities': {
        'file': 'docs/json/quebec_municipalities_extended.json',
        'fill': '#fafafa',
        'stroke': '#bdbdbd',
        'stroke_width': 0.3,
        'fill_opacity': 0.4,
    },
    'ny_towns': {
        'file': 'docs/json/ny_towns.json',
        'fill': '#f0f0f0',
        'stroke': '#9e9e9e',
        'stroke_width': 0.3,
        'fill_opacity': 0.5,
    },
    'nh_towns': {
        'file': 'docs/json/nh_towns.json',
        'fill': '#ebebeb',
        'stroke': '#9e9e9e',
        'stroke_width': 0.3,
        'fill_opacity': 0.5,
    },
    'ma_towns': {
        'file': 'docs/json/ma_towns.json',
        'fill': '#e5e5e5',
        'stroke': '#9e9e9e',
        'stroke_width': 0.3,
        'fill_opacity': 0.5,
    },
    'vt_towns': {
        'file': 'docs/json/vt_towns_with_water_cutouts.json',
        'fill': None,  # Uses colorMap by county - handled separately
        'stroke': '#424242',
        'stroke_width': 0.5,
        'fill_opacity': 0.7,
        'color_map': {
            'Addison': '#66bb6a',
            'Bennington': '#42a5f5',
            'Caledonia': '#ab47bc',
            'Chittenden': '#ef5350',
            'Essex': '#ffa726',
            'Franklin': '#26c6da',
            'Grand Isle': '#7e57c2',
            'Lamoille': '#ec407a',
            'Orange': '#5c6bc0',
            'Orleans': '#9ccc65',
            'Rutland': '#29b6f6',
            'Washington': '#ff7043',
            'Windham': '#26a69a',
            'Windsor': '#ffd54f',
        },
    },
    'lake_champlain': {
        'file': 'docs/json/lake_champlain_unified.json',
        'fill': '#1565c0',
        'stroke': '#0d47a1',
        'stroke_width': 1.5,
        'fill_opacity': 0.8,
    },
    'lake_memphremagog': {
        'file': 'docs/json/lake_memphremagog_full.json',
        'fill': '#1565c0',
        'stroke': '#0d47a1',
        'stroke_width': 1.5,
        'fill_opacity': 0.8,
    },
    'richelieu_river': {
        'file': 'docs/json/richelieu_river_full.json',
        'fill': 'none',
        'stroke': '#0d47a1',
        'stroke_width': 2.0,
        'fill_opacity': 0,
    },
    'vt_boundary': {
        'file': 'docs/json/vermont_boundary_detailed.json',
        'fill': 'none',
        'stroke': '#1e4320',
        'stroke_width': 3.0,
        'fill_opacity': 0,
    },
}

def load_geojson(filepath):
    """Load GeoJSON file."""
    with open(filepath) as f:
        return json.load(f)

def simplify_geometry(geom, tolerance):
    """Simplify a shapely geometry using Douglas-Peucker algorithm."""
    return geom.simplify(tolerance, preserve_topology=True)

def count_vertices(geom):
    """Count total vertices in a geometry."""
    if geom.is_empty:
        return 0
    if geom.geom_type == 'Polygon':
        count = len(geom.exterior.coords)
        for interior in geom.interiors:
            count += len(interior.coords)
        return count
    elif geom.geom_type == 'MultiPolygon':
        return sum(count_vertices(poly) for poly in geom.geoms)
    elif geom.geom_type in ('LineString', 'LinearRing'):
        return len(geom.coords)
    elif geom.geom_type == 'MultiLineString':
        return sum(len(line.coords) for line in geom.geoms)
    return 0

def project_coords(lon, lat, bounds, width, height):
    """Project lon/lat to SVG coordinates."""
    min_lon, min_lat, max_lon, max_lat = bounds
    x = (lon - min_lon) / (max_lon - min_lon) * width
    y = height - (lat - min_lat) / (max_lat - min_lat) * height  # Flip Y
    return x, y

def geometry_to_svg_path(geom, bounds, width, height):
    """Convert a shapely geometry to SVG path data."""
    paths = []

    def coords_to_path(coords, close=False):
        if len(coords) < 2:
            return ""
        points = [project_coords(c[0], c[1], bounds, width, height) for c in coords]
        d = f"M {points[0][0]:.2f},{points[0][1]:.2f}"
        for p in points[1:]:
            d += f" L {p[0]:.2f},{p[1]:.2f}"
        if close:
            d += " Z"
        return d

    if geom.geom_type == 'Polygon':
        # Exterior ring
        paths.append(coords_to_path(geom.exterior.coords, close=True))
        # Interior rings (holes)
        for interior in geom.interiors:
            paths.append(coords_to_path(interior.coords, close=True))
    elif geom.geom_type == 'MultiPolygon':
        for poly in geom.geoms:
            paths.extend(geometry_to_svg_path(poly, bounds, width, height))

    return paths

def generate_svg(layers, bounds, width_in, height_in, tolerance, output_path):
    """Generate an SVG file from layers at given simplification level."""
    width = width_in * DPI
    height = height_in * DPI

    total_original_vertices = 0
    total_simplified_vertices = 0

    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">
  <title>Vermont Print Map - Tolerance {tolerance}</title>
  <desc>Generated for pen plotter testing with original map colors</desc>

  <!-- Background -->
  <rect width="100%" height="100%" fill="white"/>

'''

    for layer_name, layer_data in layers.items():
        # Get layer style
        style = LAYER_STYLES.get(layer_name, {})
        default_fill = style.get('fill', 'none')
        stroke = style.get('stroke', '#000000')
        stroke_width = style.get('stroke_width', 0.5)
        fill_opacity = style.get('fill_opacity', 1.0)
        color_map = style.get('color_map', None)

        svg_content += f'  <!-- Layer: {layer_name} -->\n'
        svg_content += f'  <g id="{layer_name}">\n'

        for feature in layer_data['features']:
            geom = shape(feature['geometry'])
            original_vertices = count_vertices(geom)
            total_original_vertices += original_vertices

            # Simplify
            simplified = simplify_geometry(geom, tolerance)
            simplified_vertices = count_vertices(simplified)
            total_simplified_vertices += simplified_vertices

            # Convert to SVG paths
            paths = geometry_to_svg_path(simplified, bounds, width, height)

            # Get properties for styling
            props = feature.get('properties', {})

            # Determine fill color
            if color_map and 'county_name' in props:
                county = props.get('county_name', '')
                fill = color_map.get(county, default_fill or 'none')
            else:
                fill = default_fill if default_fill else 'none'

            # Build style string
            if fill and fill != 'none':
                fill_style = f'fill="{fill}" fill-opacity="{fill_opacity}"'
            else:
                fill_style = 'fill="none"'

            for path_d in paths:
                if path_d:
                    svg_content += f'    <path d="{path_d}" {fill_style} stroke="{stroke}" stroke-width="{stroke_width}"/>\n'

        svg_content += '  </g>\n\n'

    svg_content += '</svg>'

    # Write file
    with open(output_path, 'w') as f:
        f.write(svg_content)

    file_size = os.path.getsize(output_path) / 1024  # KB

    return {
        'original_vertices': total_original_vertices,
        'simplified_vertices': total_simplified_vertices,
        'reduction_pct': (1 - total_simplified_vertices / total_original_vertices) * 100 if total_original_vertices > 0 else 0,
        'file_size_kb': file_size
    }

def main():
    print("=" * 60)
    print("PEN PLOTTER SVG GENERATOR")
    print("Generating test files at different simplification levels")
    print("=" * 60)

    # Create output directory
    output_dir = 'output/plotter_test_svgs'
    os.makedirs(output_dir, exist_ok=True)

    # Layer configurations for each map type
    MAP_LAYERS = {
        'vermont_12x18': [
            'quebec', 'ny', 'nh', 'ma', 'me',  # Background state counties
            'quebec_municipalities', 'ny_towns', 'nh_towns', 'ma_towns',  # Town boundaries
            'vt_towns',                         # VT towns with county colors
            'lake_champlain', 'lake_memphremagog', 'richelieu_river',  # Water features
            'vt_boundary',                      # VT border on top
        ],
        'lake_champlain_12x24': [
            'quebec', 'ny', 'nh', 'ma', 'me',  # Background state counties
            'quebec_municipalities', 'ny_towns', 'nh_towns', 'ma_towns',  # Town boundaries
            'vt_towns',                         # VT towns with county colors
            'lake_champlain', 'lake_memphremagog', 'richelieu_river',  # Water features
        ],
    }

    # Load all layers once
    print("\nLoading layers...")
    all_layers = {}
    all_layer_names = set()
    for layer_list in MAP_LAYERS.values():
        all_layer_names.update(layer_list)

    for name in all_layer_names:
        if name not in LAYER_STYLES:
            continue
        filepath = LAYER_STYLES[name]['file']
        if os.path.exists(filepath):
            all_layers[name] = load_geojson(filepath)
            print(f"  Loaded {name}: {len(all_layers[name]['features'])} features")
        else:
            print(f"  WARNING: {filepath} not found")

    # Generate SVGs for each map configuration
    for map_name, layer_order in MAP_LAYERS.items():
        config = PRINT_CONFIGS[map_name]

        # Build layers dict for this map
        layers = {name: all_layers[name] for name in layer_order if name in all_layers}

        print(f"\n{'=' * 60}")
        print(f"MAP: {map_name}")
        print(f"Generating SVGs at {config['width_in']}x{config['height_in']} inches ({DPI} DPI preview)")
        print("-" * 60)

        results = []
        for level_name, tolerance in SIMPLIFICATION_LEVELS.items():
            output_path = os.path.join(output_dir, f'{map_name}_{level_name}.svg')
            print(f"\n{level_name.upper()} (tolerance={tolerance})...")

            stats = generate_svg(
                layers,
                config['bounds'],
                config['width_in'],
                config['height_in'],
                tolerance,
                output_path
            )

            print(f"  Vertices: {stats['original_vertices']:,} → {stats['simplified_vertices']:,} ({stats['reduction_pct']:.1f}% reduction)")
            print(f"  File size: {stats['file_size_kb']:.1f} KB")
            print(f"  Output: {output_path}")

            results.append({
                'level': level_name,
                'tolerance': tolerance,
                **stats
            })

        # Summary for this map
        print(f"\n{'-' * 60}")
        print(f"SUMMARY: {map_name}")
        print(f"{'Level':<15} {'Tolerance':<12} {'Vertices':<12} {'Reduction':<12} {'Size':<10}")
        print("-" * 60)
        for r in results:
            print(f"{r['level']:<15} {r['tolerance']:<12} {r['simplified_vertices']:<12,} {r['reduction_pct']:<11.1f}% {r['file_size_kb']:.1f} KB")

    print(f"\nFiles saved to: {output_dir}/")
    print("Open these in your vector software to inspect path detail.")

if __name__ == '__main__':
    main()
