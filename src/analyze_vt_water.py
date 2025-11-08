#!/usr/bin/env python3
"""
Analyze Vermont Open Data water features to understand what's available
for Lake Champlain and the Champlain Islands.
"""

import geopandas as gpd
import pandas as pd
import json

print("=" * 70)
print("VERMONT OPEN DATA - WATER ANALYSIS")
print("=" * 70)

# Load VT Open Data water polygons
print("\n1. Loading VT Open Geodata water polygons...")
vt_water_url = "https://services1.arcgis.com/BkFxaEFNwHqX3tAw/arcgis/rest/services/FS_VCGI_OPENDATA_Water_VHDCARTO_poly_SP_v1/FeatureServer/0/query?where=1%3D1&outFields=*&f=geojson"
vt_water = gpd.read_file(vt_water_url)
print(f"   Total features: {len(vt_water)}")
print(f"   Columns: {list(vt_water.columns)}")

# Calculate areas
if vt_water.crs != 'EPSG:4326':
    vt_water_wgs84 = vt_water.to_crs('EPSG:4326')
else:
    vt_water_wgs84 = vt_water.copy()

vt_water_wgs84['area_sqkm'] = vt_water_wgs84.geometry.area * 111 * 111

print(f"\n2. Area statistics:")
print(f"   Min area: {vt_water_wgs84['area_sqkm'].min():.6f} sq km")
print(f"   Max area: {vt_water_wgs84['area_sqkm'].max():.2f} sq km")
print(f"   Mean area: {vt_water_wgs84['area_sqkm'].mean():.4f} sq km")

# Find large water bodies (potential Lake Champlain features)
print(f"\n3. Large water bodies (>10 sq km):")
large = vt_water_wgs84[vt_water_wgs84['area_sqkm'] > 10].sort_values('area_sqkm', ascending=False)
if len(large) > 0:
    for idx, row in large.iterrows():
        name = row.get('NAME', row.get('PNAME', row.get('GNIS_NAME', 'Unnamed')))
        print(f"   - {name}: {row['area_sqkm']:.2f} sq km")
        print(f"     Geometry type: {row.geometry.geom_type}")
else:
    print("   No water bodies larger than 10 sq km found!")

# Look specifically for Lake Champlain
print(f"\n4. Searching for 'Champlain' in names...")
name_cols = [col for col in vt_water_wgs84.columns if 'NAME' in col.upper()]
print(f"   Name columns: {name_cols}")

champlain_features = []
for col in name_cols:
    if col in vt_water_wgs84.columns:
        champlain = vt_water_wgs84[vt_water_wgs84[col].astype(str).str.contains('Champlain', case=False, na=False)]
        if len(champlain) > 0:
            print(f"   Found {len(champlain)} features in column '{col}'")
            champlain_features.extend(champlain.index.tolist())

if champlain_features:
    print(f"\n   Total Champlain features: {len(set(champlain_features))}")
    for idx in set(champlain_features):
        row = vt_water_wgs84.loc[idx]
        print(f"   - Area: {row['area_sqkm']:.2f} sq km")
        for col in name_cols:
            if col in row:
                print(f"     {col}: {row[col]}")
else:
    print("   ❌ No features with 'Champlain' in name found!")

# Geometry types
print(f"\n5. Geometry types:")
geom_types = vt_water_wgs84.geometry.geom_type.value_counts()
for geom_type, count in geom_types.items():
    print(f"   {geom_type}: {count}")

# Sample some features
print(f"\n6. Sample features (first 5):")
for idx, row in vt_water_wgs84.head(5).iterrows():
    name = 'Unnamed'
    for col in name_cols:
        if col in row and pd.notna(row[col]) and str(row[col]).strip():
            name = row[col]
            break
    print(f"   - {name}: {row['area_sqkm']:.4f} sq km ({row.geometry.geom_type})")

print("\n" + "=" * 70)
print("Now checking Census TIGER data for comparison...")
print("=" * 70)

# Load Census TIGER water for the 4 Lake Champlain counties
counties = {
    '50013': 'Grand Isle',
    '50007': 'Chittenden',
    '50011': 'Franklin',
    '50001': 'Addison'
}

all_tiger_water = []
for fips, name in counties.items():
    print(f"  Loading {name} County...")
    url = f"https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_{fips}_areawater.zip"
    gdf = gpd.read_file(url)
    all_tiger_water.append(gdf)

tiger_water = gpd.GeoDataFrame(pd.concat(all_tiger_water, ignore_index=True))
tiger_water['area_sqkm'] = tiger_water.geometry.area * 111 * 111

print(f"\n7. Census TIGER - Lake Champlain features:")
champlain_tiger = tiger_water[tiger_water['FULLNAME'].astype(str).str.contains('Champlain', case=False, na=False)]
print(f"   Found {len(champlain_tiger)} features")
print(f"   Total area: {champlain_tiger['area_sqkm'].sum():.2f} sq km")

# Largest TIGER features
print(f"\n8. Census TIGER - Largest water features:")
for idx, row in tiger_water.nlargest(10, 'area_sqkm').iterrows():
    print(f"   - {row['FULLNAME']}: {row['area_sqkm']:.2f} sq km")

print("\n" + "=" * 70)
print("RECOMMENDATION:")
print("=" * 70)
print("Based on this analysis, I recommend:")
if len(champlain_features) == 0:
    print("• VT Open Data may not have Lake Champlain as polygon features")
    print("• Census TIGER data appears to have better Lake Champlain coverage")
    print("• Consider using the categorized water datasets we already created")
print("\nFor Vermont boundary with Champlain Islands:")
print("• Use VT Open Geodata boundary (includes islands)")
print("• Combine with categorized water data for complete visualization")
