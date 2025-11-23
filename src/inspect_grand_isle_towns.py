#!/usr/bin/env python3
"""
Investigate Grand Isle County towns in the VT towns data
Check if Champlain Islands towns have proper geometries
"""

import geopandas as gpd
import json

print("=" * 70)
print("INVESTIGATING GRAND ISLE COUNTY TOWNS")
print("=" * 70)

# Load the VT towns JSON we created
print("\n1. Loading VT towns data from JSON...")
with open('docs/json/vt_towns.json', 'r') as f:
    towns_data = json.load(f)

# Convert back to GeoDataFrame
towns_gdf = gpd.GeoDataFrame.from_features(towns_data['features'])
towns_gdf.crs = 'EPSG:4326'

print(f"   Total towns loaded: {len(towns_gdf)}")

# Filter to Grand Isle County
grand_isle = towns_gdf[towns_gdf['county_name'] == 'Grand Isle'].copy()

print(f"\n2. Grand Isle County towns: {len(grand_isle)}")
print()

for idx, row in grand_isle.iterrows():
    print(f"   {row['NAME']}")
    print(f"      GEOID: {row['GEOID']}")
    print(f"      Land Area: {row['land_area_sqkm']:.2f} sq km")
    print(f"      Water Area: {row['water_area_sqkm']:.2f} sq km")
    print(f"      Total Area: {row['total_area_sqkm']:.2f} sq km")
    print(f"      Geometry Type: {row['geometry'].geom_type}")
    print(f"      Is Empty: {row['geometry'].is_empty}")
    if not row['geometry'].is_empty:
        bounds = row['geometry'].bounds
        print(f"      Bounds: ({bounds[1]:.4f}°N to {bounds[3]:.4f}°N, {bounds[0]:.4f}°W to {bounds[2]:.4f}°W)")
        print(f"      Centroid: ({row['geometry'].centroid.y:.4f}°N, {row['geometry'].centroid.x:.4f}°W)")
    print()

# Check if geometries are valid
print("\n3. Geometry validation:")
for idx, row in grand_isle.iterrows():
    is_valid = row['geometry'].is_valid
    print(f"   {row['NAME']}: Valid={is_valid}, Empty={row['geometry'].is_empty}")

# Also load directly from Census to compare
print("\n4. Loading directly from Census TIGER for comparison...")
url = "https://www2.census.gov/geo/tiger/TIGER2023/COUSUB/tl_2023_50_cousub.zip"
direct_gdf = gpd.read_file(url)

# Filter to Grand Isle County (COUNTYFP = 013)
direct_grand_isle = direct_gdf[direct_gdf['COUNTYFP'] == '013'].copy()

if direct_grand_isle.crs != 'EPSG:4326':
    direct_grand_isle = direct_grand_isle.to_crs('EPSG:4326')

print(f"   Direct from Census: {len(direct_grand_isle)} Grand Isle towns")
print()

for idx, row in direct_grand_isle.iterrows():
    print(f"   {row['NAME']}")
    print(f"      GEOID: {row['GEOID']}")
    print(f"      Land Area (ALAND): {row['ALAND']/1_000_000:.2f} sq km")
    print(f"      Water Area (AWATER): {row['AWATER']/1_000_000:.2f} sq km")
    print(f"      Geometry Type: {row['geometry'].geom_type}")
    if not row['geometry'].is_empty:
        bounds = row['geometry'].bounds
        print(f"      Bounds: ({bounds[1]:.4f}°N to {bounds[3]:.4f}°N, {bounds[0]:.4f}°W to {bounds[2]:.4f}°W)")
    print()

print("\n" + "=" * 70)
print("INVESTIGATION COMPLETE")
print("=" * 70)
