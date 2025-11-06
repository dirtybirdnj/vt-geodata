"""
Process and clean geospatial data for pen plotting
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
from shapely.geometry import box, MultiPolygon, Polygon
from shapely.ops import unary_union
import json


# Vermont bounding box (approximate)
VT_BBOX = {
    'minx': -73.43774,
    'miny': 42.72685,
    'maxx': -71.46528,
    'maxy': 45.01666
}

# Lake Champlain approximate bounds
CHAMPLAIN_BBOX = {
    'minx': -73.45,
    'miny': 43.5,
    'maxx': -73.0,
    'maxy': 45.1
}


def clip_to_vermont(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Clip a GeoDataFrame to Vermont boundaries

    Args:
        gdf: Input GeoDataFrame

    Returns:
        Clipped GeoDataFrame
    """
    vt_box = box(VT_BBOX['minx'], VT_BBOX['miny'],
                 VT_BBOX['maxx'], VT_BBOX['maxy'])

    # Ensure same CRS
    if gdf.crs != 'EPSG:4326':
        gdf = gdf.to_crs('EPSG:4326')

    # Clip to VT bounds
    return gdf.clip(vt_box)


def simplify_geometry(gdf: gpd.GeoDataFrame, tolerance: float = 0.001) -> gpd.GeoDataFrame:
    """
    Simplify geometries for pen plotting (reduces point count)

    Args:
        gdf: Input GeoDataFrame
        tolerance: Simplification tolerance (higher = more simplified)

    Returns:
        Simplified GeoDataFrame
    """
    gdf['geometry'] = gdf.geometry.simplify(tolerance, preserve_topology=True)
    return gdf


def extract_lake_champlain(water_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Extract Lake Champlain from a water bodies dataset

    Args:
        water_gdf: GeoDataFrame containing water bodies

    Returns:
        GeoDataFrame with just Lake Champlain
    """
    # Clip to Lake Champlain area
    lc_box = box(CHAMPLAIN_BBOX['minx'], CHAMPLAIN_BBOX['miny'],
                 CHAMPLAIN_BBOX['maxx'], CHAMPLAIN_BBOX['maxy'])

    if water_gdf.crs != 'EPSG:4326':
        water_gdf = water_gdf.to_crs('EPSG:4326')

    # Clip to LC bounds
    lc_gdf = water_gdf.clip(lc_box)

    # Try to identify Lake Champlain by name or size
    if 'NAME' in lc_gdf.columns or 'FULLNAME' in lc_gdf.columns:
        name_col = 'NAME' if 'NAME' in lc_gdf.columns else 'FULLNAME'
        lc_gdf = lc_gdf[lc_gdf[name_col].str.contains('Champlain', case=False, na=False)]

    # If name filtering didn't work, get largest water bodies
    if len(lc_gdf) == 0:
        lc_gdf = water_gdf.clip(lc_box)
        lc_gdf['area'] = lc_gdf.geometry.area
        # Get top 20 largest water bodies in the region
        lc_gdf = lc_gdf.nlargest(20, 'area')

    return lc_gdf


def merge_datasets(datasets: dict) -> dict:
    """
    Merge multiple datasets into processed layers

    Args:
        datasets: Dictionary of {name: GeoDataFrame}

    Returns:
        Dictionary of processed layers
    """
    processed = {}

    # Vermont boundary
    if 'boundary' in datasets:
        print("Processing Vermont boundary...")
        vt_boundary = datasets['boundary']
        vt_boundary = clip_to_vermont(vt_boundary)
        vt_boundary = simplify_geometry(vt_boundary, tolerance=0.001)
        processed['vermont_boundary'] = vt_boundary

    # Water bodies (combine all water sources)
    water_datasets = [v for k, v in datasets.items() if 'water' in k.lower() or 'hydro' in k.lower()]
    if water_datasets:
        print("Processing water bodies...")
        all_water = pd.concat(water_datasets, ignore_index=True)
        all_water = clip_to_vermont(all_water)

        # Extract Lake Champlain separately
        lake_champlain = extract_lake_champlain(all_water)
        lake_champlain = simplify_geometry(lake_champlain, tolerance=0.0005)
        processed['lake_champlain'] = lake_champlain

        # Other water bodies (exclude Lake Champlain area)
        lc_box = box(CHAMPLAIN_BBOX['minx'], CHAMPLAIN_BBOX['miny'],
                     CHAMPLAIN_BBOX['maxx'], CHAMPLAIN_BBOX['maxy'])
        other_water = all_water[~all_water.geometry.intersects(lc_box)]
        other_water = simplify_geometry(other_water, tolerance=0.002)
        processed['other_water'] = other_water

    return processed


def load_all_datasets(data_dir: str = 'data/raw') -> dict:
    """
    Load all available shapefiles

    Args:
        data_dir: Directory containing raw data

    Returns:
        Dictionary of {name: GeoDataFrame}
    """
    data_path = Path(data_dir)
    shapefiles = list(data_path.rglob("*.shp"))

    datasets = {}
    for shp_path in shapefiles:
        try:
            print(f"Loading {shp_path.stem}...")
            gdf = gpd.read_file(shp_path)
            datasets[shp_path.stem] = gdf
        except Exception as e:
            print(f"✗ Error loading {shp_path.stem}: {e}")

    return datasets


def save_processed_data(processed: dict, output_dir: str = 'data/processed'):
    """
    Save processed datasets

    Args:
        processed: Dictionary of processed GeoDataFrames
        output_dir: Output directory
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for name, gdf in processed.items():
        # Save as GeoJSON (easier to work with than shapefiles)
        geojson_path = output_path / f"{name}.geojson"
        gdf.to_file(geojson_path, driver='GeoJSON')
        print(f"✓ Saved {name}: {len(gdf)} features → {geojson_path}")


def process_all_data(data_dir: str = 'data/raw', output_dir: str = 'data/processed'):
    """
    Main processing pipeline

    Args:
        data_dir: Input directory with raw data
        output_dir: Output directory for processed data
    """
    print("=" * 60)
    print("VT GeoData Processor")
    print("=" * 60)
    print()

    # Load all datasets
    print("Loading datasets...")
    datasets = load_all_datasets(data_dir)

    if not datasets:
        print(f"No datasets found in {data_dir}")
        print("Run 'python src/download.py' first")
        return

    print(f"\nLoaded {len(datasets)} dataset(s)")

    # Process and merge
    print("\nProcessing and merging datasets...")
    processed = merge_datasets(datasets)

    if not processed:
        print("No data could be processed")
        return

    # Save processed data
    print("\nSaving processed data...")
    save_processed_data(processed, output_dir)

    # Summary
    print("\n" + "=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)
    for name, gdf in processed.items():
        print(f"{name}:")
        print(f"  Features: {len(gdf)}")
        print(f"  Geometry: {gdf.geometry.type.unique().tolist()}")
        if len(gdf) > 0:
            bounds = gdf.total_bounds
            print(f"  Bounds: [{bounds[0]:.4f}, {bounds[1]:.4f}, {bounds[2]:.4f}, {bounds[3]:.4f}]")

    print("\nNext step: python src/export.py")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process Vermont geodata')
    parser.add_argument('--data-dir', default='data/raw',
                       help='Input directory with raw data')
    parser.add_argument('--output-dir', default='data/processed',
                       help='Output directory for processed data')

    args = parser.parse_args()

    process_all_data(args.data_dir, args.output_dir)
