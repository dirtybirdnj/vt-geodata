#!/usr/bin/env python3
"""
Inspect available fields in NY Census TIGER water data
"""

import geopandas as gpd
import pandas as pd

print("=" * 70)
print("INSPECTING NY CENSUS TIGER WATER DATA FIELDS")
print("=" * 70)

# Load a sample county (Clinton - where Rouses Point is)
fips = '36019'
county_name = 'Clinton'

print(f"\nLoading {county_name} County water data...")
url = f"https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_{fips}_areawater.zip"
gdf = gpd.read_file(url)

print(f"Loaded {len(gdf)} features\n")

print("=" * 70)
print("AVAILABLE FIELDS:")
print("=" * 70)
for i, col in enumerate(gdf.columns, 1):
    print(f"{i:2d}. {col:20s} - {gdf[col].dtype}")

print("\n" + "=" * 70)
print("SAMPLE DATA (first 5 rows):")
print("=" * 70)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
print(gdf.head())

print("\n" + "=" * 70)
print("FEATURES NEAR ROUSES POINT (Latitude ~45.0, Longitude ~-73.4):")
print("=" * 70)

# Calculate area
if gdf.crs != 'EPSG:4326':
    gdf = gdf.to_crs('EPSG:4326')

gdf['area_sqkm'] = gdf.geometry.area * 111 * 111

# Find features near Rouses Point
rouses_point_lat = 45.0
rouses_point_lon = -73.4

# Calculate distance from Rouses Point (rough approximation)
gdf['centroid'] = gdf.geometry.centroid
gdf['dist_from_rp'] = ((gdf['centroid'].y - rouses_point_lat)**2 +
                         (gdf['centroid'].x - rouses_point_lon)**2)**0.5

# Get features within ~0.05 degrees (~5km) of Rouses Point
near_rouses = gdf[gdf['dist_from_rp'] < 0.05].sort_values('area_sqkm', ascending=False)

print(f"\nFound {len(near_rouses)} features near Rouses Point:")
for idx, row in near_rouses.iterrows():
    print(f"\n  FULLNAME: {row['FULLNAME']}")
    print(f"  HYDROID:  {row['HYDROID']}")
    print(f"  MTFCC:    {row['MTFCC']}")
    print(f"  Area:     {row['area_sqkm']:.3f} sq km")
    print(f"  Location: ({row['centroid'].y:.4f}, {row['centroid'].x:.4f})")

print("\n" + "=" * 70)
print("MTFCC CODES EXPLANATION:")
print("=" * 70)
print("H2030 = Lake/Pond")
print("H2040 = Reservoir")
print("H2053 = Swamp/Marsh")
print("H2081 = Glacier")
print("H3010 = Stream/River")
print("H3013 = Braided Stream")
print("H3020 = Canal/Ditch/Aqueduct")
