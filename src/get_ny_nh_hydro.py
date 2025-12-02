#!/usr/bin/env python3
"""
Download and process NY and NH hydro data from Census TIGER for border region.

This creates water feature datasets for counties adjacent to Vermont:
- NY: Clinton, Essex, Washington, Franklin, Warren, Saratoga, Rensselaer
- NH: Coos, Grafton, Sullivan, Cheshire

Data source: Census TIGER/Line 2023 AREAWATER
"""

import geopandas as gpd
import pandas as pd
import json
from pathlib import Path
import requests
import zipfile
import io
import tempfile
import os

# County FIPS codes
NY_COUNTIES = {
    'Clinton': '36019',
    'Essex': '36031',
    'Washington': '36115',
    'Franklin': '36033',
    'Warren': '36113',
    'Saratoga': '36091',
    'Rensselaer': '36083',
}

NH_COUNTIES = {
    'Coos': '33007',
    'Grafton': '33009',
    'Sullivan': '33019',
    'Cheshire': '33005',
}

# Minimum area for inclusion (sq meters from AWATER field)
MIN_WATER_AREA = 50000  # 0.05 sq km


def download_county_water(state_fips: str, county_fips: str, county_name: str) -> gpd.GeoDataFrame:
    """Download TIGER areawater for a county."""
    url = f"https://www2.census.gov/geo/tiger/TIGER2023/AREAWATER/tl_2023_{county_fips}_areawater.zip"

    print(f"  Downloading {county_name} ({county_fips})...")

    try:
        response = requests.get(url)
        response.raise_for_status()

        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(tmpdir)

            shp_files = list(Path(tmpdir).glob('*.shp'))
            if not shp_files:
                print(f"    No shapefile found for {county_name}")
                return None

            gdf = gpd.read_file(shp_files[0])
            gdf['county_name'] = county_name
            print(f"    Loaded {len(gdf)} water features")
            return gdf

    except Exception as e:
        print(f"    Error: {e}")
        return None


def process_water(gdf: gpd.GeoDataFrame, state_name: str) -> tuple:
    """Process water features into rivers and lakes."""
    # Convert to WGS84
    if gdf.crs != 'EPSG:4326':
        gdf = gdf.to_crs('EPSG:4326')

    # Filter by minimum area
    gdf = gdf[gdf['AWATER'] >= MIN_WATER_AREA].copy()

    # Add area in sq km
    gdf['area_sqkm'] = gdf['AWATER'] / 1_000_000

    # Categorize by name
    rivers = []
    lakes = []

    for _, row in gdf.iterrows():
        name = (row.get('FULLNAME') or '').lower()

        # Skip Lake Champlain (handled separately)
        if 'champlain' in name:
            continue

        # River indicators
        if any(kw in name for kw in ['river', 'brook', 'creek', 'stream', 'branch', 'run']):
            rivers.append(row)
        else:
            lakes.append(row)

    rivers_gdf = gpd.GeoDataFrame(rivers, crs='EPSG:4326') if rivers else gpd.GeoDataFrame()
    lakes_gdf = gpd.GeoDataFrame(lakes, crs='EPSG:4326') if lakes else gpd.GeoDataFrame()

    return rivers_gdf, lakes_gdf


def export_geojson(gdf: gpd.GeoDataFrame, output_path: Path, name: str):
    """Export GeoDataFrame to GeoJSON."""
    if gdf is None or len(gdf) == 0:
        print(f"  Skipping {name} - no features")
        return

    geojson = json.loads(gdf.to_json())
    geojson['name'] = name
    geojson['feature_count'] = len(gdf)

    with open(output_path, 'w') as f:
        json.dump(geojson, f)

    size_kb = output_path.stat().st_size / 1024
    print(f"  Saved {name}: {len(gdf)} features, {size_kb:.1f} KB")


def main():
    print("=" * 70)
    print("NY/NH HYDRO DATA PROCESSOR")
    print("=" * 70)

    output_dir = Path(__file__).parent.parent / 'docs' / 'json'
    output_dir.mkdir(parents=True, exist_ok=True)

    all_ny_water = []
    all_nh_water = []

    # Process NY counties
    print("\n" + "=" * 60)
    print("NEW YORK COUNTIES")
    print("=" * 60)

    for county_name, fips in NY_COUNTIES.items():
        gdf = download_county_water('36', fips, county_name)
        if gdf is not None:
            all_ny_water.append(gdf)

    if all_ny_water:
        ny_combined = gpd.GeoDataFrame(pd.concat(all_ny_water, ignore_index=True))
        ny_rivers, ny_lakes = process_water(ny_combined, 'NY')

        print(f"\nNY Results:")
        print(f"  Rivers: {len(ny_rivers)}")
        print(f"  Lakes/Ponds: {len(ny_lakes)}")

        export_geojson(ny_rivers, output_dir / 'ny_rivers.json', 'NY Rivers (Border Region)')
        export_geojson(ny_lakes, output_dir / 'ny_lakes.json', 'NY Lakes (Border Region)')

        # Combined
        ny_all = gpd.GeoDataFrame(pd.concat([ny_rivers, ny_lakes], ignore_index=True))
        ny_all = ny_all.set_crs('EPSG:4326')
        export_geojson(ny_all, output_dir / 'ny_hydro.json', 'NY Hydro (Border Region)')

    # Process NH counties
    print("\n" + "=" * 60)
    print("NEW HAMPSHIRE COUNTIES")
    print("=" * 60)

    for county_name, fips in NH_COUNTIES.items():
        gdf = download_county_water('33', fips, county_name)
        if gdf is not None:
            all_nh_water.append(gdf)

    if all_nh_water:
        nh_combined = gpd.GeoDataFrame(pd.concat(all_nh_water, ignore_index=True))
        nh_rivers, nh_lakes = process_water(nh_combined, 'NH')

        print(f"\nNH Results:")
        print(f"  Rivers: {len(nh_rivers)}")
        print(f"  Lakes/Ponds: {len(nh_lakes)}")

        export_geojson(nh_rivers, output_dir / 'nh_rivers.json', 'NH Rivers (Border Region)')
        export_geojson(nh_lakes, output_dir / 'nh_lakes.json', 'NH Lakes (Border Region)')

        # Combined
        nh_all = gpd.GeoDataFrame(pd.concat([nh_rivers, nh_lakes], ignore_index=True))
        nh_all = nh_all.set_crs('EPSG:4326')
        export_geojson(nh_all, output_dir / 'nh_hydro.json', 'NH Hydro (Border Region)')

    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
