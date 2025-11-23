#!/usr/bin/env python3
"""
Find the actual missing water piece NORTH of Rouses Point
"""

import geopandas as gpd

print("=" * 70)
print("FINDING WATER FEATURES NORTH OF ROUSES POINT")
print("=" * 70)

# Load Clinton County water
fips = '36019'
print(f"\nLoading Clinton County water data...")
url = f"https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_{fips}_areawater.zip"
gdf = gpd.read_file(url)

if gdf.crs != 'EPSG:4326':
    gdf = gdf.to_crs('EPSG:4326')

gdf['area_sqkm'] = gdf['AWATER'] / 1_000_000

# Rouses Point is at approximately 45.01, -73.37
# Search for features that extend NORTH of latitude 45.0
print(f"\nSearching for features that extend north of 45.0° latitude...")
print(f"Rouses Point location: ~45.01°N, -73.37°W\n")

# Get features that have any part above 45.0
gdf['centroid'] = gdf.geometry.centroid
gdf['max_lat'] = gdf.geometry.bounds['maxy']
north_of_45 = gdf[gdf['max_lat'] > 45.0].copy()

# Filter to reasonable size (>0.5 sq km) and near Rouses Point longitude
near_rouses = north_of_45[
    (north_of_45['area_sqkm'] > 0.5) &
    (north_of_45['centroid'].x > -73.5) &
    (north_of_45['centroid'].x < -73.2)
].sort_values('area_sqkm', ascending=False)

print(f"Found {len(near_rouses)} features >0.5 sq km extending north of 45.0°:\n")
for idx, row in near_rouses.iterrows():
    print(f"  HYDROID: {row['HYDROID']}")
    print(f"  FULLNAME: {row['FULLNAME']}")
    print(f"  Area: {row['area_sqkm']:.2f} sq km")
    print(f"  Centroid: ({row['centroid'].y:.4f}°N, {row['centroid'].x:.4f}°W)")
    print(f"  MTFCC: {row['MTFCC']}")
    print()
