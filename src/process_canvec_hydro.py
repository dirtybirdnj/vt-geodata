#!/usr/bin/env python3
"""
Process Canvec 1M hydro data for Vermont border region.

Extracts lakes and rivers from the Canadian Canvec 1:1,000,000 hydro dataset
for the area near the Vermont border.

Data source: Natural Resources Canada - CanVec
"""

import geopandas as gpd
import json
from pathlib import Path
import subprocess
import os

# Canvec data paths
CANVEC_DIR = Path(__file__).parent.parent / 'data' / 'canvec_1M_hydro' / 'canvec_1M_CA_Hydro'

# Bounding box for Vermont border region (southern Quebec + Lake Champlain extension)
BORDER_BBOX = {
    'min_lat': 44.5,
    'max_lat': 46.5,
    'min_lon': -74.0,
    'max_lon': -71.0
}

# Minimum area thresholds (sq km)
MIN_LAKE_AREA = 0.5   # 0.5 sq km
MIN_RIVER_AREA = 0.1  # 0.1 sq km


def load_shapefile(shp_path):
    """Load shapefile with geopandas."""
    print(f"Loading {shp_path.name}...")
    gdf = gpd.read_file(shp_path)
    print(f"  Loaded {len(gdf)} features")
    print(f"  CRS: {gdf.crs}")
    print(f"  Columns: {list(gdf.columns)}")
    return gdf


def filter_to_border_region(gdf):
    """Filter features to the border region bounding box."""
    # Convert to WGS84 if needed
    if gdf.crs != 'EPSG:4326':
        print(f"  Converting from {gdf.crs} to WGS84...")
        gdf = gdf.to_crs('EPSG:4326')

    # Filter by centroid in bounding box
    centroids = gdf.geometry.centroid
    lat = centroids.y
    lon = centroids.x

    mask = (
        (lat >= BORDER_BBOX['min_lat']) &
        (lat <= BORDER_BBOX['max_lat']) &
        (lon >= BORDER_BBOX['min_lon']) &
        (lon <= BORDER_BBOX['max_lon'])
    )

    filtered = gdf[mask].copy()
    print(f"  Filtered to {len(filtered)} features in border region")
    return filtered


def calculate_area(gdf):
    """Calculate area in sq km for polygon features."""
    # Project to equal area for accurate measurement
    gdf_projected = gdf.to_crs('ESRI:102008')  # North America Albers Equal Area
    gdf['area_sqkm'] = gdf_projected.geometry.area / 1e6
    return gdf


def process_waterbodies():
    """Process waterbody_2.shp (lakes and ponds)."""
    print("\n" + "=" * 60)
    print("PROCESSING WATERBODIES (Lakes/Ponds)")
    print("=" * 60)

    shp_path = CANVEC_DIR / 'waterbody_2.shp'
    if not shp_path.exists():
        print(f"ERROR: {shp_path} not found")
        return None

    gdf = load_shapefile(shp_path)
    gdf = filter_to_border_region(gdf)

    if len(gdf) == 0:
        print("No waterbodies in border region")
        return None

    # Calculate area
    gdf = calculate_area(gdf)

    # Filter by minimum area
    gdf = gdf[gdf['area_sqkm'] >= MIN_LAKE_AREA].copy()
    print(f"  After area filter (>= {MIN_LAKE_AREA} sq km): {len(gdf)} features")

    # Print some stats
    print(f"\n  Largest waterbodies:")
    for _, row in gdf.nlargest(10, 'area_sqkm').iterrows():
        name = row.get('NAMELK1EN') or row.get('NAMELK1FR') or row.get('NAME') or 'Unnamed'
        print(f"    {name}: {row['area_sqkm']:.2f} sq km")

    return gdf


def process_watercourses():
    """Process watercourse_1.shp (rivers and streams)."""
    print("\n" + "=" * 60)
    print("PROCESSING WATERCOURSES (Rivers/Streams)")
    print("=" * 60)

    shp_path = CANVEC_DIR / 'watercourse_1.shp'
    if not shp_path.exists():
        print(f"ERROR: {shp_path} not found")
        return None

    gdf = load_shapefile(shp_path)
    gdf = filter_to_border_region(gdf)

    if len(gdf) == 0:
        print("No watercourses in border region")
        return None

    # For linear features, calculate length
    gdf_projected = gdf.to_crs('ESRI:102008')
    gdf['length_km'] = gdf_projected.geometry.length / 1000

    # Filter by minimum length (10km for major rivers)
    major_rivers = gdf[gdf['length_km'] >= 10].copy()
    print(f"  Major rivers (>= 10 km): {len(major_rivers)} features")

    # Print some stats
    print(f"\n  Longest watercourses:")
    for _, row in gdf.nlargest(10, 'length_km').iterrows():
        name = row.get('NAMELK1EN') or row.get('NAMELK1FR') or row.get('NAME') or 'Unnamed'
        print(f"    {name}: {row['length_km']:.1f} km")

    return major_rivers


def process_water_linear_flow():
    """Process water_linear_flow_1.shp (river centerlines)."""
    print("\n" + "=" * 60)
    print("PROCESSING WATER LINEAR FLOW")
    print("=" * 60)

    shp_path = CANVEC_DIR / 'water_linear_flow_1.shp'
    if not shp_path.exists():
        print(f"ERROR: {shp_path} not found")
        return None

    gdf = load_shapefile(shp_path)
    gdf = filter_to_border_region(gdf)

    if len(gdf) == 0:
        print("No water linear flow in border region")
        return None

    return gdf


def export_geojson(gdf, output_path, name):
    """Export GeoDataFrame to GeoJSON."""
    if gdf is None or len(gdf) == 0:
        print(f"Skipping {name} - no features")
        return

    # Simplify geometry for smaller file size
    gdf = gdf.copy()
    gdf['geometry'] = gdf['geometry'].simplify(0.001, preserve_topology=True)

    # Convert to GeoJSON
    geojson = json.loads(gdf.to_json())
    geojson['name'] = name
    geojson['feature_count'] = len(gdf)

    with open(output_path, 'w') as f:
        json.dump(geojson, f)

    size_kb = output_path.stat().st_size / 1024
    print(f"Exported {name}: {len(gdf)} features, {size_kb:.1f} KB")


def main():
    print("=" * 70)
    print("CANVEC HYDRO DATA PROCESSOR - BORDER REGION")
    print("=" * 70)
    print(f"\nSource: {CANVEC_DIR}")
    print(f"Bounding box: {BORDER_BBOX}")

    output_dir = Path(__file__).parent.parent / 'docs' / 'json'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each layer
    waterbodies = process_waterbodies()
    watercourses = process_watercourses()

    # Export
    print("\n" + "=" * 60)
    print("EXPORTING FILES")
    print("=" * 60)

    export_geojson(
        waterbodies,
        output_dir / 'quebec_lakes.json',
        'Quebec Lakes (Border Region)'
    )

    export_geojson(
        watercourses,
        output_dir / 'quebec_rivers.json',
        'Quebec Rivers (Border Region)'
    )

    # Combined hydro
    if waterbodies is not None and watercourses is not None:
        import pandas as pd
        combined = gpd.GeoDataFrame(pd.concat([waterbodies, watercourses], ignore_index=True))
        combined = combined.set_crs('EPSG:4326')
        export_geojson(
            combined,
            output_dir / 'quebec_hydro.json',
            'Quebec Hydro (Border Region)'
        )

    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
