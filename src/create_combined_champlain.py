#!/usr/bin/env python3
"""
Create a combined Lake Champlain geometry from VT and NY water features.
Preserves islands as holes in the water polygon.
"""

import geopandas as gpd
import pandas as pd
import json
from shapely.ops import unary_union
from shapely.geometry import mapping, shape
from pathlib import Path

def main():
    print("=" * 70)
    print("COMBINED LAKE CHAMPLAIN (VT + NY)")
    print("=" * 70)

    output_dir = Path('docs/json')

    # Load VT Lake Champlain
    print("\n1. Loading VT Lake Champlain water features...")
    vt_champlain = gpd.read_file(output_dir / 'lake_champlain_water.json')
    print(f"   VT features: {len(vt_champlain)}")
    print(f"   VT total area: {vt_champlain['area_sqkm'].sum():.2f} sq km")

    # Load NY Lake Champlain
    print("\n2. Loading NY Lake Champlain water features...")
    ny_champlain = gpd.read_file(output_dir / 'ny_lake_champlain_water.json')
    print(f"   NY features: {len(ny_champlain)}")
    print(f"   NY total area: {ny_champlain['area_sqkm'].sum():.2f} sq km")

    # Combine all features
    print("\n3. Combining VT and NY Lake Champlain...")
    combined = gpd.GeoDataFrame(pd.concat([vt_champlain, ny_champlain], ignore_index=True))
    print(f"   Combined features: {len(combined)}")

    # Union all geometries into one
    print("\n4. Creating unified geometry (preserving islands as holes)...")
    unified_geometry = unary_union(combined.geometry)
    print(f"   Geometry type: {unified_geometry.geom_type}")

    if unified_geometry.geom_type == 'MultiPolygon':
        print(f"   Number of polygons: {len(unified_geometry.geoms)}")
        # Count holes (islands) across all polygons
        total_holes = sum(len(poly.interiors) for poly in unified_geometry.geoms)
        print(f"   Total holes (islands): {total_holes}")
    elif unified_geometry.geom_type == 'Polygon':
        print(f"   Number of holes (islands): {len(unified_geometry.interiors)}")

    # Calculate area
    # Approximate area calculation (degrees to sq km at ~44 latitude)
    # 1 degree longitude ≈ 79 km at 44°N
    # 1 degree latitude ≈ 111 km
    total_area_sqkm = combined['area_sqkm'].sum()
    print(f"\n5. Total Lake Champlain area: {total_area_sqkm:.2f} sq km")

    # Create GeoDataFrame with single unified feature
    unified_gdf = gpd.GeoDataFrame(
        [{
            'geometry': unified_geometry,
            'NAME': 'Lake Champlain',
            'FULLNAME': 'Lake Champlain (Combined VT + NY)',
            'area_sqkm': total_area_sqkm,
            'source': 'US Census TIGER 2022 (VT + NY counties)',
            'vt_features': len(vt_champlain),
            'ny_features': len(ny_champlain),
        }],
        crs='EPSG:4326'
    )

    # Export combined file
    print("\n6. Exporting combined Lake Champlain...")

    # Export as GeoJSON
    combined_geojson = json.loads(unified_gdf.to_json())
    combined_geojson['metadata'] = {
        'description': 'Lake Champlain combined water (VT + NY sides)',
        'source': 'US Census TIGER/Line 2022',
        'vt_features_merged': len(vt_champlain),
        'ny_features_merged': len(ny_champlain),
        'total_area_sqkm': total_area_sqkm,
        'note': 'Islands preserved as holes in the water polygon'
    }

    with open(output_dir / 'lake_champlain_combined.json', 'w') as f:
        json.dump(combined_geojson, f, indent=2)
    print(f"   ✓ Saved lake_champlain_combined.json")

    # Also export the multi-feature version (all individual pieces)
    print("\n7. Exporting multi-feature version (all pieces)...")
    combined['source_state'] = ['VT'] * len(vt_champlain) + ['NY'] * len(ny_champlain)
    multi_geojson = json.loads(combined.to_json())
    multi_geojson['metadata'] = {
        'description': 'Lake Champlain water features (VT + NY, all pieces)',
        'source': 'US Census TIGER/Line 2022',
        'vt_features': len(vt_champlain),
        'ny_features': len(ny_champlain),
        'total_features': len(combined),
        'total_area_sqkm': total_area_sqkm
    }

    with open(output_dir / 'lake_champlain_combined_multi.json', 'w') as f:
        json.dump(multi_geojson, f, indent=2)
    print(f"   ✓ Saved lake_champlain_combined_multi.json")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nVT Lake Champlain:")
    print(f"  - Features: {len(vt_champlain)}")
    print(f"  - Area: {vt_champlain['area_sqkm'].sum():.2f} sq km")

    print(f"\nNY Lake Champlain:")
    print(f"  - Features: {len(ny_champlain)}")
    print(f"  - Area: {ny_champlain['area_sqkm'].sum():.2f} sq km")

    print(f"\nCombined Lake Champlain:")
    print(f"  - Total area: {total_area_sqkm:.2f} sq km")
    print(f"  - Geometry type: {unified_geometry.geom_type}")

    if unified_geometry.geom_type == 'MultiPolygon':
        for i, poly in enumerate(unified_geometry.geoms):
            # Calculate approximate area for each polygon
            poly_area = poly.area * 79 * 111  # rough conversion
            print(f"  - Polygon {i+1}: {len(poly.interiors)} holes, ~{poly_area:.1f} sq km")

    print("\n" + "=" * 70)
    print("✅ COMPLETE!")
    print("=" * 70)
    print("\nFiles created:")
    print("  • docs/json/lake_champlain_combined.json - Unified single geometry")
    print("  • docs/json/lake_champlain_combined_multi.json - All individual pieces")
    print("\nNote: Islands are preserved as holes in the water polygon")


if __name__ == '__main__':
    main()
