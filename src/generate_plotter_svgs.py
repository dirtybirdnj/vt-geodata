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
PRINT_CONFIGS = {
    'vermont_12x18': {
        'width_in': 12,
        'height_in': 18,
        'bounds': [-73.5, 42.7, -71.4, 45.1],  # [min_lon, min_lat, max_lon, max_lat]
    },
    'lake_champlain_12x24': {
        'width_in': 12,
        'height_in': 24,
        'bounds': [-73.8, 43.5, -72.8, 45.2],
    }
}

# SVG output at 72 DPI for preview (scales perfectly in vector software)
DPI = 72

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
  <desc>Generated for pen plotter testing</desc>

  <!-- Background -->
  <rect width="100%" height="100%" fill="white"/>

'''

    for layer_name, layer_data in layers.items():
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

            # Get name for comment
            props = feature.get('properties', {})
            name = props.get('NAME', props.get('MUS_NM_MRC', props.get('county_name', '')))

            for path_d in paths:
                if path_d:
                    svg_content += f'    <path d="{path_d}" fill="none" stroke="black" stroke-width="0.5"/>\n'

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

    # Load layers for Vermont 12x18 print map
    print("\nLoading layers...")
    layers = {}

    layer_files = {
        'quebec': 'docs/json/quebec_border_mrc.json',
        'ny': 'docs/json/ny_counties_grey.json',
        'nh': 'docs/json/nh_counties_grey.json',
        'ma': 'docs/json/ma_counties_grey.json',
        'vt_towns': 'docs/json/vt_towns_with_water_cutouts.json',
        'lake_champlain': 'docs/json/lake_champlain_unified.json',
        'vt_boundary': 'docs/json/vermont_boundary_detailed.json',
    }

    for name, filepath in layer_files.items():
        if os.path.exists(filepath):
            layers[name] = load_geojson(filepath)
            print(f"  Loaded {name}: {len(layers[name]['features'])} features")
        else:
            print(f"  WARNING: {filepath} not found")

    # Get config
    config = PRINT_CONFIGS['vermont_12x18']

    print(f"\nGenerating SVGs at {config['width_in']}x{config['height_in']} inches ({DPI} DPI preview)")
    print("-" * 60)

    results = []
    for level_name, tolerance in SIMPLIFICATION_LEVELS.items():
        output_path = os.path.join(output_dir, f'vermont_{level_name}.svg')
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

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'Level':<15} {'Tolerance':<12} {'Vertices':<12} {'Reduction':<12} {'Size':<10}")
    print("-" * 60)
    for r in results:
        print(f"{r['level']:<15} {r['tolerance']:<12} {r['simplified_vertices']:<12,} {r['reduction_pct']:<11.1f}% {r['file_size_kb']:.1f} KB")

    print(f"\nFiles saved to: {output_dir}/")
    print("Open these in your vector software to inspect path detail.")

if __name__ == '__main__':
    main()
