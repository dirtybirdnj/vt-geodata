#!/usr/bin/env python3
"""
Download and process MA and NH hydro data from Census TIGER.

This creates water feature datasets for counties within the map bounds:
- MA: Berkshire, Franklin (border VT)
- NH: Coos, Grafton, Sullivan, Cheshire (border VT)

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
from shapely.geometry import box

# Map bounds (from 12x18 config - widest extent)
MAP_BOUNDS = [-73.9293, 42.4271, -71.1694, 45.4050]

# County FIPS codes - counties that border Vermont
MA_COUNTIES = {
    'Berkshire': '25003',
    'Franklin': '25011',
}

NH_COUNTIES = {
    'Coos': '33007',
    'Grafton': '33009',
    'Sullivan': '33019',
    'Cheshire': '33005',
}

# Minimum area for inclusion (sq meters from AWATER field)
MIN_WATER_AREA = 50000  # 0.05 sq km


def download_county_water(county_fips: str, county_name: str) -> gpd.GeoDataFrame:
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


def process_water(gdf: gpd.GeoDataFrame) -> tuple:
    """Process water features into rivers and lakes."""
    # Convert to WGS84
    if gdf.crs != 'EPSG:4326':
        gdf = gdf.to_crs('EPSG:4326')

    # Filter by minimum area
    gdf = gdf[gdf['AWATER'] >= MIN_WATER_AREA].copy()

    # Clip to map bounds
    bounds_box = box(MAP_BOUNDS[0], MAP_BOUNDS[1], MAP_BOUNDS[2], MAP_BOUNDS[3])
    gdf = gdf[gdf.geometry.intersects(bounds_box)].copy()

    if len(gdf) == 0:
        return gpd.GeoDataFrame(), gpd.GeoDataFrame()

    # Add area in sq km
    gdf['area_sqkm'] = gdf['AWATER'] / 1_000_000

    # Categorize by name
    rivers = []
    lakes = []

    for _, row in gdf.iterrows():
        name = (row.get('FULLNAME') or '').lower()

        # River indicators
        if any(kw in name for kw in ['river', 'brook', 'creek', 'stream', 'branch', 'run', 'bog']):
            rivers.append(row)
        else:
            lakes.append(row)

    rivers_gdf = gpd.GeoDataFrame(rivers, crs='EPSG:4326') if rivers else gpd.GeoDataFrame()
    lakes_gdf = gpd.GeoDataFrame(lakes, crs='EPSG:4326') if lakes else gpd.GeoDataFrame()

    return rivers_gdf, lakes_gdf


def simplify_geometry(gdf: gpd.GeoDataFrame, tolerance: float = 0.0005) -> gpd.GeoDataFrame:
    """Simplify geometries to reduce file size."""
    if len(gdf) == 0:
        return gdf
    gdf = gdf.copy()
    gdf['geometry'] = gdf.geometry.simplify(tolerance, preserve_topology=True)
    return gdf


def export_geojson(gdf: gpd.GeoDataFrame, output_path: Path, name: str):
    """Export GeoDataFrame to GeoJSON."""
    if gdf is None or len(gdf) == 0:
        print(f"  Skipping {name} - no features")
        return

    # Simplify for smaller files
    gdf = simplify_geometry(gdf)

    geojson = json.loads(gdf.to_json())
    geojson['name'] = name
    geojson['feature_count'] = len(gdf)

    with open(output_path, 'w') as f:
        json.dump(geojson, f)

    size_kb = output_path.stat().st_size / 1024
    print(f"  Saved {name}: {len(gdf)} features, {size_kb:.1f} KB")


def main():
    print("=" * 70)
    print("MA/NH HYDRO DATA PROCESSOR")
    print("=" * 70)
    print(f"Map bounds: {MAP_BOUNDS}")

    output_dir = Path(__file__).parent.parent / 'docs' / 'json'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process MA counties
    print("\n" + "=" * 60)
    print("MASSACHUSETTS COUNTIES")
    print("=" * 60)

    all_ma_water = []
    for county_name, fips in MA_COUNTIES.items():
        gdf = download_county_water(fips, county_name)
        if gdf is not None:
            all_ma_water.append(gdf)

    if all_ma_water:
        ma_combined = gpd.GeoDataFrame(pd.concat(all_ma_water, ignore_index=True))
        ma_rivers, ma_lakes = process_water(ma_combined)

        print(f"\nMA Results (within bounds):")
        print(f"  Rivers: {len(ma_rivers)}")
        print(f"  Lakes/Ponds: {len(ma_lakes)}")

        export_geojson(ma_rivers, output_dir / 'ma_rivers.json', 'MA Rivers')
        export_geojson(ma_lakes, output_dir / 'ma_lakes.json', 'MA Lakes')

    # Process NH counties
    print("\n" + "=" * 60)
    print("NEW HAMPSHIRE COUNTIES")
    print("=" * 60)

    all_nh_water = []
    for county_name, fips in NH_COUNTIES.items():
        gdf = download_county_water(fips, county_name)
        if gdf is not None:
            all_nh_water.append(gdf)

    if all_nh_water:
        nh_combined = gpd.GeoDataFrame(pd.concat(all_nh_water, ignore_index=True))
        nh_rivers, nh_lakes = process_water(nh_combined)

        print(f"\nNH Results (within bounds):")
        print(f"  Rivers: {len(nh_rivers)}")
        print(f"  Lakes/Ponds: {len(nh_lakes)}")

        export_geojson(nh_rivers, output_dir / 'nh_rivers.json', 'NH Rivers')
        export_geojson(nh_lakes, output_dir / 'nh_lakes.json', 'NH Lakes')

    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
