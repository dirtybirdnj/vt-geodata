#!/usr/bin/env python3
"""
Create regional towns (NH, MA, ME) with water areas cut out using hydro data
Performs geometric difference: Town polygons - Water polygons (lakes + rivers)
"""

import geopandas as gpd
import json
from shapely.ops import unary_union
from shapely.validation import make_valid
from pathlib import Path


def create_towns_with_water_cutouts(
    state_code,
    towns_file,
    lakes_file,
    rivers_file=None,
    output_file=None
):
    """
    Create town geometries with water areas cut out

    Args:
        state_code: State abbreviation (nh, ma, me)
        towns_file: Path to towns GeoJSON
        lakes_file: Path to lakes GeoJSON
        rivers_file: Path to rivers GeoJSON (optional)
        output_file: Path to output GeoJSON (default: {state}_towns_with_water_cutouts.json)
    """
    state_name = {
        'nh': 'New Hampshire',
        'ma': 'Massachusetts',
        'me': 'Maine'
    }.get(state_code.lower(), state_code.upper())

    if output_file is None:
        output_file = f'docs/json/{state_code.lower()}_towns_with_water_cutouts.json'

    print("=" * 70)
    print(f"{state_name.upper()} TOWNS WITH WATER CUTOUTS")
    print("=" * 70)

    # Load towns data
    print(f"\n1. Loading {state_name} towns data...")
    with open(towns_file, 'r') as f:
        towns_data = json.load(f)

    towns = gpd.GeoDataFrame.from_features(towns_data['features'])
    towns.crs = 'EPSG:4326'
    print(f"   Total towns: {len(towns)}")

    # Load lakes data
    print(f"\n2. Loading {state_name} lakes data...")
    with open(lakes_file, 'r') as f:
        lakes_data = json.load(f)

    lakes = gpd.GeoDataFrame.from_features(lakes_data['features'])
    lakes.crs = 'EPSG:4326'
    print(f"   Lakes features: {len(lakes)}")

    # Load rivers data if provided
    water_features = [lakes]
    if rivers_file and Path(rivers_file).exists():
        print(f"\n3. Loading {state_name} rivers data...")
        with open(rivers_file, 'r') as f:
            rivers_data = json.load(f)

        rivers = gpd.GeoDataFrame.from_features(rivers_data['features'])
        rivers.crs = 'EPSG:4326'
        print(f"   Rivers features: {len(rivers)}")
        water_features.append(rivers)

    # Combine all water features
    print(f"\n4. Creating unified water geometry...")
    all_water = gpd.GeoDataFrame(pd.concat(water_features, ignore_index=True), crs='EPSG:4326')

    # Make geometries valid and union
    valid_water = all_water.geometry.apply(make_valid)
    water_union = unary_union(valid_water)
    print(f"   ✓ {len(all_water)} water features merged into single geometry")

    # Perform geometric difference for each town
    print(f"\n5. Cutting water from town geometries...")
    results = []
    towns_modified = 0

    for idx, town in towns.iterrows():
        town_name = town.get('NAME', f'Town {idx}')
        original_geom = town.geometry

        # Make geometry valid
        if not original_geom.is_valid:
            original_geom = make_valid(original_geom)

        # Perform difference: town - water
        try:
            new_geom = original_geom.difference(water_union)

            # Check if geometry was modified
            if not new_geom.equals(original_geom):
                towns_modified += 1

            # Create new feature with updated geometry
            new_feature = town.copy()
            new_feature['geometry'] = new_geom
            results.append(new_feature)

        except Exception as e:
            print(f"   ⚠️  Error processing {town_name}: {e}")
            results.append(town)

    print(f"   ✓ Processed {len(towns)} towns, {towns_modified} modified")

    # Create output GeoDataFrame
    print(f"\n6. Creating output dataset...")
    result_gdf = gpd.GeoDataFrame(results, crs='EPSG:4326')

    # Export to GeoJSON
    print(f"\n7. Exporting to GeoJSON...")
    output_geojson = json.loads(result_gdf.to_json())
    output_geojson['metadata'] = {
        'description': f'{state_name} towns with water areas cut out',
        'total_towns': len(result_gdf),
        'towns_modified': towns_modified,
        'source_towns': towns_file,
        'source_lakes': lakes_file,
        'source_rivers': rivers_file,
        'method': 'Geometric difference (town polygons - water polygons)'
    }

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(output_geojson, f)

    file_size = Path(output_file).stat().st_size / 1024
    print(f"   ✓ Saved to {output_file}")
    print(f"   File size: {file_size:.1f} KB")

    print("\n" + "=" * 70)
    print("✅ COMPLETE!")
    print("=" * 70)

    return output_file


def create_nh_towns_with_water_cutouts():
    """Create NH towns with water cutouts"""
    return create_towns_with_water_cutouts(
        state_code='nh',
        towns_file='docs/json/nh_towns.json',
        lakes_file='docs/json/nh_lakes.json',
        rivers_file='docs/json/nh_rivers.json',
        output_file='docs/json/nh_towns_with_water_cutouts.json'
    )


def create_ma_towns_with_water_cutouts():
    """Create MA towns with water cutouts"""
    return create_towns_with_water_cutouts(
        state_code='ma',
        towns_file='docs/json/ma_towns.json',
        lakes_file='docs/json/ma_lakes.json',
        rivers_file='docs/json/ma_rivers.json',
        output_file='docs/json/ma_towns_with_water_cutouts.json'
    )


def create_me_towns_with_water_cutouts():
    """Create ME towns with water cutouts"""
    return create_towns_with_water_cutouts(
        state_code='me',
        towns_file='docs/json/me_towns.json',
        lakes_file='docs/json/me_lakes.json',
        rivers_file='docs/json/me_rivers.json',
        output_file='docs/json/me_towns_with_water_cutouts.json'
    )


if __name__ == '__main__':
    import pandas as pd
    import sys

    if len(sys.argv) > 1:
        state = sys.argv[1].lower()
        if state == 'nh':
            create_nh_towns_with_water_cutouts()
        elif state == 'ma':
            create_ma_towns_with_water_cutouts()
        elif state == 'me':
            create_me_towns_with_water_cutouts()
        else:
            print(f"Unknown state: {state}")
            print("Usage: python create_regional_towns_water_cutouts.py [nh|ma|me]")
    else:
        # Default to NH
        create_nh_towns_with_water_cutouts()
