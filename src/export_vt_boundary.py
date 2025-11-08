#!/usr/bin/env python3
"""
Export Vermont state boundary to GeoJSON for simplification demo.
"""

import geopandas as gpd
import json

# Load Vermont boundary from Census TIGER
print("Loading Vermont boundary from Census TIGER 2023...")
url = "https://www2.census.gov/geo/tiger/TIGER2023/STATE/tl_2023_us_state.zip"
states = gpd.read_file(url)

# Filter to Vermont (FIPS code 50)
vt = states[states['STATEFP'] == '50'].copy()

print(f"Vermont boundary loaded: {vt['NAME'].values[0]}")

# Convert to GeoJSON
geojson = json.loads(vt.to_json())

# Save to file
output_path = 'docs/json/vermont_boundary.json'
with open(output_path, 'w') as f:
    json.dump(geojson, f, indent=2)

print(f"✓ Saved to {output_path}")

# Print some stats
coords = geojson['features'][0]['geometry']['coordinates']
if geojson['features'][0]['geometry']['type'] == 'Polygon':
    total_points = sum(len(ring) for ring in coords)
elif geojson['features'][0]['geometry']['type'] == 'MultiPolygon':
    total_points = sum(sum(len(ring) for ring in polygon) for polygon in coords)
else:
    total_points = 0

print(f"Total coordinate points: {total_points:,}")
