#!/usr/bin/env python3
"""
Debug why specific edits aren't being applied.
"""

import json
import geopandas as gpd
import pandas as pd

# Load the edits file
with open('docs/json/categorized_water_edits.json', 'r') as f:
    edits_data = json.load(f)

# Target HYDROIDs to debug
target_hydroids = ['110262630370317', '110262630370329']

print("=" * 60)
print("Checking if HYDROIDs exist in edits file:")
print("=" * 60)

for hydroid in target_hydroids:
    found = [e for e in edits_data['edits'] if e['hydroid'] == hydroid]
    if found:
        print(f"\n✓ {hydroid} in edits file:")
        print(f"  {found[0]}")
    else:
        print(f"\n✗ {hydroid} NOT in edits file")

# Load water data from the 4 counties
print("\n" + "=" * 60)
print("Checking if HYDROIDs exist in source TIGER data:")
print("=" * 60)

counties = {
    '50013': 'Grand Isle',
    '50007': 'Chittenden',
    '50011': 'Franklin',
    '50001': 'Addison'
}

all_water = []
for fips, name in counties.items():
    print(f"  Loading {name} County...")
    url = f"https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_{fips}_areawater.zip"
    gdf = gpd.read_file(url)
    all_water.append(gdf)

water = gpd.GeoDataFrame(pd.concat(all_water, ignore_index=True))

print(f"\nTotal features: {len(water)}")

for hydroid in target_hydroids:
    found = water[water['HYDROID'] == hydroid]
    if len(found) > 0:
        row = found.iloc[0]
        print(f"\n✓ {hydroid} EXISTS in source data:")
        print(f"  FULLNAME: {row['FULLNAME']}")
        print(f"  MTFCC: {row['MTFCC']}")
        print(f"  AWATER: {row['AWATER']}")
    else:
        print(f"\n✗ {hydroid} NOT FOUND in source TIGER data")
