"""
Download geospatial datasets for Vermont and Lake Champlain
"""

import os
import requests
from pathlib import Path
from typing import Dict, List
import zipfile
import io


# Data source URLs
DATA_SOURCES = {
    # Vermont Open Geodata Portal
    'vt_boundaries': {
        'name': 'Vermont State Boundaries',
        'url': 'https://geodata.vermont.gov/datasets/vt-data-boundary-vtbound-2020/explore',
        'type': 'arcgis',
        'description': 'Official Vermont state boundary polygon'
    },
    'vt_hydrography': {
        'name': 'Vermont Hydrography (NHD)',
        'url': 'https://geodata.vermont.gov/datasets/vt-data-hydrography-nhdwaterbody-2019',
        'type': 'arcgis',
        'description': 'Lakes, ponds, and rivers including Lake Champlain'
    },

    # US Census TIGER/Line
    'census_water_2023': {
        'name': 'TIGER/Line Water Bodies (Vermont)',
        'url': 'https://www2.census.gov/geo/tiger/TIGER2023/AREAWATER/tl_2023_50_areawater.zip',
        'type': 'shapefile',
        'description': 'Census water body polygons for Vermont (FIPS 50)'
    },
    'census_state_2023': {
        'name': 'TIGER/Line State Boundaries',
        'url': 'https://www2.census.gov/geo/tiger/TIGER2023/STATE/tl_2023_us_state.zip',
        'type': 'shapefile',
        'description': 'US state boundaries (filter for VT)'
    },

    # USGS National Map - Manual download note
    'usgs_nhd': {
        'name': 'USGS National Hydrography Dataset',
        'url': 'https://www.usgs.gov/national-hydrography/access-national-hydrography-products',
        'type': 'manual',
        'description': 'High-resolution NHD data (requires manual download via The National Map)'
    }
}


def download_shapefile(url: str, output_dir: Path, name: str) -> bool:
    """
    Download and extract a shapefile from a direct URL

    Args:
        url: Direct URL to shapefile zip
        output_dir: Directory to extract files
        name: Dataset name for subfolder

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"Downloading {name}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Create subfolder for this dataset
        dataset_dir = output_dir / name
        dataset_dir.mkdir(parents=True, exist_ok=True)

        # Extract zip file
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall(dataset_dir)

        print(f"✓ Successfully downloaded and extracted {name}")
        return True

    except Exception as e:
        print(f"✗ Error downloading {name}: {e}")
        return False


def download_all_datasets(data_dir: str = 'data/raw'):
    """
    Download all available datasets

    Args:
        data_dir: Base directory for raw data storage
    """
    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("VT GeoData Downloader")
    print("=" * 60)
    print()

    successful = []
    failed = []
    manual = []

    for key, source in DATA_SOURCES.items():
        print(f"\n{source['name']}")
        print(f"  Description: {source['description']}")

        if source['type'] == 'shapefile':
            if download_shapefile(source['url'], data_path, key):
                successful.append(key)
            else:
                failed.append(key)

        elif source['type'] == 'arcgis':
            print(f"  Type: ArcGIS Feature Service")
            print(f"  Note: Visit {source['url']}")
            print(f"  → Click 'Download' → Choose 'Shapefile' format")
            print(f"  → Extract to {data_path / key}")
            manual.append(key)

        elif source['type'] == 'manual':
            print(f"  Type: Manual download required")
            print(f"  URL: {source['url']}")
            print(f"  → Download NHD data for Vermont (VT)")
            print(f"  → Extract to {data_path / key}")
            manual.append(key)

    # Summary
    print("\n" + "=" * 60)
    print("DOWNLOAD SUMMARY")
    print("=" * 60)
    print(f"✓ Successful downloads: {len(successful)}")
    for s in successful:
        print(f"  - {DATA_SOURCES[s]['name']}")

    if failed:
        print(f"\n✗ Failed downloads: {len(failed)}")
        for f in failed:
            print(f"  - {DATA_SOURCES[f]['name']}")

    if manual:
        print(f"\n⚠ Manual downloads needed: {len(manual)}")
        for m in manual:
            print(f"  - {DATA_SOURCES[m]['name']}")

    print("\nNext steps:")
    print("1. Complete any manual downloads listed above")
    print("2. Run 'python src/explore.py' to visualize datasets")


def list_downloaded_files(data_dir: str = 'data/raw'):
    """
    List all shapefiles found in the data directory

    Args:
        data_dir: Base directory to search
    """
    data_path = Path(data_dir)
    shapefiles = list(data_path.rglob("*.shp"))

    print(f"\nFound {len(shapefiles)} shapefile(s):")
    for shp in sorted(shapefiles):
        print(f"  {shp.relative_to(data_path)}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Download Vermont geodata')
    parser.add_argument('--data-dir', default='data/raw',
                       help='Output directory for raw data')
    parser.add_argument('--list', action='store_true',
                       help='List already downloaded files')

    args = parser.parse_args()

    if args.list:
        list_downloaded_files(args.data_dir)
    else:
        download_all_datasets(args.data_dir)
