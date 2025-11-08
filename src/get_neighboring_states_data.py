#!/usr/bin/env python3
"""
Get neighboring state data (NH, MA) for complete regional view.
"""

import geopandas as gpd
import json

print("=" * 70)
print("NEIGHBORING STATES DATA")
print("=" * 70)

# New Hampshire
print("\n1. Loading New Hampshire state boundary...")
url = "https://www2.census.gov/geo/tiger/TIGER2023/STATE/tl_2023_us_state.zip"
states = gpd.read_file(url)
nh = states[states['STUSPS'] == 'NH'].copy()

if nh.crs != 'EPSG:4326':
    nh = nh.to_crs('EPSG:4326')

nh_geojson = json.loads(nh.to_json())
with open('docs/json/nh_boundary.json', 'w') as f:
    json.dump(nh_geojson, f, indent=2)
print("   ✓ Saved to docs/json/nh_boundary.json")

# Massachusetts
print("\n2. Loading Massachusetts state boundary...")
ma = states[states['STUSPS'] == 'MA'].copy()

if ma.crs != 'EPSG:4326':
    ma = ma.to_crs('EPSG:4326')

ma_geojson = json.loads(ma.to_json())
with open('docs/json/ma_boundary.json', 'w') as f:
    json.dump(ma_geojson, f, indent=2)
print("   ✓ Saved to docs/json/ma_boundary.json")

# New York (full state for context)
print("\n3. Loading New York state boundary...")
ny = states[states['STUSPS'] == 'NY'].copy()

if ny.crs != 'EPSG:4326':
    ny = ny.to_crs('EPSG:4326')

ny_geojson = json.loads(ny.to_json())
with open('docs/json/ny_boundary.json', 'w') as f:
    json.dump(ny_geojson, f, indent=2)
print("   ✓ Saved to docs/json/ny_boundary.json")

print("\n" + "=" * 70)
print("✅ COMPLETE!")
print("=" * 70)
print("\nFiles created:")
print("  • docs/json/nh_boundary.json - New Hampshire state boundary")
print("  • docs/json/ma_boundary.json - Massachusetts state boundary")
print("  • docs/json/ny_boundary.json - New York state boundary (full)")
print("\nNote: Quebec data would require Statistics Canada data")
print("      which has different licensing and format requirements.")
