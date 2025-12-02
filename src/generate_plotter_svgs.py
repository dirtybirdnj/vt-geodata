#!/usr/bin/env python3
"""
Generate SVG files for pen plotter at different simplification levels.
"""

import os
from geodata_tools import load_geojson
from geodata_tools.svg import generate_svg
from geodata_tools.colors import VT_COUNTY_COLORS

# Simplification levels (Douglas-Peucker tolerance in degrees)
SIMPLIFICATION_LEVELS = {
    'ultra_fine': 0.0001,
    'fine': 0.0005,
    'medium': 0.001,
    'coarse': 0.005,
    'very_coarse': 0.01,
}

# Print configurations
PRINT_CONFIGS = {
    'vermont_12x18': {
        'width_in': 12,
        'height_in': 18,
        'bounds': [-73.9293, 42.4271, -71.1694, 45.4050],
    },
    'lake_champlain_12x24': {
        'width_in': 12,
        'height_in': 24,
        'bounds': [-73.84, 43.5, -72.66, 45.2],
    }
}

# Layer styles
LAYER_STYLES = {
    # Regional backgrounds
    'quebec': {'file': 'docs/json/quebec_border_mrc.json', 'fill': '#f5ebe0', 'stroke': '#c9b99a', 'stroke_width': 0.5, 'fill_opacity': 0.5},
    'ny': {'file': 'docs/json/ny_counties_grey.json', 'fill': '#e3e8ed', 'stroke': '#8a9bab', 'stroke_width': 0.75, 'fill_opacity': 0.6},
    'nh': {'file': 'docs/json/nh_counties_grey.json', 'fill': '#e8e8e8', 'stroke': '#9e9e9e', 'stroke_width': 0.75, 'fill_opacity': 0.6},
    'ma': {'file': 'docs/json/ma_counties_grey.json', 'fill': '#ede5dc', 'stroke': '#a89888', 'stroke_width': 0.75, 'fill_opacity': 0.6},
    'me': {'file': 'docs/json/me_counties_grey.json', 'fill': '#e0e8e4', 'stroke': '#8aa898', 'stroke_width': 0.75, 'fill_opacity': 0.6},

    # Town boundaries
    'quebec_municipalities': {'file': 'docs/json/quebec_municipalities_extended.json', 'fill': None, 'stroke': '#c9b99a', 'stroke_width': 0.3, 'fill_opacity': 0.6, 'region': 'quebec'},
    'ny_towns': {'file': 'docs/json/ny_towns_with_water_cutouts.json', 'fill': None, 'stroke': '#8a9bab', 'stroke_width': 0.3, 'fill_opacity': 0.6, 'region': 'ny'},
    'nh_towns': {'file': 'docs/json/nh_towns.json', 'fill': None, 'stroke': '#9e9e9e', 'stroke_width': 0.3, 'fill_opacity': 0.6, 'region': 'nh'},
    'ma_towns': {'file': 'docs/json/ma_towns.json', 'fill': None, 'stroke': '#a89888', 'stroke_width': 0.3, 'fill_opacity': 0.6, 'region': 'ma'},
    'me_towns': {'file': 'docs/json/me_towns.json', 'fill': None, 'stroke': '#8aa898', 'stroke_width': 0.3, 'fill_opacity': 0.6, 'region': 'me'},
    'vt_towns': {'file': 'docs/json/vt_towns_with_water_cutouts.json', 'fill': None, 'stroke': '#424242', 'stroke_width': 0.5, 'fill_opacity': 0.7, 'color_map': VT_COUNTY_COLORS},

    # Unified VT hydro (all counties)
    'vt_rivers': {'file': 'docs/json/vt_rivers_all.json', 'fill': '#42a5f5', 'stroke': '#1976d2', 'stroke_width': 0.5, 'fill_opacity': 0.7},
    'vt_lakes': {'file': 'docs/json/vt_lakes_all.json', 'fill': '#64b5f6', 'stroke': '#1976d2', 'stroke_width': 0.5, 'fill_opacity': 0.7},

    # NH hydro
    'nh_rivers': {'file': 'docs/json/nh_rivers.json', 'fill': '#42a5f5', 'stroke': '#1976d2', 'stroke_width': 0.5, 'fill_opacity': 0.7},
    'nh_lakes': {'file': 'docs/json/nh_lakes.json', 'fill': '#64b5f6', 'stroke': '#1976d2', 'stroke_width': 0.5, 'fill_opacity': 0.7},

    # MA hydro
    'ma_rivers': {'file': 'docs/json/ma_rivers.json', 'fill': '#42a5f5', 'stroke': '#1976d2', 'stroke_width': 0.5, 'fill_opacity': 0.7},
    'ma_lakes': {'file': 'docs/json/ma_lakes.json', 'fill': '#64b5f6', 'stroke': '#1976d2', 'stroke_width': 0.5, 'fill_opacity': 0.7},

    # NY hydro
    'ny_rivers': {'file': 'docs/json/ny_rivers.json', 'fill': '#42a5f5', 'stroke': '#1976d2', 'stroke_width': 0.5, 'fill_opacity': 0.7},
    'ny_lakes': {'file': 'docs/json/ny_lakes.json', 'fill': '#64b5f6', 'stroke': '#1976d2', 'stroke_width': 0.5, 'fill_opacity': 0.7},

    # Quebec hydro
    'quebec_rivers': {'file': 'docs/json/quebec_rivers.json', 'fill': '#42a5f5', 'stroke': '#1976d2', 'stroke_width': 0.5, 'fill_opacity': 0.7},
    'quebec_lakes': {'file': 'docs/json/quebec_lakes.json', 'fill': '#64b5f6', 'stroke': '#1976d2', 'stroke_width': 0.5, 'fill_opacity': 0.7},

    # Major water bodies (dark blue)
    'lake_champlain': {'file': 'docs/json/lake_champlain_with_island_cutouts.json', 'fill': '#1565c0', 'stroke': '#0d47a1', 'stroke_width': 0.5, 'fill_opacity': 0.8},
    'lake_memphremagog': {'file': 'docs/json/lake_memphremagog_full.json', 'fill': '#1565c0', 'stroke': '#0d47a1', 'stroke_width': 0.5, 'fill_opacity': 0.8},
    'richelieu_corridor': {'file': 'docs/json/richelieu_corridor_complete.json', 'fill': '#1565c0', 'stroke': '#0d47a1', 'stroke_width': 0.5, 'fill_opacity': 0.8, 'merge_features': True},
    'missisquoi_quebec': {'file': 'docs/json/missisquoi_bay_quebec_waters.json', 'fill': '#1565c0', 'stroke': '#0d47a1', 'stroke_width': 0.5, 'fill_opacity': 0.8},

    # Regional Highways (all states: VT, NY, NH, MA) - reduced stroke widths for plotter
    'regional_interstates': {'file': 'docs/json/regional_interstates.json', 'fill': 'none', 'stroke': '#d32f2f', 'stroke_width': 1.0, 'fill_opacity': 0},
    'regional_us_highways': {'file': 'docs/json/regional_us_highways.json', 'fill': 'none', 'stroke': '#1976d2', 'stroke_width': 0.75, 'fill_opacity': 0},
    'regional_state_routes': {'file': 'docs/json/regional_state_routes.json', 'fill': 'none', 'stroke': '#616161', 'stroke_width': 0.5, 'fill_opacity': 0},

    # Quebec Highways (Autoroutes)
    'quebec_highways': {'file': 'docs/json/quebec_highways.json', 'fill': 'none', 'stroke': '#424242', 'stroke_width': 0.75, 'fill_opacity': 0},

    # State boundary
    'vt_boundary': {'file': 'docs/json/vermont_boundary_detailed.json', 'fill': 'none', 'stroke': '#1e4320', 'stroke_width': 3.0, 'fill_opacity': 0},
}

