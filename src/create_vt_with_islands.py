#!/usr/bin/env python3
"""
Create a comprehensive Vermont map showing the mainland and Champlain Islands.
Uses VT Open Geodata boundary + Census TIGER water for accurate island representation.
"""

import geopandas as gpd
import pandas as pd
import json
from pathlib import Path

print("=" * 70)
print("VERMONT BOUNDARY WITH CHAMPLAIN ISLANDS")
print("=" * 70)

# 1. Load Vermont boundary from VT Open Geodata
print("\n1. Loading Vermont state boundary...")
vt_boundary_url = "https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPENDATA_Boundary_BNDHASH_poly_vtbnd_SP_v1/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson"
vt_boundary = gpd.read_file(vt_boundary_url)
print(f"   Loaded {len(vt_boundary)} boundary features")

# Convert to WGS84
if vt_boundary.crs != 'EPSG:4326':
    vt_boundary = vt_boundary.to_crs('EPSG:4326')

# 2. Load Lake Champlain water from Census TIGER (4 counties)
print("\n2. Loading Lake Champlain region water (Census TIGER)...")
counties = {
    '50013': 'Grand Isle',
    '50007': 'Chittenden',
    '50011': 'Franklin',
    '50001': 'Addison'
}

all_water = []
for fips, name in counties.items():
    print(f"   Loading {name} County...")
    url = f"https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_{fips}_areawater.zip"
    gdf = gpd.read_file(url)
    all_water.append(gdf)

water = gpd.GeoDataFrame(pd.concat(all_water, ignore_index=True))
water['area_sqkm'] = water.geometry.area * 111 * 111

print(f"\n   Total water features: {len(water)}")

# Get Lake Champlain features
champlain = water[water['FULLNAME'].astype(str).str.contains('Champlain', case=False, na=False)]
print(f"   Lake Champlain features: {len(champlain)}")
print(f"   Total Lake Champlain area: {champlain['area_sqkm'].sum():.2f} sq km")

# 3. Export Vermont boundary
print("\n3. Exporting Vermont boundary...")
vt_geojson = json.loads(vt_boundary.to_json())
with open('docs/json/vermont_boundary_detailed.json', 'w') as f:
    json.dump(vt_geojson, f, indent=2)
print("   ✓ Saved to docs/json/vermont_boundary_detailed.json")

# 4. Export Lake Champlain
print("\n4. Exporting Lake Champlain water features...")
champlain_geojson = json.loads(champlain.to_json())
champlain_geojson['metadata'] = {
    'description': 'Lake Champlain water features from Census TIGER 2022',
    'source': 'US Census TIGER/Line Shapefiles',
    'counties': list(counties.values()),
    'total_features': len(champlain),
    'total_area_sqkm': float(champlain['area_sqkm'].sum())
}

with open('docs/json/lake_champlain_water.json', 'w') as f:
    json.dump(champlain_geojson, f, indent=2)
print("   ✓ Saved to docs/json/lake_champlain_water.json")

# 5. Count coordinate points
vt_coords = vt_geojson['features'][0]['geometry']['coordinates']
if vt_geojson['features'][0]['geometry']['type'] == 'Polygon':
    vt_points = sum(len(ring) for ring in vt_coords)
elif vt_geojson['features'][0]['geometry']['type'] == 'MultiPolygon':
    vt_points = sum(sum(len(ring) for ring in polygon) for polygon in vt_coords)

print(f"\n5. Statistics:")
print(f"   Vermont boundary points: {vt_points:,}")
print(f"   Lake Champlain features: {len(champlain)}")
print(f"   Largest Champlain piece: {champlain['area_sqkm'].max():.2f} sq km")

print("\n" + "=" * 70)
print("✅ COMPLETE!")
print("=" * 70)
print("\nFiles created:")
print("  • docs/json/vermont_boundary_detailed.json - VT boundary with islands")
print("  • docs/json/lake_champlain_water.json - Lake Champlain water features")
print("\nNext steps:")
print("  • Create interactive map showing VT boundary + Lake Champlain")
print("  • Islands will appear as holes/gaps in Lake Champlain water")
