#!/usr/bin/env python3
"""
Get New York state data for Lake Champlain region to complement VT data.
NY counties bordering Lake Champlain: Clinton, Essex, Washington
"""

import geopandas as gpd
import pandas as pd
import json

print("=" * 70)
print("NEW YORK - LAKE CHAMPLAIN REGION DATA")
print("=" * 70)

# NY counties along Lake Champlain
ny_counties = {
    '36019': 'Clinton',
    '36031': 'Essex',
    '36115': 'Washington'
}

print("\n1. Loading NY county boundaries...")
all_county_boundaries = []
for fips, name in ny_counties.items():
    print(f"   Loading {name} County boundary...")
    url = f"https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip"
    counties = gpd.read_file(url)
    county = counties[counties['GEOID'] == fips].copy()
    all_county_boundaries.append(county)

ny_counties_gdf = gpd.GeoDataFrame(pd.concat(all_county_boundaries, ignore_index=True))
print(f"   Loaded {len(ny_counties_gdf)} NY counties")

# Convert to WGS84
if ny_counties_gdf.crs != 'EPSG:4326':
    ny_counties_gdf = ny_counties_gdf.to_crs('EPSG:4326')

print("\n2. Loading NY water data for Lake Champlain counties...")
all_water = []
for fips, name in ny_counties.items():
    print(f"   Loading {name} County water...")
    url = f"https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_{fips}_areawater.zip"
    gdf = gpd.read_file(url)
    all_water.append(gdf)

ny_water = gpd.GeoDataFrame(pd.concat(all_water, ignore_index=True))
ny_water['area_sqkm'] = ny_water.geometry.area * 111 * 111

print(f"   Total NY water features: {len(ny_water)}")

# Find Lake Champlain features
champlain = ny_water[ny_water['FULLNAME'].astype(str).str.contains('Champlain', case=False, na=False)]
print(f"   Lake Champlain features: {len(champlain)}")
print(f"   Total Lake Champlain area (NY side): {champlain['area_sqkm'].sum():.2f} sq km")

print("\n3. Exporting NY county boundaries...")
ny_counties_geojson = json.loads(ny_counties_gdf.to_json())
with open('docs/json/ny_champlain_counties.json', 'w') as f:
    json.dump(ny_counties_geojson, f, indent=2)
print("   ✓ Saved to docs/json/ny_champlain_counties.json")

print("\n4. Exporting NY Lake Champlain water...")
ny_champlain_geojson = json.loads(champlain.to_json())
ny_champlain_geojson['metadata'] = {
    'description': 'Lake Champlain water features (NY side) from Census TIGER 2022',
    'source': 'US Census TIGER/Line Shapefiles',
    'counties': list(ny_counties.values()),
    'total_features': len(champlain),
    'total_area_sqkm': float(champlain['area_sqkm'].sum())
}

with open('docs/json/ny_lake_champlain_water.json', 'w') as f:
    json.dump(ny_champlain_geojson, f, indent=2)
print("   ✓ Saved to docs/json/ny_lake_champlain_water.json")

print("\n5. Statistics:")
print(f"   NY counties: {len(ny_counties_gdf)}")
print(f"   NY Lake Champlain features: {len(champlain)}")
print(f"   Largest NY Champlain piece: {champlain['area_sqkm'].max():.2f} sq km")

# Compare with VT data
print("\n6. Comparison with VT data:")
with open('docs/json/lake_champlain_water.json', 'r') as f:
    vt_data = json.load(f)
    vt_area = vt_data['metadata']['total_area_sqkm']
    ny_area = float(champlain['area_sqkm'].sum())

    print(f"   VT side: {vt_area:.2f} sq km")
    print(f"   NY side: {ny_area:.2f} sq km")
    print(f"   Total Lake Champlain: {vt_area + ny_area:.2f} sq km")

print("\n" + "=" * 70)
print("✅ COMPLETE!")
print("=" * 70)
print("\nFiles created:")
print("  • docs/json/ny_champlain_counties.json - NY county boundaries")
print("  • docs/json/ny_lake_champlain_water.json - NY Lake Champlain water")
print("\nNext step:")
print("  • Update vermont_with_islands.html to include NY data")