# Shared layer order (bottom to top) - same for all maps, only crop differs
SHARED_LAYERS = [
    # Background regions
    'quebec', 'ny', 'nh', 'ma', 'me',
    # Major water bodies (BEFORE towns so islands show through holes)
    'lake_champlain', 'lake_memphremagog', 'richelieu_corridor', 'missisquoi_quebec',
    # Town boundaries (on top of water - islands will show their county color)
    'quebec_municipalities', 'ny_towns', 'nh_towns', 'ma_towns', 'me_towns',
    'vt_towns',
    # Regional hydro (smaller water features) - all states/provinces
    'quebec_rivers', 'quebec_lakes',
    'ny_rivers', 'ny_lakes',
    'vt_rivers', 'vt_lakes',
    'nh_rivers', 'nh_lakes',
    'ma_rivers', 'ma_lakes',
    # Regional highways (on top of everything)
    'regional_state_routes', 'quebec_highways', 'regional_us_highways', 'regional_interstates',
]

# Layer order for each map - all use shared layers, only crop/bounds differ
MAP_LAYERS = {
    'vermont_12x18': SHARED_LAYERS,
    'lake_champlain_12x24': SHARED_LAYERS,
}


def main():
    print("=" * 60)
    print("PEN PLOTTER SVG GENERATOR")
    print("=" * 60)

    output_dir = 'output/plotter_test_svgs'
    os.makedirs(output_dir, exist_ok=True)

    # Load all layers
    print("\nLoading layers...")
    all_layers = {}
    all_names = set()
    for layers in MAP_LAYERS.values():
        all_names.update(layers)

    for name in all_names:
        if name in LAYER_STYLES:
            filepath = LAYER_STYLES[name]['file']
            if os.path.exists(filepath):
                all_layers[name] = load_geojson(filepath)
                print(f"  {name}: {len(all_layers[name]['features'])} features")

    # Generate SVGs
    for map_name, layer_order in MAP_LAYERS.items():
        config = PRINT_CONFIGS[map_name]
        layers = {n: all_layers[n] for n in layer_order if n in all_layers}

        print(f"\n{'=' * 60}")
        print(f"MAP: {map_name}")
        print("-" * 60)

        for level, tolerance in SIMPLIFICATION_LEVELS.items():
            output_path = os.path.join(output_dir, f'{map_name}_{level}.svg')

            svg_content, stats = generate_svg(
                layers=layers,
                layer_styles=LAYER_STYLES,
                bounds=config['bounds'],
                width_in=config['width_in'],
                height_in=config['height_in'],
                tolerance=tolerance,
                title=f"{map_name} - {level}"
            )

            with open(output_path, 'w') as f:
                f.write(svg_content)

            size_kb = os.path.getsize(output_path) / 1024
            print(f"  {level}: {stats['simplified_vertices']:,} vertices, {size_kb:.1f} KB")

    print(f"\nOutput: {output_dir}/")


if __name__ == '__main__':
    main()
