#!/usr/bin/env python3
"""
Merge Lake Champlain water features from VT and NY into a single unified geometry.
Preserves islands as holes in the water polygon.
"""

import json
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
from shapely.validation import make_valid

def load_geojson(filepath):
    """Load GeoJSON file and return features."""
    with open(filepath) as f:
        data = json.load(f)
    return data['features']

def merge_lake_features():
    """Merge VT and NY lake features into a single unified geometry."""

    # Load source data
    print("Loading VT TIGER hydroids...")
    vt_features = load_geojson('docs/json/vt_champlain_tiger_hydroids.json')
    print(f"  Loaded {len(vt_features)} VT features")

    print("Loading NY TIGER hydroids...")
    ny_features = load_geojson('docs/json/ny_champlain_tiger_hydroids.json')
    print(f"  Loaded {len(ny_features)} NY features")

    # Convert all features to shapely geometries
    all_geometries = []

    print("\nConverting VT geometries...")
    for feat in vt_features:
        try:
            geom = shape(feat['geometry'])
            if not geom.is_valid:
                geom = make_valid(geom)
            all_geometries.append(geom)
        except Exception as e:
            print(f"  Warning: Could not process VT feature: {e}")

    print("Converting NY geometries...")
    for feat in ny_features:
        try:
            geom = shape(feat['geometry'])
            if not geom.is_valid:
                geom = make_valid(geom)
            all_geometries.append(geom)
        except Exception as e:
            print(f"  Warning: Could not process NY feature: {e}")

    print(f"\nTotal geometries to merge: {len(all_geometries)}")

    # Union all geometries into a single shape
    print("Performing union operation (this may take a moment)...")
    merged = unary_union(all_geometries)

    # Make sure result is valid
    if not merged.is_valid:
        print("Making result valid...")
        merged = make_valid(merged)

    # Calculate stats
    area_sqkm = merged.area * 111 * 111  # Rough conversion at ~44° latitude

    print(f"\nResult geometry type: {merged.geom_type}")
    print(f"Approximate area: {area_sqkm:.2f} sq km")

    if merged.geom_type == 'MultiPolygon':
        print(f"Number of polygons: {len(merged.geoms)}")
        # Count total holes (interior rings)
        total_holes = sum(len(list(poly.interiors)) for poly in merged.geoms)
        print(f"Total holes (islands): {total_holes}")
    elif merged.geom_type == 'Polygon':
        print(f"Number of holes (islands): {len(list(merged.interiors))}")

    # Create output GeoJSON
    output = {
        "type": "FeatureCollection",
        "features": [
            {
                "id": "0",
                "type": "Feature",
                "properties": {
                    "NAME": "Lake Champlain",
                    "FULLNAME": "Lake Champlain (Unified VT + NY)",
                    "area_sqkm": round(area_sqkm, 2),
                    "source": "US Census TIGER 2022 - VT & NY hydroids merged",
                    "vt_features": len(vt_features),
                    "ny_features": len(ny_features),
                    "geometry_type": merged.geom_type
                },
                "geometry": mapping(merged)
            }
        ]
    }

    # Write output
    output_path = 'docs/json/lake_champlain_unified.json'
    print(f"\nWriting to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(output, f)

    # Get file size
    import os
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Output file size: {size_mb:.2f} MB")

    print("\nDone!")
    return output_path

if __name__ == '__main__':
    merge_lake_features()
