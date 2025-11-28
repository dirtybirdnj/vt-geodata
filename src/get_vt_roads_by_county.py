#!/usr/bin/env python3
"""
Download and process Vermont road data by county from Census TIGER/Line.

Downloads ALL roads (not just primary/secondary) for each of Vermont's 14 counties.
This provides much more detailed local road coverage.

TIGER road types (MTFCC codes):
- S1100: Primary Road (Interstate)
- S1200: Secondary Road (US/State highways)
- S1400: Local Neighborhood Road
- S1500: Vehicular Trail (4WD)
- S1630: Ramp
- S1640: Service Drive
- S1730: Alley
- S1740: Private Road
- S1780: Parking Lot Road
- S1820: Bike Path/Trail
"""

import geopandas as gpd
import pandas as pd
import json
from pathlib import Path
import requests
import zipfile
import io
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

# Vermont FIPS code
VT_FIPS = '50'

# Vermont counties with FIPS codes
VT_COUNTIES = {
    '001': 'Addison',
    '003': 'Bennington',
    '005': 'Caledonia',
    '007': 'Chittenden',
    '009': 'Essex',
    '011': 'Franklin',
    '013': 'Grand Isle',
    '015': 'Lamoille',
    '017': 'Orange',
    '019': 'Orleans',
    '021': 'Rutland',
    '023': 'Washington',
    '025': 'Windham',
    '027': 'Windsor'
}

# Road type descriptions
ROAD_TYPES = {
    'S1100': 'Interstate',
    'S1200': 'US/State Highway',
    'S1400': 'Local Road',
    'S1500': 'Vehicular Trail',
    'S1630': 'Ramp',
    'S1640': 'Service Drive',
    'S1730': 'Alley',
    'S1740': 'Private Road',
    'S1780': 'Parking Lot',
    'S1820': 'Bike Path'
}


def get_tiger_url(county_fips: str) -> str:
    """Get TIGER roads URL for a Vermont county."""
    full_fips = f"{VT_FIPS}{county_fips}"
    return f"https://www2.census.gov/geo/tiger/TIGER2023/ROADS/tl_2023_{full_fips}_roads.zip"


def download_county_roads(county_fips: str, county_name: str) -> gpd.GeoDataFrame:
    """Download roads for a single county."""
    url = get_tiger_url(county_fips)

    try:
        print(f"  Downloading {county_name} County...")
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                z.extractall(tmpdir)

            shp_files = list(Path(tmpdir).glob('*.shp'))
            if not shp_files:
                print(f"    Warning: No shapefile found for {county_name}")
                return None

            gdf = gpd.read_file(shp_files[0])

            # Add county info
            gdf['county_fips'] = county_fips
            gdf['county_name'] = county_name

            print(f"    {county_name}: {len(gdf)} road segments")
            return gdf

    except Exception as e:
        print(f"    Error downloading {county_name}: {e}")
        return None


def process_county_roads(gdf: gpd.GeoDataFrame) -> dict:
    """Process roads and return statistics."""
    if gdf is None or len(gdf) == 0:
        return {}

    # Ensure WGS84
    if gdf.crs != 'EPSG:4326':
        gdf = gdf.to_crs('EPSG:4326')

    # Count by road type
    stats = {}
    if 'MTFCC' in gdf.columns:
        for mtfcc, count in gdf['MTFCC'].value_counts().items():
            road_type = ROAD_TYPES.get(mtfcc, mtfcc)
            stats[road_type] = count

    return gdf, stats


def export_county_geojson(gdf: gpd.GeoDataFrame, output_path: Path, county_name: str):
    """Export county roads to GeoJSON."""
    if gdf is None or len(gdf) == 0:
        return 0

    # Ensure WGS84
    if gdf.crs != 'EPSG:4326':
        gdf = gdf.to_crs('EPSG:4326')

    # Convert to GeoJSON
    geojson = json.loads(gdf.to_json())
    geojson['name'] = f"{county_name} County Roads"
    geojson['feature_count'] = len(gdf)

    with open(output_path, 'w') as f:
        json.dump(geojson, f)

    file_size = output_path.stat().st_size / 1024 / 1024
    return file_size


def main():
    """Download and process all Vermont county roads."""
    print("=" * 60)
    print("Vermont Roads by County Downloader")
    print("=" * 60)
    print(f"\nDownloading ALL roads for {len(VT_COUNTIES)} Vermont counties...")
    print("(This includes local roads, not just highways)\n")

    output_dir = Path(__file__).parent.parent / 'docs' / 'json' / 'roads'
    output_dir.mkdir(parents=True, exist_ok=True)

    all_roads = []
    county_stats = {}

    # Download each county
    print("1. Downloading county road data...")
    for fips, name in VT_COUNTIES.items():
        gdf = download_county_roads(fips, name)
        if gdf is not None:
            processed_gdf, stats = process_county_roads(gdf)
            all_roads.append(processed_gdf)
            county_stats[name] = {
                'segments': len(processed_gdf),
                'types': stats
            }

    # Export per-county files
    print("\n2. Exporting per-county GeoJSON files...")
    total_size = 0
    for gdf in all_roads:
        if gdf is not None and len(gdf) > 0:
            county_name = gdf['county_name'].iloc[0]
            filename = county_name.lower().replace(' ', '_') + '_roads.json'
            output_path = output_dir / filename
            size = export_county_geojson(gdf, output_path, county_name)
            total_size += size
            print(f"    {county_name}: {len(gdf)} segments, {size:.2f} MB")

    # Combine all roads
    print("\n3. Creating combined roads file...")
    if all_roads:
        combined = gpd.GeoDataFrame(pd.concat(all_roads, ignore_index=True))
        combined_path = output_dir.parent / 'vt_all_roads.json'

        # Export combined (this will be large!)
        if combined.crs != 'EPSG:4326':
            combined = combined.to_crs('EPSG:4326')

        geojson = json.loads(combined.to_json())
        geojson['name'] = 'Vermont All Roads'
        geojson['feature_count'] = len(combined)

        with open(combined_path, 'w') as f:
            json.dump(geojson, f)

        combined_size = combined_path.stat().st_size / 1024 / 1024
        print(f"    Combined: {len(combined)} segments, {combined_size:.2f} MB")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total_segments = sum(s['segments'] for s in county_stats.values())
    print(f"\nTotal road segments: {total_segments:,}")
    print(f"Total file size: {total_size:.2f} MB (per-county)")
    print(f"Combined file: {combined_size:.2f} MB")

    print("\nPer-county breakdown:")
    for county, stats in sorted(county_stats.items(), key=lambda x: -x[1]['segments']):
        print(f"  {county}: {stats['segments']:,} segments")

    print(f"\nFiles saved to: {output_dir}")
    print("\nRoad type distribution (all counties):")
    all_types = {}
    for stats in county_stats.values():
        for road_type, count in stats['types'].items():
            all_types[road_type] = all_types.get(road_type, 0) + count

    for road_type, count in sorted(all_types.items(), key=lambda x: -x[1]):
        print(f"  {road_type}: {count:,}")


if __name__ == '__main__':
    main()
