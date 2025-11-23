#!/usr/bin/env python3
"""
Find Poultney River features in VT and NY data
The Poultney River forms part of the VT-NY border near Rutland County
"""

import geopandas as gpd
import pandas as pd

print("=" * 70)
print("SEARCHING FOR POULTNEY RIVER FEATURES")
print("=" * 70)

# VT counties near Poultney River (Rutland, Bennington)
vt_counties = {
    '50021': 'Rutland',
    '50003': 'Bennington'
}

# NY counties near Poultney River (Washington)
ny_counties = {
    '36115': 'Washington'
}

print("\n1. Loading VT water data for Rutland and Bennington counties...")
vt_water = []
for fips, name in vt_counties.items():
    print(f"   Loading {name} County water...")
    url = f"https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_{fips}_areawater.zip"
    gdf = gpd.read_file(url)
    vt_water.append(gdf)

vt_all = gpd.GeoDataFrame(pd.concat(vt_water, ignore_index=True))
vt_all['area_sqkm'] = vt_all['AWATER'] / 1_000_000

print(f"\n2. Searching VT data for 'Poultney' features...")
poultney_vt = vt_all[vt_all['FULLNAME'].astype(str).str.contains('Poultney', case=False, na=False)]
print(f"   Found {len(poultney_vt)} features with 'Poultney' in name\n")

if len(poultney_vt) > 0:
    for idx, row in poultney_vt.sort_values('area_sqkm', ascending=False).iterrows():
        print(f"   VT - {row['FULLNAME']}")
        print(f"      HYDROID: {row['HYDROID']}")
        print(f"      MTFCC: {row['MTFCC']} ({row.get('MTFCC', 'Unknown')})")
        print(f"      Area: {row['area_sqkm']:.4f} sq km")
        print()

print("\n3. Loading NY water data for Washington County...")
ny_water = []
for fips, name in ny_counties.items():
    print(f"   Loading {name} County water...")
    url = f"https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_{fips}_areawater.zip"
    gdf = gpd.read_file(url)
    ny_water.append(gdf)

ny_all = gpd.GeoDataFrame(pd.concat(ny_water, ignore_index=True))
ny_all['area_sqkm'] = ny_all['AWATER'] / 1_000_000

print(f"\n4. Searching NY data for 'Poultney' features...")
poultney_ny = ny_all[ny_all['FULLNAME'].astype(str).str.contains('Poultney', case=False, na=False)]
print(f"   Found {len(poultney_ny)} features with 'Poultney' in name\n")

if len(poultney_ny) > 0:
    for idx, row in poultney_ny.sort_values('area_sqkm', ascending=False).iterrows():
        print(f"   NY - {row['FULLNAME']}")
        print(f"      HYDROID: {row['HYDROID']}")
        print(f"      MTFCC: {row['MTFCC']}")
        print(f"      Area: {row['area_sqkm']:.4f} sq km")
        print()

# Also check for unnamed features near Poultney location (~43.5N, -73.2W)
print("\n5. Checking for unnamed water features near Poultney location...")
print("   Poultney, VT is approximately at 43.5°N, 73.2°W")

if vt_all.crs != 'EPSG:4326':
    vt_all = vt_all.to_crs('EPSG:4326')

vt_all['centroid'] = vt_all.geometry.centroid

# Find features near Poultney
near_poultney = vt_all[
    (vt_all['centroid'].y > 43.4) & (vt_all['centroid'].y < 43.6) &
    (vt_all['centroid'].x > -73.3) & (vt_all['centroid'].x < -73.1) &
    (vt_all['area_sqkm'] > 0.01)
].copy()

print(f"\n   Found {len(near_poultney)} VT features >0.01 sq km near Poultney:\n")
for idx, row in near_poultney.sort_values('area_sqkm', ascending=False).head(20).iterrows():
    print(f"   {row['FULLNAME'] if row['FULLNAME'] else '(unnamed)'}")
    print(f"      HYDROID: {row['HYDROID']}")
    print(f"      MTFCC: {row['MTFCC']}")
    print(f"      Area: {row['area_sqkm']:.4f} sq km")
    print(f"      Location: ({row['centroid'].y:.4f}°N, {row['centroid'].x:.4f}°W)")
    print()

print("\n" + "=" * 70)
print("SEARCH COMPLETE")
print("=" * 70)
