#!/usr/bin/env python3
"""
Get specific VT Census TIGER water features by HYDROID
These are water features that touch the Champlain Islands or VT coast
Identified manually using the interactive mashup map
"""

import geopandas as gpd
import pandas as pd
import json

def main():
    """Main function to get VT Champlain TIGER HYDROIDs"""
    print("=" * 70)
    print("VT CHAMPLAIN TIGER HYDROIDS - First Order Data Source")
    print("=" * 70)

    # List of HYDROIDs that touch Champlain Islands or VT coast
    # Extracted from categorized water data (big lake + rivers)
    champlain_hydroids = [
        "11026263037025",    # Unnamed
        "110492575435",      # Lk Champlain
        "11026263036983",    # Lk Champlain
        "11026263036993",    # Lk Champlain
        "11026263036991",    # Lk Champlain
        "11026263036992",    # Lk Champlain
        "110492575713",      # Unnamed
        "110492575436",      # Lk Champlain
        "110492575437",      # Lk Champlain
        "11026263036994",    # Lk Champlain
        "11026263036982",    # Lk Champlain
        "11026263036990",    # Lk Champlain
        "110804867027",      # Lk Champlain
        "110322409845",      # Lk Champlain
        "110492575428",      # Mud Crk
        "110492575429",      # Mud Crk
        "110325943935",      # Missisquoi Bay
        "110325943898",      # First Crk
        "110491164105",      # Unnamed
        "110491164111",      # Unnamed
        "110491163695",      # Unnamed
        "11026263037031",    # Unnamed
        "11026263037029",    # Unnamed
        "110325943908",      # Jewett Brk
        "110491164114",      # Unnamed
        "110491163652",      # Lamoille Riv
        "110491164117",      # Unnamed
        "110491164112",      # Unnamed
        "110491164107",      # Unnamed
        "110491164087",      # Unnamed
        "110491164312",      # Unnamed
        "110491164078",      # Unnamed
        "110491164315",      # Unnamed
        "110491164314",      # Unnamed
        "11026263037131",    # Arrowhead Mountain Lk
        "11026263037132",    # Arrowhead Mountain Lk
        "110325943925",      # Lamoille Riv
        "110804869121",      # Unnamed
        "110804867056",      # Little Otter Crk
        "110804867054",      # South Slang
        "110804866991",      # Lewis Crk
        "110804866989",      # Lewis Crk
        "110804869798",      # Unnamed
        "110491164088",      # Unnamed
        "110804866996",      # Otter Crk
    ]

    if not champlain_hydroids:
        print("\n⚠️  No HYDROIDs specified yet!")
        print("Please update the champlain_hydroids list in this script.")
        print("Use the Towns Over Champlain mashup map to collect HYDROIDs.")
        return

    print(f"\n1. Looking for {len(champlain_hydroids)} specific HYDROIDs...")

    # Load all VT water data
    print("\n2. Loading VT census water data (all 14 counties)...")
    counties = {
        '50001': 'Addison',
        '50003': 'Bennington',
        '50005': 'Caledonia',
        '50007': 'Chittenden',
        '50009': 'Essex',
        '50011': 'Franklin',
        '50013': 'Grand Isle',
        '50015': 'Lamoille',
        '50017': 'Orange',
        '50019': 'Orleans',
        '50021': 'Rutland',
        '50023': 'Washington',
        '50025': 'Windham',
        '50027': 'Windsor'
    }

    all_water = []
    for fips, name in counties.items():
        print(f"   Loading {name} County water...")
        url = f"https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_{fips}_areawater.zip"
        gdf = gpd.read_file(url)
        all_water.append(gdf)

    water = gpd.GeoDataFrame(pd.concat(all_water, ignore_index=True))
    print(f"   Total VT water features: {len(water)}")

    # Convert to WGS84
    if water.crs != 'EPSG:4326':
        water = water.to_crs('EPSG:4326')

    # Filter to just our HYDROIDs
    print(f"\n3. Filtering to {len(champlain_hydroids)} Champlain HYDROIDs...")
    champlain_water = water[water['HYDROID'].isin(champlain_hydroids)].copy()

    print(f"   Found {len(champlain_water)} matching features")

    if len(champlain_water) != len(champlain_hydroids):
        print(f"   ⚠️  Warning: Expected {len(champlain_hydroids)} but found {len(champlain_water)}")
        missing = set(champlain_hydroids) - set(champlain_water['HYDROID'].values)
        if missing:
            print(f"   Missing HYDROIDs: {missing}")

    # Calculate areas
    champlain_water['area_sqkm'] = champlain_water['AWATER'] / 1_000_000

    print("\n4. Feature details:")
    for idx, row in champlain_water.sort_values('area_sqkm', ascending=False).iterrows():
        name = row['FULLNAME'] if row['FULLNAME'] is not None else 'Unnamed'
        print(f"   {name:30s} - {row['area_sqkm']:8.2f} sq km - HYDROID: {row['HYDROID']}")

    print(f"\n   Total area: {champlain_water['area_sqkm'].sum():.2f} sq km")

    # Export to GeoJSON
    print("\n5. Exporting to GeoJSON...")
    champlain_geojson = json.loads(champlain_water.to_json())
    champlain_geojson['metadata'] = {
        'description': 'VT Census TIGER water features touching Champlain Islands or VT coast',
        'source': 'US Census TIGER/Line Shapefiles 2022 - Filtered by HYDROID',
        'total_features': len(champlain_water),
        'total_area_sqkm': float(champlain_water['area_sqkm'].sum()),
        'collection_method': 'Interactive selection from Towns Over Champlain mashup map',
        'hydroids': champlain_hydroids
    }

    with open('docs/json/vt_champlain_tiger_hydroids.json', 'w') as f:
        json.dump(champlain_geojson, f, indent=2)
    print("   ✓ Saved to docs/json/vt_champlain_tiger_hydroids.json")

    # Check file size
    import os
    file_size = os.path.getsize('docs/json/vt_champlain_tiger_hydroids.json') / 1024
    print(f"   File size: {file_size:.1f} KB")

    print("\n" + "=" * 70)
    print("✅ COMPLETE!")
    print("=" * 70)
    print("\nFile created:")
    print("  • docs/json/vt_champlain_tiger_hydroids.json")
    print(f"\nContains {len(champlain_water)} water features")
    print("Next: Run generate_champlain_tiger_map.py to create visualization")


if __name__ == '__main__':
    main()
