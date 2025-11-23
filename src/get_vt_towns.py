#!/usr/bin/env python3
"""
Get Vermont town/city boundaries from Census TIGER County Subdivisions
Vermont FIPS: 50
"""

import geopandas as gpd
import json

def main():
    """Main function to get VT town boundaries"""
    print("=" * 70)
    print("VERMONT - TOWN/CITY BOUNDARIES (County Subdivisions)")
    print("=" * 70)

    print("\n1. Downloading Vermont county subdivisions from Census TIGER 2023...")
    url = "https://www2.census.gov/geo/tiger/TIGER2023/COUSUB/tl_2023_50_cousub.zip"

    gdf = gpd.read_file(url)
    print(f"   Loaded {len(gdf)} towns/cities")

    # Convert to WGS84
    if gdf.crs != 'EPSG:4326':
        gdf = gdf.to_crs('EPSG:4326')

    print("\n2. Processing town data...")
    # Calculate areas in sq km
    # ALAND and AWATER are in square meters from Census
    gdf['land_area_sqkm'] = gdf['ALAND'] / 1_000_000
    gdf['water_area_sqkm'] = gdf['AWATER'] / 1_000_000
    gdf['total_area_sqkm'] = gdf['land_area_sqkm'] + gdf['water_area_sqkm']

    # Get county name from COUNTYFP
    county_names = {
        '001': 'Addison',
        '003': 'Bennington',
        '005': 'Caledonia',
        '007': 'Chittenden',
        '009': 'Essex',
        '011': 'Franklin',
        '013': 'Grand Isle',
        '015': 'Lamoille',
        '017': 'Orange',
        '019': 'Orleans',
        '021': 'Rutland',
        '023': 'Washington',
        '025': 'Windham',
        '027': 'Windsor'
    }
    gdf['county_name'] = gdf['COUNTYFP'].map(county_names)

    print(f"   Total towns/cities: {len(gdf)}")
    print(f"   Total land area: {gdf['land_area_sqkm'].sum():.2f} sq km")
    print(f"   Total water area: {gdf['water_area_sqkm'].sum():.2f} sq km")

    print("\n3. Statistics by county:")
    county_stats = gdf.groupby('county_name').agg({
        'NAME': 'count',
        'land_area_sqkm': 'sum'
    }).round(2)
    county_stats.columns = ['Towns', 'Land Area (sq km)']
    print(county_stats.to_string())

    print("\n4. Largest towns by total area:")
    top_towns = gdf.nlargest(10, 'total_area_sqkm')[['NAME', 'county_name', 'total_area_sqkm']]
    for idx, row in top_towns.iterrows():
        print(f"   {row['NAME']:30s} ({row['county_name']:12s}): {row['total_area_sqkm']:6.2f} sq km")

    print("\n5. Exporting to JSON...")

    # Create GeoJSON with selected fields
    export_gdf = gdf[['NAME', 'GEOID', 'COUNTYFP', 'county_name',
                      'land_area_sqkm', 'water_area_sqkm', 'total_area_sqkm',
                      'geometry']].copy()

    towns_geojson = json.loads(export_gdf.to_json())
    towns_geojson['metadata'] = {
        'description': 'Vermont town and city boundaries from Census TIGER 2023',
        'source': 'US Census TIGER/Line Shapefiles - County Subdivisions',
        'total_towns': len(gdf),
        'total_land_area_sqkm': float(gdf['land_area_sqkm'].sum()),
        'total_water_area_sqkm': float(gdf['water_area_sqkm'].sum()),
        'year': 2023
    }

    with open('docs/json/vt_towns.json', 'w') as f:
        json.dump(towns_geojson, f, indent=2)
    print("   ✓ Saved to docs/json/vt_towns.json")

    # Check file size
    import os
    file_size = os.path.getsize('docs/json/vt_towns.json') / 1024
    print(f"   File size: {file_size:.1f} KB")

    print("\n" + "=" * 70)
    print("✅ COMPLETE!")
    print("=" * 70)
    print("\nFile created:")
    print("  • docs/json/vt_towns.json - Vermont town boundaries")
    print(f"\nData includes {len(gdf)} towns/cities across {len(county_names)} Vermont counties")


if __name__ == '__main__':
    main()
