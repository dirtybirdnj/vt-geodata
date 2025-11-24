#!/usr/bin/env python3
"""
Create complete VT towns dataset with water cutouts for specific towns
Replaces specified GEOIDs with water-trimmed versions
"""

import geopandas as gpd
import pandas as pd
import json
from shapely.ops import unary_union
from pathlib import Path

def create_vt_towns_with_water_cutouts(
    champlain_geoids,
    memphremagog_geoids,
    output_json='docs/json/vt_towns_with_water_cutouts.json'
):
    """
    Create complete VT towns dataset with water cutouts for specified towns

    Args:
        champlain_geoids: List of GEOIDs to trim with Champlain HYDROIDs
        memphremagog_geoids: List of GEOIDs to trim with Lake Memphremagog
        output_json: Path to output GeoJSON file
    """
    print("=" * 70)
    print("VT TOWNS WITH WATER CUTOUTS - Complete Dataset")
    print("=" * 70)

    # Load VT towns data
    print("\n1. Loading VT towns data...")
    with open('docs/json/vt_towns.json', 'r') as f:
        vt_towns_data = json.load(f)

    vt_towns = gpd.GeoDataFrame.from_features(vt_towns_data['features'])
    vt_towns.crs = 'EPSG:4326'
    print(f"   Total VT towns: {len(vt_towns)}")

    # Combine all GEOIDs for summary
    all_geoids = champlain_geoids + memphremagog_geoids
    print(f"\n2. Identifying {len(all_geoids)} towns for water cutouts...")
    print(f"   - Champlain shoreline: {len(champlain_geoids)} towns")
    print(f"   - Lake Memphremagog: {len(memphremagog_geoids)} towns")

    towns_unchanged = vt_towns[~vt_towns['GEOID'].isin(all_geoids)].copy()
    print(f"   - Towns unchanged: {len(towns_unchanged)}")

    trimmed_towns = []
    total_water_removed = 0

    # Process Champlain shoreline towns
    if champlain_geoids:
        print("\n3. Processing Champlain shoreline towns...")
        print("   Loading VT Champlain TIGER HYDROIDs...")
        with open('docs/json/vt_champlain_tiger_hydroids.json', 'r') as f:
            champlain_data = json.load(f)

        champlain_water = gpd.GeoDataFrame.from_features(champlain_data['features'])
        champlain_water.crs = 'EPSG:4326'
        print(f"   Champlain water features: {len(champlain_water)}")

        champlain_union = unary_union(champlain_water.geometry)

        champlain_towns = vt_towns[vt_towns['GEOID'].isin(champlain_geoids)].copy()
        print(f"   Cutting water from {len(champlain_towns)} Champlain towns...")

        for idx, town in champlain_towns.iterrows():
            town_name = town['NAME']
            geoid = town['GEOID']
            original_area = town['land_area_sqkm']

            try:
                new_geom = town.geometry.difference(champlain_union)
                new_area = new_geom.area * 111.32 * 111.32
                water_cut = original_area - new_area

                new_feature = town.copy()
                new_feature['geometry'] = new_geom
                new_feature['original_land_area_sqkm'] = original_area
                new_feature['new_land_area_sqkm'] = new_area
                new_feature['water_cutout_applied'] = True
                new_feature['water_source'] = 'Champlain HYDROIDs'

                trimmed_towns.append(new_feature)
                total_water_removed += water_cut
                print(f"   {town_name:25s} ({geoid}) - Cut: {water_cut:7.2f} sq km")

            except Exception as e:
                print(f"   ⚠️  Error processing {town_name}: {e}")
                trimmed_towns.append(town)

    # Process Lake Memphremagog towns
    if memphremagog_geoids:
        print("\n4. Processing Lake Memphremagog towns...")
        print("   Loading Lake Memphremagog from Orleans County water data...")

        url = 'https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_50019_areawater.zip'
        orleans_water = gpd.read_file(url)
        if orleans_water.crs != 'EPSG:4326':
            orleans_water = orleans_water.to_crs('EPSG:4326')

        # Filter for Lake Memphremagog only
        memph_water = orleans_water[orleans_water['FULLNAME'].str.contains('Memphremagog', case=False, na=False)]
        print(f"   Lake Memphremagog features: {len(memph_water)}")
        print(f"   Area: {memph_water['AWATER'].sum() / 1_000_000:.2f} sq km")

        memph_union = unary_union(memph_water.geometry)

        memph_towns = vt_towns[vt_towns['GEOID'].isin(memphremagog_geoids)].copy()
        print(f"   Cutting water from {len(memph_towns)} Memphremagog towns...")

        for idx, town in memph_towns.iterrows():
            town_name = town['NAME']
            geoid = town['GEOID']
            original_area = town['land_area_sqkm']

            try:
                new_geom = town.geometry.difference(memph_union)
                new_area = new_geom.area * 111.32 * 111.32
                water_cut = original_area - new_area

                new_feature = town.copy()
                new_feature['geometry'] = new_geom
                new_feature['original_land_area_sqkm'] = original_area
                new_feature['new_land_area_sqkm'] = new_area
                new_feature['water_cutout_applied'] = True
                new_feature['water_source'] = 'Lake Memphremagog'

                trimmed_towns.append(new_feature)
                total_water_removed += water_cut
                print(f"   {town_name:25s} ({geoid}) - Cut: {water_cut:7.2f} sq km")

            except Exception as e:
                print(f"   ⚠️  Error processing {town_name}: {e}")
                trimmed_towns.append(town)

    print(f"\n   Total trimmed towns: {len(trimmed_towns)}")
    print(f"   Total water removed: {total_water_removed:.2f} sq km")

    # Add water_cutout_applied = False to unchanged towns
    for idx, town in towns_unchanged.iterrows():
        town['water_cutout_applied'] = False
        town['original_land_area_sqkm'] = town['land_area_sqkm']
        town['new_land_area_sqkm'] = town['land_area_sqkm']

    # Combine trimmed and unchanged towns
    print("\n5. Combining trimmed and unchanged towns...")
    all_towns = trimmed_towns + [towns_unchanged.iloc[i] for i in range(len(towns_unchanged))]
    result_gdf = gpd.GeoDataFrame(all_towns, crs='EPSG:4326')

    print(f"   Total towns in final dataset: {len(result_gdf)}")
    print(f"   Towns with water cutouts: {len([t for t in all_towns if t.get('water_cutout_applied', False)])}")

    # Export to GeoJSON
    print("\n6. Exporting to GeoJSON...")
    output_geojson = json.loads(result_gdf.to_json())
    output_geojson['metadata'] = {
        'description': 'Complete VT towns dataset with water cutouts for lakefront towns',
        'total_towns': len(result_gdf),
        'towns_with_cutouts': len(trimmed_towns),
        'towns_unchanged': len(towns_unchanged),
        'water_removed_sqkm': float(total_water_removed),
        'champlain_towns': len(champlain_geoids),
        'memphremagog_towns': len(memphremagog_geoids),
        'geoids_trimmed': all_geoids,
        'source_towns': 'US Census TIGER/Line County Subdivisions 2023',
        'source_water_champlain': 'VT Champlain TIGER HYDROIDs (Census TIGER 2022)',
        'source_water_memphremagog': 'Lake Memphremagog from Orleans County TIGER (Census TIGER 2022)',
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
    print(f"\nComplete VT towns dataset: {len(result_gdf)} towns")
    print(f"  • {len(trimmed_towns)} towns with water cutouts")
    print(f"  • {len(towns_unchanged)} towns unchanged")
    print(f"  • {total_water_removed:.2f} sq km water removed")

    return output_json, result_gdf


if __name__ == '__main__':
    # Lake Champlain shoreline towns - trimmed with Champlain HYDROIDs
    champlain_geoids = [
        # Grand Isle County (Champlain Islands)
        "5001300860",  # Alburgh
        "5001335875",  # Isle La Motte
        "5001350650",  # North Hero
        "5001329275",  # Grand Isle
        "5001367000",  # South Hero
        # Chittenden County (Champlain shoreline)
        "5000714875",  # Colchester
        "5000766175",  # South Burlington
        "5000764300",  # Shelburne
        "5000713300",  # Charlotte
        "5000710675",  # Burlington
        # Franklin County (Champlain shoreline)
        "5001127700",  # Georgia
        "5000745250",  # Milton
        "5001161750",  # St. Albans
        "5001171725",  # Swanton
        "5001133025",  # Highgate
        # Addison County (Champlain shoreline)
        "5000126300",  # Ferrisburgh
        "5000153950",  # Panton
        "5000100325",  # Addison
        "5000108575",  # Bridport
        "5000165050",  # Shoreham
        "5000153725",  # Orwell
        # Rutland County (Champlain shoreline)
        "5002105200",  # Benson
        "5002180875",  # West Haven
        "5002125375",  # Fair Haven
        "5002156875",  # Poultney
        "5002177950",  # Wells
        "5002154250",  # Pawlet
        # Bennington County (western border - Champlain watershed)
        "5000361000",  # Rupert
        "5000362875",  # Sandgate
        "5000301450",  # Arlington
        "5000363550",  # Shaftsbury
        "5000304825",  # Bennington
        "5000357025",  # Pownal
    ]

    # Lake Memphremagog towns - trimmed with Lake Memphremagog only
    memphremagog_geoids = [
        "5001948925",  # Newport (city)
        "5001917350",  # Derby
        "5001948850",  # Newport (town)
    ]

    create_vt_towns_with_water_cutouts(
        champlain_geoids=champlain_geoids,
        memphremagog_geoids=memphremagog_geoids,
        output_json='docs/json/vt_towns_with_water_cutouts.json'
    )
