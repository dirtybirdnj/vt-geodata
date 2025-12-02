#!/usr/bin/env python3
"""
Download and process Quebec highway data from Statistics Canada National Road Network.

This script downloads the NRN Quebec shapefile and extracts major highways
for the Vermont border region.

Data source: Statistics Canada - National Road Network (NRN)
https://open.canada.ca/data/en/dataset/3d282116-e556-400c-9306-ca1a3cada77f

Road classifications in NRN:
- Autoroute (highway class 1) - Major highways like A-10, A-15, A-20, A-35, etc.
- National Highway (highway class 2)
- Regional Road (highway class 3)
- Local / Collector (highway class 4-5)
"""

import geopandas as gpd
import json
from pathlib import Path
import requests
import zipfile
import io
import tempfile
import os

# Quebec NRN download URL (Statistics Canada)
NRN_QC_URL = 'https://geo.statcan.gc.ca/nrn_rrn/qc/nrn_rrn_qc_SHAPE.zip'

# Bounding box for Vermont border region (southern Quebec)
# Roughly from 44.9°N to 46°N, -74°W to -71°W
BORDER_BBOX = {
    'min_lat': 44.9,
    'max_lat': 46.5,
    'min_lon': -74.0,
    'max_lon': -71.0
}


def download_and_extract(url: str, data_dir: Path) -> Path:
    """Download and extract Quebec NRN data."""
    zip_path = data_dir / 'nrn_qc.zip'
    extract_dir = data_dir / 'nrn_qc'

    if extract_dir.exists():
        print(f"Data already extracted to {extract_dir}")
        return extract_dir

    print(f"Downloading Quebec NRN data (~200MB)...")
    print(f"URL: {url}")

    response = requests.get(url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0

    with open(zip_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total_size:
                pct = (downloaded / total_size) * 100
                print(f"\r  Downloaded: {downloaded / 1e6:.1f} MB ({pct:.1f}%)", end='')

    print(f"\n  Saved to: {zip_path}")

    print(f"Extracting...")
    extract_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_dir)

    print(f"  Extracted to: {extract_dir}")
    return extract_dir


def find_road_shapefile(extract_dir: Path) -> Path:
    """Find the road segment shapefile in extracted data."""
    # NRN uses different naming conventions - look for road segment file
    patterns = [
        '**/NRN_QC_*_ROADSEG.shp',
        '**/RRN_QC_*_ROADSEG.shp',
        '**/*ROADSEG*.shp',
        '**/*roadseg*.shp',
        '**/nrn_qc_*/NRN_*.shp',
    ]

    for pattern in patterns:
        files = list(extract_dir.glob(pattern))
        if files:
            print(f"Found road file: {files[0]}")
            return files[0]

    # List what we have
    print("Available shapefiles:")
    for shp in extract_dir.rglob('*.shp'):
        print(f"  {shp.relative_to(extract_dir)}")

    raise FileNotFoundError("Could not find road segment shapefile")


def process_highways(gdf: gpd.GeoDataFrame) -> dict:
    """Process roads to extract highways for border region."""
    print(f"\nProcessing {len(gdf)} road segments...")

    # Print column info
    print(f"Columns: {list(gdf.columns)}")

    # Convert to WGS84 if needed
    if gdf.crs != 'EPSG:4326':
        print(f"Converting from {gdf.crs} to WGS84...")
        gdf = gdf.to_crs('EPSG:4326')

    # Filter to border region
    print(f"\nFiltering to border region...")
    print(f"  Lat: {BORDER_BBOX['min_lat']}° to {BORDER_BBOX['max_lat']}°")
    print(f"  Lon: {BORDER_BBOX['min_lon']}° to {BORDER_BBOX['max_lon']}°")

    # Get centroid for filtering
    gdf['centroid'] = gdf.geometry.centroid
    gdf['lat'] = gdf['centroid'].y
    gdf['lon'] = gdf['centroid'].x

    border_gdf = gdf[
        (gdf['lat'] >= BORDER_BBOX['min_lat']) &
        (gdf['lat'] <= BORDER_BBOX['max_lat']) &
        (gdf['lon'] >= BORDER_BBOX['min_lon']) &
        (gdf['lon'] <= BORDER_BBOX['max_lon'])
    ].copy()

    print(f"  Found {len(border_gdf)} segments in border region")

    # Drop temporary columns
    border_gdf = border_gdf.drop(columns=['centroid', 'lat', 'lon'])

    # Look at road classification columns
    class_cols = [c for c in border_gdf.columns if 'class' in c.lower() or 'type' in c.lower() or 'rank' in c.lower()]
    print(f"\nClassification columns: {class_cols}")

    for col in class_cols:
        if col in border_gdf.columns:
            print(f"\n{col} value counts:")
            print(border_gdf[col].value_counts().head(10))

    # NRN uses ROADCLASS for road classification
    # 1 = Freeway/Highway, 2 = Expressway, 3 = Arterial, 4 = Collector, 5 = Local
    highways = gpd.GeoDataFrame()

    if 'ROADCLASS' in border_gdf.columns:
        # Filter for major roads (class 1-2 are highways/expressways)
        highways = border_gdf[border_gdf['ROADCLASS'].isin([1, 2, '1', '2', 'Freeway', 'Expressway', 'Highway'])].copy()
        print(f"\nFound {len(highways)} highway/expressway segments")
    elif 'RANK' in border_gdf.columns:
        # Some versions use RANK
        highways = border_gdf[border_gdf['RANK'].isin([1, 2, '1', '2'])].copy()
        print(f"\nFound {len(highways)} major road segments")

    # Also filter for named autoroutes
    if 'NAME' in border_gdf.columns or 'NAMEEN' in border_gdf.columns or 'NAMEFR' in border_gdf.columns:
        name_col = 'NAMEEN' if 'NAMEEN' in border_gdf.columns else ('NAMEFR' if 'NAMEFR' in border_gdf.columns else 'NAME')
        autoroutes = border_gdf[border_gdf[name_col].str.contains('Autoroute|A-|Highway|Route', case=False, na=False)]
        print(f"Found {len(autoroutes)} named autoroutes/highways")

        # Print some examples
        print("\nSample highway names:")
        for name in autoroutes[name_col].dropna().unique()[:15]:
            print(f"  - {name}")

    return {
        'all_border_roads': border_gdf,
        'highways': highways if len(highways) > 0 else border_gdf[border_gdf.get('ROADCLASS', border_gdf.get('RANK', pd.Series())).isin([1, 2, 3])]
    }


def export_to_geojson(gdf: gpd.GeoDataFrame, output_path: Path, name: str):
    """Export GeoDataFrame to GeoJSON."""
    if len(gdf) == 0:
        print(f"Skipping {name} - no features")
        return

    # Simplify geometry slightly for smaller file
    gdf = gdf.copy()
    gdf['geometry'] = gdf['geometry'].simplify(0.0001, preserve_topology=True)

    # Convert to GeoJSON
    geojson = json.loads(gdf.to_json())
    geojson['name'] = name
    geojson['feature_count'] = len(gdf)

    with open(output_path, 'w') as f:
        json.dump(geojson, f)

    file_size = output_path.stat().st_size / 1024
    print(f"Exported {name}: {len(gdf)} features, {file_size:.1f} KB")


def main():
    print("=" * 70)
    print("QUEBEC HIGHWAY DATA PROCESSOR")
    print("=" * 70)
    print("\nData Source: Statistics Canada - National Road Network (NRN)")

    # Setup directories
    data_dir = Path(__file__).parent.parent / 'data'
    output_dir = Path(__file__).parent.parent / 'docs' / 'json'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Download and extract
    extract_dir = download_and_extract(NRN_QC_URL, data_dir)

    # Find road shapefile
    road_shp = find_road_shapefile(extract_dir)

    # Load with geopandas
    print(f"\nLoading road data from {road_shp}...")
    gdf = gpd.read_file(road_shp)
    print(f"Loaded {len(gdf)} total road segments")

    # Process
    results = process_highways(gdf)

    # Export
    print("\n" + "=" * 70)
    print("EXPORTING FILES")
    print("=" * 70)

    if 'highways' in results and len(results['highways']) > 0:
        export_to_geojson(
            results['highways'],
            output_dir / 'quebec_highways.json',
            'Quebec Highways (Border Region)'
        )

    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
