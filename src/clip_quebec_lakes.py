#!/usr/bin/env python3
"""
Clip Quebec lakes at the US/CA border.

Quebec lakes data extends south into Lake Champlain. This clips
all features to stay north of the border (~45.0 latitude).
"""

import geopandas as gpd
import json
from pathlib import Path
from shapely.geometry import box
from shapely.ops import clip_by_rect

# US/CA border is approximately 45.0 latitude
# Use slightly south to avoid artifacts at exact border
BORDER_LAT = 45.005

# Bounding box for clipping (north of border only)
CLIP_BOUNDS = {
    'min_lon': -74.5,
    'max_lon': -70.5,
    'min_lat': BORDER_LAT,
    'max_lat': 47.0
}


def clip_to_canada(gdf):
    """Clip geometries to stay north of the US/CA border."""
    print(f"Clipping to north of latitude {BORDER_LAT}...")

    # Create clip box
    clip_box = box(
        CLIP_BOUNDS['min_lon'],
        CLIP_BOUNDS['min_lat'],
        CLIP_BOUNDS['max_lon'],
        CLIP_BOUNDS['max_lat']
    )

    # Clip each geometry
    clipped_geoms = []
    valid_indices = []

    for idx, row in gdf.iterrows():
        try:
            clipped = row.geometry.intersection(clip_box)
            if not clipped.is_empty and clipped.area > 0:
                clipped_geoms.append(clipped)
                valid_indices.append(idx)
        except Exception as e:
            print(f"  Warning: Could not clip feature {idx}: {e}")

    # Create new GeoDataFrame with clipped geometries
    result = gdf.loc[valid_indices].copy()
    result['geometry'] = clipped_geoms

    return result


def main():
    print("=" * 60)
    print("CLIP QUEBEC LAKES AT US/CA BORDER")
    print("=" * 60)

    input_path = Path(__file__).parent.parent / 'docs' / 'json' / 'quebec_lakes.json'
    output_path = input_path  # Overwrite

    print(f"\nInput: {input_path}")

    # Load current data
    gdf = gpd.read_file(input_path)
    print(f"Loaded {len(gdf)} features")

    # Check how many extend south of border
    min_lats = []
    for idx, row in gdf.iterrows():
        bounds = row.geometry.bounds
        min_lats.append(bounds[1])  # miny

    south_of_border = sum(1 for lat in min_lats if lat < BORDER_LAT)
    print(f"Features extending south of {BORDER_LAT}: {south_of_border}")

    # Clip to Canada only
    gdf_clipped = clip_to_canada(gdf)
    print(f"After clipping: {len(gdf_clipped)} features")

    # Simplify slightly for smaller file
    gdf_clipped['geometry'] = gdf_clipped.geometry.simplify(0.0005, preserve_topology=True)

    # Remove any tiny slivers that might have been created
    gdf_clipped['area_check'] = gdf_clipped.geometry.area
    gdf_clipped = gdf_clipped[gdf_clipped['area_check'] > 1e-8].copy()
    gdf_clipped = gdf_clipped.drop(columns=['area_check'])
    print(f"After removing slivers: {len(gdf_clipped)} features")

    # Export
    geojson = json.loads(gdf_clipped.to_json())
    geojson['name'] = 'Quebec Lakes (Border Region - Clipped)'
    geojson['feature_count'] = len(gdf_clipped)

    with open(output_path, 'w') as f:
        json.dump(geojson, f)

    size_kb = output_path.stat().st_size / 1024
    print(f"\nExported: {len(gdf_clipped)} features, {size_kb:.1f} KB")
    print("=" * 60)


if __name__ == '__main__':
    main()
