#!/usr/bin/env python3
"""
Download and process Vermont road data from Census TIGER/Line.

TIGER road types (MTFCC codes):
- S1100: Primary Road (Interstate highways)
- S1200: Secondary Road (US routes, state highways)
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

# Vermont FIPS code
VT_FIPS = '50'

# Census TIGER URLs for Vermont roads
TIGER_ROADS_URL = f'https://www2.census.gov/geo/tiger/TIGER2023/PRISECROADS/tl_2023_{VT_FIPS}_prisecroads.zip'


def download_and_load_shapefile(url: str) -> gpd.GeoDataFrame:
    """Download a TIGER shapefile and load it as a GeoDataFrame."""
    print(f"Downloading from {url}...")
    response = requests.get(url)
    response.raise_for_status()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Extract zip
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(tmpdir)

        # Find the .shp file
        shp_files = list(Path(tmpdir).glob('*.shp'))
        if not shp_files:
            raise FileNotFoundError("No shapefile found in archive")

        # Load with geopandas
        gdf = gpd.read_file(shp_files[0])
        print(f"Loaded {len(gdf)} features")
        return gdf


def process_roads(gdf: gpd.GeoDataFrame) -> dict:
    """Process roads into categories."""
    # Ensure WGS84 projection
    if gdf.crs != 'EPSG:4326':
        gdf = gdf.to_crs('EPSG:4326')

    # Print available columns
    print(f"\nColumns: {list(gdf.columns)}")

    # Print MTFCC value counts
    if 'MTFCC' in gdf.columns:
        print(f"\nRoad types (MTFCC):")
        print(gdf['MTFCC'].value_counts())

    # Print RTTYP value counts (route type)
    if 'RTTYP' in gdf.columns:
        print(f"\nRoute types (RTTYP):")
        print(gdf['RTTYP'].value_counts())

    # Categorize roads
    categories = {
        'interstate': gdf[gdf['MTFCC'] == 'S1100'] if 'MTFCC' in gdf.columns else gpd.GeoDataFrame(),
        'highway': gdf[gdf['MTFCC'] == 'S1200'] if 'MTFCC' in gdf.columns else gpd.GeoDataFrame(),
    }

    # Print feature names
    if 'FULLNAME' in gdf.columns:
        print(f"\nSample road names:")
        for name in gdf['FULLNAME'].dropna().unique()[:20]:
            print(f"  - {name}")

    return gdf, categories


def export_to_geojson(gdf: gpd.GeoDataFrame, output_path: Path, name: str):
    """Export GeoDataFrame to GeoJSON."""
    if len(gdf) == 0:
        print(f"Skipping {name} - no features")
        return

    # Convert to GeoJSON
    geojson = json.loads(gdf.to_json())

    # Add metadata
    geojson['name'] = name
    geojson['feature_count'] = len(gdf)

    # Write file
    with open(output_path, 'w') as f:
        json.dump(geojson, f)

    file_size = output_path.stat().st_size / 1024 / 1024
    print(f"Exported {name}: {len(gdf)} features, {file_size:.2f} MB")


def main():
    """Main function to download and process Vermont roads."""
    print("=" * 60)
    print("Vermont Road Data Downloader")
    print("=" * 60)

    # Output directory
    output_dir = Path(__file__).parent.parent / 'docs' / 'json'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Download primary/secondary roads
    print("\n1. Downloading Primary & Secondary Roads...")
    roads_gdf = download_and_load_shapefile(TIGER_ROADS_URL)

    # Process and categorize
    print("\n2. Processing roads...")
    all_roads, categories = process_roads(roads_gdf)

    # Export all roads combined
    print("\n3. Exporting GeoJSON files...")
    export_to_geojson(all_roads, output_dir / 'vt_roads.json', 'Vermont Primary & Secondary Roads')

    # Export by category
    if len(categories['interstate']) > 0:
        export_to_geojson(categories['interstate'], output_dir / 'vt_interstate.json', 'Vermont Interstate Highways')

    if len(categories['highway']) > 0:
        export_to_geojson(categories['highway'], output_dir / 'vt_highways.json', 'Vermont State Highways')

    print("\n" + "=" * 60)
    print("Done! Road data exported to docs/json/")
    print("=" * 60)


if __name__ == '__main__':
    main()
