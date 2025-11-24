#!/usr/bin/env python3
"""
Create VT towns with water areas cut out using TIGER HYDROID data
Performs geometric difference: Town polygons - Water polygons
"""

import geopandas as gpd
import json
from shapely.ops import unary_union
from pathlib import Path

def create_towns_with_water_cutouts(
    counties=['Grand Isle'],
    output_json='docs/json/vt_towns_water_cutouts.json',
    output_html='docs/vt_towns_water_cutouts.html'
):
    """
    Create town geometries with water areas cut out

    Args:
        counties: List of county names to process (default: ['Grand Isle'])
        output_json: Path to output GeoJSON file
        output_html: Path to output HTML map
    """
    print("=" * 70)
    print("VT TOWNS WITH WATER CUTOUTS - Second Order Transform")
    print("=" * 70)

    # Load VT towns data
    print("\n1. Loading VT towns data...")
    with open('docs/json/vt_towns.json', 'r') as f:
        vt_towns_data = json.load(f)

    vt_towns = gpd.GeoDataFrame.from_features(vt_towns_data['features'])
    vt_towns.crs = 'EPSG:4326'
    print(f"   Total VT towns: {len(vt_towns)}")

    # Filter to specified counties
    print(f"\n2. Filtering to counties: {', '.join(counties)}...")
    target_towns = vt_towns[vt_towns['county_name'].isin(counties)].copy()
    print(f"   Towns in target counties: {len(target_towns)}")

    for county in counties:
        county_towns = target_towns[target_towns['county_name'] == county]
        print(f"   {county}: {len(county_towns)} towns")

    # Load VT Champlain water data
    print("\n3. Loading VT Champlain TIGER water data...")
    with open('docs/json/vt_champlain_tiger_hydroids.json', 'r') as f:
        water_data = json.load(f)

    water = gpd.GeoDataFrame.from_features(water_data['features'])
    water.crs = 'EPSG:4326'
    print(f"   Water features: {len(water)}")
    print(f"   Total water area: {water_data['metadata']['total_area_sqkm']:.2f} sq km")

    # Union all water features into single geometry for faster processing
    print("\n4. Creating unified water geometry...")
    water_union = unary_union(water.geometry)
    print(f"   ✓ Water features merged into single geometry")

    # Perform geometric difference for each town
    print("\n5. Cutting water from town geometries...")
    results = []
    original_area = 0
    new_area = 0
    water_removed = 0

    for idx, town in target_towns.iterrows():
        town_name = town['NAME']
        original_geom = town.geometry
        original_town_area = town['land_area_sqkm']

        # Perform difference: town - water
        try:
            new_geom = original_geom.difference(water_union)

            # Calculate new area
            new_town_area = new_geom.area * 111.32 * 111.32  # Rough conversion to sq km at this latitude
            water_cut = original_town_area - new_town_area

            # Create new feature with updated geometry
            new_feature = town.copy()
            new_feature['geometry'] = new_geom
            new_feature['original_land_area_sqkm'] = original_town_area
            new_feature['new_land_area_sqkm'] = new_town_area
            new_feature['water_removed_sqkm'] = water_cut

            results.append(new_feature)

            original_area += original_town_area
            new_area += new_town_area
            water_removed += water_cut

            print(f"   {town_name:25s} - Original: {original_town_area:6.2f} sq km, "
                  f"New: {new_town_area:6.2f} sq km, Cut: {water_cut:6.2f} sq km")

        except Exception as e:
            print(f"   ⚠️  Error processing {town_name}: {e}")
            results.append(town)

    print(f"\n   Total original area: {original_area:.2f} sq km")
    print(f"   Total new area: {new_area:.2f} sq km")
    print(f"   Total water removed: {water_removed:.2f} sq km")

    # Create output GeoDataFrame
    print("\n6. Creating output dataset...")
    result_gdf = gpd.GeoDataFrame(results, crs='EPSG:4326')

    # Export to GeoJSON
    print("\n7. Exporting to GeoJSON...")
    output_geojson = json.loads(result_gdf.to_json())
    output_geojson['metadata'] = {
        'description': 'VT towns with water areas cut out using TIGER HYDROID data',
        'counties': counties,
        'total_towns': len(result_gdf),
        'original_area_sqkm': float(original_area),
        'new_area_sqkm': float(new_area),
        'water_removed_sqkm': float(water_removed),
        'source_towns': 'US Census TIGER/Line County Subdivisions 2023',
        'source_water': 'VT Champlain TIGER HYDROIDs (Census TIGER 2022)',
        'method': 'Geometric difference (town polygons - water polygons)'
    }

    Path(output_json).parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, 'w') as f:
        json.dump(output_geojson, f, indent=2)

    file_size = Path(output_json).stat().st_size / 1024
    print(f"   ✓ Saved to {output_json}")
    print(f"   File size: {file_size:.1f} KB")

    print("\n" + "=" * 70)
    print("✅ COMPLETE!")
    print("=" * 70)
    print(f"\nCreated dataset with {len(result_gdf)} towns")
    print(f"Counties: {', '.join(counties)}")
    print(f"Water removed: {water_removed:.2f} sq km")
    print(f"\nNext: Run generate_water_cutout_maps.py to create visualizations")

    return output_json, result_gdf


if __name__ == '__main__':
    # Start with Grand Isle County
    create_towns_with_water_cutouts(
        counties=['Grand Isle'],
        output_json='docs/json/vt_grand_isle_water_cutouts.json',
        output_html='docs/vt_grand_isle_water_cutouts.html'
    )
