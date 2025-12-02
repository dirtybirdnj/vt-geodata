#!/usr/bin/env python3
"""
Generate export files for two use cases:
1. Pen plotter: SVG with simplified paths at exact paper dimensions
2. Projector/mural: High-res PNG at 4K or custom resolution

Usage:
    python generate_print_exports.py --mode plotter --size 12x18
    python generate_print_exports.py --mode projector --resolution 4k
    python generate_print_exports.py --mode projector --resolution 8k --layers
"""

import json
import os
import argparse
from shapely.geometry import shape
from shapely.ops import unary_union

# Try to import PIL for PNG generation
try:
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("Note: PIL not installed. PNG export disabled. Run: pip install Pillow")

# Simplification presets
SIMPLIFICATION = {
    'ultra_fine': 0.0001,
    'fine': 0.0005,
    'medium': 0.001,
    'coarse': 0.005,
    'very_coarse': 0.01,
}

# Resolution presets
RESOLUTIONS = {
    '1080p': (1920, 1080),
    '4k': (3840, 2160),
    '5k': (5120, 2880),
    '8k': (7680, 4320),
}

# Paper sizes (inches)
PAPER_SIZES = {
    '12x18': (12, 18),
    '12x24': (11.49, 23.49),  # Actual plotter paper
    '18x24': (18, 24),
    '24x36': (24, 36),
}

# Map bounds
BOUNDS = {
    'vermont': [-73.5, 42.7, -71.4, 45.1],
    'champlain': [-73.8, 43.5, -72.5, 45.2],
}

# Layer definitions with styling
# Stroke widths - hairline for inspection (0.1-0.25)
LAYERS = {
    'quebec': {
        'file': 'docs/json/quebec_border_mrc.json',
        'stroke': '#999999',
        'fill': None,
        'stroke_width': 0.1,
    },
    'ny': {
        'file': 'docs/json/ny_counties_grey.json',
        'stroke': '#888888',
        'fill': None,
        'stroke_width': 0.1,
    },
    'nh': {
        'file': 'docs/json/nh_counties_grey.json',
        'stroke': '#888888',
        'fill': None,
        'stroke_width': 0.1,
    },
    'ma': {
        'file': 'docs/json/ma_counties_grey.json',
        'stroke': '#888888',
        'fill': None,
        'stroke_width': 0.1,
    },
    'vt_towns': {
        'file': 'docs/json/vt_towns_with_water_cutouts.json',
        'stroke': '#333333',
        'fill': None,
        'stroke_width': 0.15,
    },
    'lake_champlain': {
        'file': 'docs/json/lake_champlain_unified.json',
        'stroke': '#0066cc',
        'fill': None,
        'stroke_width': 0.2,
    },
    'vt_boundary': {
        'file': 'docs/json/vermont_boundary_detailed.json',
        'stroke': '#000000',
        'fill': None,
        'stroke_width': 0.25,
    },
}


def load_geojson(filepath):
    """Load GeoJSON file."""
    with open(filepath) as f:
        return json.load(f)


def simplify_geometry(geom, tolerance):
    """Simplify geometry using Douglas-Peucker."""
    return geom.simplify(tolerance, preserve_topology=True)


def count_vertices(geom):
    """Count vertices in geometry."""
    if geom.is_empty:
        return 0
    if geom.geom_type == 'Polygon':
        count = len(geom.exterior.coords)
        for interior in geom.interiors:
            count += len(interior.coords)
        return count
    elif geom.geom_type == 'MultiPolygon':
        return sum(count_vertices(poly) for poly in geom.geoms)
    return 0


def project_coords(lon, lat, bounds, width, height):
    """Project lon/lat to pixel coordinates."""
    min_lon, min_lat, max_lon, max_lat = bounds
    x = (lon - min_lon) / (max_lon - min_lon) * width
    y = height - (lat - min_lat) / (max_lat - min_lat) * height
    return x, y


def geometry_to_svg_paths(geom, bounds, width, height):
    """Convert geometry to SVG path strings."""
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
        paths.append(coords_to_path(geom.exterior.coords, close=True))
        for interior in geom.interiors:
            paths.append(coords_to_path(interior.coords, close=True))
    elif geom.geom_type == 'MultiPolygon':
        for poly in geom.geoms:
            paths.extend(geometry_to_svg_paths(poly, bounds, width, height))

    return paths


def geometry_to_pixel_coords(geom, bounds, width, height):
    """Convert geometry to list of pixel coordinate tuples for PIL."""
    polygons = []

    def coords_to_pixels(coords):
        return [project_coords(c[0], c[1], bounds, width, height) for c in coords]

    if geom.geom_type == 'Polygon':
        exterior = coords_to_pixels(geom.exterior.coords)
        holes = [coords_to_pixels(interior.coords) for interior in geom.interiors]
        polygons.append({'exterior': exterior, 'holes': holes})
    elif geom.geom_type == 'MultiPolygon':
        for poly in geom.geoms:
            polygons.extend(geometry_to_pixel_coords(poly, bounds, width, height))

    return polygons


def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def generate_svg(layers_data, bounds, width, height, tolerance, output_path):
    """Generate SVG file."""
    total_vertices = 0

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{width}" height="{height}"
     viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white"/>
