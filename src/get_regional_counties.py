#!/usr/bin/env python3
"""
Get county boundaries for surrounding states (NY, NH, MA) for the regional Vermont map.
This creates simplified county boundaries for context around Vermont.

NY Counties:
- Lake Champlain counties: Clinton, Essex, Washington (already have these)
- Adjacent counties: Franklin, Warren, Saratoga, Rensselaer

NH Counties adjacent to Vermont:
- Cheshire, Sullivan, Grafton, Coos

MA Counties adjacent to Vermont:
- Berkshire
"""

import geopandas as gpd
import pandas as pd
import json
from pathlib import Path

def simplify_geometry(gdf, tolerance=0.005):
    """Simplify geometry for smaller file size (tolerance in degrees ~500m)"""
    gdf = gdf.copy()
    gdf['geometry'] = gdf['geometry'].simplify(tolerance, preserve_topology=True)
    return gdf

def main():
    print("=" * 70)
    print("REGIONAL COUNTY DATA FOR VERMONT MAP")
    print("=" * 70)

    # Load all US counties once
    print("\n1. Loading US county boundaries from Census TIGER 2023...")
    url = "https://www2.census.gov/geo/tiger/TIGER2023/COUNTY/tl_2023_us_county.zip"
    all_counties = gpd.read_file(url)
    print(f"   Loaded {len(all_counties)} US counties")

    # Convert to WGS84
    if all_counties.crs != 'EPSG:4326':
        all_counties = all_counties.to_crs('EPSG:4326')

    # County FIPS codes
    # NY Champlain counties (current)
    ny_champlain_fips = ['36019', '36031', '36115']  # Clinton, Essex, Washington

    # NY adjacent counties
    ny_adjacent_fips = [
        '36033',  # Franklin - borders Clinton, Essex
        '36113',  # Warren - borders Essex, Washington
        '36091',  # Saratoga - borders Washington
        '36083',  # Rensselaer - borders Washington
    ]

    # NH counties adjacent to Vermont
    nh_fips = [
        '33005',  # Cheshire
        '33019',  # Sullivan
        '33009',  # Grafton
        '33007',  # Coos
    ]

    # MA counties adjacent to Vermont
    ma_fips = [
        '25003',  # Berkshire
    ]

    # Get NY Champlain counties (for reference/existing data)
    print("\n2. Extracting NY Lake Champlain counties...")
    ny_champlain = all_counties[all_counties['GEOID'].isin(ny_champlain_fips)].copy()
    print(f"   Found {len(ny_champlain)} NY Champlain counties:")
    for _, row in ny_champlain.iterrows():
        print(f"     - {row['NAME']} County (FIPS: {row['GEOID']})")

    # Get NY adjacent counties
    print("\n3. Extracting NY adjacent counties...")
    ny_adjacent = all_counties[all_counties['GEOID'].isin(ny_adjacent_fips)].copy()
    print(f"   Found {len(ny_adjacent)} NY adjacent counties:")
    for _, row in ny_adjacent.iterrows():
        print(f"     - {row['NAME']} County (FIPS: {row['GEOID']})")

    # Get NH counties
    print("\n4. Extracting NH counties...")
    nh_counties = all_counties[all_counties['GEOID'].isin(nh_fips)].copy()
    print(f"   Found {len(nh_counties)} NH counties:")
    for _, row in nh_counties.iterrows():
        print(f"     - {row['NAME']} County (FIPS: {row['GEOID']})")

    # Get MA counties
    print("\n5. Extracting MA counties...")
    ma_counties = all_counties[all_counties['GEOID'].isin(ma_fips)].copy()
    print(f"   Found {len(ma_counties)} MA counties:")
    for _, row in ma_counties.iterrows():
        print(f"     - {row['NAME']} County (FIPS: {row['GEOID']})")

    # Simplify geometries
    print("\n6. Simplifying geometries for smaller file size...")
    ny_champlain_simple = simplify_geometry(ny_champlain)
    ny_adjacent_simple = simplify_geometry(ny_adjacent)
    nh_counties_simple = simplify_geometry(nh_counties)
    ma_counties_simple = simplify_geometry(ma_counties)

    # Export files
    output_dir = Path('docs/json')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export NY Champlain counties (update existing with simplified version)
    print("\n7. Exporting county files...")

    # NY Champlain counties
    ny_champlain_geojson = json.loads(ny_champlain_simple.to_json())
    with open(output_dir / 'ny_champlain_counties.json', 'w') as f:
        json.dump(ny_champlain_geojson, f, indent=2)
    print(f"   ✓ Saved ny_champlain_counties.json ({len(ny_champlain)} counties)")

    # NY adjacent counties
    ny_adjacent_geojson = json.loads(ny_adjacent_simple.to_json())
    with open(output_dir / 'ny_adjacent_counties.json', 'w') as f:
        json.dump(ny_adjacent_geojson, f, indent=2)
    print(f"   ✓ Saved ny_adjacent_counties.json ({len(ny_adjacent)} counties)")

    # All NY counties (combined)
    all_ny = gpd.GeoDataFrame(pd.concat([ny_champlain_simple, ny_adjacent_simple], ignore_index=True))
    all_ny_geojson = json.loads(all_ny.to_json())
    with open(output_dir / 'ny_regional_counties.json', 'w') as f:
        json.dump(all_ny_geojson, f, indent=2)
    print(f"   ✓ Saved ny_regional_counties.json ({len(all_ny)} counties)")

    # NH counties
    nh_geojson = json.loads(nh_counties_simple.to_json())
    with open(output_dir / 'nh_counties.json', 'w') as f:
        json.dump(nh_geojson, f, indent=2)
    print(f"   ✓ Saved nh_counties.json ({len(nh_counties)} counties)")

    # MA counties
    ma_geojson = json.loads(ma_counties_simple.to_json())
    with open(output_dir / 'ma_counties.json', 'w') as f:
        json.dump(ma_geojson, f, indent=2)
    print(f"   ✓ Saved ma_counties.json ({len(ma_counties)} counties)")

    # Combined surrounding counties (all states)
    print("\n8. Creating combined surrounding counties file...")
    all_surrounding = gpd.GeoDataFrame(pd.concat([
        all_ny,
        nh_counties_simple,
        ma_counties_simple
    ], ignore_index=True))

    # Add state abbreviation for styling
    all_surrounding['STATE'] = all_surrounding['STATEFP'].map({
        '36': 'NY',
        '33': 'NH',
        '25': 'MA'
    })

    surrounding_geojson = json.loads(all_surrounding.to_json())
    with open(output_dir / 'surrounding_counties.json', 'w') as f:
        json.dump(surrounding_geojson, f, indent=2)
    print(f"   ✓ Saved surrounding_counties.json ({len(all_surrounding)} counties total)")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"\nNY Champlain counties: {len(ny_champlain)}")
    for _, row in ny_champlain.iterrows():
        print(f"  - {row['NAME']}")

    print(f"\nNY Adjacent counties: {len(ny_adjacent)}")
    for _, row in ny_adjacent.iterrows():
        print(f"  - {row['NAME']}")

    print(f"\nNH counties: {len(nh_counties)}")
    for _, row in nh_counties.iterrows():
        print(f"  - {row['NAME']}")

    print(f"\nMA counties: {len(ma_counties)}")
    for _, row in ma_counties.iterrows():
        print(f"  - {row['NAME']}")

    print(f"\nTotal surrounding counties: {len(all_surrounding)}")

    print("\n" + "=" * 70)
    print("✅ COMPLETE!")
    print("=" * 70)
    print("\nFiles created:")
    print("  • docs/json/ny_champlain_counties.json - NY Champlain (Clinton, Essex, Washington)")
    print("  • docs/json/ny_adjacent_counties.json - NY Adjacent (Franklin, Warren, Saratoga, Rensselaer)")
    print("  • docs/json/ny_regional_counties.json - All NY regional counties")
    print("  • docs/json/nh_counties.json - NH counties touching VT")
    print("  • docs/json/ma_counties.json - MA counties touching VT")
    print("  • docs/json/surrounding_counties.json - All surrounding counties")


if __name__ == '__main__':
    main()
