#!/usr/bin/env python3
"""
Get specific NY Census TIGER water features by HYDROID
These are water features that touch Lake Champlain on the NY side
Identified manually using the interactive mashup map
"""

import geopandas as gpd
import pandas as pd
import json

def main():
    """Main function to get NY Champlain TIGER HYDROIDs"""
    print("=" * 70)
    print("NY CHAMPLAIN TIGER HYDROIDS - First Order Data Source")
    print("=" * 70)

    # List of HYDROIDs that touch Lake Champlain on NY side
    # Collected from the Towns Over Champlain mashup map
    champlain_hydroids = [
        "110449409804",      # Unnamed
        "110449409787",      # Unnamed
        "11027899510961",    # Lk Champlain
        "110449409693",      # Treadwell Bay
        "110449409644",      # Allens Bay
        "110449409695",      # Cumberland Bay
        "11027899510959",    # Lk Champlain
        "110782060212",      # Lk Champlain
        "11027899510960",    # Lk Champlain
        "11027899510956",    # Lk Champlain
        "110795959087",      # Lk Champlain
        "110795959016"       # South Bay
    ]

    print(f"\n1. Looking for {len(champlain_hydroids)} specific HYDROIDs...")

    # Load all NY water data (all 62 counties)
    print("\n2. Loading NY census water data (all 62 counties)...")
    ny_counties = {
        '36001': 'Albany',
        '36003': 'Allegany',
        '36005': 'Bronx',
        '36007': 'Broome',
        '36009': 'Cattaraugus',
        '36011': 'Cayuga',
        '36013': 'Chautauqua',
        '36015': 'Chemung',
        '36017': 'Chenango',
        '36019': 'Clinton',
        '36021': 'Columbia',
        '36023': 'Cortland',
        '36025': 'Delaware',
        '36027': 'Dutchess',
        '36029': 'Erie',
        '36031': 'Essex',
        '36033': 'Franklin',
        '36035': 'Fulton',
        '36037': 'Genesee',
        '36039': 'Greene',
        '36041': 'Hamilton',
        '36043': 'Herkimer',
        '36045': 'Jefferson',
        '36047': 'Kings',
        '36049': 'Lewis',
        '36051': 'Livingston',
        '36053': 'Madison',
        '36055': 'Monroe',
        '36057': 'Montgomery',
        '36059': 'Nassau',
        '36061': 'New York',
        '36063': 'Niagara',
        '36065': 'Oneida',
        '36067': 'Onondaga',
        '36069': 'Ontario',
        '36071': 'Orange',
        '36073': 'Orleans',
        '36075': 'Oswego',
        '36077': 'Otsego',
        '36079': 'Putnam',
        '36081': 'Queens',
        '36083': 'Rensselaer',
        '36085': 'Richmond',
        '36087': 'Rockland',
        '36089': 'St. Lawrence',
        '36091': 'Saratoga',
        '36093': 'Schenectady',
        '36095': 'Schoharie',
        '36097': 'Schuyler',
        '36099': 'Seneca',
        '36101': 'Steuben',
        '36103': 'Suffolk',
        '36105': 'Sullivan',
        '36107': 'Tioga',
        '36109': 'Tompkins',
        '36111': 'Ulster',
        '36113': 'Warren',
        '36115': 'Washington',
        '36117': 'Wayne',
        '36119': 'Westchester',
        '36121': 'Wyoming',
        '36123': 'Yates'
    }

    all_water = []
    for fips, name in ny_counties.items():
        print(f"   Loading {name} County water...")
        url = f"https://www2.census.gov/geo/tiger/TIGER2022/AREAWATER/tl_2022_{fips}_areawater.zip"
        gdf = gpd.read_file(url)
        all_water.append(gdf)

    water = gpd.GeoDataFrame(pd.concat(all_water, ignore_index=True))
    print(f"   Total NY water features: {len(water)}")

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
        'description': 'NY Census TIGER water features touching Lake Champlain on NY side',
        'source': 'US Census TIGER/Line Shapefiles 2022 - Filtered by HYDROID',
        'total_features': len(champlain_water),
        'total_area_sqkm': float(champlain_water['area_sqkm'].sum()),
        'collection_method': 'Interactive selection from Towns Over Champlain mashup map',
        'hydroids': champlain_hydroids
    }

    with open('docs/json/ny_champlain_tiger_hydroids.json', 'w') as f:
        json.dump(champlain_geojson, f, indent=2)
    print("   ✓ Saved to docs/json/ny_champlain_tiger_hydroids.json")

    # Check file size
    import os
    file_size = os.path.getsize('docs/json/ny_champlain_tiger_hydroids.json') / 1024
    print(f"   File size: {file_size:.1f} KB")

    print("\n" + "=" * 70)
    print("✅ COMPLETE!")
    print("=" * 70)
    print("\nFile created:")
    print("  • docs/json/ny_champlain_tiger_hydroids.json")
    print(f"\nContains {len(champlain_water)} water features")
    print("Next: Run generate_champlain_tiger_maps.py to create visualizations")


if __name__ == '__main__':
    main()