'''

    for layer_name, layer_info in layers_data.items():
        config = LAYERS[layer_name]
        svg += f'  <g id="{layer_name}">\n'

        for feature in layer_info['features']:
            geom = shape(feature['geometry'])
            simplified = simplify_geometry(geom, tolerance)
            total_vertices += count_vertices(simplified)

            paths = geometry_to_svg_paths(simplified, bounds, width, height)

            stroke = config['stroke']
            fill = config['fill'] or 'none'
            stroke_width = config['stroke_width']

            for path_d in paths:
                if path_d:
                    svg += f'    <path d="{path_d}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>\n'

        svg += '  </g>\n'

    svg += '</svg>'

    with open(output_path, 'w') as f:
        f.write(svg)

    return total_vertices


def generate_png(layers_data, bounds, width, height, tolerance, output_path, layer_filter=None):
    """Generate high-res PNG file."""
    if not HAS_PIL:
        print("ERROR: PIL/Pillow not installed. Cannot generate PNG.")
        return 0

    # Create white background image
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    total_vertices = 0

    for layer_name, layer_info in layers_data.items():
        if layer_filter and layer_name not in layer_filter:
            continue

        config = LAYERS[layer_name]

        for feature in layer_info['features']:
            geom = shape(feature['geometry'])
            simplified = simplify_geometry(geom, tolerance)
            total_vertices += count_vertices(simplified)

            polygons = geometry_to_pixel_coords(simplified, bounds, width, height)

            fill_color = hex_to_rgb(config['fill']) if config['fill'] else None
            stroke_color = hex_to_rgb(config['stroke'])
            # Scale stroke width for resolution
            stroke_width = max(1, int(config['stroke_width'] * (width / 1000)))

            for poly in polygons:
                exterior = [(int(x), int(y)) for x, y in poly['exterior']]

                if fill_color:
                    draw.polygon(exterior, fill=fill_color, outline=stroke_color, width=stroke_width)
                else:
                    draw.polygon(exterior, outline=stroke_color, width=stroke_width)

                # Draw holes
                for hole in poly['holes']:
                    hole_coords = [(int(x), int(y)) for x, y in hole]
                    draw.polygon(hole_coords, fill='white', outline=stroke_color, width=stroke_width)

    img.save(output_path, 'PNG', optimize=True)
    return total_vertices


def main():
    parser = argparse.ArgumentParser(description='Generate print/projection exports')
    parser.add_argument('--mode', choices=['plotter', 'projector'], default='plotter',
                        help='Export mode: plotter (SVG) or projector (PNG)')
    parser.add_argument('--size', choices=list(PAPER_SIZES.keys()), default='12x18',
                        help='Paper size for plotter mode')
    parser.add_argument('--resolution', choices=list(RESOLUTIONS.keys()), default='4k',
                        help='Resolution for projector mode')
    parser.add_argument('--quality', choices=list(SIMPLIFICATION.keys()), default='medium',
                        help='Simplification level')
    parser.add_argument('--map', choices=list(BOUNDS.keys()), default='vermont',
                        help='Map bounds to use')
    parser.add_argument('--layers', action='store_true',
                        help='Export individual layers separately')
    parser.add_argument('--dpi', type=int, default=72,
                        help='DPI for plotter SVG (default: 72 for preview)')
    args = parser.parse_args()

    # Create output directory
    output_dir = 'output/print_exports'
    os.makedirs(output_dir, exist_ok=True)

    # Load all layers
    print("Loading layers...")
    layers_data = {}
    for name, config in LAYERS.items():
        if os.path.exists(config['file']):
            layers_data[name] = load_geojson(config['file'])
            print(f"  {name}: {len(layers_data[name]['features'])} features")

    bounds = BOUNDS[args.map]
    tolerance = SIMPLIFICATION[args.quality]

    if args.mode == 'plotter':
        # SVG for pen plotter
        paper_w, paper_h = PAPER_SIZES[args.size]
        width = int(paper_w * args.dpi)
        height = int(paper_h * args.dpi)

        output_path = os.path.join(output_dir, f'{args.map}_{args.size}_{args.quality}.svg')
        print(f"\nGenerating SVG: {paper_w}x{paper_h}\" at {args.dpi} DPI ({width}x{height}px)")

        vertices = generate_svg(layers_data, bounds, width, height, tolerance, output_path)
        size_kb = os.path.getsize(output_path) / 1024

        print(f"  Vertices: {vertices:,}")
        print(f"  File: {output_path} ({size_kb:.1f} KB)")

    else:
        # PNG for projector
        width, height = RESOLUTIONS[args.resolution]

        # Adjust for map aspect ratio
        map_aspect = (bounds[2] - bounds[0]) / (bounds[3] - bounds[1])
        target_aspect = width / height

        if map_aspect > target_aspect:
            # Map is wider - fit to width
            new_height = int(width / map_aspect)
            height = new_height
        else:
            # Map is taller - fit to height
            new_width = int(height * map_aspect)
            width = new_width

        if args.layers:
            # Export each layer separately
            layer_names = ['vt_boundary', 'vt_towns', 'lake_champlain', 'ny', 'nh', 'ma', 'quebec']
            for layer_name in layer_names:
                if layer_name in layers_data:
                    output_path = os.path.join(output_dir, f'{args.map}_{args.resolution}_{layer_name}.png')
                    print(f"\nGenerating PNG layer: {layer_name} at {width}x{height}")

                    vertices = generate_png(
                        layers_data, bounds, width, height, tolerance,
                        output_path, layer_filter=[layer_name]
                    )
                    size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    print(f"  File: {output_path} ({size_mb:.1f} MB)")
        else:
            # Export all layers combined
            output_path = os.path.join(output_dir, f'{args.map}_{args.resolution}_{args.quality}.png')
            print(f"\nGenerating PNG: {args.resolution} ({width}x{height}px)")

            vertices = generate_png(layers_data, bounds, width, height, tolerance, output_path)
            size_mb = os.path.getsize(output_path) / (1024 * 1024)

            print(f"  Vertices: {vertices:,}")
            print(f"  File: {output_path} ({size_mb:.1f} MB)")


if __name__ == '__main__':
    main()
